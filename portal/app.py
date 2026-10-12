import os, json, secrets, hashlib, time
from datetime import datetime, timezone
from urllib.parse import urlsplit
from flask import Flask, request, jsonify, session, render_template, redirect, Response
from werkzeug.security import check_password_hash
from portal import db
from portal.seed import bootstrap
from portal.model import ranked, recommendations, RANK_VERSION, DEFAULT_PROFILE, STAGES

def create_app(test=False):
    bootstrap()
    from portal.migrations import upgrade
    upgrade()
    app=Flask(__name__)
    production=os.environ.get('PORTAL_ENV')=='production'
    secret=os.environ.get('SECRET_KEY')
    if production and (not secret or len(secret)<32 or not os.environ.get('PORTAL_PASSWORD_HASH') or not os.environ.get('PORTAL_ORIGIN')): raise RuntimeError('Production requires SECRET_KEY (32+ chars), PORTAL_PASSWORD_HASH and PORTAL_ORIGIN')
    app.secret_key=secret or secrets.token_hex(32)
    app.config.update(SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SAMESITE='Strict',SESSION_COOKIE_SECURE=production,MAX_CONTENT_LENGTH=12_000_000,PERMANENT_SESSION_LIFETIME=3600*12)
    app.config['SESSION_COOKIE_NAME']='atlas_'+hashlib.sha256(os.environ.get('PORTAL_ORIGIN','http://127.0.0.1:8765').encode()).hexdigest()[:8]
    app.config['TESTING']=test
    @app.before_request
    def protect():
        allowed_origin=os.environ.get('PORTAL_ORIGIN','http://127.0.0.1:8765')
        allowed_host=urlsplit(allowed_origin).netloc
        if request.host!=allowed_host and not test: return jsonify(error='Unrecognized host'),400
        if request.path=='/health': return None
        if not production and request.remote_addr not in ['127.0.0.1','::1'] and not test: return jsonify(error='Local development access only'),403
        if request.method not in ['GET','HEAD','OPTIONS']:
            if request.headers.get('Origin')!=allowed_origin and not test: return jsonify(error='Origin check failed'),403
        if request.path.startswith('/static/') or request.path=='/login': return None
        if production:
            token=session.get('token')
            with db.connect() as c: valid=c.execute('SELECT 1 FROM sessions WHERE token_hash=? AND expires>?',(hashlib.sha256((token or '').encode()).hexdigest(),int(time.time()))).fetchone()
            if not valid: return (jsonify(error='Sign in required'),401) if request.path.startswith('/api/') else redirect('/login')
        if request.method not in ['GET','HEAD','OPTIONS'] and request.headers.get('X-CSRF-Token')!=session.get('csrf'): return jsonify(error='CSRF validation failed'),403
    @app.after_request
    def headers(response):
        response.headers.update({'X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','X-Frame-Options':'DENY','Cache-Control':'no-store','Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"})
        if request.path.endswith('/pdf') and request.path.startswith('/api/studio/documents/'):
            response.headers['X-Frame-Options']='SAMEORIGIN'
            response.headers['Content-Security-Policy']=response.headers['Content-Security-Policy'].replace("frame-ancestors 'none'","frame-ancestors 'self'")
        if production: response.headers['Strict-Transport-Security']='max-age=31536000'
        return response
    @app.get('/health')
    def health(): return jsonify(status='ok')
    @app.route('/login',methods=['GET','POST'])
    def login():
        if request.method=='GET':
            session['login_nonce']=secrets.token_urlsafe(24)
            return render_template('login.html',nonce=session['login_nonce'],error=None)
        epoch=int(time.time()); ip=request.remote_addr
        with db.connect() as c:
            c.execute('DELETE FROM login_attempts WHERE at<?',(epoch-900,))
            attempts=c.execute('SELECT COUNT(*) FROM login_attempts WHERE ip=?',(ip,)).fetchone()[0]
            c.execute('INSERT INTO login_attempts VALUES(?,?)',(ip,epoch))
        if attempts>=10: return 'Too many attempts. Try again in 15 minutes.',429
        if not secrets.compare_digest(request.form.get('nonce',''),session.get('login_nonce','invalid')): return 'Invalid sign-in request',403
        if not check_password_hash(os.environ.get('PORTAL_PASSWORD_HASH',''),request.form.get('password','')): return render_template('login.html',nonce=session.get('login_nonce'),error='Incorrect password'),401
        session.clear(); token=secrets.token_urlsafe(32); session['token']=token; session.permanent=True
        with db.connect() as c: c.execute('INSERT INTO sessions VALUES(?,?)',(hashlib.sha256(token.encode()).hexdigest(),epoch+12*3600))
        return redirect('/')
    @app.get('/')
    def index():
        session.setdefault('csrf',secrets.token_urlsafe(32))
        return render_template('index.html')
    @app.get('/api/state')
    def state():
        session.setdefault('csrf',secrets.token_urlsafe(32))
        p=db.get_meta('profile',DEFAULT_PROFILE); src=db.sources(); data=db.rows()
        for r in data:
            problems=[s for s in src if s['error'] and any(e['source_id']==s['id'] for e in r['sources'])]
            if problems: r['verification_warning']='Latest source check failed; last known record retained.'
        as_of=db.now()[:10]
        with db.connect() as c: runs=[dict(r) for r in c.execute('SELECT * FROM runs ORDER BY id DESC LIMIT 5')]
        from portal.checklist import for_record
        for r in data:r['application_checklist']=for_record(r)
        ordered=ranked(data,p,as_of)
        return jsonify(profile=p,recommendations=[r['id'] for r in recommendations(ordered)],opportunities=ordered,sources=src,runs=runs,csrf=session['csrf'],saved_searches=db.get_meta('saved_searches',[]),worker_heartbeat=db.get_meta('worker_heartbeat'),as_of=as_of,local=not production,ranking_version=RANK_VERSION)
    @app.get('/api/opportunities/<identity>/history')
    def history(identity):
        with db.connect() as c: records=[{'at':r['at'],'fields':json.loads(r['fields'])} for r in c.execute('SELECT * FROM changes WHERE opportunity_id=? ORDER BY id DESC LIMIT 30',(identity,))]
        return jsonify(records)
    @app.post('/api/workflow/<identity>')
    def workflow(identity):
        d=request.get_json() or {}
        with db.connect() as c:
            if not c.execute('SELECT 1 FROM opportunities WHERE id=?',(identity,)).fetchone(): return jsonify(error='Listing not found'),404
            row=c.execute('SELECT * FROM workflow WHERE opportunity_id=?',(identity,)).fetchone()
            old=dict(row) if row else {'stage':None,'notes':'','dismissed':False,'bookmarked':False}
            stage=d.get('stage',old['stage']); notes=d.get('notes',old['notes']); dismissed=d.get('dismissed',bool(old['dismissed'])); bookmarked=d.get('bookmarked',bool(old['bookmarked']))
            if stage is not None and stage not in STAGES or not isinstance(notes,str) or len(notes)>10000 or type(dismissed)!=bool or type(bookmarked)!=bool: return jsonify(error='Invalid workflow'),400
            c.execute('INSERT INTO workflow(opportunity_id,stage,notes,dismissed,updated,bookmarked) VALUES(?,?,?,?,?,?) ON CONFLICT(opportunity_id) DO UPDATE SET stage=excluded.stage,notes=excluded.notes,dismissed=excluded.dismissed,bookmarked=excluded.bookmarked,updated=excluded.updated',(identity,stage,notes,int(dismissed),db.now(),int(bookmarked)))
        return jsonify(ok=True)
    @app.post('/api/profile')
    def profile():
        d=request.get_json() or {}; p=db.get_meta('profile',DEFAULT_PROFILE)
        for k in ['name','university','degree','graduation','availability_start','residence_conditions','commitment']:
            if k in d:
                if d[k] is not None and (not isinstance(d[k],str) or len(d[k])>5000): return jsonify(error='Invalid '+k),400
                p[k]=d[k] or None
        for k in ['hours_hard','commitment_confirmed','enrolled']:
            if k in d:
                if d[k] is not None and type(d[k])!=bool: return jsonify(error='Invalid '+k),400
                p[k]=d[k]
        for k in ['skills','locations','interests','projects','education']:
            if k in d:
                if not isinstance(d[k],list) or len(d[k])>100 or any(not isinstance(v,str) or len(v)>1500 for v in d[k]): return jsonify(error='Invalid '+k),400
                p[k]=d[k]
        if 'languages' in d:
            if not isinstance(d['languages'],dict) or len(d['languages'])>30 or any(not isinstance(v,str) or len(v)>100 for v in d['languages'].values()): return jsonify(error='Invalid languages'),400
            p['languages']=d['languages']
        if 'max_hours' in d:
            if type(d['max_hours']) not in [int,float] or not 1<=d['max_hours']<=80: return jsonify(error='Hours must be 1–80'),400
            p['max_hours']=d['max_hours']
        if 'weights' in d:
            if not isinstance(d['weights'],dict) or set(d['weights'])!=set(DEFAULT_PROFILE['weights']) or any(type(v) not in [int,float] or not 0<=v<=100 for v in d['weights'].values()): return jsonify(error='Invalid weights'),400
            p['weights']=d['weights']
        for key in ['availability_start','graduation']:
            if p.get(key):
                try: datetime.fromisoformat(p[key])
                except ValueError: return jsonify(error=key+' must be a valid ISO date'),400
        db.set_meta('profile',p); return jsonify(ok=True)
    @app.post('/api/visit')
    def visit():
        p=db.get_meta('profile'); p['last_visit']=db.now(); db.set_meta('profile',p); return jsonify(ok=True)
    @app.post('/api/searches')
    def searches():
        d=request.get_json()
        if not isinstance(d,list) or len(d)>30 or len(json.dumps(d))>10000: return jsonify(error='Invalid saved searches'),400
        db.set_meta('saved_searches',d); return jsonify(ok=True)
    @app.post('/api/sources')
    def add_source():
        d=request.get_json() or {}; url=d.get('url',''); p=urlsplit(url)
        if p.scheme!='https' or not p.hostname or p.username or p.password or len(url)>2000: return jsonify(error='Enter a public HTTPS URL'),400
        identity=hashlib.sha256(url.encode()).hexdigest()[:12]
        data={'url':url,'name':p.hostname,'category':'research','adapter':'pending','enabled':False,'status':'Pending setup','interval_hours':24,'coverage':'Terms, robots and parser review required. Adding a URL does not enable fetching.'}
        with db.connect() as c: c.execute('INSERT OR IGNORE INTO sources(id,data) VALUES(?,?)',(identity,json.dumps(data)))
        return jsonify(ok=True)
    @app.post('/api/sources/<identity>')
    def source_settings(identity):
        d=request.get_json() or {}; hours=d.get('interval_hours')
        if hours not in [12,24]: return jsonify(error='Interval must be 12 or 24 hours'),400
        with db.connect() as c:
            row=c.execute('SELECT data FROM sources WHERE id=?',(identity,)).fetchone()
            if not row: return jsonify(error='Source not found'),404
            source=json.loads(row['data']); source['interval_hours']=hours
            c.execute('UPDATE sources SET data=? WHERE id=?',(json.dumps(source),identity))
        return jsonify(ok=True)
    @app.post('/api/refresh')
    def refresh():
        with db.connect() as c:
            c.execute('BEGIN IMMEDIATE')
            last=c.execute('SELECT created FROM requests ORDER BY id DESC LIMIT 1').fetchone()
            if last and time.time()-datetime.fromisoformat(last['created']).timestamp()<900: return jsonify(error='Manual refresh is limited to once every 15 minutes. Source backoff still applies.'),429
            c.execute('INSERT INTO requests(created,status) VALUES(?,?)',(db.now(),'queued'))
        return jsonify(ok=True,message='Queued for the independent worker. Only sources due for a check will run.'),202
    @app.get('/api/export')
    def export():
        return jsonify(profile=db.get_meta('profile'),opportunities=db.rows(),sources=db.sources(),saved_searches=db.get_meta('saved_searches'))
    @app.post('/api/delete-personal')
    def delete_personal():
        if (request.get_json() or {}).get('confirm')!='DELETE': return jsonify(error='Type DELETE to confirm'),400
        with db.connect() as c:
            c.execute('DELETE FROM workflow'); c.execute('DELETE FROM sessions')
        db.set_meta('profile',DEFAULT_PROFILE); db.set_meta('saved_searches',[])
        # Delete local personal import files and backups too, so restart cannot restore them.
        for f in [db.DB_PATH.parent/'profile.json',*(db.DB_PATH.parent/'backups').glob('*.sqlite3')]:
            if f.exists(): f.unlink()
        session.clear(); return jsonify(ok=True)
    @app.post('/api/logout')
    def logout():
        token=session.get('token','')
        with db.connect() as c: c.execute('DELETE FROM sessions WHERE token_hash=?',(hashlib.sha256(token.encode()).hexdigest(),))
        session.clear(); return jsonify(ok=True)
    from portal.studio_api import bp
    app.register_blueprint(bp)
    return app
app=create_app()
if __name__=='__main__': app.run(host='127.0.0.1',port=int(os.environ.get('PORTAL_PORT','8765')),debug=False)
