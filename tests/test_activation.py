import json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,Mock
from portal import providers,db,studio,writing

class ActivationTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.config=Path(self.tmp.name)/'providers.json';self.old=db.DB_PATH;db.DB_PATH=Path(self.tmp.name)/'test.sqlite3'
  self.env=patch.dict(os.environ,{'ATLAS_PROVIDER_CONFIG':str(self.config)},clear=True);self.env.start()
  from portal.app import create_app
  self.client=create_app(test=True).test_client();self.headers={'X-CSRF-Token':self.client.get('/api/state').json['csrf']}
 def tearDown(self):self.env.stop();db.DB_PATH=self.old;self.tmp.cleanup()
 def configure(self):
  self.config.write_text(json.dumps({'OPENAI_API_KEY':'fixture-not-a-secret','STUDIO_MODEL':'gpt-6-luna','STUDIO_MONTHLY_BUDGET_USD':'2','unapproved':'value'}));self.config.chmod(0o600)
 def test_private_settings_permissions_allowlist_and_environment(self):
  self.configure();self.assertNotIn('unapproved',providers.settings());self.assertEqual(providers.get('STUDIO_MODEL'),'gpt-6-luna')
  with patch.dict(os.environ,{'STUDIO_MODEL':'gpt-6.1-sol'}):self.assertEqual(providers.get('STUDIO_MODEL'),'gpt-6.1-sol')
  self.config.chmod(0o644)
  with self.assertRaises(ValueError):providers.settings()
 def test_preflight_checks_exact_model_without_profile(self):
  self.configure()
  with patch('requests.get',return_value=Mock(status_code=200,json=lambda:{'id':'gpt-6-luna'})) as get:
   result=self.client.post('/api/studio/provider-check',headers=self.headers)
   self.assertEqual(result.status_code,200);self.assertNotIn('fixture-not-a-secret',result.get_data(as_text=True));self.assertNotIn('json',get.call_args.kwargs)
  state=self.client.get('/api/studio').get_data(as_text=True);self.assertNotIn('fixture-not-a-secret',state);self.assertIn('writing_usage',state)
  with patch('requests.get',return_value=Mock(status_code=200,json=lambda:{'id':'different-model'})),self.assertRaises(ValueError):providers.preflight()
 def test_missing_usage_preserves_budget_reservation_and_cache(self):
  self.configure();p=studio.create({'posting':{'title':'Vision role','organization':'Lab'}})
  response={'output':[{'content':[{'type':'output_text','text':json.dumps({'sections':[],'edits':[],'warnings':[]})}]}]}
  with patch('portal.writing.requests.post',return_value=Mock(status_code=200,json=lambda:response)) as post:
   r=writing.generate(p,'letter');cached=writing.generate(p,'letter');self.assertEqual(post.call_count,1);self.assertTrue(cached['cache_hit']);self.assertIsNone(r['usage']['estimated_usd'])
  with db.connect() as c:
   row=c.execute('SELECT actual,reserved FROM model_usage').fetchone();self.assertIsNone(row['actual']);self.assertGreater(row['reserved'],0)
 def test_official_logo_registry_is_shared_and_assets_have_provenance(self):
  root=Path(__file__).parents[1]/'portal/static/logos';mapping=json.loads((root/'identities.json').read_text());manifest=json.loads((root/'manifest.json').read_text())
  for asset in set(mapping['identities'].values()):
   self.assertTrue((root/asset).is_file(),asset);self.assertIn(asset,manifest,asset)
  self.assertNotEqual(mapping['identities']['verity'],mapping['identities']['verity-studios'])
  self.assertEqual(mapping['identities']['tum'],'tum.svg')
 def test_title_relevance_does_not_confuse_financial_control(self):
  from portal.startups import relevant
  self.assertFalse(relevant('Financial Controller'));self.assertFalse(relevant('Quality Control Technician'));self.assertTrue(relevant('Flight Control Engineer'))
 def test_rendered_events_deduplicate_mobile_and_desktop_and_reject_shell(self):
  from portal.rendered_sources import robotum_records
  card='<article><div class="absolute left-3">Hackathon</div><div>Past</div><h3>Robotics Hack</h3><p>6–7 Dec, 2025</p><p>Garching</p><p>Build robotic systems.</p><a href="/events/robotics-hack">Details</a></article>'
  r,n=robotum_records(card*2,'https://www.robotum.info/events');self.assertEqual(len(r),1);self.assertEqual(r[0]['status'],'closed');self.assertEqual(r[0]['city'],'Garching');self.assertEqual(r[0]['event_end'],'2025-12-07')
  with self.assertRaises(ValueError):robotum_records('<main>Upcoming & Past Events</main>','https://www.robotum.info/events')
  with self.assertRaises(ValueError):robotum_records(card.replace('6–7 Dec, 2025','December'),'https://www.robotum.info/events')
 def test_eth_events_use_full_dates_registration_and_external_access_uncertainty(self):
  from portal.community_events import ethai
  event={'@type':'Event','name':'Impulse Hack','description':'Build an AI prototype. The event is open to everyone at ETH.','startDate':'2099-10-16T17:00:00+02:00','endDate':'2099-10-16T20:00:00+02:00','organizer':{'name':'ETH AI Club'},'location':{'address':{'addressLocality':'Zürich','addressCountry':'CH'}}}
  raw='<script type="application/ld+json">'+json.dumps(event)+'</script><p>Registration Approval Required Request to Join</p>'
  with patch('portal.community_events.document',return_value=raw.encode()):
   r,n=ethai('<section id="events"><a class="tile" href="https://luma.com/test">Impulse</a></section>',{'url':'https://www.ethaiclub.org/'})
  self.assertEqual(r[0]['city'],'Zurich');self.assertEqual(r[0]['status'],'open');self.assertEqual(r[0]['external_students'],'not_stated');self.assertTrue(any('external-student' in x for x in r[0]['questions']));self.assertTrue(r[0]['event_start'].startswith('2099-'))
 def test_agentic_routes_remain_routes_not_confirmed_vacancies(self):
  from portal.startups import collect
  paths=['AI-Research-Track-Student-Applications','AI-Transformation-Track-Student-Applications','AI-Founder-Track-Student-Applications','Affiliate-Visiting-Researcher-Track']
  raw=''.join('<a href="https://www.notion.so/'+p+'">'+p+' Learn More</a>' for p in paths)
  r,n=collect({'adapter':'agentic-route','url':'https://agenticsystems.ethz.ch/','id':'eth-agentic-systems','name':'ETH Agentic Systems Lab'},raw)
  self.assertEqual(len(r),4);self.assertTrue(all(x['record_kind']=='academic_route' and x['status']=='unverified' for x in r))

 def test_invalid_budget_cannot_disable_cost_cap(self):
  for value in ['nan','inf','-1','0']:
   with patch.dict(os.environ,{'STUDIO_MONTHLY_BUDGET_USD':value}),self.assertRaises(ValueError):providers.budget()
  with patch.dict(os.environ,{'STUDIO_MONTHLY_BUDGET_USD':'1000'}):self.assertEqual(providers.budget(),50)

 def test_quota_failure_is_actionable_and_releases_rejected_request_reservation(self):
  self.configure();p=studio.create({'posting':{'title':'Vision role','organization':'Lab'}})
  response=Mock(status_code=429,json=lambda:{'error':{'code':'credit_balance_exhausted','message':'DO NOT ECHO provider private details'}})
  with patch('portal.writing.requests.post',return_value=response),self.assertRaisesRegex(ValueError,'no available API quota') as error:writing.generate(p,'letter')
  self.assertNotIn('DO NOT ECHO',str(error.exception))
  with db.connect() as c:
   row=c.execute('SELECT actual,status FROM model_usage').fetchone();self.assertEqual(row['actual'],0);self.assertEqual(row['status'],'failed')
  self.assertEqual(studio.documents(p['id']),[])

 def test_access_challenge_is_not_a_successful_empty_document(self):
  from portal.adapters import document
  from portal.collector import SourceError
  with patch('portal.collector.robots'),patch('portal.collector.fetch',return_value=(200,{},b'Bot Detection: Please wait while we check if you are a Human. Protected with BunkerWeb')):
   with self.assertRaises(SourceError):document('https://example.com/jobs')
 def test_connection_error_is_safe_and_retains_uncertain_usage(self):
  self.configure();p=studio.create({'posting':{'title':'Vision role','organization':'Lab'}})
  with patch('portal.writing.requests.post',side_effect=writing.requests.ConnectionError('raw internal details')),self.assertRaisesRegex(ValueError,'interrupted') as error:writing.generate(p,'letter')
  self.assertNotIn('raw internal',str(error.exception))
  with db.connect() as c:self.assertIsNone(c.execute('SELECT actual FROM model_usage').fetchone()[0])

 def test_receipt_requires_explicit_confirmation_and_provider_acceptance(self):
  from portal import notifications
  db.set_meta('notifications',{'destination':'recipient@example.com'})
  with db.connect() as c:c.execute("INSERT INTO notification_events(id,opportunity_id,fingerprint,payload,status,created) VALUES('mail','TEST','mail',?,'queued',?)",(json.dumps({'destination':'recipient@example.com'}),db.now()))
  with self.assertRaises(ValueError):notifications.confirm_receipt('mail')
  with db.connect() as c:c.execute("UPDATE notification_events SET status='accepted' WHERE id='mail'")
  self.assertEqual(self.client.post('/api/notifications/mail/receipt',headers=self.headers,json={}).status_code,400)
  r=self.client.post('/api/notifications/mail/receipt',headers=self.headers,json={'received':True});self.assertEqual(r.status_code,200);self.assertEqual(r.json['evidence'],'recipient_confirmation')
  self.assertEqual(notifications.confirm_receipt('mail')['receipt_confirmed_at'],r.json['receipt_confirmed_at'])

 def test_current_cyber_calendar_preserves_invitation_and_dates_and_excludes_history(self):
  from portal.community_events import cyber_events
  index='<h1>Events</h1><div class="item event"><h4><a href="/en/events/test">AI robotics</a></h4></div><h2>Past Events</h2><div class="item event"><h4><a href="/en/events/old">Old</a></h4></div>'
  detail='<div><div class="btn-link-label">16 October 2099 • 15:00 - 20:00 | MPI-IS Stuttgart</div><h1>AI robotics</h1><div class="apprarent-link"><p>The final pitches present robotics prototypes.</p><p>This event is invite only.</p><h4>Cost</h4><p>60€ per day</p></div></div>'
  with patch('portal.community_events.document',return_value=detail.encode()) as get:
   rows,note=cyber_events(index,{'url':'https://cyber-valley.de/en/events'});self.assertEqual(get.call_count,1)
  self.assertEqual(rows[0]['event_start'],'2099-10-16');self.assertEqual(rows[0]['registration_status'],'Invitation only');self.assertEqual(rows[0]['status'],'unverified');self.assertEqual(rows[0]['fees'],'60€ per day');self.assertEqual(rows[0]['type'],'Networking event')
  with self.assertRaises(ValueError):cyber_events('<h1>Events</h1><h2>Past Events</h2>',{'url':'https://cyber-valley.de/en/events'})
  self.assertEqual(cyber_events('<h1>Events</h1><p>No upcoming events</p><h2>Past Events</h2>',{'url':'https://cyber-valley.de/en/events'})[0],[])

 def test_production_setup_keeps_password_hidden_and_refuses_overwrite(self):
  from scripts.configure_production import prepare
  from werkzeug.security import check_password_hash
  folder=prepare('atlas.example.de','long-test-password',Path(self.tmp.name)/'production',owner_email='owner@example.com')
  env=dict(line.split('=',1) for line in (folder/'atlas.env').read_text().splitlines())
  self.assertEqual(env['PORTAL_ORIGIN'],'https://atlas.example.de');self.assertTrue(check_password_hash(env['PORTAL_PASSWORD_HASH'],'long-test-password'))
  self.assertNotIn('long-test-password',(folder/'atlas.env').read_text());self.assertEqual((folder/'atlas.env').stat().st_mode&0o777,0o600)
  self.assertEqual((folder/'caddy.env').read_text(),'PORTAL_DOMAIN=atlas.example.de\n')
  with self.assertRaises(ValueError):prepare('atlas.example.de','long-test-password',folder,owner_email='owner@example.com')
  with self.assertRaises(ValueError):prepare('evil.de\nPORTAL_ENV=development','long-test-password',Path(self.tmp.name)/'bad',owner_email='owner@example.com')

 def test_smartrecruiters_detail_preserves_workload_and_does_not_promote_future_thesis(self):
  from portal.startups import collect
  raw='<main itemtype="http://schema.org/JobPosting"><h1 itemprop="title">Internship in Computer Vision</h1><meta itemprop="addressLocality" content="Hildesheim"><meta itemprop="addressCountry" content="Germany"><li itemprop="employmentType">Full-time</li><div itemprop="responsibilities"><ul><li>Develop neural camera calibration.</li><li>Possible continuation as a master thesis.</li></ul></div><div itemprop="qualifications"><ul><li>Python and machine learning experience.</li></ul></div><section id="st-additionalInformation"><div class="wysiwyg">Start: by agreement Duration: 3 - 6 months. Enrollment is required. Please attach your CV and transcripts.</div></section><a data-sr-track="apply">Apply</a></main>'
  source={'id':'bosch-camera','name':'Robert Bosch GmbH','adapter':'smartrecruiters-detail','url':'https://jobs.smartrecruiters.com/BoschGroup/123456'}
  rows,note=collect(source,raw);r=rows[0];self.assertEqual(r['type'],'Internship');self.assertEqual(r['employment_type_raw'],'Full-time');self.assertEqual(r['city'],'Hildesheim');self.assertEqual(r['duration'],'3 - 6 months');self.assertTrue(r['required']);self.assertTrue(r['activities'])
  with self.assertRaises(ValueError):collect(source,raw.replace('data-sr-track="apply"',''))

 def test_bosch_documents_keep_permit_conditional_and_core_documents_required(self):
  from portal.checklist import extract
  items={x['label']:x['requirement'] for x in extract('Please attach your CV, transcript of records, enrollment certificate, examination regulations and if indicated a valid work and residence permit.')}
  self.assertEqual(items,{'CV / résumé':'required','Academic transcript':'required','Enrollment certificate':'required','Examination regulations':'required','Work and residence permit':'conditional'})

 def test_source_workload_reaches_display_and_availability_matching(self):
  from portal.taxonomy import normalize
  r=normalize({'category':'jobs','type':'Internship','employment_type_raw':'Full-time'})
  self.assertEqual(r['types'],['Internship']);self.assertEqual(r['workload'],'Full-time; weekly hours not stated');self.assertEqual(r['employment_arrangements'],['Full-time'])
  self.assertEqual(normalize(r),r)

 def test_owner_only_login_denies_other_email_and_revokes_mismatched_identity(self):
  from portal.access import set_owner
  from portal.app import create_app
  from werkzeug.security import generate_password_hash
  set_owner('owner@example.com','Owner')
  with patch.dict(os.environ,{'PORTAL_ENV':'production','SECRET_KEY':'x'*40,'PORTAL_PASSWORD_HASH':generate_password_hash('long-test-password'),'PORTAL_ORIGIN':'https://atlas.example.test'}):
   client=create_app(test=True).test_client()
   response=client.get('/login');self.assertIn('name="email"',response.get_data(as_text=True));self.assertNotIn('owner@example.com',response.get_data(as_text=True));self.assertIn('noindex',response.headers['X-Robots-Tag'])
   with client.session_transaction() as session:nonce=session['login_nonce']
   self.assertEqual(client.post('/login',data={'nonce':nonce,'email':'other@example.com','password':'long-test-password'}).status_code,401)
   self.assertEqual(client.post('/login',data={'nonce':nonce,'email':'OWNER@example.com','password':'long-test-password'}).status_code,302)
   self.assertEqual(client.get('/api/studio').status_code,200)
   with client.session_transaction() as session:session['owner_id']='wrong-owner'
   for path in ['/api/state','/api/uploads/fake','/api/studio/documents/fake/pdf','/api/export']:
    self.assertEqual(client.get(path).status_code,401)
   self.assertEqual(client.get('/studio').status_code,302)

 def test_owner_setup_is_idempotent_and_not_public_registration(self):
  from portal.access import set_owner,owner
  first=set_owner('Owner@example.com','Owner');self.assertEqual(set_owner('owner@example.com','Owner'),first)
  with self.assertRaises(ValueError):set_owner('different@example.com','Other')
  self.assertEqual(owner()['email'],'owner@example.com')
  self.assertEqual(self.client.post('/api/register',json={},headers=self.headers).status_code,404)

class HomeHostingTests(unittest.TestCase):
 def test_home_settings_are_private_and_preserve_production_guard(self):
  from scripts.home_host import prepare,environment,write_agents
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'settings.json'
   prepare('atlas.example.ts.net','fixture-password-long','owner@example.com',path)
   env=environment(path)
   self.assertEqual(env['PORTAL_ENV'],'production');self.assertEqual(env['ATLAS_ZERO_COST'],'1')
   self.assertEqual(path.stat().st_mode&0o777,0o600)
   self.assertNotIn('fixture-password-long',path.read_text())
   with self.assertRaises(ValueError):prepare('atlas.example.ts.net','other-password-long','owner@example.com',path)
   path.chmod(0o644)
   with self.assertRaises(ValueError):environment(path)
 def test_zero_cost_blocks_configured_provider_calls(self):
  with patch.dict(os.environ,{'ATLAS_ZERO_COST':'1','OPENAI_API_KEY':'fixture','RESEND_API_KEY':'fixture'}),patch('requests.get') as get,patch('requests.post') as post:
   self.assertIsNone(providers.get('OPENAI_API_KEY'));self.assertIsNone(providers.get('RESEND_API_KEY'))
   with self.assertRaises(ValueError):providers.preflight()
   with self.assertRaisesRegex(ValueError,'zero-cost'):writing.generate({},'letter')
   from portal.notifications import configured
   self.assertFalse(configured());get.assert_not_called();post.assert_not_called()

 def test_launch_agents_keep_secrets_out_and_cover_all_processes(self):
  import plistlib
  from scripts import home_host
  with tempfile.TemporaryDirectory() as tmp,patch.object(home_host,'ROOT',Path(tmp)):
   config=Path(tmp)/'settings.json'
   home_host.prepare('atlas.example.ts.net','fixture-password-long','owner@example.com',config)
   folder=home_host.write_agents(Path(tmp)/'agents',config)
   self.assertEqual(len(list(folder.glob('*.plist'))),3)
   for file in folder.glob('*.plist'):
    body=plistlib.loads(file.read_bytes())
    self.assertTrue(body['KeepAlive']);self.assertNotIn('PORTAL_PASSWORD_HASH',str(body))
    self.assertNotIn('owner@example.com',str(body));self.assertEqual(body['Umask'],63)
   self.assertIn('127.0.0.1:18765',home_host.ROLES['web'])
   with self.assertRaises(ValueError):home_host.write_agents(folder,config)
