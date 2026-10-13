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
