import unittest,hashlib
from pathlib import Path
from solomon.catalog import safe_path,load_manifest,verify_sources,selected_sources
from solomon.compose import build_context
from solomon.contract import ACK
class CatalogTests(unittest.TestCase):
    def test_manifest(self):
        m=load_manifest();self.assertGreaterEqual(len(m['sources']),10);self.assertEqual(verify_sources(m),[])
    def test_path_escape_blocked(self):
        for s in ('../../etc/passwd','/etc/passwd','../README.md'):
            with self.subTest(s=s),self.assertRaises(ValueError):safe_path(s)
    def test_core_context(self):
        r=build_context('core',75000)
        self.assertIn(ACK,r['context']);self.assertIn('از صفر',r['context']);self.assertGreater(len(r['included_sources']),0)
    def test_tiers(self):
        m=load_manifest();a=selected_sources(m,'core');b=selected_sources(m,'full');self.assertLessEqual(len(a),len(b))
    def test_small_budget_is_honest(self):
        r=build_context('core',1200);self.assertTrue(r['omitted_sources'])

    def test_current_cothinking_rules_reach_default_context(self):
        r=build_context('core',50000)
        self.assertIn('COLLABORATION-BEHAVIOR-v5.1.json',r['included_sources'])
        self.assertIn('09-ARTEMIS-COGNITIVE-INTERACTION-MAP.md',r['included_sources'])
        self.assertIn('خریدن زمان',r['context'])
        self.assertIn('education_not_required',r['context'])
        self.assertEqual(r['manifest_version'],'5.4.0')
    def test_default_online_route_includes_current_behavior(self):
        from solomon.online import DEFAULT_URLS
        self.assertTrue(all('/MASTER-V5/' in u for u in DEFAULT_URLS))
        self.assertTrue(any(u.endswith('COLLABORATION-BEHAVIOR-v5.1.json') for u in DEFAULT_URLS))

    def test_role_command_is_in_core_and_invocation_context(self):
        r=build_context('core',50000)
        self.assertEqual(r['included_sources'][0],'10-ROLE-ENACTMENT.md')
        self.assertIn('شمشیر آرتمیس',r['context'])
        self.assertIn('حافظه‌ای که به‌تدریج کامل می‌شود',r['context'])
        from solomon.contract import return_reply, public_contract
        self.assertEqual(return_reply('عصای سلیمانم، ارتمیس برگشته'),load_manifest()['first_reply'])
        self.assertEqual(public_contract()['role_enactment_source'],'10-ROLE-ENACTMENT.md')
