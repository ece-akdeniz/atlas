"""Bounded, deterministic collection. Source HTML is data, never instructions."""
import hashlib, json, re, socket, ipaddress, time, urllib.robotparser
from urllib.parse import urlsplit, urljoin
from datetime import datetime, timedelta, timezone
import urllib3
from bs4 import BeautifulSoup
from portal import db
from portal.model import tags, validate
from portal.extraction import VERSION, enrich, recognize_skills
AGENT='AtlasOpportunityPortal/2.0'
MAX_BYTES=2_000_000
class SourceError(Exception): pass

def safe_url(url):
    p=urlsplit(url)
    if p.scheme!='https' or not p.hostname or p.username or p.password or p.port not in (None,443): raise SourceError('Only public HTTPS sources on port 443 are supported')
    addresses=socket.getaddrinfo(p.hostname,443,type=socket.SOCK_STREAM)
    ips=sorted(set(a[4][0] for a in addresses))
    if not ips or any(not ipaddress.ip_address(ip).is_global for ip in ips): raise SourceError('Private or reserved network destination blocked')
    return p,ips[0]

def fetch(url,headers=None,redirects=0,allow_missing=False):
    if redirects>3: raise SourceError('Too many redirects')
    p,ip=safe_url(url)
    # Pin the validated IP while validating TLS against the original hostname.
    pool=urllib3.HTTPSConnectionPool(ip,port=443,server_hostname=p.hostname,assert_hostname=p.hostname,cert_reqs='CERT_REQUIRED',timeout=urllib3.Timeout(connect=8,read=15))
    path=p.path or '/'
    if p.query: path+='?'+p.query
    try:
        r=pool.urlopen('GET',path,headers={'Host':p.hostname,'User-Agent':AGENT,'Accept':'text/html,application/json,application/pdf;q=0.8','Accept-Encoding':'identity',**(headers or {})},redirect=False,retries=False,preload_content=False)
        if r.status in [301,302,303,307,308]:
            target=urljoin(url,r.headers.get('Location',''))
            # Redirect target receives fresh network and robots validation.
            if not allow_missing: robots(target)
            return fetch(target,headers,redirects+1,allow_missing)
        raw=r.read(MAX_BYTES+1)
        if len(raw)>MAX_BYTES: raise SourceError('Response exceeds 2 MB budget')
        if r.status not in ([200,304,404,410] if allow_missing else [200,304]): raise SourceError('HTTP '+str(r.status)+'; last known records preserved')
        return r.status,dict(r.headers),raw
    finally: pool.close()

def robots_allowed(policy,url):
    groups=[]; agents=[]; rules=[]; delay=1; seen_rules=False
    for line in policy.splitlines():
        line=line.split('#',1)[0].strip()
        if ':' not in line: continue
        key,value=[v.strip() for v in line.split(':',1)]; key=key.lower()
        if key=='user-agent':
            if seen_rules:
                groups.append((agents,rules,delay));agents=[];rules=[];delay=1;seen_rules=False
            agents.append(value.lower())
        elif key in ['allow','disallow','crawl-delay'] and agents:
            seen_rules=True
            if key=='crawl-delay':
                try: delay=max(1,float(value))
                except ValueError: pass
            elif value: rules.append((key,value))
    groups.append((agents,rules,delay))
    specific=[g for g in groups if any(a!='*' and a in AGENT.lower() for a in g[0])]
    selected=specific or [g for g in groups if '*' in g[0]]
    path=urlsplit(url).path or '/'
    if urlsplit(url).query: path+='?'+urlsplit(url).query
    matches=[]
    for _,rs,_ in selected:
        for action,pattern in rs:
            suffix='$' if pattern.endswith('$') else ''
            expr='^'+re.escape(pattern.removesuffix('$')).replace(r'\*','.*')+suffix
            if re.search(expr,path): matches.append((len(pattern.replace('*','').rstrip('$')),action=='allow'))
    return (max(matches)[1] if matches else True),max([g[2] for g in selected] or [1])

def robots(url):
    p=urlsplit(url); origin=f'{p.scheme}://{p.netloc}'
    try: code,_,body=fetch(origin+'/robots.txt',allow_missing=True)
    except Exception as e: raise SourceError('Cannot verify robots policy: '+str(e))
    if code in [404,410]: return
    allowed,delay=robots_allowed(body.decode('utf-8','replace'),url)
    if not allowed: raise SourceError('Collection disallowed by robots.txt')
    if delay>30: raise SourceError('Crawl delay exceeds worker budget; adapter needs scheduling review')
    time.sleep(max(1,delay))

def text(node): return ' '.join(BeautifulSoup(str(node or ''),'html.parser').get_text(' ',strip=True).split())

def jsonld(html,url):
    soup=BeautifulSoup(html,'html.parser'); entries=[]
    def walk(value):
        if isinstance(value,list):
            for v in value: walk(v)
        elif isinstance(value,dict):
            kind=value.get('@type',[]); kind=[kind] if isinstance(kind,str) else kind
            if any(t in kind for t in ['JobPosting','Event']): entries.append(value)
            for k in ['@graph','itemListElement','item']:
                if k in value: walk(value[k])
    for script in soup.find_all('script',type='application/ld+json'):
        try: walk(json.loads(script.string or script.get_text()))
        except (ValueError,TypeError): continue
    result=[]
    for e in entries[:30]:
        title=text(e.get('title') or e.get('name')); desc=text(e.get('description'))
        if not title or not desc: continue
        kind=e.get('@type'); event='Event' in (kind if isinstance(kind,list) else [kind])
        loc=e.get('location') if event else e.get('jobLocation'); loc=loc[0] if isinstance(loc,list) and loc else loc or {}
        address=loc.get('address',{}) if isinstance(loc,dict) else {}; address=address if isinstance(address,dict) else {}
        org=e.get('organizer') if event else e.get('hiringOrganization'); org=org[0] if isinstance(org,list) and org else org or {}
        research=bool(re.search(r'thesis|masterarbeit|abschlussarbeit|semester.?project',title,re.I))
        country=address.get('addressCountry'); country=country.get('name') if isinstance(country,dict) else country
        country={'DE':'Germany','CH':'Switzerland'}.get(country,country)
        record={'title':title,'organization':text(org.get('name')) or urlsplit(url).hostname,'url':url,'application_url':urljoin(url,e.get('url') or url),'category':'events' if event else 'research' if research else 'jobs','type':'Event' if event else 'Thesis' if research else 'Internship' if 'intern' in title.lower() or 'praktik' in title.lower() else 'Working student' if 'werkstudent' in title.lower() or 'working student' in title.lower() else 'Role','summary':desc[:320]+'…' if len(desc)>320 else desc,'tags':tags(title+' '+desc),'city':address.get('addressLocality'),'country':country,'published':e.get('datePosted'),'deadline':e.get('validThrough'),'event_start':e.get('startDate'),'event_end':e.get('endDate'),'workload':e.get('employmentType'),'status':'open','extraction_version':VERSION,'evidence_method':'Deterministic JSON-LD; original description available at source','required':[text(e['qualifications'])] if e.get('qualifications') else [],'skills':[],'preferred':[],'activities':[],'languages':{},'questions':['Structured feed does not separate all requirements; inspect the original posting.']}
        ident=e.get('identifier'); record['publisher_id']=str(ident.get('value')) if isinstance(ident,dict) and ident.get('value') else None
        validate(record); result.append(record)
    return result

def rpg(html,url):
    soup=BeautifulSoup(html,'html.parser'); records=[]
    for heading in soup.find_all(['h2','h3','h4']):
        title=heading.get_text(' ',strip=True)
        if not any(mark in title for mark in [' - Available',' - Taken',' - Closed']): continue
        contents=[]
        for sibling in heading.next_siblings:
            if getattr(sibling,'name',None) in ['h2','h3','h4']: break
            contents.append(str(sibling))
        desc=text(' '.join(contents))
        if len(desc)<60: continue
        clean=re.sub(r' - (Available|Taken|Closed).*$', '',title).strip()
        key=re.sub(r'[^a-z0-9]+','-',clean.lower()).strip('-')
        record={'title':clean,'organization':'University of Zurich','publisher':'University of Zurich','academic_affiliations':['University of Zurich · Robotics and Perception Group'],'department':'Robotics and Perception Group','partners':re.findall(r'in collaboration with ([^)]+)',clean),'category':'research','type':'Master’s thesis / semester project' if 'Semester Project' in desc else 'Master’s thesis','url':url,'identity_url':url+'#'+key,'publisher_id':'rpg-'+key,'summary':clean,'city':'Zurich','country':'Switzerland','tags':tags(clean+' '+desc),'external_students':'not_stated','status':'open' if ' - Available' in title else 'closed','evidence_method':'Project-specific sections on the official RPG page','questions':['Confirm external-student access and home-university supervision.']}
        enrich(record,' '.join(contents),section=clean)
        sirop=BeautifulSoup(' '.join(contents),'html.parser').find('a',href=re.compile(r'https://sirop.org/app/'))
        if sirop:record['publisher_identifiers']={'sirop':sirop['href'].rstrip('/').split('/')[-1],'rpg':record['publisher_id']}
        # Stable legacy ID preserves notes; the SiROP ID is retained for cross-source reconciliation.
        validate(record); records.append(record)
    return records

def hackatum(html,url):
    from portal.seed import RECORDS
    body=text(BeautifulSoup(html,'html.parser').get_text(' ',strip=True))
    timing=re.search(r'hackaTUM (20\d{2}) will take place on ([A-Za-z]+) (\d{1,2})[-–](\d{1,2})',body)
    if not timing: raise SourceError('Event dates not recognized; review required')
    year,month,a,b=timing.groups()
    month_number=datetime.strptime(month,'%B').month
    r=next(dict(r) for sid,r in RECORDS if sid=='hackatum')
    r['title']='hackaTUM '+year
    r['publisher_id']='hackatum-'+year
    r['summary']='An on-site hackathon with partner challenges. Check the organizer’s current participation and application rules.'
    r['city']='Garching' if 'on-site in Garching' in body else None
    r['metro']='Munich'
    r['record_kind']='event'
    r['extraction_complete']=True
    r['event_start']=f'{year}-{month_number:02d}-{int(a):02d}'
    r['event_end']=f'{year}-{month_number:02d}-{int(b):02d}'
    r['fees']='No participation fee' if 'There are no participation fees' in body else None
    r['open_to_all']='open for everyone' in body
    r['external_students']='yes' if r['open_to_all'] else 'not_stated'
    r['funding_confirmed']=all(x in body for x in ['free food and drinks','cannot provide travel reimbursements','sleeping rooms','We do not provide accommodation'])
    if not r['funding_confirmed']: r['funding']=None
    if 'between 2 and 4 members' not in body: r['team']=None
    if 'language of the event is English' not in body: r['languages']={}
    if 'everyone has to apply individually' not in body: r['application_method']=None
    r['extraction_version']=VERSION
    r['evidence_method']='Deterministic official FAQ date and clause checks; unknown clauses left unconfirmed'
    r['questions']=['Confirm application deadline and current technical tracks.']
    if re.search(r'notification[^.]{0,100}2025',body): r['questions'].append('FAQ includes an outdated 2025 notification date; confirm the current application timeline.')
    return [r]

def collect_source(s):
    url=s['url']; robots(url)
    with db.connect() as c: cached=c.execute('SELECT * FROM cache WHERE url=?',(url,)).fetchone()
    headers={}
    if cached and cached['version']==VERSION and s['adapter'] in ['rpg','hackatum','jsonld','tumai','lever']:
        if cached['etag']: headers['If-None-Match']=cached['etag']
        if cached['modified']: headers['If-Modified-Since']=cached['modified']
    status,h,raw=fetch(url,headers)
    digest=hashlib.sha256(raw).hexdigest()
    at=db.now()
    if cached and s['adapter'] in ['rpg','hackatum','jsonld','tumai','lever'] and (status==304 or (digest==cached['hash'] and cached['version']==VERSION)):
        records=json.loads(cached['data'])
        for r in records: db.upsert(r,s['id'],at)
        return len(records),'Unchanged; cached validated extraction'
    html=raw.decode('utf-8','replace')
    if any(x in html.lower() for x in ['cf-chl-platform','captcha challenge','verify you are human']): raise SourceError('Access challenge detected; no bypass attempted')
    adapter=s['adapter']
    if adapter=='hackatum': records=hackatum(html,url)
    elif adapter=='rpg': records=rpg(html,url)
    elif adapter=='jsonld': records=jsonld(html,url)
    elif adapter in ['dlr','tum-cvg','tum-srl','iff','tumai','lever','eth-projects','fraunhofer','cyber']:
        from portal.adapters import collect
        records,note=collect(s,html)
    else: records=[]
    if adapter in ['rpg','jsonld','hackatum','dlr','tum-cvg','tum-srl','iff','eth-projects','fraunhofer','cyber'] and not records: raise SourceError('No valid records extracted; page format may have changed')
    note=locals().get('note') or 'Extracted '+str(len(records))+' records'
    if adapter=='reviewed':
        existing=[r for r in db.rows() if any(e['source_id']==s['id'] for e in r['sources'])]
        # HTML fetch success cannot certify older manually reviewed field values.
        for old in existing:
            with db.connect() as c:
                original=json.loads(c.execute('SELECT data FROM opportunities WHERE id=?',(old['id'],)).fetchone()['data'])
            original['verification_warning']='Source fetched; structured details await review of current content.'
            # Retain last substantive verification date.
            db.upsert(original,s['id'],old['verified'])
        note='Reachable; structured details need review' if existing else 'Reachable; no listing parser configured'
    if adapter=='discovery':
        links=[]
        for a in BeautifulSoup(html,'html.parser').find_all('a',href=True):
            target=urljoin(url,a['href'])
            if urlsplit(target).scheme=='https' and re.search(r'thesis|project|student|sirop|\.pdf',target,re.I): links.append({'url':target,'title':text(a)[:160]})
        db.set_meta('candidates:'+s['id'],links[:25]); note=f'{len(links[:25])} candidate links stored; review required before following'
    identities=set()
    previous_records=db.rows()
    for record in records:
        old=next((r for r in previous_records if r.get('publisher_id')==record.get('publisher_id') and r.get('organization')==record.get('organization')),None)
        failed_documents=any(doc.get('status')=='Failed' for doc in record.get('documents',[]))
        if failed_documents:
            record['verification_warning']='Document collection incomplete; last known details retained where available.'
            if old:
                for field in ['required','preferred','activities','contacts','application_method','materials','research_question']:
                    if not record.get(field) and old.get(field):
                        record[field]=old[field]
                        record['field_states'][field]={'state':'incomplete'}
                        if old.get('field_evidence',{}).get(field):record['field_evidence'][field]=old['field_evidence'][field]
        identities.add(db.upsert(record,s['id'],old['verified'] if failed_documents and old else at))
    if records and adapter in ['rpg','dlr','iff','fraunhofer','lever','eth-projects','tum-cvg','tum-srl','tumai']:

        for old in db.rows():
            if old['id'] not in identities and any(e['source_id']==s['id'] for e in old['sources']):
                with db.connect() as c: original=json.loads(c.execute('SELECT data FROM opportunities WHERE id=?',(old['id'],)).fetchone()[0])
                original['verification_warning']='Not present in the latest successful collection; current availability requires confirmation.'
                db.upsert(original,s['id'],old['verified'])
    with db.connect() as c: c.execute('INSERT INTO cache VALUES(?,?,?,?,?,?,?) ON CONFLICT(url) DO UPDATE SET hash=excluded.hash,etag=excluded.etag,modified=excluded.modified,version=excluded.version,data=excluded.data,checked=excluded.checked',(url,digest,h.get('ETag'),h.get('Last-Modified'),VERSION,json.dumps(records),at))
    return len(records),note

def refresh(force=False):
    import os
    from portal.seed import bootstrap
    bootstrap(); epoch=int(time.time())
    due=[s for s in db.sources() if s.get('enabled') and s['adapter']!='pending' and (not s.get('next_due') or s['next_due']<=db.now())]
    if not due: return []
    with db.connect() as c:
        c.execute('DELETE FROM locks WHERE until<?',(epoch,))
        try: c.execute('INSERT INTO locks VALUES(?,?)',('refresh',epoch+3600))
        except Exception: return {'status':'busy'}
        cursor=c.execute('INSERT INTO runs(started,status) VALUES(?,?)',(db.now(),'running')); run_id=cursor.lastrowid
    results=[]
    try:
        for s in due:
            if not s.get('enabled') or s['adapter']=='pending': continue
            # A manual run does not override source-specific backoff/rate limits.
            if s.get('next_due') and s['next_due']>db.now(): continue
            db.set_meta('worker_heartbeat',db.now())
            count=0; error=None
            try: count,note=collect_source(s)
            except Exception as e: error=str(e)[:500]; note=error
            at=db.now(); failures=s['failures']+1 if error else 0
            delay=min(72,2**min(failures,6)) if error else s.get('interval_hours',24)
            due=(datetime.now(timezone.utc)+timedelta(hours=delay)).isoformat(timespec='seconds')
            d={k:v for k,v in s.items() if k not in ['id','last_attempt','last_success','error','failures','next_due']}; d['status']='Failing' if error else 'Supported' if count>0 else 'Needs review' if s['adapter']=='reviewed' else 'No listings collected'; d['last_result']=note;
            if not error and not note.startswith('Unchanged'):d['collection_report']=note
            d['last_record_count']=count; d['operational']=bool(count and not error)
            with db.connect() as c: c.execute('UPDATE sources SET data=?,last_attempt=?,last_success=?,error=?,failures=?,next_due=? WHERE id=?',(json.dumps(d),at,s['last_success'] if error else at,error,failures,due,s['id']))
            results.append({'source':s['id'],'records':count,'error':error})
        with db.connect() as c: c.execute('UPDATE runs SET finished=?,status=?,detail=? WHERE id=?',(db.now(),'partial' if any(x['error'] for x in results) else 'complete',json.dumps(results),run_id))
        return results
    finally:
        with db.connect() as c: c.execute("DELETE FROM locks WHERE name='refresh'")
