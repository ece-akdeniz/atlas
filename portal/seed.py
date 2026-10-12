"""Public source facts reviewed 2026-10-12. No personal profile in source control."""
import json
from portal import db
from portal.model import DEFAULT_PROFILE
VERIFIED='2026-10-12'
SOURCES=[
('bmw','BMW Group · student roles','jobs','https://www.bmwgroup.jobs/de/de/jobfinder/job-description.196070.html','jsonld',True),
('bosch','Bosch · computer vision','jobs','https://jobs.bosch.de/de/job/Praktikum-im-Computer-Vision-Stuttgart-Mitte?id=dadc07dc-69c4-4750-ba7b-59e087068551','reviewed',True),
('rpg','UZH · Robotics and Perception Group','research','https://rpg.ifi.uzh.ch/student_projects.php','rpg',True),
('rsl','ETH · Robotic Systems Lab','research','https://rsl.ethz.ch/education-students/student-projects0.html','discovery',True),
('eth-mobility','ETH · project mobility','research','https://ethz.ch/en/studies/non-degree-courses/project.html','reviewed',True),
('energy-now','ETH · Energy Now!','events','https://esc.ethz.ch/industry/entrepreneurship/energy-now.html','reviewed',True),
('hackatum','hackaTUM · official FAQ','events','https://hack.tum.de/faq/','hackatum',True),
('hackzurich','HackZurich · organizer','events','https://hackzurich.com/','reviewed',True),
('airbus','Airbus · careers','jobs','https://www.airbus.com/en/careers','pending',False),
('mercedes','Mercedes-Benz · careers','jobs','https://jobs.mercedes-benz.com/','pending',False),
('porsche','Porsche · careers','jobs','https://jobs.porsche.com/','pending',False),
('anybotics','ANYbotics · robotics careers','jobs','https://www.anybotics.com/careers/','pending',False),
('stuttgart-ilr','Stuttgart · ILR university–industry routes','research','https://www.ilr.uni-stuttgart.de/','pending',False),
('stuttgart-ipr','Stuttgart · IPR robotics','research','https://www.ipr.uni-stuttgart.de/','pending',False),
('tum','TUM · robotics & AI','research','https://www.mirmi.tum.de/','pending',False),
('dlr','DLR · student research','research','https://www.dlr.de/en/careers','pending',False),
('fraunhofer','Fraunhofer · jobs & theses','research','https://jobs.fraunhofer.de/','pending',False),
('mpi-is','Max Planck · Intelligent Systems','research','https://is.mpg.de/jobs','pending',False),
('cyber-valley','Cyber Valley · ecosystem announcements','events','https://cyber-valley.de/en/events','pending',False),
('start-hack','START Hack · organizer','events','https://www.startglobal.org/start-hack','pending',False),
('stuttgart-events','Stuttgart · university events','events','https://www.uni-stuttgart.de/en/university/news/event/','pending',False),
('daad','DAAD · scholarships & mobility','events','https://www.daad.de/en/studying-in-germany/scholarships/','pending',False),
('workingstudentjobs','Working Student Jobs · secondary discovery','jobs','https://www.workingstudentjobs.de/de','pending',False),
('hackathonhub','Hackathon Hub · secondary discovery','events','https://hackathonhub.eu/events','pending',False),
]
def record(title,organization,category,url,**kw):
    return {'title':title,'organization':organization,'category':category,'url':url,'summary':kw.pop('summary'),'status':'open','type':kw.pop('type'),'tags':[], 'required':[], 'preferred':[], 'skills':[], 'activities':[], 'partners':[], 'languages':{}, 'evidence_method':'Human-reviewed official source; concise factual paraphrase', 'extraction_version':'curated-2026-10-12.1',**kw}
RECORDS=[
('bmw',record('Intern Computer Vision and Sensor Fusion','BMW Group','jobs',SOURCES[0][3],type='Internship',city='Munich',country='Germany',department='Driver assistance',publisher_id='196070',summary='Build multi-sensor 3D reconstructions and digital twins for driving simulation.',tags=['computer vision','sensor fusion','autonomous systems','machine learning'],skills=['Python','PyTorch','Open3D'],activities=['Develop and validate reconstruction and novel-view pipelines.'],required=['Master’s or PhD studies in a relevant quantitative field.','Practical 3D reconstruction and deep learning experience.'],preferred=['Camera/LiDAR fusion experience; German.'],languages={'English':'Good'},workload='Full-time',duration='4 months',start_date='2026-11-02',published='2026-10-05',funding='Compensation offered; amount not stated. Student apartments subject to availability.',enrollment_required=True,questions=['Full-time internship may not fit concurrent study commitments.'])),
('bosch',record('Praktikum im Computer Vision','Bosch Secure Authentication GmbH','jobs',SOURCES[1][3],type='Internship',city='Stuttgart',country='Germany',publisher_id='REF285617L',summary='Develop product-facing computer vision solutions, run feasibility studies and evaluate new methods.',tags=['computer vision','machine learning'],skills=['Python'],required=['Current relevant university enrollment.','Strong Python; very good German and English.'],preferred=['C++'],languages={'German':'Very good; CEFR level not stated','English':'Very good; CEFR level not stated'},hours=40,workload='Full-time',duration='6 months',arrangement='On-site',start_flexibility='By agreement',published='2026-05-08',enrollment_required=True,materials=['CV','Transcript','Enrollment certificate','Examination regulations','Work/residence permission if applicable'],application_method='Online employer portal only',questions=['Your German B1 may fall short of “very good”; confirm with the employer.'],translation='English factual paraphrase of German posting.')),
('eth-mobility',record('Project mobility · research project or thesis','ETH Zurich','research','https://ethz.ch/content/main/en/studium/non-degree-angebote/project.html',type='Visiting research / thesis route',city='Zurich',country='Switzerland',summary='External bachelor’s and master’s students may undertake a supervised, degree-recognized project at ETH.',tags=[],external_students='yes',workload='Full-time',arrangement='On-site',duration='91–365 days',enrollment_required=True,required=['Enrollment at a university entitled to award doctorates.','ETH professor as supervisor; home-university credit recognition.','English B2 or higher; sufficient financial resources.'],languages={'English':'B2'},funding='No tuition fees. No Student Exchange Office grants or scholarships.',funding_confirmed=False,application_method='Project mobility application after securing an ETH supervisor',academic_credit='Home-university recognition required',research_question=None,questions=['Apply at least two months before starting; three months recommended when a visa is required.','This route is not an employment arrangement.','This is a mobility route, not an advertised individual thesis position.'])),
('hackatum',record('hackaTUM 2026','Technical University of Munich','events',SOURCES[6][3],type='Hackathon',publisher_id='hackatum-2026',city='Munich / Garching',country='Germany',summary='An on-site hackathon with partner challenges, individual applications and teams of two to four.',tags=[],event_start='2026-11-27',event_end='2026-11-29',open_to_all=True,external_students='yes',languages={'English':'Event language; level not stated'},fees='No participation fee',funding='Food and drinks provided. Venue sleeping rooms; bring a sleeping bag. No hotel or travel reimbursement.',funding_confirmed=True,team='Apply individually; teams of 2–4',application_method='Organizer application form; applications start in October',arrangement='On-site',questions=['FAQ still contains a 2025 acceptance-notification date. Confirm the 2026 application deadline.','Technical challenges are announced at the opening; robotics-specific relevance is not yet established.'])),
('energy-now',record('Energy Now! 5.0 · impact accelerator','ETH Zurich · Energy Science Center','events',SOURCES[5][3],type='Program',city='Zurich',country='Switzerland',summary='Student–industry teams develop solutions to energy challenges, including AI and control applications.',tags=['AI','machine learning'],status='closed',local_enrollment='ETH Zurich',enrollment_required=True,questions=['Official page states challenge registration is closed.','Monitor future editions; external-student eligibility is not established.'])),
]
def bootstrap():
    db.init()
    if db.get_meta('initialized'):
        from portal.registry import upgrade
        upgrade()
        return
    with db.connect() as c:
        for sid,name,cat,url,adapter,enabled in SOURCES:
            d={'name':name,'category':cat,'url':url,'adapter':adapter,'enabled':enabled,'interval_hours':24,'terms_review':'Public factual metadata only; robots checked at every run. No login or full-text reproduction.','coverage':'Bounded to this page; linked candidates require review.','status':'Ready for first check' if enabled else 'Pending setup'}
            c.execute('INSERT OR IGNORE INTO sources(id,data) VALUES(?,?)',(sid,json.dumps(d)))
    for sid,r in RECORDS: db.upsert(r,sid,VERIFIED)
    db.set_meta('profile',DEFAULT_PROFILE)
    db.set_meta('saved_searches',[])
    db.set_meta('initialized',True)
    from portal.registry import upgrade
    upgrade()
