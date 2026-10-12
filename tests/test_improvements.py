import unittest,tempfile,json
from pathlib import Path
from unittest.mock import patch
from portal import db
from portal.seed import bootstrap,RECORDS
from portal.collector import rpg,collect_source
from portal.extraction import enrich,recognize_skills,pdf_details
from portal.model import ranked,recommendations,DEFAULT_PROFILE,status
from portal.adapters import cvg,tumai,sirop

class ImprovementTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=db.DB_PATH;db.DB_PATH=Path(self.tmp.name)/'isolated.db';bootstrap()
 def tearDown(self):db.DB_PATH=self.old;self.tmp.cleanup()
 def test_token_boundaries_and_ros_aliases(self):
  self.assertEqual(recognize_skills('across gross Rosetta cPython'),[])
  self.assertEqual(recognize_skills('ROS2 / ROS 2 / ROS-2'),['ROS 2'])
  self.assertEqual(recognize_skills('ROS and ROS2 with C++.'),['C++','ROS 2','ROS'])
 def test_rpg_all_projects_requirements_contacts_evidence(self):
  html=''.join(f'<h3>Odometry {i} - Available</h3><p><b>Description:</b> Learn trajectories across environments with inertial sensors.</p><p>Requirements:\n- Python required.\n- PyTorch is a plus.</p><p><b>Goal:</b> Evaluate motion estimates from multiple IMUs.</p><p><b>Contact Details:</b> Send CV to person@example.edu.</p>' for i in range(25))
  rs=rpg(html,'https://example.edu/projects');self.assertEqual(len(rs),25)
  r=rs[0];self.assertNotIn('ROS',r['skills']);self.assertEqual(r['required'],['Python required.']);self.assertIn('PyTorch is a plus.',r['preferred']);self.assertEqual(r['contacts'],['person@example.edu']);self.assertEqual(r['field_states']['required']['state'],'extracted');self.assertIn('Requirements',r['field_evidence']['preferred']['section'])
 def test_incomplete_is_not_absent(self):
  r=enrich(dict(RECORDS[0][1]),'<p>Unstructured text</p>',complete=False)
  self.assertEqual(r['field_states']['required']['state'],'incomplete')
  complete=enrich(dict(RECORDS[0][1]),'<p>No labeled prerequisites provided.</p>')
  self.assertEqual(complete['field_states']['research_question']['state'],'absent')
 def test_cross_publisher_identity_keeps_notes_and_conflicts(self):
  r=dict(RECORDS[0][1],publisher='lab',publisher_identifiers={'sirop':'same-id'},required=['Python'])
  first=db.upsert(r,'lab')
  with db.connect() as c:c.execute('INSERT INTO workflow(opportunity_id,stage,notes,dismissed,updated,bookmarked) VALUES(?,?,?,?,?,?)',(first,'Applied','private note',0,db.now(),1))
  other=dict(r,publisher='platform',organization='Different publisher name',publisher_id='different',required=['C++'])
  second=db.upsert(other,'platform');self.assertEqual(first,second)
  stored=next(x for x in db.rows() if x['id']==first);self.assertEqual(stored['notes'],'private note');self.assertEqual(stored['field_states']['required']['state'],'conflict');self.assertTrue(stored['bookmarked'])
 def test_idempotent_upsert_preserves_change_count(self):
  r=rpg('<h3>Vision - Available</h3><p>Description:\nInvestigate visual motion across novel scenes and camera systems.\nRequirements:\nPython.</p>','https://example.edu/projects')[0]
  db.upsert(r,'test');db.upsert(r,'test')
  with db.connect() as c:n=c.execute('SELECT count(*) FROM changes').fetchone()[0]
  db.upsert(r,'test')
  with db.connect() as c:self.assertEqual(c.execute('SELECT count(*) FROM changes').fetchone()[0],n)
 def test_recommendation_determinism_and_gate(self):
  p=dict(DEFAULT_PROFILE,skills=['Python'],interests=['robotics','machine learning','computer vision'])
  r=dict(db.rows()[0],record_kind='opening',extraction_complete=True,skills=['Python'],tags=p['interests'],city='Stuttgart',hours=20,workload='Part-time',status='open',verified='2026-10-12',id='b')
  route=dict(r,id='route',record_kind='academic_route');old=dict(r,id='past',category='events',event_end='2026-10-01');conflict=dict(r,id='conflict',local_enrollment='ETH Zurich');p['university']='University of Stuttgart'
  data=[r,route,old,conflict];a=recommendations(ranked(data,p,'2026-10-12'));b=recommendations(ranked(list(reversed(data)),p,'2026-10-12'));self.assertEqual([x['id'] for x in a],['b']);self.assertEqual(a,b)
 def test_profile_and_bookmark_api_persist(self):
  from portal.app import create_app
  c=create_app(test=True).test_client();s=c.get('/api/state').get_json();headers={'X-CSRF-Token':s['csrf']};id=s['opportunities'][0]['id']
  for payload in [{'bookmarked':True},{'stage':'Preparing'},{'stage':'Applied','notes':'keep this'}]:self.assertEqual(c.post('/api/workflow/'+id,json=payload,headers=headers).status_code,200)
  r=next(x for x in c.get('/api/state').get_json()['opportunities'] if x['id']==id);self.assertTrue(r['bookmarked']);self.assertEqual(r['notes'],'keep this')
  self.assertEqual(c.post('/api/workflow/'+id,json={'stage':None},headers=headers).status_code,200)
  removed=next(x for x in c.get('/api/state').get_json()['opportunities'] if x['id']==id)
  self.assertIsNone(removed['stage']);self.assertTrue(removed['bookmarked']);self.assertEqual(removed['notes'],'keep this')
  self.assertEqual(c.post('/api/profile',json={'max_hours':18,'languages':{'German':'B1'}},headers=headers).status_code,200)
  self.assertEqual(c.get('/api/state').get_json()['profile']['max_hours'],18)
  self.assertEqual(c.post('/api/profile',json={'availability_start':'nonsense'},headers=headers).status_code,400)
  self.assertEqual(c.get('/api/state').get_json()['profile']['max_hours'],18)
 def test_pdf_linewrap_requirements_and_contact_boundary(self):
  text='Voraussetzungen:\n• Experience with Python and\nLinux.\n• PyTorch is a plus.\nKontakt:\nDr. Example person@example.edu\nStudent(s) Name(s):\nProject Report Abstract:\nInternal template text'
  r=enrich(dict(RECORDS[0][1]),pdf_details(text),complete=False)
  self.assertIn('Experience with Python and Linux.',r['required']);self.assertIn('PyTorch is a plus.',r['preferred'])
  self.assertNotIn('Internal template',r['application_method']);self.assertEqual(r['contacts'],['person@example.edu'])
 def test_historical_event_not_upcoming(self):
  r=dict(db.rows()[0],category='events',event_start='2026-04-17',event_end='2026-04-19');self.assertIn('Expired',status(r,'2026-10-12'))
 def test_tum_type_columns_not_blanket_master_thesis(self):
  html='<table class="inline"><tr><td>Dense SLAM</td><td>Advisor</td><td>✅</td><td>✅</td><td>✅</td><td>❌</td><td>Python, C++</td></tr></table>'
  rs,_=cvg(html,{'url':'https://example.edu/projects'});self.assertNotIn('Master’s thesis',rs[0]['project_types'])
 def test_public_feed_no_double_items_or_false_deadline(self):
  item={'title':'Robot mapping','url':'https://sirop.org/app/uuid','status':'Published','organization':'Lab','latestEndDate':'2027-01-01','detailDescription':[{'title':'Description','value':'Robot mapping with Python.'}], 'labels':[]}
  payload={'opportunities':[item],'items':[item]}
  with patch('portal.adapters.document',return_value=json.dumps(payload).encode()):rs,_=sirop('<div data-feed="https://feeds.sirop.org/feed.json"></div>',{'url':'https://ethz.ch/lab'})
  self.assertEqual(len(rs),1);self.assertNotIn('deadline',rs[0]);self.assertEqual(rs[0]['project_end'],'2027-01-01')
 def test_failure_api_never_fresh_verified_label(self):
  from portal.app import create_app
  with db.connect() as c:c.execute("UPDATE sources SET error='HTTP 503' WHERE id='bmw'")
  c=create_app(test=True).test_client();r=next(x for x in c.get('/api/state').get_json()['opportunities'] if any(e['source_id']=='bmw' for e in x['sources']))
  self.assertIn('Unverified',r['states']);self.assertTrue(r['verification_label'].startswith('Last verified'))
if __name__=='__main__':unittest.main()
