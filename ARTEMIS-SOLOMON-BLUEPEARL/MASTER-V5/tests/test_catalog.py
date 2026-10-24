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
