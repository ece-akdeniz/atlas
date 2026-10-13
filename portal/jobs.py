"""Independent durable document queue. Browser closure never cancels a job."""
import json,uuid,time,signal
from datetime import datetime,timedelta,timezone
from portal import db,studio,uploads

def enqueue(kind,data):
    if kind not in ['compile','write']:raise ValueError('Invalid job kind')
    data={**data,'project_id':project_id(data)}
    encoded=json.dumps(data,sort_keys=True)
    with db.connect() as c:
        existing=c.execute("SELECT id FROM jobs WHERE kind=? AND data=? AND status IN ('queued','running')",(kind,encoded)).fetchone()
        if existing:return existing['id']
        identity=uuid.uuid4().hex;c.execute('INSERT INTO jobs(id,kind,data,status,created) VALUES(?,?,?,?,?)',(identity,kind,encoded,'queued',db.now()))
    return identity

def once():
    cutoff=(datetime.now(timezone.utc)-timedelta(minutes=5)).isoformat(timespec='seconds')
    with db.connect() as c:
        c.execute('BEGIN IMMEDIATE')
        c.execute("UPDATE jobs SET status='failed',finished=?,result=? WHERE status='running' AND started<?",(db.now(),json.dumps({'error':'Worker interrupted; retry this job'}),cutoff))
        row=c.execute("SELECT * FROM jobs WHERE status='queued' ORDER BY created LIMIT 1").fetchone()
        if not row:return False
        c.execute("UPDATE jobs SET status='running',started=? WHERE id=?",(db.now(),row['id']))
    data=json.loads(row['data'])
    try:
        if row['kind']=='compile':
            from portal.compilation import compile_source
            d=studio.document(data['document_id']);result=compile_source(d['source'],d['metadata'].get('template_id'),uploads.root()/'compiled'/d['id']);d['metadata']['compilation']=result
            with db.connect() as c:c.execute('UPDATE studio_documents SET metadata=? WHERE id=?',(json.dumps(d['metadata']),d['id']))
            result['document_id']=d['id']
        else:
            from portal.writing import generate
            p=studio.project(data['project_id']);kind=data['kind'];template=data.get('template_id');current=studio.document(data['document_id']) if data.get('document_id') else None;generated=generate(p,kind,template,data.get('section'),current['source'] if current else None)
            source=studio.template_source(template,kind)
            if kind=='letter':source=studio.populate_letter(studio.target_letter(source,p['target']),'\n\n'.join(studio.tex(s['text']) for s in generated['sections']))
            # Model résumé suggestions are review-only. Apply selected edits explicitly through the UI.
            if current and data.get('section'):
                if len(generated.get('sections',[]))!=1:raise ValueError('Revision must return exactly one section')
                d=studio.revise_section(current['id'],data['section']['id'],generated['sections'][0]['text'])
                d['metadata']['generation']=generated
                with db.connect() as c:c.execute('UPDATE studio_documents SET metadata=? WHERE id=?',(json.dumps(d['metadata']),d['id']))
            else:d=studio.new_document(p['id'],kind,source,{'template_id':template,'method':'model-suggestions','generation':generated,'review_required':True,'before':source if kind=='resume' else None})
            result={'document_id':d['id']}
        status='complete'
    except Exception as e:status='failed';result={'error':str(e)[-10000:]}
    with db.connect() as c:c.execute('UPDATE jobs SET status=?,finished=?,result=? WHERE id=?',(status,db.now(),json.dumps(result),row['id']))
    return True

def main():
    from portal.seed import bootstrap
    from portal.migrations import upgrade
    bootstrap();upgrade();running=True
    def stop(*_):
        nonlocal running
        running=False
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    while running:
        db.set_meta('studio_heartbeat',db.now())
        if not once():time.sleep(2)


def project_id(data):
    if data.get('project_id'):return data['project_id']
    try:return studio.document(data['document_id'])['project_id']
    except (ValueError,KeyError):return None

if __name__=='__main__':main()
