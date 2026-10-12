import re
from datetime import datetime, timezone, timedelta
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
RANK_VERSION='2.1.0'
from portal.extraction import normalize_skill, SKILLS
CATEGORIES=['jobs','research','events']
STAGES=['Saved','Preparing','Applied','Interviewing','Offer','Rejected','Archived']
TAGS={'computer vision':['computer vision','3d vision','bildverarbeitung','3d bin picking','vision-based','visual perception'],'machine learning':['machine learning','deep learning','neural','pytorch'],'robotics':['robot','robots','robotics','robotik','roboter','roboterbasierten','roboterbasiert','exoskeleton','exoskelett','exoskeletten','exoskelette'],'SLAM':['slam','localization','visual odometry','lidar odometry','simultaneous localization'],'sensor fusion':['sensor fusion','multi-modal','multimodal'],'autonomous systems':['autonomous','navigation','drone'],'mechatronics':['mechatronic','mechatronics','mechatronik','regelung','digitaler menschmodellierung','menschmodelle'],'AI':['artificial intelligence',' ai ','reinforcement learning','künstliche intelligenz','ki','virtuelle realität']}
DEFAULT_PROFILE={'name':'Your workspace','citizenship':'Turkish','university':None,'degree':None,'enrolled':None,'graduation':None,'skills':[],'languages':{},'interests':list(TAGS),'locations':['Stuttgart','Zurich','Munich'],'max_hours':20,'hours_hard':False,'availability_start':None,'commitment':None,'commitment_confirmed':False,'residence_conditions':None,'weights':{'topics':35,'skills':25,'location':20,'zurich':10,'practical':10},'provenance':{},'last_visit':None}
def canonical_url(url):
    p=urlsplit(url)
    query=urlencode(sorted((k,v) for k,v in parse_qsl(p.query) if not k.startswith('utm_') and k not in ['ref','tracking','trk']))
    return urlunsplit((p.scheme.lower(),p.netloc.lower(),p.path.rstrip('/') or '/',query,p.fragment))
def validate(r):
    for k in ['title','organization','url','category','summary']:
        if not isinstance(r.get(k),str) or not r[k].strip(): raise ValueError('Missing or invalid '+k)
    if r['category'] not in CATEGORIES: raise ValueError('Invalid category')
    if urlsplit(r['url']).scheme!='https': raise ValueError('Source must use HTTPS')
    if r.get('application_url') and urlsplit(r['application_url']).scheme!='https': raise ValueError('Unsafe application URL')
    if len(r['title'])>400 or len(r['summary'])>20000: raise ValueError('Record exceeds bounds')
    if r.get('hours') is not None and (type(r['hours']) not in [int,float] or not 0<r['hours']<=168): raise ValueError('Invalid weekly hours')
    for k in ['deadline','event_start','event_end','start_date']:
        if r.get(k): datetime.fromisoformat(r[k].replace('Z','+00:00'))
    for k in ['tags','required','preferred','skills','activities']:
        if k in r and (not isinstance(r[k],list) or any(not isinstance(x,str) for x in r[k])): raise ValueError('Invalid '+k)
    if r.get('status','open') not in ['open','closed','unverified']: raise ValueError('Invalid status')
def tags(text):
    t=' '+text.lower()+' '
    return [k for k,v in TAGS.items() if any(re.search(r'(?<!\w)'+re.escape(x.strip())+r'(?!\w)',t) for x in v)]
def status(r,as_of):
    states=[]
    if r.get('status')=='closed': states.append('Closed')
    deadline=r.get('deadline')
    if deadline and deadline[:10]<as_of[:10]: states.append('Expired')
    elif deadline and deadline[:10]<=(datetime.fromisoformat(as_of).date()+timedelta(days=7)).isoformat(): states.append('Closing soon')
    if r.get('event_end') and r['event_end'][:10]<as_of[:10] and 'Expired' not in states: states.append('Expired')
    if r.get('project_end') and r['project_end'][:10]<as_of[:10]: states.append('Unverified')
    if r.get('verification_warning') or r.get('status')=='unverified' or not r.get('verified') or r['verified'][:10]<(datetime.fromisoformat(as_of).date()-timedelta(days=7)).isoformat(): states.append('Unverified')
    cutoff=(datetime.fromisoformat(as_of).date()-timedelta(days=7)).isoformat()
    if r.get('changed') and r['changed'][:10]>=cutoff: states.append('Updated')
    if r.get('discovered','')[:10]>=cutoff: states.append('New')
    return list(dict.fromkeys(states)) or ['Verified']
def evaluate(r,p,as_of):
    why=[]; gaps=[]; questions=[]; conflicts=[]
    if r.get('explicit_conflict') and p.get('citizenship')=='Turkish':conflicts.append(r['explicit_conflict'])
    topics=sorted(set(r.get('tags',[]))&set(p.get('interests',[])))
    skills=sorted(set(normalize_skill(x) for x in r.get('skills',[]))&set(normalize_skill(x) for x in p.get('skills',[])))
    missing=sorted(set(normalize_skill(x) for x in r.get('required_skills',r.get('skills',[])))-set(normalize_skill(x) for x in p.get('skills',[])))
    if topics: why.append('Interest overlap: '+', '.join(topics)+'.')
    if skills: why.append('Your experience: '+', '.join(next((name for name in SKILLS if normalize_skill(name)==value),value) for value in skills)+'.')
    if missing: gaps.append('Not evidenced in your profile: '+', '.join(missing)+'. This is not a claim that you lack these skills.')
    city=r.get('city') or ''
    metro=r.get('metro') or city
    priority=next((i for i,x in enumerate(p.get('locations',[])) if x.lower() in metro.lower()),None)
    if priority is not None: why.append(city+' is one of your priority locations.')
    zurich='zurich' in city.lower() and r['category']=='research'
    if zurich: why.append('Could build an academic connection in Zurich; acceptance is not predicted.')
    hours=r.get('hours')
    if hours and hours>p.get('max_hours',20):
        gaps.append(f"{hours:g} hours/week exceeds your {p.get('max_hours',20)}-hour preference.")
        if p.get('hours_hard'): conflicts.append('Your hard workload constraint is exceeded (a personal constraint, not an immigration ruling).')
    elif str(r.get('workload','')).startswith('Full-time'): gaps.append('Full-time commitment; compatibility with your study availability needs confirmation.')
    if p.get('availability_start') and r.get('start_date') and r['start_date'][:10]<p['availability_start'][:10]: gaps.append('The published start precedes your available-from date; confirm flexibility.')
    if p.get('commitment_confirmed') and p.get('commitment'): questions.append('Your confirmed academic commitment needs a manual schedule check: '+p['commitment'])
    if not p.get('commitment_confirmed'): questions.append('Dates and workload of your upcoming academic commitment are not confirmed.')
    if p.get('enrolled') is False and r.get('enrollment_required'): conflicts.append('The posting requires current enrollment; your profile says you are not enrolled.')
    if r.get('local_enrollment') and p.get('university') and r['local_enrollment'].lower() not in p['university'].lower(): conflicts.append('The stated enrollment condition is '+r['local_enrollment']+'; your profile lists '+p['university']+'. Confirm whether exceptions exist.')
    if r['category']=='research':
        questions.extend(['Confirm supervision, home-university recognition and academic credit.'])
        if r.get('external_students')!='yes': questions.append('External-student access is not explicitly confirmed for this project.')
    legal='Insufficient information'
    if r['category'] in ['jobs','research']:
        if r.get('country')=='Switzerland': questions.append('Swiss hosting, residence and any work authorization must be confirmed separately; German student status does not establish Swiss work rights.')
        else: questions.append('Confirm residence-permit conditions, internship/thesis classification and student social-insurance treatment separately.')
    allowed=r.get('allowed_applicant_organizations') or []
    if allowed and p.get('university'):
        names=[x if isinstance(x,str) else x.get('name',x.get('title','')) for x in allowed]
        if not any(p['university'].casefold() in x.casefold() or x.casefold() in p['university'].casefold() for x in names if x):
            conflicts.append('Publisher limits applications to '+', '.join(names)+'. Your university is not listed.')
    if r.get('non_eu_conditions') and p.get('citizenship')=='Turkish':questions.append(r['non_eu_conditions'])
    language=r.get('languages') or {}
    for lang,level in language.items():
        known=p.get('languages',{}).get(lang)
        if not known: questions.append(f'{lang} ({level}) is required; your level is not recorded.')
        else:
            levels=['A1','A2','B1','B2','C1','C2'];required=re.search(r'\b[ABC][12]\b',level.upper())
            if required and known.upper() in levels and levels.index(known.upper())<levels.index(required[0]):conflicts.append(f'{lang} {required[0]} required; your profile states {known}.')
            elif re.search(r'very good|fluent|sehr gut|fließend',level,re.I) and known.upper() in ['A1','A2','B1']:
                questions.append(f'{lang}: source asks for {level}; your {known} level needs confirmation. No CEFR equivalence is assumed.')
    if not r.get('funding'): questions.append('Compensation/funding and total personal cost are not stated.')
    questions.extend(r.get('questions',[]))
    if conflicts: label='Explicit requirement conflict'
    elif r.get('external_students')=='yes' or r.get('enrollment_required') and p.get('enrolled'): label='Potentially compatible; confirmation required'
    else: label='Insufficient information'
    if r['category']=='events' and r.get('open_to_all'): label='Appears compatible with the information provided'
    if conflicts: label='Explicit requirement conflict'
    weights=p.get('weights',DEFAULT_PROFILE['weights'])
    factors={'topics':min(len(topics)/3,1),'skills':len(skills)/max(len(r.get('skills',[])),1),'location':1 if priority is not None else .3 if r.get('arrangement')=='Remote' else 0,'zurich':int(zurich),'practical':.5*bool(hours and hours<=p.get('max_hours',20))+.5*bool(r.get('funding_confirmed'))}
    points={k:round(factors[k]*weights.get(k,0),2) for k in factors}
    fit=round(sum(points.values()),2)
    states=status(r,as_of)
    future=bool(conflicts or r.get('requires_graduation') or hours and hours>p.get('max_hours',20) or str(r.get('workload','')).startswith('Full-time'))
    return {**r,'verification_label':('Last verified ' if 'Unverified' in states else 'Checked ')+(r.get('verified') or 'never')[:10],'match':{'points':fit,'factors':points,'version':RANK_VERSION,'why':why,'gaps':gaps,'questions':list(dict.fromkeys(questions)),'conflicts':conflicts,'eligibility':label,'authorization':legal,'future':future},'states':states}
def ranked(records,p,as_of):
    evaluated=[evaluate(r,p,as_of) for r in records]
    return sorted(evaluated,key=lambda r:(bool({'Closed','Expired'}&set(r['states'])),bool(r['match']['conflicts']),-r['match']['points'],r.get('deadline') or '9999',r.get('title','').casefold(),r['id']))

def recommendations(ordered):
    """Versioned gate; no city/category quotas. Tie-breaks inherited from ranked()."""
    return [r for r in ordered if not r.get('dismissed')
            and r.get('record_kind') in ['opening','event']
            and r.get('extraction_complete')
            and not ({'Closed','Expired','Unverified'} & set(r['states']))
            and not r['match']['conflicts'] and not r['match']['future']
            and not any(x.get('state')=='conflict' for x in r.get('field_states',{}).values())
            and r['match']['factors']['topics']>0 and r['match']['factors']['skills']>0
            and r['match']['points']>=40][:3]
