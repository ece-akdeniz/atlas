"""Evidence-bearing application checklists, independent of applicant documents."""
import re,hashlib
VERSION='checklist-2.0'
def extract(text,url='',section='Application instructions'):
    items=[]
    sentences=[]
    for original in re.split(r'(?<=[.!?])\s+|\n+',str(text or '')):
        # Commas/semicolons separate document groups; conjunctions only split when
        # followed by a different named document (never bachelor's and master's).
        parts=re.split(r';|,|\b(?:but|however)\b|\band\s+(?=(?:(?:an?|your|the|optional|required)\s+)*(?:CV\b|cover\s+letter|portfolio|GitHub|enrol|recommendation|references))',original,flags=re.I)
        inherited=bool(re.search(r'please|send|submit|attach|include|upload|provide',parts[0],re.I))
        global_required=bool(re.search(r'\b(?:are required|must be (?:submitted|provided))\b',original,re.I)) and not re.search(r'optional|not required|do not',original,re.I)
        for part in parts:
            if part.strip():sentences.append((part.strip(),original.strip(),inherited or global_required))
    for sentence,original,inherited in sentences:
        if not sentence.strip():continue
        status='optional' if re.search(r'optional|if you wish|welcome to|optionally|freiwillig',sentence,re.I) else 'conditional' if re.search(r'if applicable|where applicable|if available|falls|sofern',sentence,re.I) else 'required' if re.search(r'please|send|submit|attach|required|include|upload|provide|application.{0,15}with|bewerb|einreichen|schicken',sentence,re.I) else 'required' if inherited else 'unclear'
        if re.search(r'(?:not required|do not (?:need|require)|brauchen wir nicht|nicht erforderlich)',sentence,re.I):continue
        candidates=[]
        for pattern,label,kind in [(r'\bcv\b|curriculum vitae|r[eé]sum[eé]|lebenslauf','CV / résumé','document'),(r'cover\s+letter|motivation\s+letter|motivational\s+letter|anschreiben|motivationsschreiben','Cover / motivation letter','document'),(r'enrol[l]?ment certificate|immatrikulationsbescheinigung','Enrollment certificate','document'),(r'portfolio','Portfolio','document'),(r'github','GitHub link','answer'),(r'publication(?:s| list)?','Publications','document'),(r'(?:description|summary|overview)s? of (?:your |the )?(?:relevant |previous |past )?projects|project descriptions?|projektbeschreibungen','Descriptions of relevant projects','document'),(r'recommendation letters?|reference letters?','Recommendation letters','document'),(r'\breferences\b','References','answer'),(r'availability|verf[uü]gbarkeit','Availability','answer'),(r'(?:preferred |desired |earliest )?start date|eintrittsdatum','Preferred start date','answer')]:
            if re.search(pattern,sentence,re.I):candidates.append((label,kind))
        if re.search('transcript|notenspiegel|notenübersicht',sentence,re.I):
            degrees=[]
            if re.search(r'bachelor|undergraduate',sentence,re.I):degrees.append('Bachelor’s transcript')
            if re.search(r'master|\bgraduate\b',sentence,re.I):degrees.append('Master’s transcript')
            candidates.extend((x,'document') for x in (degrees or ['Academic transcript']))
        for label,kind in candidates:
            evidence={'url':url,'section':section,'excerpt':sentence.strip()[:1200],'version':VERSION}
            constraints={}
            for key,pattern in [('format',r'\bPDF|\bDOCX?\b'),('size_limit',r'\b\d+\s*(?:MB|KB)\b'),('language',r'\b(?:in )?(English|German|French)\b')]:
                m=re.search(pattern,sentence,re.I)
                if m:constraints[key]=m[0]
            item={'id':hashlib.sha256(label.encode()).hexdigest()[:16],'label':label,'requirement':status,'kind':kind,'constraints':constraints,'instructions':sentence.strip(),'evidence':evidence}
            old=next((x for x in items if x['label']==label),None)
            if not old:items.append(item)
            elif old['requirement']=='unclear' and status!='unclear':items[items.index(old)]=item
    return items

def for_record(record):
    # Full application instructions outrank legacy coarse materials. No standard default checklist.
    source=record.get('application_method') or ''
    items=extract(source,record.get('url',''))
    if not items and record.get('materials'):
        items=extract('\n'.join(record['materials']),record.get('url',''),'Previously extracted materials; requirement level not confirmed')
    for form in record.get('application_forms',[]):
        if isinstance(form,dict) and str(form.get('url','')).startswith('https://'):
            items.append({'id':hashlib.sha256(form['url'].encode()).hexdigest()[:16],'label':form.get('title','Application form'),'requirement':form.get('requirement','unclear'),'kind':'source_form','url':form['url'],'constraints':{},'instructions':'Publisher-supplied form','evidence':{'url':form['url'],'section':'Linked application form','version':VERSION}})
    return items
