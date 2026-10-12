"""Official ATS adapters. Complete public feeds, bounded relevant detail traversal."""
import json,re,html,io
from urllib.parse import urljoin,urlsplit
from bs4 import BeautifulSoup
from pypdf import PdfReader
from portal import db
from portal.adapters import base,document,evidence
from portal.extraction import enrich,clean,recognize_skills,pdf_details,sentences
from portal.model import tags
SOURCES=[
 ('quantum-systems','Quantum Systems','https://career.quantum-systems.com/api/offers','recruitee'),
 ('sereact','Sereact','https://jobs.ashbyhq.com/sereact','ashby-html'),
 ('wingtra','Wingtra','https://api.lever.co/v0/postings/wingtra-2?mode=json','lever-feed'),
 ('auterion','Auterion','https://boards-api.greenhouse.io/v1/boards/auterion/jobs?content=true','greenhouse'),
 ('flyability','Flyability','https://www.workable.com/api/accounts/flyability?details=true','workable'),
 ('destinus','Destinus','https://www.workable.com/api/accounts/destinusgroup?details=true','workable'),
 ('neura','NEURA Robotics','https://jobs.neura-robotics.com/category/ai/58bd0246-cfdb-4930-b2f3-bc758471b5a6','neura-html'),
 ('dufour','Dufour Aerospace','https://join.com/companies/dufour','join-html'),
 ('eth-agentic-systems','ETH Agentic Systems Lab','https://agenticsystems.ethz.ch/','agentic-route'),
 ('node','NODE Robotics','https://node-robotics-gmbh.jobs.personio.de/?language=en','personio-html'),
 ('skydio','Skydio','https://www.skydio.com/careers','skydio-html'),
 ('verity-studios','Verity Studios','https://www.veritystudios.com/careers','verity-html'),
 ('807d62512a4a','FIUS · employer postings & PDFs','https://www.fius.de/en/aushang/','fius-pdf'),
]
TECH=r'robot|autonom|computer vision|deep learning|machine learning|perception|navigation|slam|sensor|flight|control|state estimation|software|mechatronic|agentic|rag\b|ki-|künstliche'
STUDENT=r'intern|student|trainee|thes[ei]s|masterarbeit|praktik|werkstudent|junior|graduate'
SENIOR=r'senior|principal|lead\b|head\b|director|staff\b|manager|sales|marketing|recruit|finance|account|devops|business'
def relevant(title):return bool(re.search(TECH,title,re.I)) and not re.search(SENIOR,title,re.I) or bool(re.search(STUDENT,title,re.I) and re.search(r'engineering|r&d|industrialization|electronics',title,re.I)) and not re.search(SENIOR,title,re.I)
def appdata(raw):
    m=re.search(r'window\.__appData\s*=\s*',raw)
    if not m:raise ValueError('Ashby public page data missing')
    return json.JSONDecoder().raw_decode(raw[m.end():])[0]
def role(s,title,url,identity,body,city=None,country=None,requirements=None,employment=None):
    category='research' if re.search(r'thes[ei]s|masterarbeit|bachelorarbeit',title,re.I) else 'jobs'
    city=clean(city) or None
    if city in ['Zürich','Zurich ']:city='Zurich'
    if city in ['München']:city='Munich'
    r=base(title,url,s['name'],city,category);r['organization_id']=s['id'];r['publisher_id']=str(identity);r['employer']=s['name'];r['publisher']=s['name'];r['country']=country
    r['metro']='Munich' if city and re.search(r'Gilching|Garching|Oberpfaffenhofen|Munich',city,re.I) else 'Stuttgart' if city and re.search(r'Stuttgart|Metzingen|Schönaich|Weissach',city,re.I) else 'Zurich' if city and re.search(r'Zurich|Zürich|Dübendorf',city,re.I) else city
    r['type']='Master’s thesis' if category=='research' else 'Working student' if re.search(r'working student|werkstudent',title,re.I) else 'Internship' if re.search(r'intern|praktik|trainee',title,re.I) else 'Full-time role' if re.search('full.?time',str(employment),re.I) else 'Role'
    content=html.unescape(body or '');enrich(r,content,complete=True);plain=BeautifulSoup(content,'html.parser').get_text('\n',strip=True)
    # Section headings vary across ATSs; retain their actual local evidence.
    soup=BeautifulSoup(content,'html.parser')
    for heading in soup.find_all(['h1','h2','h3','h4','strong','b']):
        label=clean(heading.text);field='required' if re.search(r'require|qualification|bring|your profile|who you are|what you have|looking for|background',label,re.I) else 'activities' if re.search(r'responsib|your role|you.ll do|you will|your mission|day to day mission|tasks|challenge',label,re.I) else None
        if not field or len(label)>120:continue
        bits=[]
        for nxt in heading.find_all_next():
            if nxt.name in ['h1','h2','h3','h4'] or nxt.name in ['strong','b'] and re.search(r'require|responsib|benefit|offer|bring',nxt.text,re.I):break
            if nxt.name=='li':bits.append(clean(nxt.text))
        if bits:evidence(r,field,list(dict.fromkeys(bits)), ' '.join(bits),label)
    if requirements:
        reqs=BeautifulSoup(html.unescape(requirements),'html.parser');vals=[clean(x.text) for x in reqs.select('li')] or sentences(reqs.get_text('\n',strip=True));evidence(r,'required',vals,' '.join(vals),'Requirements')
    preferred=[x for x in r.get('required',[]) if re.search(r'plus|preferred|advantage|bonus|nice.to.have|idealerweise',x,re.I)]
    if preferred:r['required']=[x for x in r['required'] if x not in preferred];evidence(r,'preferred',preferred,' '.join(preferred),'Preferred qualifications')
    r['required_skills']=recognize_skills(' '.join(r['required']));r['tags']=tags(title+' '+plain)
    if r.get('activities'):r['summary']=r['activities'][0][:360]
    else:r['summary']=next((clean(x)[:360] for x in plain.splitlines() if re.search(r'you will|your role|your mission|develop|implement',x,re.I) and len(x)>45),title)
    for field in ['required','activities']:
        if not r.get(field) and len(plain)>300:r['field_states'][field]={'state':'incomplete'};r['extraction_complete']=False
    for lang in ['English','German']:
        matches=[x for x in sentences(plain) if re.search(r'\b'+lang+r'\b',x) and re.search(r'fluent|proficien|good|native|excellent|basic|B[12]|C[12]',x,re.I)]
        if matches:r.setdefault('languages',{})[lang]=' '.join(matches)[:400]
    hours=re.search(r'\b(\d{1,2})(?:\s*[–-]\s*(\d{1,2}))?\s*(?:hours?\s*(?:per|a|/)\s*week|h/week|Stunden)',plain,re.I)
    german_hours=re.search(r'(\d{1,2})\s*bis\s*(\d{1,2})\s*h/Woche',plain,re.I)
    if german_hours:evidence(r,'hours',int(german_hours[2]),german_hours[0],'Workload')
    if hours:evidence(r,'hours',int(hours[2] or hours[1]),hours[0],'Workload')
    restrictions=[x for x in sentences(plain) if re.search(r'citizen|nationality|work permit|work authori[sz]|visa|enroll|immatrikul|studying|enrolled',x,re.I)]
    if restrictions:evidence(r,'eligibility_requirements',restrictions,' '.join(restrictions),'Published eligibility conditions')
    if re.search(r'EU citizen|citizenship.*EU|EU.*citizenship',plain,re.I):r['nationality_restriction']='EU citizenship required';r['questions']=['Published EU citizenship restriction conflicts with Turkish citizenship; confirm before applying.'];r['explicit_conflict']='EU citizenship required'
    app=[x for x in sentences(plain) if re.search(r'send|upload|submit|attach|apply with|please include',x,re.I) and re.search(r'CV|resume|résumé|transcript|letter|project|portfolio|start date',x,re.I)]
    if app:evidence(r,'application_method',' '.join(app),' '.join(app),'Application instructions')
    if r['type']=='Full-time role':r['workload']='Full-time; weekly hours not stated';r.setdefault('questions',[]).append('Future option: confirm graduation and full-time availability.')
    return r

def collect(s,raw):
    adapter=s['adapter'];records=[];seen=set();total=0
    if adapter in ['recruitee','workable','greenhouse','lever-feed']:
        payload=json.loads(raw);rows=payload if isinstance(payload,list) else payload.get('offers',payload.get('jobs',[]));total=len(rows)
        for item in rows:
            title=item.get('title',item.get('text',''));identity=item.get('shortcode',item.get('id'));city=item.get('city') or item.get('location',{}).get('name') or item.get('categories',{}).get('location');country=item.get('country')
            if identity in seen or not relevant(title):continue
            seen.add(identity)
            if re.search(r'United States|USA|Washington|California|Virginia|San Mateo|San Francisco',str(city)+' '+str(country),re.I):continue
            body=item.get('description') or item.get('content') or ''
            for block in item.get('lists',[]):body+='<h2>'+block.get('text','')+'</h2>'+block.get('content','')
            body+=item.get('additional','')
            url=item.get('careers_url') or item.get('absolute_url') or item.get('hostedUrl') or item.get('url')
            r=role(s,title,url,identity,body,city,country,item.get('requirements'),item.get('employment_type') or item.get('employment_type_code') or item.get('categories',{}).get('commitment'))
            r['application_url']=item.get('careers_apply_url') or item.get('applyUrl') or item.get('application_url') or url
            r['published']=(item.get('published_at') or item.get('published_on') or item.get('first_published') or '')[:10] or None
            if item.get('max_hours_per_week'):
                evidence(r,'hours',float(item['max_hours_per_week']),str(item['min_hours_per_week'])+'–'+str(item['max_hours_per_week']),'Published ATS min/max hours')
                if r['type']=='Working student' and r['hours']>20:r['questions']=r.get('questions',[])+['Publisher labels this Working student but specifies over 20 hours; confirm workload.']
            if s['id']=='destinus' and 'Daedalean' in body:r['partners']=['Daedalean'];r['employer']='Destinus / Daedalean (as named in posting)'
            r['all_locations']=item.get('locations',[])
            records.append(r)
    elif adapter=='ashby-html':
        rows=appdata(raw)['jobBoard']['jobPostings'];total=len(rows)
        for item in rows:
            if not relevant(item['title']):continue
            url=s['url'].rstrip('/')+'/'+item['id'];p=appdata(document(url).decode())['posting']
            if p.get('isListed') is False:continue
            r=role(s,p['title'],url,p['id'],p['descriptionHtml'],p.get('locationName'),None,employment=p.get('employmentType'));r['application_url']=url+'/application';records.append(r)
    elif adapter=='verity-html':
        soup=BeautifulSoup(raw,'html.parser');cards=soup.select('.job[data-type]');total=len(cards)
        if total>20:raise ValueError('Verity exceeds 20 detail pages; review required')
        for card in cards:
            a=card.select_one('a[href]');title=clean(card.select_one('h3').text)
            if not relevant(title) and 'spontaneous' not in title.lower():continue
            url=urljoin(s['url'],a['href']);identity=a['href'].rstrip('/').split('/')[-1]
            detail=BeautifulSoup(document(url),'html.parser').find(attrs={'data-id':identity})
            if not detail:raise ValueError('Verity role-specific content missing; previous records retained')
            r=role(s,title,url,identity,str(detail),None,None,employment=card['data-type'])
            apply=next((a['href'] for a in detail.select('a[href]') if 'breezy.hr/p/' in a['href']),None)
            if apply:r['application_url']=apply
            r['questions']=r.get('questions',[])+['Role-specific location not stated on the source section; confirm with the linked application portal.']
            if 'spontaneous' in title.lower():r['record_kind']='application_route';r['status']='unverified';r['summary']='Published speculative-application route. No particular vacancy or employer interest is implied.'
            records.append(r)
    elif adapter=='agentic-route':
        soup=BeautifulSoup(raw,'html.parser');a=next((a for a in soup.select('a[href]') if 'AI-Research-Track-Student-Applications' in a['href']),None)
        if not a:raise ValueError('Student research-track link missing; route needs review')
        r=base('AI Research Track · student application route',s['url'],s['name'],'Zurich','research','academic_route');r['publisher_id']='ai-research-track';r['organization_id']=s['id'];r['summary']='Published route to the Agentic Systems Lab student research track. Individual projects and external-student access require confirmation.';r['application_url']=urljoin(s['url'],a['href']);r['status']='unverified';r['extraction_complete']=False;r['field_states']={k:{'state':'incomplete'} for k in ['required','activities','application_method']};r['verification_warning']='Linked track details are not extracted; this is an academic route, not a verified opening';records=[r];total=1
    elif adapter in ['personio-html','skydio-html','neura-html','join-html']:
        soup=BeautifulSoup(raw,'html.parser');links={}
        if adapter=='neura-html':
            visited={s['url']};pending=[urljoin(s['url'],a['href']) for a in soup.select('a[data-page][href],a[data-action="next"][href]')]
            while pending:
                page_url=pending.pop(0)
                if page_url in visited:continue
                if len(visited)>=8:raise ValueError('NEURA exceeds eight index pages; pagination review required')
                visited.add(page_url);page=BeautifulSoup(document(page_url),'html.parser')
                pending.extend(urljoin(page_url,a['href']) for a in page.select('a[data-page][href],a[data-action="next"][href]') if urljoin(page_url,a['href']) not in visited)
                soup.append(page)
        for a in soup.select('a[href]'):
            pattern='/job/' if adapter=='personio-html' else '/offer/' if adapter=='neura-html' else '/companies/dufour/' if adapter=='join-html' else '/jobs/'
            if pattern not in a['href']:continue
            u=urljoin(s['url'],a['href']);text=clean(a.parent.text if adapter=='skydio-html' else a.text)
            if len(text)>len(links.get(u,'')):links[u]=text
        candidates=[(u,t) for u,t in links.items() if relevant(t) and (adapter!='skydio-html' or re.search('Zurich|Zürich',t))];total=len(links)
        if len(candidates)>35:raise ValueError('Coverage limit: more than 35 relevant details')
        for url,title in candidates:
            soup=BeautifulSoup(document(url),'html.parser');job=None
            for script in soup.select('script[type="application/ld+json"]'):
                try:
                    data=json.loads(script.string or script.text);entries=data if isinstance(data,list) else data.get('@graph',[data])
                    job=next((v for v in entries if v.get('@type')=='JobPosting'),job)
                except (ValueError,AttributeError):continue
            if job:
                loc=job.get('jobLocation',{});loc=loc[0] if isinstance(loc,list) else loc;addr=loc.get('address',{});r=role(s,job['title'],url,urlsplit(url).path.rstrip('/').split('/')[-1],job.get('description',''),addr.get('addressLocality'),addr.get('addressCountry'),employment=str(job.get('employmentType')));r['published']=job.get('datePosted');r['application_url']=url
            else:
                main=soup.select_one('main') or soup;h=main.find('h1')
                if not h:raise ValueError('Detail title missing')
                r=role(s,clean(h.text),url,urlsplit(url).path.rstrip('/').split('/')[-1],str(main),'Zurich' if adapter=='skydio-html' else None);r['extraction_complete']=False;r['verification_warning']='Application requirements extraction needs review'
            records.append(r)
    elif adapter=='fius-pdf':
        soup=BeautifulSoup(raw,'html.parser');cards=soup.select('a.proj-card[data-category]');total=len(cards)
        for card in cards:
            title=clean(card.select_one('h3').text)
            if not relevant(title):continue
            url=urljoin(s['url'],card['href']);pdf=PdfReader(io.BytesIO(document(url)));pages=[p.extract_text() or '' for p in pdf.pages];text='\n'.join(pages);text=re.sub(r'(?m)^.*20260909_AURONIQ.*$|^AI_de_v01.*$|^Seite \d+.*$','',text);org=clean(card.select_one('.proj-card-meta').text)
            r=role({**s,'name':org},title,url,url, pdf_details(text),None,None)
            r['publisher']='FIUS';
            if 'J000021458' in text:
                req=text.split('Studiengänge',1)[-1].split('Literaturrecherche',1)[0];acts=text.split('Literaturrecherche',1)[-1].split('Grundlegendes Verständnis',1)[0]
                evidence(r,'required',sentences(req)+(['Grundlegendes Verständnis'+text.split('Grundlegendes Verständnis',1)[1].split('Dr. Ing.',1)[0]] if 'Grundlegendes Verständnis' in text else []),req,'Anforderungen',page=1)
                evidence(r,'activities',sentences('Literaturrecherche'+acts),acts,'Aufgaben',page=1)
                r['publisher_id']='J000021458';r['employer']='Porsche AG';r['extraction_complete']=True;r['summary']=r['activities'][0][:360] if r.get('activities') else r['summary']
            r['academic_affiliations']=[];r['organization_id']=org.lower();r['originating_page']=s['url'];r['documents']=[{'url':url,'originating_page':s['url'],'pages':len(pages),'status':'Extracted','date_evidence':clean(card.select_one('.proj-card-foot').text) if card.select_one('.proj-card-foot') else 'Not stated'}]
            for city in ['Schönaich','Weissach','Stuttgart','Nürtingen']:
                if city in text:r['city']=city;r['metro']='Stuttgart';r['country']='Germany';break
            r['status']='unverified';r['verification_warning']='Published PDF found on current board; recruitment status not explicitly confirmed'
            for field,ev in r['field_evidence'].items():ev['page']=next((i+1 for i,t in enumerate(pages) if ev.get('excerpt','')[:50] in clean(t)),None)
            records.append(r)
    else:raise ValueError('Unsupported startup adapter')
    return records,f'{len(records)} relevant validated records from {total} published entries; official publisher IDs; no title-only quota. All index entries inspected; eligible detail pages followed.'

def upgrade():
    if db.get_meta('startup_registry')=='3':return
    with db.connect() as c:
        for identity,name,url,adapter in SOURCES:
            data={'name':name,'url':url,'adapter':adapter,'category':'research' if identity=='807d62512a4a' else 'jobs','enabled':True,'interval_hours':24,'status':'Pending first collection','organization_id':identity,'coverage':'Official feed or bounded index-to-detail collector; excludes senior and unrelated roles.','operational':False}
            c.execute('INSERT INTO sources(id,data) VALUES(?,?) ON CONFLICT(id) DO UPDATE SET data=excluded.data,next_due=NULL',(identity,json.dumps(data)))
        aliases={'a4c63ea3bfa3':('tum-cvg','Covered by TUM CVG project collector; homepage retained as source history.'),'daedalean':('destinus','Shared official Destinus board; Daedalean affiliation retained when named in the posting.')}
        for identity,(target,note) in aliases.items():
            old=c.execute('SELECT data FROM sources WHERE id=?',(identity,)).fetchone();d=json.loads(old[0]) if old else {'name':'Daedalean','url':'https://daedalean.ai/careers','category':'jobs','interval_hours':24}
            d.update(adapter='alias',enabled=False,alias_of=target,status='Covered by '+target,coverage=note,operational=False);c.execute('INSERT INTO sources(id,data) VALUES(?,?) ON CONFLICT(id) DO UPDATE SET data=excluded.data',(identity,json.dumps(d)))
        manifest=json.loads((db.ROOT/'portal/source_catalog.json').read_text())
        implemented={x[0] for x in SOURCES}|set(aliases)
        for item in manifest:
            if item['id'] in implemented or item['id']=='fius':continue
            identity=item['id'];url=item['url'];note=' '.join(item.get('limitations',[])) or 'Official source identified; detail collector not yet validated.'
            d={'name':item.get('name',identity),'url':url,'adapter':'pending','enabled':False,'category':'research' if identity=='eth-agentic-systems' else 'jobs','interval_hours':24,'status':'Link only','coverage':note,'operational':False}
            if identity=='aionic-labs':d['coverage']='Assumed identity for Aionics Lab: Aionic Labs, ETH-linked. '+note
            c.execute('INSERT INTO sources(id,data) VALUES(?,?) ON CONFLICT(id) DO NOTHING',(identity,json.dumps(d)))
    db.set_meta('startup_registry','3')
