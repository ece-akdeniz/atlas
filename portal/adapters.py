"""Bounded official index-to-detail adapters; no browser or paid model dependency."""
import hashlib,json,re,io
from urllib.parse import urljoin,urlsplit
from bs4 import BeautifulSoup
from pypdf import PdfReader
from portal import db
from portal.model import tags,validate
from portal.extraction import enrich,clean,recognize_skills,VERSION,sentences,pdf_details

def slug(title):return re.sub(r'[^a-z0-9]+','-',title.lower()).strip('-')
def base(title,url,org,city,category='research',kind='opening'):
    return dict(title=title,url=url,organization=org,publisher=org,academic_affiliations=[org] if category=='research' else [],city=city,metro='Munich' if city in ['Garching','Oberpfaffenhofen'] else city,country='Switzerland' if city=='Zurich' else 'Germany',category=category,record_kind=kind,type='Student project' if category=='research' else 'Role',summary=title,status='open',publisher_id=slug(title),tags=tags(title),external_students='not_stated',evidence_method='Official source sections; deterministic extraction')

def document(url):
    from portal.collector import robots,fetch,SourceError
    robots(url);code,headers,raw=fetch(url)
    if any(x in raw[:100000].lower() for x in [b'cf-chl-platform',b'captcha challenge',b'verify you are human']):raise SourceError('Access challenge; collection stopped')
    return raw

def evidence(r,field,value,quote,section,url=None,page=None):
    if value is None or value==[] or value=='':return
    r[field]=value;r.setdefault('field_states',{})[field]={'state':'extracted'}
    r.setdefault('field_evidence',{})[field]={'url':url or r['url'],'section':section,'excerpt':clean(quote)[:1000],'page':page,'version':VERSION}

def dlr(html,s):
    soup=BeautifulSoup(html,'html.parser');main=soup.select_one('main') or soup
    links=list(dict.fromkeys(urljoin(s['url'],a['href']) for a in main.select('a[href]') if '/jobs/students/' in a['href']))
    if len(links)>30:raise ValueError('DLR coverage limit: more than 30 detail pages; review pagination')
    records=[]
    for url in links:
        detail=BeautifulSoup(document(url),'html.parser');h=detail.find('h1')
        if not h:raise ValueError('DLR detail title missing')
        main=detail.select_one('main') or detail;title=clean(h.get_text(' ',strip=True));body=main.get_text('\n',strip=True)
        category='jobs' if re.search('working student|werkstudent',title,re.I) else 'research'
        r=base(title,url,'DLR · Robotics and Mechatronics','Oberpfaffenhofen',category)
        r['type']=title;r['employer']='DLR';r['publisher_id']=urlsplit(url).path.rstrip('/').split('/')[-1]
        enrich(r,str(main),complete=True);r['tags']=tags(title+' '+body)
        # DLR pages use natural-language section headings; collect each heading's own siblings.
        for heading in main.find_all(['h2','h3','h4']):
            label=clean(heading.text);parts=[]
            for node in heading.find_all_next():
                if node.name in ['h2','h3','h4','footer']:break
                if node.name in ['li','p']:parts.append(node.get_text(' ',strip=True))
            content='\n'.join(parts)
            field='required' if re.search('qualification|bring|profile|requirements',label,re.I) else 'activities' if re.search('contribution|task|expect|work|project',label,re.I) else None
            if field:evidence(r,field,sentences(content),content,label)
        preferred=[x for x in r.get('required',[]) if re.search('advantage|plus|preferred',x,re.I)]
        if preferred:
            r['required']=[x for x in r['required'] if x not in preferred]
            evidence(r,'preferred',preferred,' '.join(preferred),'Your Qualifications · preferred')
        contact=main.select_one('.contact-detail')
        if contact:
            evidence(r,'supervisor',clean(contact.get_text(' ',strip=True)),contact.text,'Published contact')
            evidence(r,'application_method','Use the Contact control on the official posting to reach '+clean(contact.select_one('.name').text if contact.select_one('.name') else contact.text)+'.',contact.text,'Contact')
            r['contact_links']=[url+'#'+str(main.select_one('.contact-list').get('id',''))] if main.select_one('.contact-list') else [url]
        duration=re.search(r'(?:Min\.?\s*)?\d+\s*(?:months|Monate)',body,re.I)
        if duration:evidence(r,'duration',duration[0],duration[0],'Duration')
        r['required_skills']=recognize_skills(' '.join(r.get('required',[])))
        if category=='jobs':
            m=re.search(r'(\d{1,2})\s*[–-]\s*(\d{1,2})\s*(?:hours|h\b)',body,re.I)
            if m:evidence(r,'hours',int(m[2]),m[0],'Workload');r['hours_min']=int(m[1])
        if re.search(r'master.{0,30}enroll|enroll.{0,40}master',body,re.I):r['enrollment_required']=True
        if r.get('activities'):r['summary']=r['activities'][0][:360]
        r['document_urls']=[urljoin(url,a['href']) for a in main.select('a[href]') if '.pdf' in a['href']]
        records.append(r)
    return records,f'{len(records)} of {len(links)} linked student postings; single index; maximum 30 details'

def cvg(html,s):
    soup=BeautifulSoup(html,'html.parser');records=[]
    for row in soup.select('table.inline tr'):
        cells=row.find_all('td')
        if len(cells)!=7:continue
        title=clean(cells[0].text);r=base(title,s['url'],'TUM · Computer Vision and AI','Garching')
        r['identity_url']=s['url']+'#'+slug(title)
        types=[label for label,c in zip(['Interdisciplinary project','Guided research','Bachelor’s thesis','Master’s thesis'],cells[2:6]) if '✅' in c.text]
        r['type']=' / '.join(types);r['project_types']=types
        enrich(r,'<b>Requirements:</b>'+str(cells[6]),section=title)
        evidence(r,'required',[clean(cells[6].text)],cells[6].text,'Prerequisites')
        evidence(r,'supervisor',clean(cells[1].text),cells[1].text,'Advisor')
        r['contact_links']=[urljoin(s['url'],a['href']) for a in cells[1].select('a[href]')]
        r['materials']=['CV','Recent transcript'];r['application_method']='Contact the named advisor with your CV and recent transcript.'
        r['summary']=title+'. Available as '+', '.join(types)+'.';r['tags']=tags(title+' '+cells[6].text)
        r['research_question']=None;r['field_states']['research_question']={'state':'absent'}
        records.append(r)
    return records,f'{len(records)} project rows; all table rows inspected; thesis suitability preserved'

def srl(html,s):
    soup=BeautifulSoup(html,'html.parser');h=next((h for h in soup.find_all(['h2','h3']) if 'Learning to walk' in h.text),None)
    if not h:return [],'Project heading not recognized'
    container=h.parent
    while len(container.get_text())<500 and container.parent:container=container.parent
    title=clean(h.text);r=base(title,s['url'],'TUM · Smart Robotics Lab','Garching')
    enrich(r,str(container),section=title,complete=False);r['tags']=tags(container.get_text());r['summary']='Investigate how perceived elevation maps can inform bipedal walking on uneven terrain.'
    r['record_kind']='lab_lead';r['status']='unverified';r['verification_warning']='Published project page has no dated recruitment confirmation.'
    return [r],'1 published project lead; current availability needs confirmation'

def iff(html,s):
    soup=BeautifulSoup(html,'html.parser');records=[];panels=soup.select('.panel');pdf_count=0;pdf_errors=[]
    for panel in panels:
        heading=panel.select_one('.panel-heading');body=panel.select_one('.panel-body')
        if not heading or not body:continue
        title=clean(heading.text);txt=body.get_text('\n',strip=True)
        if not tags(title+' '+txt):continue
        current=bool(re.search(r'WS\s*26\s*/\s*27|2026',title+' '+txt))
        r=base(title,s['url'],'University of Stuttgart · IFF','Stuttgart',kind='opening' if current else 'academic_route')
        r['partners']=[];r['academic_affiliations']=['University of Stuttgart · IFF'];r['publisher_id']='iff-'+slug(title)
        r['type']='Student project / thesis';r['summary']=sentences(clean(txt.split('Abteilung:')[0]))[0][:360]
        enrich(r,str(body),section=title,complete=False);r['tags']=tags(title+' '+txt)
        evidence(r,'activities',sentences(clean(txt.split('Abteilung:')[0]))[:4],txt,'Project description')
        r['date_evidence']='Winter semester 2026/27' if current else 'No current recruitment date established'
        pdfs=list(dict.fromkeys(urljoin(s['url'],a['href']) for a in body.select('a[href]') if '.pdf' in a['href']))
        r['documents']=[]
        for url in pdfs[:2]:
            doc={'url':url,'originating_page':s['url'],'date_evidence':r['date_evidence']}
            try:
                raw=document(url);reader=PdfReader(io.BytesIO(raw));pages=[p.extract_text() or '' for p in reader.pages[:12]];pdf_count+=1
                doc['pages']=len(reader.pages);doc['content_hash']=hashlib.sha256(raw).hexdigest();doc['coverage']='All pages' if len(reader.pages)<=12 else 'First 12 pages only'
                for page_no,content in enumerate(pages,1):
                    parsed=enrich(dict(r),pdf_details(content),complete=False)
                    for field in ['required','preferred','contacts','application_method','materials','activities','research_question']:
                        if parsed.get(field):evidence(r,field,parsed[field],content,'Document page',url,page_no)
                    flat=clean(content)
                    patterns=[r'Vorausgesetzt werden.*?Die Voraussetzungen unterscheiden sich je nach bearbeitetem Thema\.',r'We are inviting Master.s students.*?encouraged to participate\.']
                    for pattern in patterns:
                        match=re.search(pattern,flat,re.I)
                        if match:evidence(r,'required',[match[0]],match[0],'Prerequisites',url,page_no)
                    if 'Faculty 4 and Faculty 7' in flat:r.setdefault('questions',[]).append('The PDF invites Faculty 4 and Faculty 7 master’s students; confirm departmental access for your Computer Science degree.')
                    goal=re.search(r'Ziel (?:dieser Arbeit|unseres Forschungsprojekts) ist.*?\.',flat)
                    if goal:evidence(r,'research_question',goal[0],goal[0],'Research goal',url,page_no)
                    application=re.search(r'Bewerbungen \(Anschreiben und Lebenslauf\).*?(?:[\w.+-]+@[\w.-]+\.[A-Za-z]{2,})',flat)
                    if application:
                        evidence(r,'application_method',application[0],application[0],'Application',url,page_no)
                        evidence(r,'materials',['Cover letter','CV'],application[0],'Application',url,page_no)
                    r['skills']=list(dict.fromkeys(r.get('skills',[])+recognize_skills(content)))
                doc['status']='Extracted';doc['page_references']=list(range(1,len(pages)+1))
            except Exception as e:doc['status']='Failed';doc['error']=str(e)[:300];pdf_errors.append(url)
            r['documents'].append(doc)
        r['required_skills']=recognize_skills(' '.join(r.get('required',[])))
        if not current:r['status']='unverified';r['verification_warning']='Undated or older topic; confirm availability with the institute.'
        r.setdefault('questions',[]).append('Confirm supervision, external-student access and the current scope.')
        records.append(r)
    return records,f'{len(records)} relevant topics from {len(panels)} panels; {pdf_count} PDFs extracted; {len(pdf_errors)} PDF failures; maximum 2 PDFs/topic and 12 pages/PDF'

def collect(s,html):
    return {'dlr':dlr,'tum-cvg':cvg,'tum-srl':srl,'iff':iff}[s['adapter']](html,s)

def sirop(html,s):
    import html as htmlmod
    soup=BeautifulSoup(html,'html.parser');feeds=list(dict.fromkeys(el.get('data-feed') for el in soup.select('[data-feed]') if el.get('data-feed','').startswith('https://feeds.sirop.org/')))
    if not feeds:raise ValueError('No public publisher feed found; protected SIROP app is not collected')
    records=[];seen=set();restricted=0
    if len(feeds)>5:raise ValueError('More than five public feeds; source coverage incomplete')
    for feed in feeds:
        payload=json.loads(document(feed))
        for item in payload.get('opportunities',[]):
            url=item.get('url','');identity=url.rstrip('/').split('/')[-1]
            if identity in seen:continue
            seen.add(identity)
            parts=item.get('detailDescription',[]);locked=any('LOG IN' in d.get('title','') for d in parts)
            txt=' '.join(d.get('value') or '' for d in parts)
            if not tags(item['title']+' '+txt+' '+item.get('keywords','')):continue
            r=base(item['title'],s['url'],'ETH Zurich · '+item.get('organization',payload.get('title','')),'Zurich')
            r.update(publisher_id='sirop-'+identity,publisher_identifiers={'sirop':identity},published=item.get('publishedSince'),start_date=item.get('earliestStartDate'),project_end=item.get('latestEndDate'),status='open' if item.get('status')=='Published' else 'unverified',type=' / '.join(x['title'] for x in item.get('labels',[]) if x['title']!='ETH Zurich (ETHZ)'),feed_url=feed,sirop_url=url)
            content=''.join('<p><b>'+htmlmod.escape(d.get('title',''))+':</b></p><p>'+htmlmod.escape(d.get('value') or '').replace('\n','</p><p>')+'</p>' for d in parts)
            enrich(r,content,section=item['title'],complete=not locked);r['tags']=tags(item['title']+' '+txt+' '+item.get('keywords',''))
            r['allowed_applicant_organizations']=item.get('allowedApplicantOrganizations',[])
            if r['allowed_applicant_organizations']:r['questions']=['Publisher restricts applicant organizations: '+json.dumps(r['allowed_applicant_organizations'],ensure_ascii=False)]
            for d in parts:
                title=d.get('title','').lower();value=d.get('value')
                if value and title=='work packages':evidence(r,'activities',sentences(value.replace('●','\n')),value,'Work Packages',feed)
                if value and title=='description' and re.search(r'apply (?:through|via|on) sirop',value,re.I):
                    r['application_url']=url;evidence(r,'application_method','Apply through SiROP with CV, current transcript and supporting material.',value,'Description · application',feed);r['materials']=['CV','Current transcript','Supporting material']
            description=next((d.get('value') or '' for d in parts if d.get('title','').lower()=='description'),'')
            if not r.get('research_question'):
                goal=next((x for x in sentences(description) if re.search(r'this (?:project|thesis) (?:aims|introduces|investigates|focuses)|goal (?:is|of)',x,re.I)),None)
                if goal:evidence(r,'research_question',goal,goal,'Description',feed)
            if 'RAI Institute' in txt:r['employer']='RAI Institute';r['partners']=['RAI Institute','ETH Zurich'];r['academic_affiliations']=['ETH Zurich']
            if re.search(r'advertisement is deliberately kept general',txt):r['record_kind']='academic_route'
            if locked:
                restricted+=1;r['extraction_complete']=False;r['summary']=item.get('abstract') or item['title'];r['verification_warning']='Detailed description restricted to signed-in eligible applicants.'
                for field in ['required','preferred','activities','research_question','application_method']:r['field_states'][field]={'state':'incomplete'};r.pop(field,None)
            for ev in r['field_evidence'].values():ev['url']=feed
            records.append(r)
    return records,f'{len(records)} relevant projects from {len(feeds)} official public lab feeds; {restricted} restricted descriptions; full SIROP search not collected'

def tumai(html,s):
    soup=BeautifulSoup(html,'html.parser');items=[]
    for script in soup.find_all('script'):
        value=script.string or ''
        if not value.startswith('self.__next_f.push('):continue
        try:
            args=json.loads(value[len('self.__next_f.push('):].rstrip().removesuffix(')').removesuffix(';').removesuffix(')'))
            flight=args[1] if len(args)>1 and isinstance(args[1],str) else ''
            marker='"initialEvents":'
            if marker in flight:items=json.JSONDecoder().raw_decode(flight.split(marker,1)[1])[0];break
        except (ValueError,TypeError):continue
    if not items:raise ValueError('Event data not found in official page; format review needed')
    records=[]
    for item in items:
        title=item.get('title','');desc=item.get('description','') or '';body=desc+' '+(item.get('detail') or '')
        if not re.search(r'hack|makeathon|\bAI\b|artificial intelligence',title+' '+body,re.I):continue
        r=base(title,s['url'],'TUM.ai',item.get('city') or 'Munich','events','event')
        r.update(publisher_id=str(item['id']),type='Hackathon' if re.search('hack|makeathon',title,re.I) else 'Event',event_start=item.get('event_date'),event_end=item.get('event_date'),summary=clean(desc)[:360] or title,registration_status='Check organizer',tags=tags(title+' '+body))
        enrich(r,'<p>'+body+'</p>',complete=False)
        if item.get('sign_up','').startswith('https://'):r['application_url']=item['sign_up']
        records.append(r)
    return records,f'{len(records)} relevant events from {len(items)} published entries; past editions excluded from upcoming views; end times incomplete'

def lever(html,s):
    from datetime import datetime,timezone
    first=json.loads(html);items=list(first);skip=100
    while len(first)==100 and skip<500:
        first=json.loads(document(s['url']+'&skip='+str(skip)));items+=first;skip+=100
    if len(first)==100:raise ValueError('Lever pagination exceeds 500-record budget; increase reviewed bound')
    records=[]
    for item in items:
        title=item['text'];loc=item.get('categories',{}).get('location','')
        if not re.search('zurich|zürich',loc,re.I):continue
        if not re.search(r'software|robotic|perception|autonom|machine learning|hardware|test.*engineer',title,re.I):continue
        r=base(title,item['hostedUrl'],'ANYbotics','Zurich','research' if re.search('thesis',title,re.I) else 'jobs')
        r.update(employer='ANYbotics',publisher='ANYbotics via Lever',publisher_id=item['id'],application_url=item['applyUrl'],type='Internship' if 'intern' in title.lower() else 'Full-time role',workload='Full-time',published=datetime.fromtimestamp(item['createdAt']/1000,timezone.utc).date().isoformat())
        content=(item.get('descriptionBody') or item.get('description') or '')+''.join('<p><b>'+v['text']+':</b></p>'+v['content'] for v in item.get('lists',[]))+(item.get('additional') or '')
        enrich(r,content,complete=True)
        for group in item.get('lists',[]):
            name=group['text'];txt=BeautifulSoup(group['content'],'html.parser').get_text('\n',strip=True)
            field='preferred' if re.search('bonus|nice|plus',name,re.I) else 'required' if re.search('profile|bring|require',name,re.I) else 'activities' if re.search('impact|task|responsib',name,re.I) else None
            if field:evidence(r,field,sentences(txt),txt,name)
        if r.get('activities'):r['summary']=r['activities'][0][:360]
        body=BeautifulSoup(content,'html.parser').get_text(' ',strip=True);r['tags']=tags(title+' '+body)
        if re.search(r'Non.EU|non.EU',body):
            r['non_eu_conditions']='Mandatory internship supported by university letter; Swiss residence and work authorization require confirmation.'
            r.setdefault('questions',[]).append(r['non_eu_conditions'])
        if re.search('3.?000',body):r['funding']='CHF 3,000 / month (internship)';r['funding_confirmed']=True
        records.append(r)
    return records,f'{len(records)} relevant Zurich roles from {len(items)} published employer postings; pagination checked; full-time roles marked future options'

def fraunhofer(html,s):
    soup=BeautifulSoup(html,'html.parser');pages=[soup];visited={s['url']};todo=[urljoin(s['url'],a['href']) for a in soup.select('.pagination a[href]')]
    while todo:
        u=todo.pop(0)
        if u in visited:continue
        if len(visited)>=8:raise ValueError('Fraunhofer pagination exceeds 8-page reviewed budget')
        if urlsplit(u).netloc!=urlsplit(s['url']).netloc:continue
        visited.add(u);page=BeautifulSoup(document(u),'html.parser');pages.append(page);todo.extend(urljoin(u,a['href']) for a in page.select('.pagination a[href]'))
    links=list(dict.fromkeys(urljoin(s['url'],a['href']) for page in pages for a in page.select('#searchresults a.jobTitle-link[href]')))
    if len(links)>50:raise ValueError('Fraunhofer index exceeds 50-detail reviewed budget')
    records=[]
    for url in links:
        page=BeautifulSoup(document(url),'html.parser');title=page.select_one('[itemprop=title]');desc=page.select_one('[itemprop=description]')
        if not title or not desc:raise ValueError('Fraunhofer microdata missing')
        txt=desc.get_text('\n',strip=True);title=clean(title.text)
        if not tags(title+' '+txt):continue
        r=base(title,url,'Fraunhofer IPA','Stuttgart');r.update(type='Student research assistant',employer='Fraunhofer IPA',publisher='Fraunhofer jobs',academic_affiliations=[],publisher_id=urlsplit(url).path.rstrip('/').split('/')[-1])
        enrich(r,str(desc),complete=True);r['tags']=tags(title+' '+txt)
        # Section boundaries are bold paragraphs in SuccessFactors microdata.
        labels=list(desc.find_all(['strong','b']))
        for label in labels:
            name=clean(label.text);field='activities' if re.search('Aufgaben|Was Sie bei uns tun|Tätigkeit|sorgen Sie für Veränderung',name,re.I) else 'required' if re.search('mitbringen|Profil|Voraussetzung|bringen Sie sich ein',name,re.I) else None
            if not field:continue
            chunks=[]
            for node in label.find_all_next():
                if node is not label and node.name in ['strong','b']:break
                if node.name=='li':chunks.append(clean(node.text))
            evidence(r,field,chunks,' '.join(chunks),name)
        if r.get('activities'):r['summary']=r['activities'][0][:360]
        preferred=[x for x in r.get('required',[]) if re.search('Vorteil|idealerweise|bevorzugt',x,re.I)]
        if preferred:r['required']=[x for x in r['required'] if x not in preferred];evidence(r,'preferred',preferred,' '.join(preferred),'Preferred experience')
        r['required_skills']=recognize_skills(' '.join(r.get('required',[])))
        if not r.get('required') or not r.get('activities'):
            r['extraction_complete']=False
            for field in ['required','activities']:
                if not r.get(field):r['field_states'][field]={'state':'incomplete'}
        identifier=re.search(r'Kennziffer:\s*(\d+)',txt)
        if identifier:r['publisher_identifiers']={'fraunhofer':identifier[1]}
        r['application_method']='Apply through the official Fraunhofer online application form.'
        if re.search('Fließende Englisch',txt,re.I):r['languages']={'English':'Fluent (CEFR not stated)'}
        posted=page.select_one('[itemprop=datePosted]');r['published']=posted.get('content') or clean(posted.text) if posted else None
        valid=page.select_one('[itemprop=validThrough]');r['listing_valid_through']=valid.get('content') if valid else None
        r['questions']=['Published structured expiry is not a confirmed application deadline.']
        app=next((a for a in page.select('a[href]') if '/talentcommunity/apply/' in a['href']),None)
        if app:r['application_url']=urljoin(url,app['href'])
        if re.search('Hochschule|immatrikuliert|eingeschrieben',txt):r['enrollment_required']=True
        if re.search('sehr gute Deutsch',txt,re.I):r['languages']={'German':'Very good (CEFR not stated)','English':'Very good (CEFR not stated)'}
        records.append(r)
    return records,f'{len(records)} relevant IPA student research roles from {len(links)} details / {len(pages)} index pages; up to 8 pages and 50 details'

def cyber(html,s):
    soup=BeautifulSoup(html,'html.parser');h=soup.find('h1')
    if not h:raise ValueError('Event heading missing')
    container=h.parent;txt=container.get_text(' ',strip=True)
    if s['id']=='cyber-niclas':
        if not all(term in txt for term in ['2026','20','21','60']):raise ValueError('Event date/fee pattern changed')
        r=base(clean(h.text),s['url'],'Cyber Valley · nICLAS','Tübingen / Stuttgart','events','event')
        r.update(event_start='2026-10-20',event_end='2026-10-21',metro='Stuttgart',type='Workshop / networking',fees='€60 per day',summary='AI and robotics for laboratory automation, with a hands-on day at Fraunhofer IPA in Stuttgart.',tags=['AI','robotics'],registration_status='Needs confirmation',questions=['Confirm remaining places and registration. No travel or fee support is stated.'])
    else:raise ValueError('Event adapter not configured')
    enrich(r,str(container),complete=False);r['field_evidence']['event_start']={'url':s['url'],'section':'Event date','excerpt':txt[:700],'version':VERSION}
    return [r],'1 official event; registration status and financial support require confirmation'

# Only explicit adapters are callable; scraped pages cannot select code.
def collect(s,html):
    return {'dlr':dlr,'tum-cvg':cvg,'tum-srl':srl,'iff':iff,'eth-projects':sirop,'tumai':tumai,'lever':lever,'fraunhofer':fraunhofer,'cyber':cyber}[s['adapter']](html,s)
