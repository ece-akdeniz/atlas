"""Private bounded uploads and conservative, entirely local CV import."""
import io,json,hashlib,uuid,zipfile,re,shutil
from pathlib import Path,PurePosixPath
from pypdf import PdfReader
from portal import db
from portal.extraction import recognize_skills
ALLOWED={'.tex','.sty','.cls','.bib','.bst','.png','.jpg','.jpeg','.pdf','.ttf','.otf'}
def root():
    p=db.DB_PATH.parent/'private';p.mkdir(exist_ok=True);p.chmod(0o700);return p

def files_from_upload(name,raw):
    if len(raw)>10_000_000:raise ValueError('Upload limit is 10 MB')
    if name.lower().endswith('.zip'):
        z=zipfile.ZipFile(io.BytesIO(raw));members=[m for m in z.infolist() if not m.is_dir() and not m.filename.startswith('__MACOSX/')]
        if len(members)>100 or sum(m.file_size for m in members)>20_000_000:raise ValueError('Bundle exceeds 100 files / 20 MB expanded')
        out={}
        for m in members:
            path=PurePosixPath(m.filename)
            if path.is_absolute() or '..' in path.parts or '\\' in m.filename or len(path.parts)>5 or (m.external_attr>>16)&0o170000==0o120000:raise ValueError('Unsafe bundle path or symbolic link')
            if path.suffix.lower() not in ALLOWED:raise ValueError('Unsupported asset: '+path.name)
            if m.compress_size and m.file_size/m.compress_size>200:raise ValueError('Archive compression ratio exceeds limit')
            out[str(path)]=z.read(m)
        return out
    suffix=Path(name).suffix.lower()
    if suffix not in ALLOWED:raise ValueError('Use PDF, LaTeX or a ZIP containing template assets')
    return {Path(name).name:raw}

def store(name,raw,kind,main=None):
    if kind not in ['cv','resume_template','letter_template']:raise ValueError('Invalid upload kind')
    digest=hashlib.sha256(raw).hexdigest()
    with db.connect() as c:old=c.execute('SELECT * FROM uploads WHERE kind=? AND hash=?',(kind,digest)).fetchone()
    if old:return {**dict(old),'metadata':json.loads(old['metadata']),'duplicate':True}
    files=files_from_upload(name,raw);tex=[n for n in files if n.endswith('.tex')];pdf=[n for n in files if n.endswith('.pdf')]
    main=main or (tex[0] if len(tex)==1 else pdf[0] if not tex and len(pdf)==1 else None)
    if main not in files:raise ValueError('Specify the main .tex or PDF filename in this bundle')
    if kind!='cv' and not main.endswith('.tex'):raise ValueError('Templates need a main LaTeX .tex file')
    identity=uuid.uuid4().hex;folder=root()/identity;folder.mkdir(mode=0o700)
    for rel,content in files.items():
        target=folder/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(content);target.chmod(0o600)
    meta={'main':main,'files':list(files),'parser':'local-cv-1.0','review':[],'changes':{}}
    with db.connect() as c:c.execute('INSERT INTO uploads VALUES(?,?,?,?,?,?)',(identity,kind,Path(name).name,digest,json.dumps(meta),db.now()))
    return {'id':identity,'kind':kind,'name':Path(name).name,'hash':digest,'metadata':meta,'duplicate':False}

def get(identity):
    with db.connect() as c:r=c.execute('SELECT * FROM uploads WHERE id=?',(identity,)).fetchone()
    if not r:raise ValueError('Upload not found')
    return {**dict(r),'metadata':json.loads(r['metadata'])}

def latex_text(text):
    # Never execute a CV during import. Preserve macro argument text and section boundaries.
    text=re.sub(r'(?m)(?<!\\)%.*$','',text)
    text=re.sub(r'\\(?:section|subsection)\*?(?:\[[^\]]*\])?\{([^}]*)\}',r'\n\n\1\n',text)
    text=re.sub(r'\\(?:documentclass|usepackage|includegraphics|input|include)(?:\[[^\]]*\])?\{[^}]*\}','',text)
    text=re.sub(r'\\(?:item|resumeItem|cventry|resumeSubheading)\b',r'\n',text)
    text=re.sub(r'\\(?:begin|end)\{[^}]*\}','\n',text)
    text=text.replace('\\\\','\n');text=re.sub(r'\\[A-Za-z]+\*?(?:\[[^\]]*\])?',' ',text)
    return text.replace('\\&','&').replace('{',' ').replace('}',' ').replace('~',' ')

def parse_cv(upload):
    path=root()/upload['id']/upload['metadata']['main']
    if path.suffix=='.pdf':
        reader=PdfReader(path)
        if len(reader.pages)>15:raise ValueError('CV exceeds 15 pages')
        text='\n'.join(p.extract_text() or '' for p in reader.pages)
    else:text=latex_text(path.read_text(errors='replace'))
    if len(text.strip())<50:raise ValueError('No usable text extracted; scanned PDFs need a text layer or your LaTeX source')
    fields={};section=None
    aliases={'education':'education','academic background':'education','ausbildung':'education','experience':'experience','work experience':'experience','professional experience':'experience','projects':'projects','selected projects':'projects','research projects':'projects','research & projects':'projects','relevant experience':'experience','skills':'skills','technical skills':'skills','languages':'languages','sprachen':'languages','interests':'ignore','interests and hobbies':'ignore'}
    for line in text.splitlines():
        line=' '.join(line.split()).strip('•- ')
        if not line:continue
        label=line.rstrip(':').casefold()
        if label in aliases:section=aliases[label];continue
        if section in ['education','experience','projects'] and len(line)>15:fields.setdefault(section,[]).append(line[:1500])
        if section=='skills':fields.setdefault('skills',[]).extend(recognize_skills(line))
        if section=='languages' or 'spoken languages' in line.lower():
            for lang in ['English','German','Turkish','French','Italian','Spanish']:
                m=re.search(r'\b'+lang+r'\b\s*[(:–—-]?\s*(Native|Mother tongue|[ABC][12]|Fluent|Intermediate|Basic)',line,re.I)
                if m:fields.setdefault('languages',{})[lang]=m[1]

    if path.suffix=='.tex':
        source=path.read_text(errors='replace')
        # Keep a complete dated entry together; never split accomplishments into separate projects.
        for title,key,macro in [('Education','education','resumeSubheading'),('Relevant Experience','experience','resumeSubheading'),('Experience','experience','resumeSubheading'),('Research \\& Projects','projects','resumeProjectHeading'),('Projects','projects','resumeProjectHeading')]:
            match=re.search(r'\\section\{'+re.escape(title)+r'\}(.*?)(?=\\section\{|\\end\{document\})',source,re.S)
            if not match:continue
            blocks=re.split(r'(?=\\'+macro+r'\b)',match[1])[1:]
            entries=[]
            for block in blocks:
                entry=' '.join(latex_text(block).split())
                entry=re.sub(r'\[leftmargin=.*?\]','',entry)
                if len(entry)>15:entries.append(entry[:1500])
            if entries:fields[key]=entries

    for k,v in list(fields.items()):
        if isinstance(v,list):fields[k]=list(dict.fromkeys(v))[:100]
    return fields,text

def import_cv(upload):
    if upload.get('duplicate'):return upload
    fields,text=parse_cv(upload);before=db.get_meta('profile',{});after=json.loads(json.dumps(before));changes={};review=[]
    prov=after.setdefault('provenance',{})
    for key,values in fields.items():
        if key=='languages':
            current=after.setdefault(key,{})
            for lang,value in values.items():
                if lang in current and current[lang].casefold()!=value.casefold():review.append({'field':'languages','key':lang,'current':current[lang],'proposed':value});continue
                if lang not in current:current[lang]=value;changes.setdefault('languages',{})[lang]=value
        elif key=='skills':
            current=after.setdefault(key,[])
            for value in values:
                if value.casefold() not in {x.casefold() for x in current}:current.append(value);changes.setdefault(key,[]).append(value)
        else:
            current=after.get(key,[])
            if not current:after[key]=values;changes[key]=values
            else:
                for value in values:
                    if value.casefold() not in {x.casefold() for x in current}:review.append({'field':key,'proposed':value,'reason':'Confirm this entry and its dates; preserve existing wording'})
        if key in changes:prov[key]={'source':'cv','upload_id':upload['id'],'parser':'local-cv-1.0','at':db.now()}
    meta=upload['metadata'];meta.update(changes=changes,review=review,extracted=fields)
    with db.connect() as c:
        version=c.execute('INSERT INTO profile_versions(profile,changes,upload_id,created) VALUES(?,?,?,?)',(json.dumps(before),json.dumps({'before':before,'after':after,'changes':changes}),upload['id'],db.now())).lastrowid
        meta['version_id']=version;c.execute('UPDATE uploads SET metadata=? WHERE id=?',(json.dumps(meta),upload['id']))
    db.set_meta('profile',after);db.set_meta('active_cv_version',version);upload['metadata']=meta;return upload

def undo(version_id):
    with db.connect() as c:r=c.execute('SELECT * FROM profile_versions WHERE id=?',(version_id,)).fetchone()
    if not r or r['undone']:raise ValueError('This import has already been undone or is unavailable')
    delta=json.loads(r['changes']);p=db.get_meta('profile');conflicts=[]
    for key in delta['changes']:
        if p.get(key)==delta['after'].get(key):
            if key in delta['before']:p[key]=delta['before'][key]
            else:p.pop(key,None)
            if key in delta['before'].get('provenance',{}):p.setdefault('provenance',{})[key]=delta['before']['provenance'][key]
            else:p.get('provenance',{}).pop(key,None)
        else:conflicts.append(key)
    if conflicts:raise ValueError('Newer edits preserved. Review these fields before undoing: '+', '.join(conflicts))
    db.set_meta('profile',p)
    with db.connect() as c:c.execute('UPDATE profile_versions SET undone=1 WHERE id=?',(version_id,))
    return p
