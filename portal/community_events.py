"""Official organizer index → public registration pages, no account or model."""
import json,re
from datetime import datetime,timezone
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
from portal.adapters import document,evidence
from portal.extraction import enrich,clean,sentences
from portal.model import validate,tags

def ethai(raw,s):
 from portal.collector import jsonld
 soup=BeautifulSoup(raw,'html.parser');section=soup.select_one('section#events')
 if not section:raise ValueError('Organizer calendar missing; previous records retained')
 links=list(dict.fromkeys(a['href'] for a in section.select('a.tile[href]') if urlsplit(a['href']).hostname=='luma.com'))
 if not links:raise ValueError('Upcoming event cards absent; empty state needs verification')
 if len(links)>20:raise ValueError('Calendar exceeds 20 detail pages; coverage incomplete')
 records=[]
 for url in links:
  detail=document(url).decode('utf-8','replace');page=BeautifulSoup(detail,'html.parser');body=clean(page.get_text(' ',strip=True));entries=jsonld(detail,url)
  events=[e for e in entries if e['category']=='events']
  if len(events)!=1:raise ValueError('Expected one authoritative event on '+url)
  r=events[0];event=next(json.loads(x.get_text()) for x in page.select('script[type="application/ld+json"]') if isinstance(json.loads(x.get_text()),dict) and json.loads(x.get_text()).get('@type')=='Event')
  desc=event.get('description','').replace('\\n','\n');enrich(r,desc,complete=True)
  start=r.get('event_start');end=r.get('event_end') or start
  if not start or not end:raise ValueError('Event year/date missing')
  parsed=datetime.fromisoformat(end.replace('Z','+00:00'))
  if parsed.tzinfo is None:raise ValueError('Event timezone missing')
  closed=parsed<datetime.now(timezone.utc) or bool(re.search(r'registration (?:is )?closed|event (?:has )?ended|registration full',body,re.I))
  registration=bool(re.search(r'Request to Join|Register Now|Registration Approval Required',body,re.I))
  r.update(organization='ETH AI Club',organization_id='eth-ai-club',publisher='ETH AI Club via Luma',publisher_id=urlsplit(url).path.strip('/'),record_kind='event',city='Zurich' if r.get('city')=='Zürich' else r.get('city'),status='closed' if closed else 'open' if registration else 'unverified',type='Hackathon' if re.search(r'hack|hacking',r['title']+' '+desc,re.I) else 'Workshop',tags=tags(r['title']+' '+desc),discovery_url=s['url'],extraction_complete=True)
  r['metro']=r.get('city');substance=[x for x in sentences(desc) if re.search(r'prototype|paper club|research loops|post-training',x,re.I)]
  r['summary']=' '.join((substance or sentences(desc))[:2])[:340]
  r['activities']=[x for x in sentences(desc) if re.search(r'prototype|demos|build|experiment|present',x,re.I)][:4]
  r['questions']=[]
  for field in ['summary','activities','event_start','event_end']:evidence(r,field,r.get(field),desc if field in ['summary','activities'] else event.get('startDate' if field=='event_start' else 'endDate',''),'Official event description' if field in ['summary','activities'] else 'Event JSON-LD')
  conditions=[x for x in sentences(desc) if re.search(r'open to|preference|ETH email|member|students',x,re.I)]
  if conditions:evidence(r,'eligibility_requirements',conditions,' '.join(conditions),'Participation conditions')
  if 'open to everyone at ETH' in desc:
   r['questions'].append('The organizer describes participation for people at ETH; external-student access must be confirmed.')
   r['external_students']='not_stated'
  if 'Approval Required' in body:r['questions'].append('Registration requires host approval.');evidence(r,'application_method','Request to join on the official event page; host approval required.','Registration Approval Required Your registration is subject to host approval.','Registration')
  else:evidence(r,'application_method','Use the official registration page; current acceptance is not guaranteed.','Register','Registration')
  r['evidence_method']='Organizer calendar and linked public Luma JSON-LD/registration text; explicit event years and timezones.'
  # A free price is recorded only when explicitly provided, never inferred from missing ticket data.
  offers=event.get('offers',[]);offers=[offers] if isinstance(offers,dict) else offers
  if offers and all(str(o.get('price')) in ['0','0.0','0.00'] for o in offers):evidence(r,'fees','Free admission',json.dumps(offers)[:500],'Event ticket offers')
  validate(r);records.append(r)
 return records,f'{len(records)} organizer-linked registration pages validated; maximum 20 upcoming cards; host/enrollment conditions retained.'


def cyber_events(raw,s):
 """Only the organizer's current section; historical pagination is out of scope."""
 from urllib.parse import urljoin
 from portal.adapters import base,slug
 soup=BeautifulSoup(raw,'html.parser')
 boundary=next((h for h in soup.find_all('h2') if clean(h.text)=='Past Events'),None)
 if boundary is None:raise ValueError('Current/past event boundary missing; collection incomplete')
 cards=list(reversed(boundary.find_all_previous('div',class_='item event')))
 links=list(dict.fromkeys(urljoin(s['url'],a['href']) for card in cards for a in card.select('h4 a[href]')))
 if len(links)>20:raise ValueError('Upcoming calendar exceeds 20 details; collection incomplete')
 if not links and not re.search(r'no upcoming events',soup.get_text(' ',strip=True),re.I):raise ValueError('No upcoming cards; explicit empty state not confirmed')
 records=[]
 for url in links:
  if urlsplit(url).hostname not in ['cyber-valley.de','www.cyber-valley.de']:raise ValueError('Unexpected event detail host')
  page=BeautifulSoup(document(url),'html.parser');h=page.find('h1')
  if not h:raise ValueError('Event title missing')
  section=h.parent;datebox=section.select_one('.btn-link-label');body=clean(section.get_text(' ',strip=True));title=clean(h.text)
  if not datebox:raise ValueError('Event dates missing')
  date_text=clean(datebox.text);dates=re.findall(r'\b\d{1,2} [A-Za-z]+ 20\d{2}\b',date_text)
  if not dates:raise ValueError('Explicit event year missing')
  start=datetime.strptime(dates[0],'%d %B %Y').date().isoformat();end=datetime.strptime(dates[-1],'%d %B %Y').date().isoformat()
  venue=date_text.split('|')[-1].strip() if '|' in date_text else None
  city='Tübingen / Stuttgart' if venue and all(x in venue for x in ['Tübingen','Stuttgart']) else 'Stuttgart' if venue and 'Stuttgart' in venue else 'Tübingen' if venue and 'Tübingen' in venue else None
  org='Cyber Valley · nICLAS' if slug(title)=='niclas-forum-2026' else 'Cyber Valley'
  r=base(title,url,org,city,'events','event');r.update(organization_id='cyber-valley',publisher='Cyber Valley',publisher_id=slug(title),event_start=start,event_end=end,venue=venue,metro='Stuttgart' if city and 'Stuttgart' in city else city,country='Germany',type='Workshop / Networking event' if re.search(r'hands.on workshops',body,re.I) else 'Networking event',originating_page=s['url'])
  enrich(r,str(section),complete=True)
  invite=bool(re.search(r'invite only|invitation.only',body,re.I));past=end<datetime.now(timezone.utc).date().isoformat()
  r.update(status='closed' if past else 'unverified',registration_status='Invitation only' if invite else 'Needs confirmation',tags=tags(body),extraction_complete=True)
  r['eligibility_requirements']=['Invitation required; invited guests have already received an email.'] if invite else []
  r['questions']=['Invitation required; no public registration offered.'] if invite else ['Confirm current registration and remaining places with the organizer.']
  content=section.select_one('.apprarent-link') or section
  paragraphs=[clean(x.get_text(' ',strip=True)) for x in content.find_all('p') if clean(x.text)]
  substance=[x for x in paragraphs if re.search(r'pitch|hands.on|workshop|robotics|prototype',x,re.I)]
  specific=[x for p in paragraphs for x in sentences(p) if re.search(r'final pitches|hands.on workshops',x,re.I)]
  r['summary']=' '.join((specific or substance or paragraphs)[:1])[:340]
  r['activities']=substance[:4]
  for field,value in [('event_start',start),('event_end',end),('venue',venue)]:evidence(r,field,value,date_text,'Published event date / venue',url)
  for field in ['summary','activities']:evidence(r,field,r[field],' '.join(substance or paragraphs),'Event description',url)
  if invite:evidence(r,'eligibility_requirements',r['eligibility_requirements'],next((x for x in paragraphs if re.search(r'invite only|invitation.only',x,re.I)),body[-500:]),'Participation restriction',url)
  fee_heading=next((x for x in section.find_all(['h3','h4']) if clean(x.text).lower()=='cost'),None)
  if fee_heading:
   fee=fee_heading.find_next_sibling('p')
   if fee:evidence(r,'fees',clean(fee.text),clean(fee.text),'Cost',url)
  more=next((a for a in section.select('a[href]') if clean(a.text).startswith('More Information')),None)
  r['application_url']=urljoin(url,more['href']) if more else url
  evidence(r,'application_method','Invitation required; contact the published organizer.' if invite else 'Review the linked organizer information for registration instructions.',clean(more.text) if more else 'This event is invite only.','Participation / further information',url)
  r['evidence_method']='Official upcoming calendar and linked detail pages; explicit event years; invitation and fee evidence. Registration availability is not assumed.'
  validate(r);records.append(r)
 return records,f'{len(records)} upcoming-section detail pages collected; maximum 20; past-event pagination excluded. Registration remains unconfirmed unless explicitly stated.'
