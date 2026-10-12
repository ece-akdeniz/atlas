"""Versioned source expansion. Registry presence is never operational proof."""
import json
from portal import db
VERSION='sources-2.0'
SOURCES=[
 ('dlr-rm','DLR · Robotics & Mechatronics students','https://www.dlr.de/en/rm/jobs/students','dlr','research'),
 ('stuttgart-iff','Stuttgart IFF · projects & institute PDFs','https://www.iff.uni-stuttgart.de/lehre/studentische-arbeiten/offene-themen-fuer-studentische-arbeiten/','iff','research'),
 ('tum-cvg','TUM · Computer Vision & AI projects','https://cvg.cit.tum.de/teaching/open_projects','tum-cvg','research'),
 ('tum-srl','TUM · Smart Robotics Lab projects','https://srl.cit.tum.de/teaching/projects','tum-srl','research'),
 ('rsl','ETH · Robotic Systems Lab public SIROP feed','https://rsl.ethz.ch/education-students/student-projects0.html','eth-projects','research'),
 ('eth-movement','ETH · Movement Biomechanics public feed','https://movement.ethz.ch/student-projects.html','eth-projects','research'),
 ('tumai','TUM.ai · published events','https://www.tum-ai.com/events','tumai','events'),
 ('anybotics','ANYbotics · public Lever postings','https://api.lever.co/v0/postings/anybotics?mode=json&limit=100','lever','jobs'),
 ('ipa-students','Fraunhofer IPA · Stuttgart student research','https://jobs.fraunhofer.de/search/?q=&locationsearch=Stuttgart&optionsFacetsDD_customfield1=Studentische+Hilfskr%C3%A4fte&optionsFacetsDD_customfield4=IPA+-+Produktionstechnik+und+Automatisierung','fraunhofer','research'),
 ('cyber-niclas','Cyber Valley · nICLAS Forum 2026','https://www.cyber-valley.de/de/events/niclas-forum-2026','cyber','events'),
 ('robotum','roboTUM · organizer events','https://www.robotum.info/events','pending','events'),
 ('sirop','SIROP · protected general search','https://sirop.org/app','pending','research'),
]
def upgrade():
    if db.get_meta('registry_version')==VERSION:return
    with db.connect() as c:
        for id,name,url,adapter,category in SOURCES:
            old=c.execute('SELECT data FROM sources WHERE id=?',(id,)).fetchone();previous=json.loads(old['data']) if old else {}
            data={**previous,'name':name,'url':url,'adapter':adapter,'category':category,'enabled':adapter!='pending','interval_hours':previous.get('interval_hours',24),'operational':False,'status':'Pending first collection' if adapter!='pending' else 'Link only','coverage':'Bounded official index and detail extraction; operational only after validated records.'}
            if id=='robotum':data['coverage']='Client-rendered event list. Supported public feed or permitted rendered adapter still required; no backend keys reused.'
            if id=='sirop':data['coverage']='General search access restricted. Selected ETH public lab feeds are collected separately; this is not full SIROP coverage.'
            c.execute('INSERT INTO sources(id,data) VALUES(?,?) ON CONFLICT(id) DO UPDATE SET data=excluded.data,next_due=NULL',(id,json.dumps(data)))
        # RPG extraction version changed: immediately eligible for reprocessing.
        c.execute("UPDATE sources SET next_due=NULL WHERE id='rpg'")
        for row in c.execute('SELECT id,data FROM opportunities').fetchall():
            r=json.loads(row['data'])
            if 'record_kind' not in r:
                r['record_kind']='academic_route' if r.get('publisher_id')=='eth-project-mobility' or 'mobility' in r.get('title','').lower() else 'event' if r['category']=='events' else 'opening'
                r['extraction_complete']=False
                r['field_states']={k:{'state':'incomplete'} for k in ['required','preferred','activities','research_question','contacts','application_method']}
                c.execute('UPDATE opportunities SET data=? WHERE id=?',(json.dumps(r),row['id']))
    db.set_meta('registry_version',VERSION)
