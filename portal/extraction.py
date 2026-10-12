"""Deterministic extraction primitives. Source text is never executable instruction."""
import re
from bs4 import BeautifulSoup

VERSION='extract-2.2.0'
SKILLS={
 'Python':r'python','C++':r'c\+\+','PyTorch':r'pytorch','ROS 2':r'ros[ -]?2',
 'ROS':r'ros(?![ -]?2\b)','MATLAB':r'matlab','Linux':r'linux','OpenCV':r'opencv',
 'TensorFlow':r'tensorflow','Git':r'git','Docker':r'docker','Gazebo':r'gazebo',
 'LiDAR':r'lidar','NumPy':r'numpy','SQL':r'sql','Eigen':r'eigen', 'CUDA':r'cuda',
}
def recognize_skills(text):
    return [name for name,pattern in SKILLS.items() if re.search(r'(?<![\w])(?:'+pattern+r')(?![\w])',text,re.I)]
def normalize_skill(value):
    value=value.casefold().strip()
    return 'ros 2' if re.fullmatch(r'ros[ -]?2',value) else value

def clean(value): return ' '.join(str(value or '').replace('\u200b','').split())
LABELS={'beschreibung':'description','ziel':'research_question','vorrausetzungen':'required','was du mitbringst':'required','was du bei uns tust (schwerpunkte nach absprache)':'activities','was du erwarten kannst':'benefits','objectives':'activities','project description':'description','voraussetzungen':'required','anforderungen':'required','ihr profil':'required','kontakt':'application_method','bewerbung':'application_method','aufgaben':'activities','ihre aufgaben':'activities','description':'description','goal':'research_question','goals':'research_question','research question':'research_question','was sie erwarten können':'benefits','relevante literatur':'references','ihre voraussetzungen':'required','requirements':'required','applicant requirements':'required','prerequisites':'required','required qualifications':'required','preferred qualifications':'preferred','your qualifications':'required','your contribution':'activities','tasks':'activities','activities':'activities','work packages':'activities','contact details':'application_method','contact':'application_method','student(s) name(s)':'internal','project report abstract':'internal','thesis type':'type','application':'application_method'}
def sections(html):
    soup=BeautifulSoup(html,'html.parser')
    for n in soup(['script','style','nav','footer']):n.decompose()
    raw=soup.get_text('\n',strip=True)
    pattern=r'(?im)(?:^|\n)\s*('+ '|'.join(sorted(map(re.escape,LABELS),key=len,reverse=True))+r')\s*:?\s*(?:\n|:)'
    matches=list(re.finditer(pattern,raw)); result={}
    for i,m in enumerate(matches):
        key=LABELS[m.group(1).lower()];value=raw[m.end():matches[i+1].start() if i+1<len(matches) else len(raw)].strip()
        result[key]=(result.get(key,'')+'\n'+value).strip()
    return result,raw

def sentences(text):
    return [clean(x).lstrip('-•● ').strip() for x in re.split(r'\n\s*[-•●]\s*|(?<=[.!?])\s+(?=[A-Z])|\n+',text) if clean(x).strip('-• ') ]

def enrich(record,html,section=None,complete=True):
    parts,raw=sections(html); url=record['url']; evidence={}; states={}
    for field in ['research_question','activities','required','preferred','application_method','contacts','materials','skills']:
        states[field]={'state':'absent' if complete else 'incomplete'}
    def put(field,value,quote,heading=None):
        if not value:return
        record[field]=value;states[field]={'state':'extracted'}
        evidence[field]={'url':url,'section':heading or section or record['title'],'excerpt':clean(quote)[:1000],'version':VERSION}
    for k in ['research_question','application_method']: put(k,clean(parts.get(k)),parts.get(k,''),k.replace('_',' '))
    for k in ['activities','required','preferred']:
        vals=sentences(parts.get(k,''));put(k,vals,parts.get(k,''),k)
    if parts.get('required'):
        required=[];preferred=list(record.get('preferred',[]))
        for value in record['required']:
            (preferred if re.search(r'\b(plus|advantage|preferred|desirable|beneficial|optional|vorteil|idealerweise)\b',value,re.I) else required).append(value)
        record['required']=required
        put('preferred',preferred,' '.join(preferred),'Requirements · preferred')
        if not required:states['required']={'state':'absent'}
    emails=list(dict.fromkeys(re.findall(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',raw)))
    put('contacts',emails,parts.get('application_method') or ' '.join(emails),'Contact details')
    if emails:record['supervisor']=clean(parts.get('application_method') or ', '.join(emails))
    skills=recognize_skills(raw);put('skills',skills,', '.join(skills),'Technical mentions')
    record['required_skills']=recognize_skills(' '.join(record.get('required',[])))
    app=record.get('application_method','')
    materials=[label for pattern,label in [(r'\bcv\b|curriculum vitae','CV'),(r'transcript','Academic transcripts'),(r'motivation|cover letter','Motivation / cover letter'),(r'start date','Desired start date')] if re.search(pattern,app,re.I)]
    put('materials',materials,app,'Application instructions')
    desc=clean(parts.get('research_question') or parts.get('description'))
    if desc:record['summary']=sentences(desc)[0][:360]; evidence['summary']={'url':url,'section':section or record['title'],'excerpt':record['summary'],'version':VERSION};states['summary']={'state':'extracted'}
    if not record.get('activities') and parts.get('description'):
        actions=[x for x in sentences(parts['description']) if re.search(r'\b(investigat|develop|evaluat|implement|explor|design|compar|analy[sz])\w*',x,re.I)]
        put('activities',actions[:5],' '.join(actions[:5]),'Description')
    record.update(field_states=states,field_evidence=evidence,extraction_version=VERSION,extraction_complete=complete,record_kind=record.get('record_kind','event' if record['category']=='events' else 'opening'))
    for key in ['required','preferred','activities','skills','materials','contacts']:record.setdefault(key,[])
    return record

def pdf_details(content):
    """Join PDF line wraps while retaining heading/list boundaries; no OCR inference."""
    import html
    content=content.replace('','•').replace('●','•')
    lines=[];buffer=[]
    for line in content.splitlines():
        line=line.strip()
        label=line.rstrip(':').casefold()
        boundary=label in LABELS or line.startswith(('•','- ')) or not line
        if boundary and buffer:lines.append(' '.join(buffer));buffer=[]
        if label in LABELS:lines.append(line.rstrip(':')+':')
        elif line:buffer.append(line)
    if buffer:lines.append(' '.join(buffer))
    return ''.join('<p>'+html.escape(line)+'</p>' for line in lines)
