import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from recover import ROOT, load_profile, recover


class RecoveryTests(unittest.TestCase):
    def test_phrases(self):
        data = load_profile()
        phrases = [data['recovery_phrase'], data['id']] + data['aliases']
        phrases += ['عصاي سليمانم ارتميس بازگشت', '  عصای   سلیمانم، ارتمیس بازگشت! ', 'عصای\u200cسلیمانم ارتمیس بازگشت']
        for phrase in phrases:
            with self.subTest(phrase=phrase):
                self.assertEqual(recover(phrase, data)['context_markdown'], data['context_markdown'])

    def test_unknown_phrase(self):
        with self.assertRaises(ValueError):
            recover('wrong phrase', load_profile())

    def test_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            root.joinpath('profile.json').write_bytes(ROOT.joinpath('profile.json').read_bytes() + b' ')
            root.joinpath('profile.sha256').write_bytes(ROOT.joinpath('profile.sha256').read_bytes())
            with self.assertRaisesRegex(ValueError, 'checksum'):
                load_profile(root)

    def test_invalid_schema(self):
        for patch in ({'schema_version': 2}, {'aliases': [42]}, {'limitations': {}}, {'context_markdown': ''}):
            with self.subTest(patch=patch), tempfile.TemporaryDirectory() as tmp:
                data = dict(load_profile(), **patch)
                raw = json.dumps(data).encode()
                root = Path(tmp)
                root.joinpath('profile.json').write_bytes(raw)
                root.joinpath('profile.sha256').write_text(hashlib.sha256(raw).hexdigest())
                with self.assertRaises(ValueError):
                    load_profile(root)

    def test_cli(self):
        for args, expected in [(['--verify'], 0), (['wrong'], 1), ([], 2)]:
            proc = subprocess.run([sys.executable, str(ROOT / 'recover.py')] + args, capture_output=True)
            self.assertEqual(proc.returncode, expected)
        proc = subprocess.run([sys.executable, str(ROOT / 'recover.py'), load_profile()['recovery_phrase'], '--format', 'json'], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(proc.returncode, 0)
        self.assertFalse(json.loads(proc.stdout)['limitations']['persistent_memory'])


if __name__ == '__main__':
    unittest.main()
