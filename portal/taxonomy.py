"""Versioned controlled types, separate from source-confirmed workload."""
import re
VERSION='types-1.2'
TYPE_OPTIONS={
 'jobs':['Working student','Internship','Research assistant','Graduate role','Professional role','Unspecified'],
 'research':['Master’s thesis','Bachelor’s thesis','Doctoral position','Semester project','Guided research','Interdisciplinary project','Student project','Thesis (degree unspecified)','Research internship','Internship','Research assistant','Visiting research','Academic collaboration','Academic route','Lab lead','Unspecified'],
 'events':['Hackathon','Competition','Summer school','Winter school','Conference','Workshop','Fellowship','Scholarship','Research program','Networking event','Event','Unspecified']}
PATTERNS=[
 ('Working student',r'working[ -]student|werkstudent'),('Research internship',r'research internship|forschungspraktik'),
 ('Internship',r'\binternship\b|\bintern\b|praktikum|praktikant'),('Research assistant',r'research assistant|student assistant|wissenschaftliche hilf|hiwi'),
 ('Master’s thesis',r'master(?:[’\']?s)?[ -]*(?:thesis|theses|arbeit)|masterarbeit|msc thesis'),
 ('Bachelor’s thesis',r'bachelor(?:[’\']?s)?[ -]*(?:thesis|theses|arbeit)|bachelorarbeit|bsc thesis'),
 ('Doctoral position',r'ph\.?d|doctoral|doktorand'),('Semester project',r'semester[ -]project|semesterarbeit'),
 ('Guided research',r'guided research'),('Interdisciplinary project',r'interdisciplinary project'),
 ('Student project',r'student[ -]project|studienarbeit'),('Visiting research',r'visiting (?:student|research)|research visit'),
 ('Academic collaboration',r'academic collaboration|joint.degree|double.degree'),('Graduate role',r'graduate role|graduate program|trainee'),
 ('Hackathon',r'hackathon|makeathon'),('Competition',r'competition|challenge'),('Summer school',r'summer school'),('Winter school',r'winter school'),
 ('Conference',r'conference|konferenz'),('Workshop',r'workshop'),('Fellowship',r'fellowship'),('Scholarship',r'scholarship|travel grant'),
 ('Research program',r'research program|research programme'),('Networking event',r'networking'),('Event',r'^event$'),('Professional role',r'^(?:full.time role|part.time role|role|job)$')]
def normalize(record):
 r=dict(record)
 original=r.get('original_type') if r.get('taxonomy_version') else r.get('type')
 original=original or ''
 r['original_type']=original
 labels=[label for label,pattern in PATTERNS if re.search(pattern,original,re.I)]
 if 'Research internship' in labels:labels.remove('Internship') if 'Internship' in labels else None
 if re.search(r'\bthesis\b|\btheses\b|abschlussarbeit',original,re.I) and not any(x in labels for x in ['Master’s thesis','Bachelor’s thesis']):labels.append('Thesis (degree unspecified)')
 if not labels and r.get('record_kind') in ['academic_route','lab_lead']:labels=[{'academic_route':'Academic route','lab_lead':'Lab lead'}[r['record_kind']]]
 allowed=TYPE_OPTIONS.get(r.get('category'),[label for label,_ in PATTERNS]+['Thesis (degree unspecified)','Academic route','Lab lead'])
 labels=[x for x in labels if x in allowed]
 r['types']=list(dict.fromkeys(labels)) or ['Unspecified']
 r['type']=' / '.join(r['types'])
 raw=r.get('employment_type_raw') or r.get('workload') or ''
 if isinstance(raw,list):raw=' / '.join(str(x) for x in raw)
 arrangements=[]
 for label,pattern in [('Full-time',r'full[ _-]?time|vollzeit|100\s*%'),('Part-time',r'part[ _-]?time|teilzeit')]:
  if re.search(pattern,str(raw),re.I):arrangements.append(label)
 r['employment_arrangements']=arrangements or ['Not stated']
 if arrangements and not r.get('workload'):r['workload']=' / '.join(arrangements)+'; weekly hours not stated'
 r['taxonomy_version']=VERSION
 return r

def matches(record,opportunity_type=None,workload=None):
 r=normalize(record)
 if opportunity_type:
  canonical=normalize({'type':opportunity_type})['types']
  if not set(canonical)&set(r['types']):return False
 return not workload or workload in r['employment_arrangements']
