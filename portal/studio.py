"""Versioned application projects; master files are never overwritten."""
import json,uuid,hashlib,re,difflib
from pathlib import Path
from portal import db,uploads
from portal.checklist import for_record

LETTER=r'''\documentclass[11pt,a4paper]{article}
\usepackage[margin=25mm]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage[hidelinks]{hyperref}
\setlength{\parindent}{0pt}
\setlength{\parskip}{9pt}
\begin{document}
% ATLAS:BEGIN body
[[LETTER_BODY]]
% ATLAS:END body
\end{document}
'''
RESUME=r'''\documentclass[11pt,a4paper]{article}
\usepackage[margin=22mm]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\begin{document}
[[RESUME_BODY]]
\end{document}
'''
def tex(value):
    mapping={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}
    return ''.join(mapping.get(c,c) for c in str(value))
def project(identity):
    with db.connect() as c:r=c.execute('SELECT * FROM studio_projects WHERE id=?',(identity,)).fetchone()
    if not r:raise ValueError('Application project not found')
    return {**json.loads(r['data']),'id':r['id'],'created':r['created'],'updated':r['updated']}
def save_project(p):
    data={k:v for k,v in p.items() if k not in ['id','created','updated']}
    with db.connect() as c:c.execute('UPDATE studio_projects SET data=?,updated=? WHERE id=?',(json.dumps(data),db.now(),p['id']))
def create(payload):
    target=next((r for r in db.rows() if r['id']==payload.get('opportunity_id')),None)
    if not target:
        t=payload.get('posting',{})
        if not t.get('title') or not t.get('organization'):raise ValueError('Title and organization are required')
        if len(json.dumps(t))>40000:raise ValueError('Posting exceeds 40 KB')
        target={'title':str(t['title'])[:400],'organization':str(t['organization'])[:300],'summary':str(t.get('text',''))[:30000],'application_method':str(t.get('text',''))[:30000],'url':t.get('url','') if str(t.get('url','')).startswith('https://') else '', 'category':'jobs','record_kind':'manual_posting','required':[]}
    p=db.get_meta('profile',{});identity=uuid.uuid4().hex
    value={'opportunity_id':target.get('id'),'target':target,'profile':p,'profile_hash':hashlib.sha256(json.dumps(p,sort_keys=True).encode()).hexdigest(),'profile_version':db.get_meta('active_cv_version'),'checklist':for_record(target),'progress':{},'templates':{},'status':'Preparing','settings':{'language':'English','length':'One page','tone':'Direct and professional','experiences':[]},'notes':''}
    with db.connect() as c:c.execute('INSERT INTO studio_projects VALUES(?,?,?,?)',(identity,json.dumps(value),db.now(),db.now()))
    return project(identity)
def document(identity):
    with db.connect() as c:r=c.execute('SELECT * FROM studio_documents WHERE id=?',(identity,)).fetchone()
    if not r:raise ValueError('Document not found')
    d={**dict(r),'metadata':json.loads(r['metadata'])}
    if d['kind']=='letter':d['sections']=letter_sections(d['source'])
    return d
def documents(pid):
    with db.connect() as c:return [document(r['id']) for r in c.execute('SELECT id FROM studio_documents WHERE project_id=? ORDER BY created DESC,rowid DESC',(pid,))]
def new_document(pid,kind,source,metadata=None):
    project(pid)
    if kind not in ['letter','resume'] or not isinstance(source,str) or len(source)>250000:raise ValueError('Invalid document')
    identity=uuid.uuid4().hex
    with db.connect() as c:c.execute('INSERT INTO studio_documents VALUES(?,?,?,?,?,?)',(identity,pid,kind,source,json.dumps(metadata or {}),db.now()))
    return document(identity)
def template_source(identity,kind):
    if not identity:return LETTER if kind=='letter' else RESUME
    u=uploads.get(identity)
    if u['kind']!=('letter_template' if kind=='letter' else 'resume_template'):raise ValueError('Template type does not match this document')
    return (uploads.root()/identity/u['metadata']['main']).read_text(errors='replace')
def tailored_resume(source,target):
    # Conservative initial tailoring: reorder complete project macro blocks without changing claims.
    m=re.search(r'(\\section\{(?:Research\s*\\?&\s*)?Projects\}.*?)(?=\\section|\\end\{document\})',source,re.S|re.I)
    if not m:return source,[], 'No recognized project blocks; master content preserved. Use direct editing or model suggestions.'
    section=m[0];blocks=list(re.finditer(r'\\resumeProjectHeading\b.*?(?=\\resumeProjectHeading\b|\\resumeSubHeadingListEnd)',section,re.S))
    if len(blocks)<2:return source,[], 'No reorderable project blocks; master preserved.'
    words=set(re.findall(r'\b[a-z]{4,}\b',(target.get('title','')+' '+target.get('summary','')).lower()))
    ordered=sorted(enumerate(blocks),key=lambda p:(-len(words&set(re.findall(r'\b[a-z]{4,}\b',p[1][0].lower()))),p[0]))
    reordered=section[:blocks[0].start()]+''.join(b[0] for _,b in ordered)+section[blocks[-1].end():]
    result=source[:m.start()]+reordered+source[m.end():]
    return result,[{'change':'Order complete project entries by overlap with the target research topic','reason':'Prioritize relevant evidence without rewriting skills, accomplishments or dates'}], 'Exact project wording retained; review the before/after diff.'
def local_draft(p,kind,template_id=None):
    source=template_source(template_id,kind);profile=p['profile'];target=p['target']
    meta={'method':'local-evidence-draft-1.0','template_id':template_id,'review_required':True,'profile_hash':p['profile_hash'],'suggestions':[]}
    if kind=='resume':
        if template_id:
            source,suggestions,note=tailored_resume(source,target);meta.update(suggestions=suggestions,note=note,before=template_source(template_id,kind))
        else:
            body=r'\section*{'+tex(profile.get('name','Your name'))+'}\n'
            for key,label in [('education','Education'),('experience','Experience'),('projects','Projects'),('skills','Skills')]:
                if profile.get(key):body+=r'\section*{'+label+'}\n'+ '\n\n'.join(tex(x) for x in profile[key])+'\n'
            source=source.replace('[[RESUME_BODY]]',body);meta['note']='Starter layout; choose your master template to preserve its formatting.'
    else:
        if p['settings'].get('language','English')!='English':raise ValueError('Local starter letters support English. Enable model assistance for German, or edit the source directly.')
        selected=p['settings'].get('experiences') or list(range(min(2,len(profile.get('projects',[])))))
        experiences=[profile.get('projects',[])[i] for i in selected if isinstance(i,int) and 0<=i<len(profile.get('projects',[]))]
        body='Dear hiring team,\n\nI am applying for '+target['title']+' at '+target['organization']+'.'
        if profile.get('degree'):body+=' I am studying '+profile['degree']+'.'
        if experiences:body+='\n\n'+'\n\n'.join(experiences)
        body+='\n\nI would welcome the opportunity to discuss how this experience relates to the work described in your posting.\n\nKind regards,\n\n'+profile.get('name','')
        source=target_letter(source,target)
        source=populate_letter(source,tex(body));meta['note']='Evidence-only starter in English. Review and adapt the connections; model writing is separately opt-in.'
    meta['diff']=diff_versions(meta.get('before',''),source) if meta.get('before') is not None else ''
    return new_document(p['id'],kind,source,meta)
def target_letter(source,target):
    # Replace only the recipient argument; keep the uploaded page layout and signature.
    return re.sub(r'(\\begin\{letter\}\{).*?\}',lambda m:m[1]+tex(target['organization'])+'}',source,flags=re.S)
def populate_letter(source,body):
    if '[[LETTER_BODY]]' in source:return source.replace('[[LETTER_BODY]]',body)
    pattern=r'(% ATLAS:BEGIN body\s*).*?(% ATLAS:END body)'
    if re.search(pattern,source,re.S):return re.sub(pattern,lambda m:m[1]+body+'\n'+m[2],source,flags=re.S)
    match=re.search(r'(\\opening\{[^}]*\})(.*?)(\\end\{letter\})',source,re.S)
    if match:
        body=re.sub(r'^Dear[^,]*,\s*','',body)
        source=source[:match.start()]+r'\opening{Dear hiring team,}'+ '\n\n'+body+'\n\n'+match[3]+source[match.end():]
        return re.sub(r'(?m)^```.*$','',source)
    raise ValueError('Add [[LETTER_BODY]] or ATLAS body markers to a copy of this template to identify the editable letter body; its layout will be preserved')
def diff_versions(before,after):return '\n'.join(difflib.unified_diff(before.splitlines(),after.splitlines(),fromfile='Previous / master',tofile='Draft',lineterm=''))


def letter_sections(source):
    marker=re.search(r'% ATLAS:BEGIN body\s*([\s\S]*?)% ATLAS:END body',source)
    if marker:start,end=marker.start(1),marker.end(1)
    else:
        opening=re.search(r'\\opening\{[^}]*\}',source)
        closing=re.search(r'\\(?:closing|end\{letter\})',source)
        if not opening or not closing:return []
        start,end=opening.end(),closing.start()
    return [{'id':str(i),'source':m[0],'text':untex(m[0]),'start':start+m.start(),'end':start+m.end()} for i,m in enumerate(re.finditer(r'\S[^\n]*(?:\n(?!\s*\n)[^\n]+)*',source[start:end]))]

def derived_metadata(d):
    meta={**d['metadata'],'parent_id':d['id'],'before':d['source'],'review_required':True}
    for key in ['compilation','visual_reviewed']:meta.pop(key,None)
    return meta

def revise_section(identity,section_id,text):
    d=document(identity)
    if d['kind']!='letter' or not isinstance(text,str) or not text.strip() or len(text)>12000:raise ValueError('Enter a letter section of at most 12,000 characters')
    section=next((s for s in letter_sections(d['source']) if s['id']==str(section_id)),None)
    if not section:raise ValueError('Section not found in this saved version')
    source=d['source'][:section['start']]+tex(text)+d['source'][section['end']:]
    meta=derived_metadata(d);meta.update(diff=diff_versions(d['source'],source),revision_section=str(section_id),method='user-section-revision')
    return new_document(d['project_id'],'letter',source,meta)

def decide_edits(identity,decisions,apply=False):
    d=document(identity);edits=d['metadata'].get('generation',{}).get('edits',[])
    if d['kind']!='resume' or not isinstance(decisions,dict):raise ValueError('Résumé suggestions required')
    if any(not str(k).isdigit() or not 0<=int(k)<len(edits) or v not in ['accepted','rejected','pending'] for k,v in decisions.items()):raise ValueError('Invalid edit decision')
    saved={**d['metadata'].get('edit_decisions',{}),**decisions};d['metadata']['edit_decisions']=saved
    if not apply:
        with db.connect() as c:c.execute('UPDATE studio_documents SET metadata=? WHERE id=?',(json.dumps(d['metadata']),identity))
        return document(identity)
    selected=[(i,e) for i,e in enumerate(edits) if saved.get(str(i))=='accepted']
    if not selected:raise ValueError('Accept at least one suggestion')
    spans=[]
    for i,e in selected:
        original=e.get('original');replacement=e.get('replacement')
        if not original or not isinstance(replacement,str) or d['source'].count(original)!=1:raise ValueError('Suggested text must match exactly once; edit the source manually if ambiguous')
        if not e.get('evidence_ids'):raise ValueError('Suggestion lacks profile evidence; keep it for manual review')
        # Models provide prose only. Never replace or introduce template commands.
        if re.search(r'\\[a-zA-Z]+|[{}]',original):raise ValueError('Suggestion touches LaTeX layout; use the source editor instead')
        start=d['source'].index(original);end=start+len(original)
        if any(start<b and end>a for a,b,_ in spans):raise ValueError('Selected suggestions overlap; apply them separately')
        spans.append((start,end,tex(replacement)))
    source=d['source']
    for start,end,replacement in sorted(spans,reverse=True):source=source[:start]+replacement+source[end:]
    meta=derived_metadata(d);meta.update(edit_decisions=saved,applied_edits=[i for i,_ in selected],diff=diff_versions(d['source'],source))
    return new_document(d['project_id'],'resume',source,meta)

def readiness(p):
    latest={}
    for d in documents(p['id']):latest.setdefault(d['kind'],d)
    required=[c for c in p['checklist'] if c['requirement']!='optional']
    missing=[c['label'] for c in required if not p.get('progress',{}).get(c['id'])]
    kinds={'resume' if c['label']=='CV / résumé' else 'letter' for c in required if c['label'] in ['CV / résumé','Cover / motivation letter']}
    kinds|=set(latest)
    pending=[k for k in kinds if k not in latest or latest[k]['metadata'].get('compilation',{}).get('status')!='compiled' or latest[k]['metadata'].get('compilation',{}).get('warnings') or not latest[k]['metadata'].get('visual_reviewed')]
    ready=bool(latest) and not missing and not pending
    return {'ready':ready,'missing_checklist':missing,'documents_to_review':pending,'label':'Ready for your final check' if ready else 'Preparing'}


def untex(value):
    replacements={r'\textbackslash{}':'\\',r'\&':'&',r'\%':'%',r'\$':'$',r'\#':'#',r'\_':'_',r'\{':'{',r'\}':'}',r'\textasciitilde{}':'~',r'\textasciicircum{}':'^'}
    for key,text in replacements.items():value=value.replace(key,text)
    return value
