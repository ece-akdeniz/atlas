from portal import providers
"""Quiet, evidence-gated alerts. No inbox access; durable outbox and provider idempotency."""
import os,re,json,hashlib,uuid,time
from datetime import datetime,timedelta,timezone
import requests
from portal import db
from portal.model import ranked
DEFAULT={'enabled':False,'destination':'','min_topics':2,'min_skills':2,'categories':['jobs','research','events'],'daily_limit':2,'mode':'immediate'}
def settings():return {**DEFAULT,**db.get_meta('notifications',{})}
def fingerprint(r):return hashlib.sha256(json.dumps({k:r.get(k) for k in ['deadline','event_start','event_end','status','registration_status','funding','funding_confirmed','fees']},sort_keys=True).encode()).hexdigest()
def qualifies(r,p,c):
    if r['category'] not in c['categories'] or r.get('record_kind') not in ['opening','event'] or r.get('status')!='open' or not r.get('extraction_complete'):return False
    if set(r['states'])&{'Closed','Expired','Unverified'} or r['match']['conflicts'] or r['match']['future'] or r.get('explicit_conflict'):return False
    if r.get('city') not in p.get('locations',[]) and r.get('metro') not in p.get('locations',[]):return False
    topics=set(x.lower() for x in r.get('tags',[]))&set(x.lower() for x in p.get('interests',[]))
    from portal.extraction import normalize_skill
    skills={normalize_skill(x) for x in r.get('skills',[])}&{normalize_skill(x) for x in p.get('skills',[])}
    practical=(r.get('hours') and r['hours']<=p.get('max_hours',20)) or r.get('external_students')=='yes' or r.get('funding_confirmed') is True
    if r['category']=='events':
        free=bool(re.search(r'\bfree\b|no participation fee|kostenlos|^0(?:[ .,]|$)',str(r.get('fees','')),re.I))
        access=r.get('external_students')=='yes' or r.get('open_to_all') is True
        return len(topics)>=c['min_topics'] and bool(r.get('event_start')) and access and (free or r.get('funding_confirmed') is True) and r.get('registration_status') not in ['closed','Closed']
    if r['category']=='research':
        return len(topics)>=c['min_topics'] and bool(r.get('activities') or r.get('research_question')) and (len(skills)>=c['min_skills'] or len(topics)>=c['min_topics']+1) and bool(practical)
    return len(topics)>=c['min_topics'] and len(skills)>=c['min_skills'] and bool(practical)
def configure(payload):
    old=settings();new={**old,**{k:v for k,v in payload.items() if k in DEFAULT}}
    if type(new['enabled'])!=bool or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',new['destination']):raise ValueError('Enter a valid destination email')
    if new['mode'] not in ['immediate','digest'] or type(new['daily_limit'])!=int or not 1<=new['daily_limit']<=5:raise ValueError('Use immediate/digest and a daily limit of 1–5')
    if any(type(new[k])!=int or not 1<=new[k]<=5 for k in ['min_topics','min_skills']):raise ValueError('Evidence thresholds must be 1–5')
    if not isinstance(new['categories'],list) or any(x not in ['jobs','research','events'] for x in new['categories']):raise ValueError('Invalid categories')
    if new['enabled'] and not old['enabled']:
        db.set_meta('notification_baseline',{r['id']:fingerprint(r) for r in db.rows()});db.set_meta('notification_initial_ids',[r['id'] for r in db.rows()]);new['enabled_at']=db.now()
    if not new['enabled'] or new['destination']!=old['destination']:
        with db.connect() as conn:conn.execute("UPDATE notification_events SET status='cancelled' WHERE status IN ('queued','retry')")
        db.set_meta('notification_batch',None)
    db.set_meta('notifications',new);return new

def discover():
    c=settings()
    if not c['enabled']:return 0
    baseline=db.get_meta('notification_baseline',{});p=db.get_meta('profile',{});count=0
    initial=db.get_meta('notification_initial_ids')
    if initial is None:
        initial=[r['id'] for r in db.rows() if r.get('discovered','')<=c.get('enabled_at',db.now())];db.set_meta('notification_initial_ids',initial)
    records=db.rows();failed={s['id'] for s in db.sources() if s.get('error')}
    for row in records:
        if any(e['source_id'] in failed for e in row.get('sources',[])):row['verification_warning']='Latest source check failed'
    for r in ranked(records,p,db.now()[:10]):
        fp=fingerprint(r);prior=baseline.get(r['id']);baseline[r['id']]=fp
        if not qualifies(r,p,c):continue
        with db.connect() as conn:notified=conn.execute("SELECT payload FROM notification_events WHERE opportunity_id=? AND status IN ('accepted','delivered') ORDER BY created DESC LIMIT 1",(r['id'],)).fetchone()
        if r['id'] in initial and not notified:continue # Immutable activation backlog only.
        changed=None
        if notified:
            old=json.loads(notified['payload']);old_deadline=old.get('deadline')
            if old_deadline!=r.get('deadline') and r.get('deadline'):
                changed='Application deadline changed from '+str(old_deadline or 'not stated')+' to '+r['deadline']
            elif old.get('event_start')!=r.get('event_start') and r.get('event_start'):
                changed='Event date changed to '+r['event_start']
            elif not old.get('funding_confirmed') and r.get('funding_confirmed') is True:
                changed='Financial support is now confirmed in the posting'
            else:continue
        payload={'title':r['title'],'organization':r['organization'],'city':r.get('city'),'type':r.get('type'),'url':r['url'],'deadline':r.get('deadline'),'why':r['match']['why'],'uncertainty':r['match']['questions'][:2],'change':changed,'destination':c['destination'],'event_start':r.get('event_start'),'funding_confirmed':r.get('funding_confirmed')}
        with db.connect() as conn:
            conn.execute("DELETE FROM notification_events WHERE opportunity_id=? AND fingerprint=? AND status='cancelled' AND attempts=0",(r['id'],fp))
            cursor=conn.execute("INSERT OR IGNORE INTO notification_events(id,opportunity_id,fingerprint,payload,status,created) VALUES(?,?,?,?,?,?)",(uuid.uuid4().hex,r['id'],fp,json.dumps(payload),'queued',db.now()));count+=cursor.rowcount
    db.set_meta('notification_baseline',baseline);return count

def configured():return bool(providers.get('RESEND_API_KEY') and providers.get('ATLAS_EMAIL_FROM') and os.getenv('PORTAL_ORIGIN','').startswith('https://'))
def queue_test():
    c=settings()
    if not configured():raise ValueError('Configure RESEND_API_KEY, a verified ATLAS_EMAIL_FROM domain, and the HTTPS PORTAL_ORIGIN first')
    if not c['destination']:raise ValueError('Save a destination address first')
    identity=uuid.uuid4().hex
    with db.connect() as conn:
        recent=conn.execute("SELECT created FROM notification_events WHERE opportunity_id='TEST' ORDER BY created DESC LIMIT 1").fetchone()
        if recent and time.time()-datetime.fromisoformat(recent['created']).timestamp()<900:raise ValueError('Test emails are limited to one per 15 minutes')
        conn.execute("INSERT INTO notification_events(id,opportunity_id,fingerprint,payload,status,created) VALUES(?,?,?,?,?,?)",(identity,'TEST',identity,json.dumps({'title':'Atlas test email','destination':c['destination'],'test':True}),'queued',db.now()))
    return identity

def deliver():
    c=settings()
    if not configured():return
    now=db.now();epoch=int(time.time())
    with db.connect() as conn:
        conn.execute('DELETE FROM locks WHERE name=? AND until<?',('mail',epoch))
        try:conn.execute('INSERT INTO locks VALUES(?,?)',('mail',epoch+120))
        except Exception:return
    try:
        with db.connect() as conn:
            sent=conn.execute("SELECT COUNT(DISTINCT provider_id) FROM notification_events WHERE sent>=? AND status IN ('accepted','delivered')",(now[:10],)).fetchone()[0]
            rows=conn.execute("SELECT * FROM notification_events WHERE status IN ('queued','retry') AND (next_due IS NULL OR next_due<=?) ORDER BY created LIMIT 20",(now,)).fetchall()
        if sent>=c['daily_limit']:return
        rows=[r for r in rows if c['enabled'] or r['opportunity_id']=='TEST']
        if not rows:return
        if c['mode']=='digest' and all(r['opportunity_id']!='TEST' for r in rows):
            if datetime.now(timezone.utc).hour<17 or db.get_meta('last_digest_day')==now[:10]:return
            rows=rows[:5]
        else:rows=rows[:1]
        batch=db.get_meta('notification_batch')
        if batch:
            with db.connect() as conn:
                stored=[conn.execute('SELECT * FROM notification_events WHERE id=?',(identity,)).fetchone() for identity in batch['ids']]
            if any(r is None or r['status'] not in ['queued','retry'] for r in stored):
                db.set_meta('notification_batch',None);return
            if any(r['next_due'] and r['next_due']>now for r in stored):return
            if time.time()-datetime.fromisoformat(batch['created']).timestamp()>20*3600:
                with db.connect() as conn:
                    for r in stored:conn.execute("UPDATE notification_events SET status='needs_review',error='Delivery outcome uncertain; automatic retry window ended' WHERE id=?",(r['id'],))
                db.set_meta('notification_batch',None);return
            rows=stored
        else:
            destination=json.loads(rows[0]['payload'])['destination']
            rows=[r for r in rows if json.loads(r['payload'])['destination']==destination]
            db.set_meta('notification_batch',{'ids':[r['id'] for r in rows],'created':now})
        current={r['id']:r for r in notification_records()};invalid=[]
        for row in rows:
            if row['opportunity_id']=='TEST':continue
            r=current.get(row['opportunity_id'])
            if not c['enabled'] or not r or not qualifies(r,db.get_meta('profile',{}),c) or row['fingerprint']!=fingerprint(r):invalid.append(row['id'])
        if invalid:
            with db.connect() as conn:
                for identity in invalid:conn.execute("UPDATE notification_events SET status='cancelled',error='Current evidence no longer supports this queued alert' WHERE id=?",(identity,))
            db.set_meta('notification_batch',None);return
        first=rows[0];key='atlas-'+hashlib.sha256('|'.join(r['id'] for r in rows).encode()).hexdigest();parts=[]
        for row in rows:
            p=json.loads(row['payload'])
            if p.get('test'):parts.append('This is a test email from Atlas. No opportunity alert was triggered.');continue
            parts.append('\n'.join([p['title'],p['organization']+' · '+str(p['city'])+' · '+str(p['type']),'Why: '+'; '.join(p['why'][:2]),'Confirm: '+'; '.join(p['uncertainty']),'Deadline: '+str(p.get('deadline') or 'Not stated'),p.get('change') or '',os.environ['PORTAL_ORIGIN']+'/#opportunity='+row['opportunity_id'],p['url']]))
        body={'from':providers.get('ATLAS_EMAIL_FROM'),'to':[json.loads(first['payload'])['destination']],'subject':'[Atlas test] Delivery check' if first['opportunity_id']=='TEST' else 'Atlas · '+('Exceptional opportunities' if len(rows)>1 else json.loads(first['payload'])['title']),'text':'\n\n---\n\n'.join(parts)}
        try:
            response=requests.post('https://api.resend.com/emails',headers={'Authorization':'Bearer '+providers.get('RESEND_API_KEY'),'Idempotency-Key':key},json=body,timeout=25)
            if response.status_code not in [200,201]:raise RuntimeError('Email provider HTTP '+str(response.status_code))
            provider_id=response.json()['id']
            with db.connect() as conn:
                for row in rows:conn.execute("UPDATE notification_events SET status='accepted',provider_id=?,sent=?,error=NULL,attempts=attempts+1 WHERE id=?",(provider_id,db.now(),row['id']))
            db.set_meta('notification_batch',None)
            if c['mode']=='digest' and first['opportunity_id']!='TEST':db.set_meta('last_digest_day',now[:10])
        except Exception as e:
            with db.connect() as conn:
                for row in rows:
                    attempts=row['attempts']+1;next_due=(datetime.now(timezone.utc)+timedelta(minutes=min(360,5*2**attempts))).isoformat(timespec='seconds')
                    # Stop within provider's 24-hour idempotency window; uncertain acceptance needs review.
                    state='needs_review' if attempts>=5 else 'retry'
                    conn.execute('UPDATE notification_events SET status=?,attempts=?,next_due=?,error=? WHERE id=?',(state,attempts,next_due,str(e)[:300],row['id']))
    finally:
        with db.connect() as conn:conn.execute("DELETE FROM locks WHERE name='mail'")


def notification_records():
    records=db.rows();failed={s['id'] for s in db.sources() if s.get('error')}
    for row in records:
        if any(e['source_id'] in failed for e in row.get('sources',[])):row['verification_warning']='Latest source check failed'
    return ranked(records,db.get_meta('profile',{}),db.now()[:10])
