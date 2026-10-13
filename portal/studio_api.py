import io,json,zipfile,shutil,secrets
from flask import Blueprint,request,jsonify,render_template,session,send_file
from portal import db,studio,uploads,jobs
bp=Blueprint('studio',__name__)
@bp.errorhandler(ValueError)
def invalid(e):return jsonify(error=str(e)),400
@bp.get('/studio')
def index():return render_template('studio.html')
@bp.get('/api/studio')
def state():
    session.setdefault('csrf',secrets.token_urlsafe(32))
    with db.connect() as c:
        projects=[{**json.loads(r['data']),'id':r['id'],'updated':r['updated']} for r in c.execute('SELECT * FROM studio_projects ORDER BY updated DESC')]
        imports=[{**dict(r),'metadata':json.loads(r['metadata'])} for r in c.execute('SELECT * FROM uploads ORDER BY created DESC')]
        queue=[{**dict(r),'result':json.loads(r['result']),'project_id':jobs.project_id(json.loads(r['data']))} for r in c.execute('SELECT id,kind,status,created,result,data FROM jobs ORDER BY created DESC,rowid DESC LIMIT 100')]
    for p in projects:p['readiness']=studio.readiness(p)
    import os
    return jsonify(projects=projects,uploads=imports,jobs=queue,heartbeat=db.get_meta('studio_heartbeat'),model_configured=bool(os.getenv('OPENAI_API_KEY')),model=os.getenv('STUDIO_MODEL','gpt-6-luna'),csrf=session.get('csrf'))
@bp.post('/api/uploads')
def upload():
    f=request.files.get('file')
    if not f:raise ValueError('Choose a file')
    u=uploads.store(f.filename,f.read(),request.form.get('kind','cv'),request.form.get('main') or None)
    if u['kind']=='cv':u=uploads.import_cv(u)
    return jsonify(u)
@bp.post('/api/uploads/<identity>/review')
def review(identity):
    return jsonify(uploads.resolve(identity,(request.get_json() or {}).get('decisions',[])))
@bp.post('/api/imports/<int:identity>/undo')
def undo(identity):return jsonify(profile=uploads.undo(identity))
@bp.delete('/api/uploads/<identity>')
def delete_upload(identity):
    uploads.get(identity)
    with db.connect() as c:
        c.execute('DELETE FROM uploads WHERE id=?',(identity,));c.execute('DELETE FROM profile_versions WHERE upload_id=?',(identity,))
    shutil.rmtree(uploads.root()/identity,ignore_errors=True)
    return jsonify(ok=True,message='Upload deleted; confirmed profile facts retained')
@bp.post('/api/studio/projects')
def create():return jsonify(studio.create(request.get_json() or {}))
@bp.route('/api/studio/projects/<identity>',methods=['GET','PATCH','DELETE'])
def project(identity):
    p=studio.project(identity)
    if request.method=='DELETE':
        for d in studio.documents(identity):shutil.rmtree(uploads.root()/'compiled'/d['id'],ignore_errors=True)
        with db.connect() as c:c.execute('DELETE FROM studio_documents WHERE project_id=?',(identity,));c.execute('DELETE FROM studio_projects WHERE id=?',(identity,))
        return jsonify(ok=True)
    if request.method=='PATCH':
        payload=request.get_json() or {}
        if not isinstance(payload,dict):raise ValueError('Expected project fields')
        for key in ['settings','progress','templates']:
            if key in payload and not isinstance(payload[key],dict):raise ValueError('Invalid '+key)
        if 'notes' in payload and (not isinstance(payload['notes'],str) or len(payload['notes'])>10000):raise ValueError('Invalid notes')
        if payload.get('status')=='Ready' and not studio.readiness(p)['ready']:raise ValueError('Complete required checklist items and review compiled documents first')
        if 'status' in payload and payload['status'] not in ['Preparing','Ready','Applied','Archived']:raise ValueError('Invalid status')
        if 'settings' in payload:
            setting=payload['settings']
            for key,allowed in [('language',['English','German']),('length',['One page','Brief (250 words)']),('tone',['Direct and professional','Warm and concise','Academic'])]:
                if setting.get(key) not in allowed:raise ValueError('Invalid '+key)
            if not isinstance(setting.get('experiences',[]),list) or any(type(i)!=int or i<0 or i>=len(p['profile'].get('projects',[])) for i in setting.get('experiences',[])):raise ValueError('Invalid selected experiences')
        if 'progress' in payload:
            valid={item['id'] for item in p['checklist']}
            if any(k not in valid or type(v)!=bool for k,v in payload['progress'].items()):raise ValueError('Invalid checklist progress')
        if 'templates' in payload:
            for kind,identity in payload['templates'].items():
                if kind not in ['letter','resume']:raise ValueError('Invalid template type')
                if identity:studio.template_source(identity,kind)
        for key in ['settings','progress','templates','notes','status']:
            if key in payload:p[key]=payload[key]
        if len(json.dumps(p))>200000:raise ValueError('Project exceeds storage limit')
        studio.save_project(p)
    return jsonify(project={**p,'readiness':studio.readiness(p)},documents=studio.documents(p['id']))
@bp.post('/api/studio/projects/<identity>/draft')
def draft(identity):
    p=studio.project(identity);d=request.get_json() or {};kind=d.get('kind','letter');template=d.get('template_id')
    if kind not in ['letter','resume']:raise ValueError('Invalid document type')
    if d.get('model'):
        if d.get('consent') is not True:raise ValueError('Confirm external processing of selected profile facts and posting')
        return jsonify(job_id=jobs.enqueue('write',{'project_id':identity,'kind':kind,'template_id':template,'section':d.get('section')})),202
    return jsonify(studio.local_draft(p,kind,template))
@bp.post('/api/studio/documents/<identity>')
def edit(identity):
    d=studio.document(identity);payload=request.get_json() or {}
    if not isinstance(payload.get('source'),str):raise ValueError('LaTeX source must be text')
    meta={**d['metadata'],'parent_id':identity};meta.pop('compilation',None);meta.pop('visual_reviewed',None);meta['before']=d['source'];meta['diff']=studio.diff_versions(d['source'],payload.get('source',''))
    return jsonify(studio.new_document(d['project_id'],d['kind'],payload.get('source'),meta))
@bp.post('/api/studio/documents/<identity>/compile')
def compile_doc(identity):studio.document(identity);return jsonify(job_id=jobs.enqueue('compile',{'document_id':identity})),202
@bp.post('/api/studio/documents/<identity>/ready')
def ready(identity):
    d=studio.document(identity);comp=d['metadata'].get('compilation',{})
    if comp.get('status')!='compiled' or comp.get('warnings'):raise ValueError('Compile successfully and resolve document warnings first')
    if (request.get_json() or {}).get('reviewed') is not True:raise ValueError('Review the PDF and factual claims first')
    d['metadata']['visual_reviewed']=db.now()
    with db.connect() as c:c.execute('UPDATE studio_documents SET metadata=? WHERE id=?',(json.dumps(d['metadata']),identity))
    return jsonify(ok=True)
@bp.get('/api/studio/documents/<identity>/<extension>')
def download(identity,extension):
    d=studio.document(identity)
    if extension=='tex':return send_file(io.BytesIO(d['source'].encode()),mimetype='text/plain',as_attachment=True,download_name=d['kind']+'.tex')
    if extension=='pdf':
        path=uploads.root()/'compiled'/identity/'document.pdf'
        if not path.exists():raise ValueError('Compile this version first')
        return send_file(path,mimetype='application/pdf',download_name=d['kind']+'.pdf',as_attachment=request.args.get('download')=='1')
    if extension=='zip':
        buffer=io.BytesIO()
        with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED) as z:
            template=d['metadata'].get('template_id');main='main.tex'
            if template:
                u=uploads.get(template);main=u['metadata']['main']
                for name in u['metadata']['files']:
                    if name!=main:z.write(uploads.root()/template/name,name)
            z.writestr(main,d['source']);z.writestr('ATLAS-README.txt','Private application draft. Review claims and layout before submitting. Master template is unchanged.')
        buffer.seek(0);return send_file(buffer,mimetype='application/zip',as_attachment=True,download_name=d['kind']+'-source.zip')
    raise ValueError('Unknown download format')
@bp.get('/api/studio/documents/<identity>/preview/<int:page>')
def preview(identity,page):
    studio.document(identity)
    if not 1<=page<=10:raise ValueError('Invalid page')
    path=uploads.root()/'compiled'/identity/f'page-{page}.png'
    if not path.exists():raise ValueError('Page preview unavailable; download the PDF')
    return send_file(path,mimetype='image/png')
@bp.route('/api/notifications',methods=['GET','POST'])
def notification_settings():
    from portal import notifications as n
    if request.method=='POST':n.configure(request.get_json() or {})
    with db.connect() as c:events=[{k:r[k] for k in ['id','status','created','sent','error']} for r in c.execute('SELECT * FROM notification_events ORDER BY created DESC LIMIT 20')]
    return jsonify(settings=n.settings(),configured=n.configured(),events=events)
@bp.post('/api/notifications/test')
def test_email():
    from portal.notifications import queue_test
    return jsonify(id=queue_test(),message='Test email queued; provider acceptance is not inbox delivery'),202

@bp.post('/api/studio/documents/<identity>/suggestions')
def suggestions(identity):
    data=request.get_json() or {}
    return jsonify(studio.decide_edits(identity,data.get('decisions',{}),data.get('apply') is True))
@bp.post('/api/studio/documents/<identity>/section')
def section_revision(identity):
    d=studio.document(identity);data=request.get_json() or {}
    if data.get('model'):
        if data.get('consent') is not True:raise ValueError('Confirm external processing')
        section=next((s for s in studio.letter_sections(d['source']) if s['id']==str(data.get('section_id'))),None)
        if not section:raise ValueError('Choose a saved letter section')
        return jsonify(job_id=jobs.enqueue('write',{'project_id':d['project_id'],'kind':'letter','template_id':d['metadata'].get('template_id'),'document_id':identity,'section':section})),202
    return jsonify(studio.revise_section(identity,data.get('section_id'),data.get('text')))
