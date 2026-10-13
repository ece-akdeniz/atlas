import unittest, tempfile, json, os
from pathlib import Path
from unittest.mock import patch
from portal import db
from portal.model import ranked,evaluate,status,validate,DEFAULT_PROFILE,canonical_url
from portal.collector import jsonld,rpg,refresh,safe_url,SourceError
from portal.seed import RECORDS,bootstrap

class PortalTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.old=db.DB_PATH; db.DB_PATH=Path(self.tmp.name)/'test.db'; bootstrap()
    def tearDown(self): db.DB_PATH=self.old; self.tmp.cleanup()
    def test_invalid_record_rejected(self):
        r=dict(RECORDS[0][1],hours=-10)
        with self.assertRaises(ValueError): validate(r)
        with self.assertRaises(ValueError): validate(dict(r,hours=10,application_url='javascript:alert(1)'))
    def test_malformed_jsonld_does_not_create_listing(self):
        self.assertEqual(jsonld('<script type="application/ld+json">{broken}</script>','https://example.com/job'),[])
    def test_jsonld_extracts_and_classifies_thesis(self):
        html='<script type="application/ld+json">'+json.dumps({'@type':'JobPosting','title':'Robotics Master Thesis','description':'Robot perception','hiringOrganization':{'name':'Industry partner'},'jobLocation':{'address':{'addressLocality':'Stuttgart','addressCountry':'DE'}}})+'</script>'
        rs=jsonld(html,'https://example.com/job'); self.assertEqual(rs[0]['category'],'research');self.assertIsNone(rs[0]['deadline'])
    def test_cross_source_dedup_retains_evidence(self):
        r=RECORDS[0][1].copy(); a=db.upsert(r,'official')
        r['url']+='?utm_source=aggregator'; b=db.upsert(r,'secondary')
        self.assertEqual(a,b); self.assertEqual(len([x for x in db.rows() if x['id']==a]),1)
        self.assertIn('secondary',[x['source_id'] for x in next(x for x in db.rows() if x['id']==a)['sources']])
    def test_research_projects_do_not_merge(self):
        for n in ['mapping','perception']:
            r=dict(RECORDS[2][1],publisher_id=n);db.upsert(r,'lab')
        self.assertEqual(len(db.rows()),7)
    def test_changed_deadline_has_history(self):
        r=dict(RECORDS[0][1],deadline='2026-11-01'); a=db.upsert(r,'bmw');r['deadline']='2026-11-15';db.upsert(r,'bmw')
        with db.connect() as c: latest=json.loads(c.execute('SELECT fields FROM changes WHERE opportunity_id=? ORDER BY id DESC',(a,)).fetchone()[0])
        self.assertEqual(latest['deadline']['before'],'2026-11-01');self.assertEqual(latest['deadline']['after'],'2026-11-15')
    def test_failed_fetch_preserves_last_verification_and_status(self):
        before={r['id']:(r['verified'],r['status']) for r in db.rows()}
        with patch('portal.collector.collect_source',side_effect=SourceError('HTTP 503')): refresh()
        after={r['id']:(r['verified'],r['status']) for r in db.rows()}
        self.assertEqual(before,after);self.assertTrue(any(s['failures']==1 for s in db.sources()))
    def test_stable_ranking_across_input_orders(self):
        rs=db.rows();self.assertEqual([r['id'] for r in ranked(rs,DEFAULT_PROFILE,'2026-10-12')],[r['id'] for r in ranked(list(reversed(rs)),DEFAULT_PROFILE,'2026-10-12')])
    def test_hours_never_prove_work_authorization(self):
        r=dict(db.rows()[0],hours=20,category='jobs',country='Switzerland'); e=evaluate(r,DEFAULT_PROFILE,'2026-10-12')
        self.assertEqual(e['match']['authorization'],'Insufficient information');self.assertTrue(any('Swiss' in x for x in e['match']['questions']))
    def test_enrollment_conflict_is_visible(self):
        r=dict(db.rows()[0],enrollment_required=True);p=dict(DEFAULT_PROFILE,enrolled=False);e=evaluate(r,p,'2026-10-12');self.assertEqual(e['match']['eligibility'],'Explicit requirement conflict')
    def test_uncertain_profile_no_invented_skills(self):
        e=evaluate(dict(db.rows()[0],skills=['PyTorch']),DEFAULT_PROFILE,'2026-10-12');self.assertIn('Not evidenced',e['match']['gaps'][0])
    def test_lifecycle_deadline_and_failed_source(self):
        r=dict(db.rows()[0],deadline='2026-10-11',verification_warning='failed');self.assertIn('Expired',status(r,'2026-10-12'));self.assertIn('Unverified',status(r,'2026-10-12'))
    def test_ssrf_rejects_private_destination(self):
        with patch('socket.getaddrinfo',return_value=[(2,1,6,'',('127.0.0.1',443))]):
            with self.assertRaises(SourceError):safe_url('https://localhost/x')
    def test_api_csrf_persistence_and_pending_sources(self):
        from portal.app import create_app
        app=create_app(test=True);client=app.test_client();s=client.get('/api/state').get_json();id=s['opportunities'][0]['id']
        self.assertEqual(client.post('/api/workflow/'+id,json={'stage':'Applied'}).status_code,403)
        headers={'X-CSRF-Token':s['csrf']};resp=client.post('/api/workflow/'+id,json={'stage':'Applied','notes':'Follow up privately','dismissed':False},headers=headers);self.assertEqual(resp.status_code,200)
        self.assertEqual(next(r for r in client.get('/api/state').get_json()['opportunities'] if r['id']==id)['stage'],'Applied')
        self.assertEqual(client.post('/api/sources',json={'url':'https://example.com/projects'},headers=headers).status_code,200)
        source=next(s for s in db.sources() if s['url']=='https://example.com/projects');self.assertFalse(source['enabled']);self.assertEqual(source['status'],'Pending setup')
        self.assertEqual(client.post('/api/refresh',json={},headers=headers).status_code,202);self.assertEqual(client.post('/api/refresh',json={},headers=headers).status_code,429)
    def test_production_refuses_missing_secrets(self):
        from portal.app import create_app
        with patch.dict(os.environ,{'PORTAL_ENV':'production'},clear=True):
            with self.assertRaises(RuntimeError):create_app(test=True)
    def test_production_login_and_unauthenticated_api(self):
        from portal.app import create_app
        from werkzeug.security import generate_password_hash
        with patch.dict(os.environ,{'PORTAL_ENV':'production','PORTAL_OWNER_EMAIL':'owner@example.com','SECRET_KEY':'x'*40,'PORTAL_PASSWORD_HASH':generate_password_hash('long-test-password'),'PORTAL_ORIGIN':'https://atlas.example'}):
            app=create_app(test=True);c=app.test_client();self.assertEqual(c.get('/api/state').status_code,401)
            c.get('/login')
            with c.session_transaction() as sess: nonce=sess['login_nonce']
            self.assertEqual(c.post('/login',data={'nonce':nonce,'email':'owner@example.com','password':'long-test-password'}).status_code,302)
            self.assertEqual(c.get('/api/state').status_code,200)
    def test_rpg_extracts_only_available_projects(self):
        html='<h3>Drone Mapping - Available</h3><p>Project in computer vision with Python and PyTorch. Thesis Type: Master Thesis. Apply with CV.</p><h3>Old topic - Taken</h3><p>Not available.</p>'
        rs=rpg(html,'https://rpg.ifi.uzh.ch/student_projects.php');self.assertEqual(len(rs),1);self.assertEqual(rs[0]['skills'],['Python','PyTorch'])

    def test_robots_wildcards_specificity_and_agent(self):
        from portal.collector import robots_allowed
        policy='User-agent: *\nDisallow: /*?secret=\nDisallow: /private/\nAllow: /private/public$'
        self.assertFalse(robots_allowed(policy,'https://example.com/job?secret=1')[0])
        self.assertFalse(robots_allowed(policy,'https://example.com/private/thing')[0])
        self.assertTrue(robots_allowed(policy,'https://example.com/private/public')[0])
        self.assertFalse(robots_allowed(policy,'https://example.com/private/public/extra')[0])
    def test_hackatum_dates_and_support_are_source_checked(self):
        from portal.collector import hackatum
        text='hackaTUM 2026 will take place on November 27-29. There are no participation fees. open for everyone. free food and drinks. cannot provide travel reimbursements. sleeping rooms. We do not provide accommodation. between 2 and 4 members. language of the event is English. everyone has to apply individually. notification latest on November 14, 2025.'
        r=hackatum(text,'https://hack.tum.de/faq/')[0]
        self.assertEqual(r['event_start'],'2026-11-27');self.assertTrue(r['funding_confirmed']);self.assertTrue(any('2025' in q for q in r['questions']))
        with self.assertRaises(SourceError): hackatum('Unknown new page','https://hack.tum.de/faq/')
    def test_personal_delete_removes_profile_workflow_and_backup(self):
        from portal.app import create_app
        app=create_app(test=True);c=app.test_client();s=c.get('/api/state').get_json();headers={'X-CSRF-Token':s['csrf']}
        (db.DB_PATH.parent/'backups').mkdir(exist_ok=True);(db.DB_PATH.parent/'backups'/'old.sqlite3').write_bytes(b'private')
        (db.DB_PATH.parent/'profile.json').write_text('{"name":"private"}')
        self.assertEqual(c.post('/api/delete-personal',json={'confirm':'DELETE'},headers=headers).status_code,200)
        self.assertFalse((db.DB_PATH.parent/'profile.json').exists());self.assertEqual(list((db.DB_PATH.parent/'backups').glob('*')),[]);self.assertEqual(db.get_meta('profile')['skills'],[])
    def test_idle_worker_does_not_write_empty_run_every_minute(self):
        with db.connect() as c:c.execute("UPDATE sources SET next_due='2099-01-01T00:00:00+00:00'")
        self.assertEqual(refresh(),[])
        with db.connect() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM runs').fetchone()[0],0)

    def test_annual_event_editions_keep_separate_identity(self):
        from portal.collector import hackatum
        records=[hackatum(f'hackaTUM {year} will take place on November 27-29. on-site in Garching','https://hack.tum.de/faq/')[0] for year in [2026,2027]]
        ids=[db.upsert(r,'hackatum') for r in records]
        self.assertNotEqual(ids[0],ids[1])

if __name__=='__main__':unittest.main()
