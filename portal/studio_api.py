import io,json,zipfile,shutil
from flask import Blueprint,request,jsonify,render_template,session,send_file
from portal import db,studio,uploads,jobs
bp=Blueprint('studio',__name__)
@bp.errorhandler(ValueError)
def invalid(e):return jsonify(error=str(e)),400
@bp.get('/studio')
def index():return render_template('studio.html')
@bp.get('/api/studio')
def state():
    with db.connect() as c:
        projects=[{**json.loads(r['data']),'id':r['id'],'updated':r['updated']} for r in c.execute('SELECT * FROM studio_projects ORDER BY updated DESC')]
        imports=[{**dict(r),'metadata':json.loads(r['metadata'])} for r in c.execute('SELECT * FROM uploads ORDER BY created DESC')]
        queue=[{**dict(r),'result':json.loads(r['result'])} for r in c.execute('SELECT id,kind,status,created,result FROM jobs ORDER BY created DESC LIMIT 20')]
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
    u=uploads.get(identity);selection=(request.get_json() or {}).get('indices',[]);p=db.get_meta('profile');before=json.loads(json.dumps(p));pending=u['metadata'].get('review',[])
    if not isinstance(selection,list) or any(type(i)!=int or i<0 or i>=len(pending) for i in selection):raise ValueError('Invalid selection')
    for i in selection:
        item=pending[i];key=item['field']
        if key=='languages':p.setdefault(key,{})[item['key']]=item['proposed']
        elif item['proposed'] not in p.setdefault(key,[]):p[key].append(item['proposed'])
        p.setdefault('provenance',{})[key]={'source':'reviewed CV','upload_id':identity,'at':db.now()}
    u['metadata']['review']=[v for i,v in enumerate(pending) if i not in selection]
    changes={k:p[k] for k in p if p[k]!=before.get(k)}
    with db.connect() as c:
        version=c.execute('INSERT INTO profile_versions(profile,changes,upload_id,created) VALUES(?,?,?,?)',(json.dumps(before),json.dumps({'before':before,'after':p,'changes':changes}),identity,db.now())).lastrowid
        u['metadata']['version_id']=version;c.execute('UPDATE uploads SET metadata=? WHERE id=?',(json.dumps(u['metadata']),identity))
    db.set_meta('profile',p);return jsonify(ok=True)
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
        for key in ['settings','progress','templates','notes','status']:
            if key in payload:p[key]=payload[key]
        if len(json.dumps(p))>200000:raise ValueError('Project exceeds storage limit')
        studio.save_project(p)
    return jsonify(project=p,documents=studio.documents(identity))
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
    d=studio.document(identity);payload=request.get_json() or {};meta={**d['metadata'],'parent_id':identity};meta.pop('compilation',None);meta.pop('visual_reviewed',None)
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
