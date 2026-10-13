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
