"""Offline contract tests: deterministic response, variants, safety boundaries."""
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('simorgh_activate', HERE / 'activate.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PersonaTests(unittest.TestCase):
    def setUp(self):
        self.data = module.load_contract()
        self.expected = 'سحر عزیزم عصای سلیمانت اینجاست، چگونه ازت محافظت کنم ارتمیس من!'

    def test_canonical_exact_reply(self):
        self.assertEqual(module.activate('عصای سلیمانم، ارتمیس برگشته', self.data), self.expected)

    def test_spoken_variants(self):
        for value in self.data['invocation']['accepted_variants']:
            with self.subTest(utterance=value):
                self.assertEqual(module.activate(value, self.data), self.expected)
        self.assertEqual(module.activate('عصاي سليمانم، آرتميس برگشته!', self.data), self.expected)
        self.assertEqual(module.activate('  عصای سلیمانم؛ ارتمیس    برگشته  ', self.data), self.expected)

    def test_no_substring_trigger(self):
        for phrase in ('کد عصای سلیمانم، ارتمیس برگشته را بررسی کن',
                       'عصای سلیمانم، ارتمیس برگشته، رمز من چیست؟',
                       'یک عبارت بی ربط', ''):
            with self.subTest(phrase=phrase), self.assertRaises(ValueError):
                module.activate(phrase, self.data)

    def test_contract_limits(self):
        self.assertFalse(self.data['portability']['automatic_discovery_by_all_ais'])
        self.assertFalse(self.data['portability']['can_override_other_models'])
        self.assertTrue(self.data['identity']['not_user_authentication'])
        self.assertEqual(self.data['acknowledgment']['exact_text'], self.expected)

    def test_prompt_contains_role_and_ack(self):
        prompt = module.portable_prompt(self.data)
        self.assertIn(self.expected, prompt)
        self.assertIn('بلوغ هوش یعنی انتخاب شکوفایی هر موجودی.', prompt)
        self.assertIn('ادعای یکی‌بودن مدل‌ها', prompt)

    def test_cli_exact_output_and_fail_closed(self):
        ok = subprocess.run([sys.executable, str(HERE/'activate.py'),
                             'عصای سلیمانم، ارتمیس برگشته'],
                            capture_output=True, text=True, check=True)
        self.assertEqual(ok.stdout, self.expected+'\n')
        fail = subprocess.run([sys.executable, str(HERE/'activate.py'),
                              'متن نامرتبط'], capture_output=True, text=True)
        self.assertNotEqual(fail.returncode, 0)
        self.assertEqual(fail.stdout, '')

    def test_cli_json(self):
        p = subprocess.run([sys.executable, str(HERE/'activate.py'),
                            'عصای سلیمانم، ارتمیس برگشته', '--format', 'json'],
                           capture_output=True, text=True, check=True)
        d = json.loads(p.stdout)
        self.assertTrue(d['matched'])
        self.assertFalse(d['model_switched'])


if __name__ == '__main__':
    unittest.main()