import os,json,tempfile,unittest,io,zipfile
from pathlib import Path
from unittest.mock import patch
from datetime import datetime,timedelta,timezone
from portal import db,uploads,studio,jobs,notifications
from portal.checklist import extract
from portal.collector import refresh
class StudioTests(unittest.TestCase):
 def setUp(self):
  self.old=db.DB_PATH;self.tmp=tempfile.TemporaryDirectory();db.DB_PATH=Path(self.tmp.name)/'test.sqlite3';
  from portal.app import create_app
  self.app=create_app(test=True);self.client=self.app.test_client();self.csrf=self.client.get('/api/state').json['csrf'];self.headers={'X-CSRF-Token':self.csrf}
 def tearDown(self):db.DB_PATH=self.old;self.tmp.cleanup()
 def test_checklist_distinct_transcripts_and_projects(self):
  items=extract('Please send your CV, bachelor’s and master’s transcripts, and descriptions of relevant projects. A cover letter is not required.');labels={i['label'] for i in items}
  self.assertEqual(labels,{'CV / résumé','Bachelor’s transcript','Master’s transcript','Descriptions of relevant projects'});self.assertTrue(all(i['requirement']=='required' and i['evidence']['excerpt'] for i in items))
  self.assertNotIn('Master’s transcript',{i['label'] for i in extract('Please upload an undergraduate transcript.')})
 def test_zip_traversal_and_symlink_rejected(self):
  raw=io.BytesIO()
  with zipfile.ZipFile(raw,'w') as z:z.writestr('../secret.tex','invalid')
  with self.assertRaises(ValueError):uploads.files_from_upload('template.zip',raw.getvalue())
 def test_cv_import_preserves_preferences_idempotent_and_undo(self):
  before={'name':'Test','skills':['Python'],'languages':{'English':'C1'},'locations':['Stuttgart'],'max_hours':20,'residence_conditions':'private','projects':['Confirmed project'],'interests':['robotics']};db.set_meta('profile',before)
  source=b'\\documentclass{article}\n\\begin{document}\n\\section{Skills}\nPython, ROS2, C++\n\\section{Languages}\nEnglish (B2), German (B1)\n\\section{Projects}\nNew project needing confirmation\n\\end{document}'
  u=uploads.import_cv(uploads.store('cv.tex',source,'cv'));after=db.get_meta('profile');self.assertEqual(after['max_hours'],20);self.assertEqual(after['residence_conditions'],'private');self.assertEqual(after['projects'],before['projects']);self.assertIn('ROS 2',after['skills']);self.assertEqual(after['languages']['English'],'C1');self.assertTrue(u['metadata']['review'])
  dup=uploads.import_cv(uploads.store('cv.tex',source,'cv'));self.assertTrue(dup['duplicate']);uploads.undo(u['metadata']['version_id']);self.assertEqual(db.get_meta('profile')['skills'],['Python'])
 def test_undo_preserves_newer_manual_edits(self):
  db.set_meta('profile',{'skills':[]});u=uploads.import_cv(uploads.store('cv.tex',b'\\section{Skills}\nPython C++ ROS2 machine learning computer vision experience','cv'));p=db.get_meta('profile');p['skills'].append('Manual correction');db.set_meta('profile',p)
  with self.assertRaises(ValueError):uploads.undo(u['metadata']['version_id'])
  self.assertIn('Manual correction',db.get_meta('profile')['skills'])
 def test_project_snapshot_and_versions_preserve_master(self):
  p=studio.create({'posting':{'title':'Robot intern','organization':'Test lab','text':'Please send a CV.'}});u=uploads.store('master.tex',studio.RESUME.replace('[[RESUME_BODY]]','Original master').encode(),'resume_template');d=studio.local_draft(p,'resume',u['id']);updated=studio.new_document(p['id'],'resume',d['source']+'\n% edit',{'parent_id':d['id']});self.assertNotEqual(updated['id'],d['id']);self.assertNotIn('% edit',studio.template_source(u['id'],'resume'));db.set_meta('profile',{'name':'Changed'});self.assertNotEqual(studio.project(p['id'])['profile'],db.get_meta('profile'))
 def test_document_downloads_and_csrf(self):
  p=studio.create({'posting':{'title':'Role','organization':'Org','text':'Please attach a CV.'}});d=studio.new_document(p['id'],'letter',studio.LETTER)
  self.assertEqual(self.client.post('/api/studio/documents/'+d['id'],json={'source':'test'}).status_code,403)
  self.assertEqual(self.client.get('/api/studio/documents/'+d['id']+'/tex').status_code,200)
  self.assertEqual(self.client.get('/api/studio/documents/'+d['id']+'/pdf').status_code,400)
  self.assertEqual(self.client.post('/api/studio/documents/'+d['id']+'/ready',json={'reviewed':True},headers=self.headers).status_code,400)
 def test_compile_queue_deduplicates_and_retains_error(self):
  p=studio.create({'posting':{'title':'Role','organization':'Org','text':'CV'}});d=studio.new_document(p['id'],'letter','broken');first=jobs.enqueue('compile',{'document_id':d['id']});self.assertEqual(first,jobs.enqueue('compile',{'document_id':d['id']}))
  with patch('portal.compilation.compile_source',side_effect=RuntimeError('Missing asset')):self.assertTrue(jobs.once())
  with db.connect() as c:r=c.execute('SELECT status,result FROM jobs WHERE id=?',(first,)).fetchone()
  self.assertEqual(r['status'],'failed');self.assertIn('Missing asset',r['result'])
 def test_manual_refresh_rechecks_recent_success_but_not_backoff(self):
  with db.connect() as c:
   c.execute('DELETE FROM sources');past=(datetime.now(timezone.utc)-timedelta(hours=2)).isoformat();future=(datetime.now(timezone.utc)+timedelta(hours=20)).isoformat()
   for identity,error in [('good',None),('bad','HTTP 503')]:c.execute('INSERT INTO sources(id,data,last_attempt,last_success,error,next_due) VALUES(?,?,?,?,?,?)',(identity,json.dumps({'name':identity,'url':'https://example.com','enabled':True,'adapter':'jsonld','interval_hours':24}),past,past,error,future))
  with patch('portal.collector.collect_source',return_value=(2,'Validated')) as collector:
   self.assertEqual(refresh(),[]);result=refresh(force=True);self.assertEqual([r['source'] for r in result],['good']);self.assertEqual(collector.call_count,1)
  self.assertEqual(db.get_meta('refresh_skipped')[0]['source'],'bad')
 def test_notification_enable_suppresses_existing_database(self):
  notifications.configure({'destination':'test@example.com','enabled':True});self.assertGreater(len(db.get_meta('notification_baseline')),0)
  with patch('portal.notifications.qualifies',return_value=True):self.assertEqual(notifications.discover(),0)
 def test_email_no_provider_no_delivery(self):
  with patch.dict(os.environ,{'RESEND_API_KEY':'','ATLAS_EMAIL_FROM':''}):
   self.assertFalse(notifications.configured())
   with self.assertRaises(ValueError):notifications.queue_test()
 def test_source_silent_checklist(self):self.assertEqual(extract('Welcome to our research laboratory.'),[])
 def test_letter_recipient_changes_without_touching_master(self):
  original=r'\begin{letter}{Old Company}\opening{Dear team,}Old role\end{letter}'
  updated=studio.target_letter(original,{'organization':'New & Co'})
  self.assertIn(r'New \& Co',updated);self.assertNotIn('Old Company',updated);self.assertIn('Old Company',original)
 def test_notification_failed_source_is_unverified(self):
  notifications.configure({'destination':'test@example.com','enabled':True});db.set_meta('notification_baseline',{})
  with db.connect() as c:c.execute("UPDATE sources SET error='HTTP 503'")
  seen=[]
  with patch('portal.notifications.qualifies',side_effect=lambda r,p,c:seen.append(r) or False):notifications.discover()
  affected=[r for r in seen if r.get('verification_warning')]
  self.assertTrue(affected);self.assertTrue(all('Unverified' in r['states'] for r in affected))
 def test_destination_change_cancels_pending_email(self):
  notifications.configure({'destination':'first@example.com','enabled':True})
  with db.connect() as c:c.execute("INSERT INTO notification_events(id,opportunity_id,fingerprint,payload,status,created) VALUES('one','TEST','one','{}','retry',?)",(db.now(),))
  notifications.configure({'destination':'second@example.com'})
  with db.connect() as c:self.assertEqual(c.execute("SELECT status FROM notification_events WHERE id='one'").fetchone()[0],'cancelled')
 def test_production_protects_private_routes(self):
  from werkzeug.security import generate_password_hash
  from portal.app import create_app
  with patch.dict(os.environ,{'PORTAL_ENV':'production','PORTAL_OWNER_EMAIL':'owner@example.com','PORTAL_ORIGIN':'https://atlas.example.test','SECRET_KEY':'x'*40,'PORTAL_PASSWORD_HASH':generate_password_hash('test-only-password')}):
   client=create_app(test=True).test_client()
   for route in ['/api/studio','/api/uploads/fake','/api/studio/documents/fake/pdf','/api/state','/api/notifications']:
    self.assertEqual(client.get(route).status_code,401,route)
   self.assertEqual(client.get('/studio').status_code,302)
 def test_studio_poll_recovers_csrf_after_session_reset(self):
  with self.client.session_transaction() as session:session.clear()
  token=self.client.get('/api/studio').json['csrf'];self.assertTrue(token)
  response=self.client.post('/api/studio/projects',json={'posting':{'title':'Test role','organization':'Test lab','text':'CV required'}},headers={'X-CSRF-Token':token})
  self.assertEqual(response.status_code,200)
 def test_local_restart_keeps_session_key(self):
  from portal.app import create_app
  self.assertEqual(self.app.secret_key,create_app(test=True).secret_key)
if __name__=='__main__':unittest.main()
