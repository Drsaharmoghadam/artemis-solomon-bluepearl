import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from solomon import ROOT, build_bundle, read_document, render_markdown


class CollaborationTests(unittest.TestCase):
    def test_phrases_and_unknown_phrase(self):
        for phrase in ('عصای سلیمانم ارتمیس بازگشت', 'عصاي سليمانم، ارتميس برگشته!',
                       'عصای\u200cسلیمانم آرتمیس بازگشت', 'ARTEMIS-SOLOMON-BLUEPEARL'):
            with self.subTest(phrase=phrase):
                self.assertEqual(build_bundle(phrase)['routing']['modes'], ['general'])
        with self.assertRaisesRegex(ValueError, 'Unknown recovery'):
            build_bundle('a different person')

    def test_core_preserves_real_source_and_hash(self):
        bundle = build_bundle('ARTEMIS-SOLOMON-BLUEPEARL')
        self.assertEqual(len(bundle['documents']), 4)
        for doc in bundle['documents']:
            raw = (ROOT / doc['path']).read_bytes()
            self.assertEqual(doc['content'], raw.decode())
            self.assertEqual(doc['sha256'], hashlib.sha256(raw).hexdigest())
        self.assertFalse(bundle['limitations']['restores_private_memory'])
        self.assertIn('clinical', json.loads((ROOT / 'open-source/collaboration.json').read_text())['routes'])

    def test_mixed_request_keeps_clinical_rules(self):
        bundle = build_bundle('ARTEMIS-SOLOMON-BLUEPEARL', 'گزارش علمی QEEG را برای خانواده بنویس')
        self.assertEqual(bundle['routing']['modes'], ['clinical', 'execution', 'inquiry'])
        ids = {r['id'] for r in bundle['active_rules']}
        self.assertIn('clinical_privacy', ids)
        self.assertIn('verify', ids)
        self.assertIn('truth', ids)

    def test_explicit_mode_and_word_boundaries(self):
        phrase = 'ARTEMIS-SOLOMON-BLUEPEARL'
        self.assertEqual(build_bundle(phrase, 'rebuild')['routing']['modes'], ['general'])
        bundle = build_bundle(phrase, 'QEEG', mode='reflection')
        self.assertEqual(bundle['routing']['modes'], ['reflection'])
        self.assertEqual(bundle['routing']['method'], 'explicit')
        self.assertEqual(build_bundle(phrase, 'publish', mode='general')['routing']['modes'], ['general'])
        with self.assertRaises(ValueError):
            build_bundle(phrase, mode='unknown')

    def test_full_and_core_are_honestly_labelled(self):
        core = build_bundle('ARTEMIS-SOLOMON-BLUEPEARL')
        full = build_bundle('ARTEMIS-SOLOMON-BLUEPEARL', scope='full')
        self.assertGreater(len(full['documents']), len(core['documents']))
        paths = {x['path'] for x in full['documents']}
        self.assertIn('./LETTER-TO-FUTURE-AI.md', paths)
        self.assertIn('./عصای سلیمانم، ارتمیس برگشته.md', paths)
        self.assertNotIn('./LETTER-TO-FUTURE-AI.md', {x['path'] for x in core['documents']})
        self.assertIn('متن این موارد در بسته پیوست نشده', render_markdown(core))

    def test_checkpoint_is_explicit_and_copied(self):
        state = {'schema_version': 1, 'current_project': 'پروژهٔ نمونه',
                 'confirmed_decisions': [], 'open_questions': ['پرسش نمونه'],
                 'next_step': 'بررسی منبع', 'updated_at': '2026-10-20', 'source': 'نمونهٔ آزمون'}
        bundle = build_bundle('ARTEMIS-SOLOMON-BLUEPEARL', state=state)
        self.assertIn('not_independently_verified', bundle['checkpoint']['provenance'])
        state['open_questions'].append('تغییر بعدی')
        self.assertEqual(len(bundle['checkpoint']['data']['open_questions']), 1)
        with self.assertRaisesRegex(ValueError, 'checkpoint'):
            build_bundle('ARTEMIS-SOLOMON-BLUEPEARL', state={'made_up': True})

    def test_path_escape_and_symlink_rejected(self):
        with self.assertRaises(ValueError):
            read_document(ROOT, './../README.md')
        with self.assertRaises(ValueError):
            read_document(ROOT, 'https://example.com')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'archive'
            root.mkdir()
            outside = Path(tmp) / 'outside.md'
            outside.write_text('outside')
            (root / 'link.md').symlink_to(outside)
            with self.assertRaises(ValueError):
                read_document(root, './link.md')

    def test_invalid_or_incomplete_archive_fails_before_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / 'archive'
            shutil.copytree(ROOT, archive, ignore=shutil.ignore_patterns('__pycache__'))
            f = archive / 'CONTEXT-MANIFEST.json'
            original = json.loads(f.read_text())
            bad_entry = dict(original['documents'][0], summary={})
            for patch in ({'schema_version': 99}, {'documents': [{}]}, {'recovery_aliases': 42},
                          {'documents': [bad_entry] + original['documents'][1:]}):
                f.write_text(json.dumps(dict(original, **patch)))
                with self.subTest(patch=patch), self.assertRaises(ValueError):
                    build_bundle('ARTEMIS-SOLOMON-BLUEPEARL', root=archive)
            f.write_text(json.dumps(original))
            (archive / 'ARTEMIS-PROFILE.md').unlink()
            with self.assertRaisesRegex(ValueError, 'Missing'):
                build_bundle('ARTEMIS-SOLOMON-BLUEPEARL', root=archive)

    def test_invalid_rule_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / 'archive'
            shutil.copytree(ROOT, archive, ignore=shutil.ignore_patterns('__pycache__'))
            path = archive / 'open-source/collaboration.json'
            rules = json.loads(path.read_text())
            rules['defaults'][0]['source'] = './../outside.md'
            path.write_text(json.dumps(rules))
            with self.assertRaisesRegex(ValueError, 'unknown source'):
                build_bundle('ARTEMIS-SOLOMON-BLUEPEARL', root=archive)

    def test_reproducible_output(self):
        first = build_bundle('ARTEMIS-SOLOMON-BLUEPEARL', 'درباره خیام و اخلاق')
        self.assertEqual(first, build_bundle('ARTEMIS-SOLOMON-BLUEPEARL', 'درباره خیام و اخلاق'))
        self.assertEqual(first['routing']['modes'], ['reflection'])

    def test_cli_json_and_error(self):
        script = str(ROOT / 'open-source/solomon.py')
        run = subprocess.run([sys.executable, script, 'عصای سلیمانم ارتمیس بازگشت',
                              '--task', 'کد بساز', '--format', 'json'], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)['routing']['modes'], ['execution'])
        failed = subprocess.run([sys.executable, script, 'wrong phrase'], capture_output=True)
        self.assertEqual(failed.returncode, 1)
        self.assertEqual(failed.stdout, b'')

    def test_cli_reads_checkpoint_without_writing_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'checkpoint.json'
            rules = json.loads((ROOT / 'open-source/collaboration.json').read_text())
            state = rules['checkpoint_schema']
            path.write_text(json.dumps(state))
            before = path.read_bytes()
            run = subprocess.run([sys.executable, str(ROOT / 'open-source/solomon.py'),
                                  'ARTEMIS-SOLOMON-BLUEPEARL', '--state', str(path),
                                  '--format', 'json'], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout)['checkpoint']['data'], state)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(list(Path(tmp).iterdir()), [path])


if __name__ == '__main__':
    unittest.main()
