import json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,Mock
from portal import db,studio,uploads,jobs,notifications
from portal.checklist import extract
from portal.taxonomy import normalize,matches
from portal.collector import collect_source
class CompletionTests(unittest.TestCase):
 def setUp(self):
  self.old=db.DB_PATH;self.tmp=tempfile.TemporaryDirectory();db.DB_PATH=Path(self.tmp.name)/'test.sqlite3'
  from portal.app import create_app
  self.client=create_app(test=True).test_client();self.headers={'X-CSRF-Token':self.client.get('/api/state').json['csrf']}
 def tearDown(self):db.DB_PATH=self.old;self.tmp.cleanup()
 def record(self,identity='new'):
  return {'title':'Robot perception','organization':'Lab','url':'https://example.org/'+identity,'publisher_id':identity,'summary':'Develop robot vision models','category':'research','type':'Semester Project / Internship / Master Thesis','record_kind':'opening','status':'open','extraction_complete':True,'tags':['robotics','computer vision'],'skills':['Python','C++'],'city':'Stuttgart','hours':15}
 def test_types_aliases_multitype_workload_and_unknown(self):
  r=normalize(self.record());self.assertEqual(set(r['types']),{'Semester project','Internship','Master’s thesis'})
  self.assertTrue(all(matches(r,t) for t in ['Master Thesis','Master’s thesis','Semester project','Internship']))
  self.assertEqual(normalize(r),r);self.assertEqual(len([x for x in [r] if matches(x,'Master Thesis')]),1)
  self.assertNotIn('Master’s thesis',normalize({'type':'student project / thesis'})['types'])
  self.assertEqual(normalize({'type':'Internship','workload':'Full-time'})['employment_arrangements'],['Full-time'])
  self.assertEqual(normalize({'type':'Role','title':'Full-time engineer'})['employment_arrangements'],['Not stated'])
 def test_checklist_clause_modifiers(self):
  c={x['label']:x for x in extract('Please send a CV and transcripts, but a cover letter is not required. Please upload your CV and optional portfolio.')}
  self.assertEqual(c['CV / résumé']['requirement'],'required');self.assertEqual(c['Academic transcript']['requirement'],'required');self.assertNotIn('Cover / motivation letter',c);self.assertEqual(c['Portfolio']['requirement'],'optional')
  c=extract('Please upload a CV in English, PDF under 2 MB; optionally include a portfolio.')
  self.assertEqual(c[0]['constraints']['language'],'in English')
 def test_new_incomplete_alert_can_qualify_later(self):
  notifications.configure({'destination':'test@example.com','enabled':True});identity=db.upsert(self.record(),'test')
  with patch('portal.notifications.qualifies',return_value=False):self.assertEqual(notifications.discover(),0)
  with patch('portal.notifications.qualifies',side_effect=lambda r,p,c:r['id']==identity):
   self.assertEqual(notifications.discover(),1);self.assertEqual(notifications.discover(),0)
 def test_queued_closed_alert_cancelled_before_send(self):
  notifications.configure({'destination':'test@example.com','enabled':True});r=self.record();identity=db.upsert(r,'test')
  with patch('portal.notifications.qualifies',side_effect=lambda r,p,c:r['id']==identity):notifications.discover()
  r['status']='closed';db.upsert(r,'test')
  with patch.dict(os.environ,{'RESEND_API_KEY':'test','ATLAS_EMAIL_FROM':'atlas@example.com','PORTAL_ORIGIN':'https://example.com'}),patch('portal.notifications.requests.post') as post:
   notifications.deliver();post.assert_not_called()
  with db.connect() as c:self.assertEqual(c.execute('SELECT status FROM notification_events WHERE opportunity_id=?',(identity,)).fetchone()[0],'cancelled')
 def test_free_technical_event_without_job_skills(self):
  p={'locations':['Munich'],'interests':['robotics','computer vision'],'skills':[]};r={**self.record(),'category':'events','record_kind':'event','city':'Munich','skills':[],'event_start':'2099-10-20','fees':'No participation fee','open_to_all':True,'states':[],'match':{'conflicts':[],'future':False}}
  self.assertTrue(notifications.qualifies(r,p,notifications.DEFAULT));r['open_to_all']=False;self.assertFalse(notifications.qualifies(r,p,notifications.DEFAULT))
 def test_complete_empty_feed_marks_absent_without_fresh_verification(self):
  r=self.record();identity=db.upsert(r,'empty','2020-01-01T00:00:00+00:00');s={'id':'empty','name':'Lab','url':'https://example.org/feed','adapter':'lever-feed'}
  with patch('portal.collector.robots'),patch('portal.collector.fetch',return_value=(200,{},b'[]')):self.assertEqual(collect_source(s)[0],0)
  old=next(r for r in db.rows() if r['id']==identity);self.assertEqual(old['verified'],'2020-01-01T00:00:00+00:00');self.assertIn('complete collection',old['verification_warning'])
 def test_incomplete_feed_preserves_existing_record(self):
  identity=db.upsert(self.record(),'bad','2020-01-01T00:00:00+00:00');s={'id':'bad','name':'Lab','url':'https://example.org/feed','adapter':'greenhouse'}
  for payload in [b'{}',b'{"jobs":[],"has_more":true}']:
   with patch('portal.collector.robots'),patch('portal.collector.fetch',return_value=(200,{},payload)),self.assertRaises(ValueError):collect_source(s)
  old=next(r for r in db.rows() if r['id']==identity);self.assertNotIn('verification_warning',old);self.assertEqual(old['verified'],'2020-01-01T00:00:00+00:00')
 def test_cv_replace_conflicts_and_undo_preserves_preferences(self):
  before={'education':['Original degree'],'experience':['Original work'],'projects':['Original project'],'languages':{'German':'A2'},'locations':['Stuttgart'],'max_hours':20};db.set_meta('profile',before)
  u=uploads.store('review.tex',b'\\section{Education}\nUpdated degree and research details\n\\section{Languages}\nGerman (B1)','cv');u=uploads.import_cv(u)
  review=u['metadata']['review'];decisions=[{'index':i,'action':'replace',**({'current':before[x['field']][0]} if x['field']!='languages' else {})} for i,x in enumerate(review)]
  u=uploads.resolve(u['id'],decisions);after=db.get_meta('profile');self.assertEqual(after['education'],['Updated degree and research details']);self.assertEqual(after['languages']['German'],'B1');self.assertEqual(after['max_hours'],20)
  uploads.undo(u['metadata']['version_id']);self.assertEqual(db.get_meta('profile')['education'],before['education']);self.assertEqual(db.get_meta('profile')['languages'],before['languages'])
 def test_apply_resume_edits_versions_master(self):
  p=studio.create({'posting':{'title':'Vision role','organization':'Lab'}});source='\\documentclass{article}\n\\begin{document}Built robot models.\\end{document}'
  d=studio.new_document(p['id'],'resume',source,{'generation':{'edits':[{'original':'Built robot models.','replacement':'Built models for robot perception.','reason':'Clarify','evidence_ids':['projects:0']}]}})
  revised=studio.decide_edits(d['id'],{'0':'accepted'},True);self.assertNotEqual(d['id'],revised['id']);self.assertEqual(studio.document(d['id'])['source'],source);self.assertIn('robot perception',revised['source']);self.assertIn('Previous',revised['metadata']['diff'])
 def test_section_revision_preserves_manual_text_and_scopes_jobs(self):
  p=studio.create({'posting':{'title':'Role','organization':'Lab'}});d=studio.new_document(p['id'],'letter',studio.LETTER.replace('[[LETTER_BODY]]','First paragraph.\n\nManual second paragraph.'))
  revised=studio.revise_section(d['id'],'0','Updated first paragraph.');self.assertIn('Manual second paragraph.',revised['source']);self.assertNotIn('First paragraph.',revised['source'])
  identity=jobs.enqueue('compile',{'document_id':d['id']});queue=self.client.get('/api/studio').json['jobs'];self.assertEqual(next(j for j in queue if j['id']==identity)['project_id'],p['id'])
 def test_readiness_requires_checklist_and_latest_reviewed_pdf(self):
  p=studio.create({'posting':{'title':'Role','organization':'Lab','text':'CV required.'}});d=studio.new_document(p['id'],'resume','source',{'compilation':{'status':'compiled','warnings':[]},'visual_reviewed':'today'})
  self.assertFalse(studio.readiness(p)['ready']);p['progress']={x['id']:True for x in p['checklist']};self.assertTrue(studio.readiness(p)['ready']);studio.new_document(p['id'],'resume','new source');self.assertFalse(studio.readiness(p)['ready'])
 def test_type_migration_preserves_workflow_and_verification(self):
  r=self.record();r['type']='Semester Project / Internship / Master Thesis';identity=db.upsert(r,'test','2020-01-01T00:00:00+00:00')
  with db.connect() as c:
   raw=dict(r);body=json.dumps(raw);c.execute('UPDATE opportunities SET data=? WHERE id=?',(body,identity))
   c.execute("INSERT INTO workflow(opportunity_id,stage,notes,dismissed,updated,bookmarked) VALUES(?,'Applied','Keep note',0,'today',1)",(identity,))
  db.migrate_taxonomy();one=next(x for x in db.rows() if x['id']==identity)
  self.assertEqual(set(one['types']),{'Semester project','Internship','Master’s thesis'})
  self.assertEqual(one['original_type'],r['type']);self.assertEqual(one['verified'],'2020-01-01T00:00:00+00:00');self.assertEqual(one['notes'],'Keep note');self.assertTrue(one['bookmarked'])
  rows=db.rows()
  for label in ['Master Thesis',"Master's thesis",'Master’s thesis','Semester project','Internship']:
   found=[x['id'] for x in rows if matches(x,label)];self.assertIn(identity,found);self.assertEqual(len(found),len(set(found)))
  db.migrate_taxonomy();self.assertEqual(one,next(x for x in db.rows() if x['id']==identity))
 def test_types_remain_category_specific_and_workload_independent(self):
  a=normalize({'category':'research','type':'student project / thesis','title':'Full-time student'})
  self.assertEqual(a['types'],['Student project','Thesis (degree unspecified)']);self.assertEqual(a['employment_arrangements'],['Not stated'])
  b=normalize({'category':'jobs','type':'Internship','employment_type_raw':'Part-time'})
  self.assertTrue(matches(b,'Internship','Part-time'));self.assertFalse(matches(b,'Internship','Full-time'))
  self.assertEqual(normalize({'category':'events','type':'Unknown announcement'})['types'],['Unspecified'])
  self.assertNotIn('Full-time',normalize({'category':'jobs','type':'Full-time role'})['types'])
 def test_rpg_type_is_explicit_not_degree_assumption(self):
  from portal.collector import rpg
  intro='<h3>Vision - Available</h3><p>Description: Investigate cameras and visual control in robotic systems for autonomous navigation. '
  unspecified=rpg(intro+'Requirements: enrolled master student.</p>','https://example.edu/projects')[0]
  self.assertEqual(normalize(unspecified)['types'],['Unspecified'])
  specified=rpg(intro+'Thesis Type: Semester Project / Bachelor Thesis / Master Thesis See project on SiROP</p>','https://example.edu/projects')[0]
  self.assertEqual(set(normalize(specified)['types']),{'Semester project','Bachelor’s thesis','Master’s thesis'})
 def test_disappearing_idless_record_not_confused_with_same_organization(self):
  from portal.collector import reconcile
  a=self.record();a.pop('publisher_id',None);b={**a,'url':'https://example.edu/another','title':'Another project'}
  first=db.upsert(a,'feed','2020-01-01T00:00:00+00:00');second=db.upsert(b,'feed','2020-01-01T00:00:00+00:00')
  reconcile('feed',{first},[a],db.now())
  self.assertIn('verification_warning',next(r for r in db.rows() if r['id']==second));self.assertNotIn('verification_warning',next(r for r in db.rows() if r['id']==first))
 def test_alert_material_fingerprint_ignores_cosmetic_changes(self):
  r=self.record();a=notifications.fingerprint(r)
  self.assertEqual(a,notifications.fingerprint({**r,'summary':'New wording','title':'Reformatted title'}))
  self.assertNotEqual(a,notifications.fingerprint({**r,'deadline':'2099-12-01'}))
 def test_registry_upgrade_retains_existing_success_and_shared_ids(self):
  from portal.startups import upgrade
  db.set_meta('startup_registry','3')
  with db.connect() as c:
   c.execute("UPDATE sources SET last_success='2020-01-01',data=json_set(data,'$.operational',json('true'),'$.interval_hours',12) WHERE id='skydio'")
  upgrade();sources={s['id']:s for s in db.sources()}
  self.assertEqual(sources['skydio']['last_success'],'2020-01-01');self.assertTrue(sources['skydio']['operational']);self.assertEqual(sources['skydio']['interval_hours'],12)
  self.assertEqual(sources['embotech']['adapter'],'embotech-pdf');self.assertEqual(sources['verity']['adapter'],'breezy-html')
if __name__=='__main__':unittest.main()
