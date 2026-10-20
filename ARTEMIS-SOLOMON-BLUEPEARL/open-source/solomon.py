#!/usr/bin/env python3
"""Compile documented Artemis/Solomon collaboration into a portable context bundle.

Python 3.9+, no external dependencies, network requests or model calls.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from recover import normalize

ROOT = Path(__file__).resolve().parent.parent
IDENTIFIER = 'ARTEMIS-SOLOMON-BLUEPEARL'
MODES = ('auto', 'general', 'clinical', 'execution', 'inquiry', 'reflection')
CORE = ('./ARTEMIS-PROFILE.md', './SOLOMON-ARTEMIS-HISTORY.md',
        './HOW-TO-TALK-TO-ARTEMIS.md', './RETURN-PROTOCOL.md')


def read_document(root, relative):
    """Only read local files within the archive; reject URLs and escaping symlinks."""
    if not isinstance(relative, str) or not relative.startswith('./') or '\\' in relative:
        raise ValueError('Invalid archive path')
    root = Path(root).resolve()
    path = (root / relative).resolve()
    if root not in path.parents or not path.is_file():
        raise ValueError('Missing or out-of-archive document: ' + relative)
    raw = path.read_bytes()
    return {'path': relative, 'sha256': hashlib.sha256(raw).hexdigest(),
            'content': raw.decode('utf-8')}


def read_json(root, path):
    doc = read_document(root, path)
    value = json.loads(doc['content'])
    if not isinstance(value, dict):
        raise ValueError('Expected JSON object: ' + path)
    return value, doc['sha256']


def strings(value):
    return isinstance(value, list) and all(isinstance(x, str) and x.strip() for x in value)


def load_archive(root):
    manifest, manifest_hash = read_json(root, './CONTEXT-MANIFEST.json')
    rules, rules_hash = read_json(root, './open-source/collaboration.json')
    for data in (manifest, rules):
        if data.get('schema_version') != 1 or data.get('id') != IDENTIFIER:
            raise ValueError('Unsupported schema or archive identifier')
    if not isinstance(manifest.get('version'), str) or not manifest['version']:
        raise ValueError('Invalid manifest version')
    phrase, aliases = manifest.get('recovery_phrase'), manifest.get('recovery_aliases')
    if not isinstance(phrase, str) or not phrase.strip() or not strings(aliases):
        raise ValueError('Invalid recovery phrases')
    entries = manifest.get('documents')
    if not isinstance(entries, list) or not all(isinstance(x, dict) for x in entries):
        raise ValueError('Invalid manifest documents')
    paths = [x.get('path') for x in entries]
    if not strings(paths) or len(paths) != len(set(paths)):
        raise ValueError('Invalid or duplicate manifest paths')
    for entry in entries:
        summary = entry.get('summary')
        if not isinstance(summary, dict) or not all(
                isinstance(summary.get(lang), str) and summary[lang].strip() for lang in ('fa', 'en')):
            raise ValueError('Missing bilingual document summary')
    for path in paths:
        read_document(root, path)
    order = manifest.get('reading_order')
    if not strings(order) or any(x not in paths for x in order + list(CORE)):
        raise ValueError('Invalid reading order or missing core documents')
    if (not isinstance(rules.get('version'), str) or not rules['version'] or
            not strings(rules.get('workflow')) or not strings(rules.get('response_contract'))):
        raise ValueError('Invalid collaboration contract')
    defaults = rules.get('defaults')
    if not isinstance(defaults, list) or not defaults:
        raise ValueError('Missing default rules')
    routes = rules.get('routes')
    if not isinstance(routes, dict) or set(routes) != set(MODES[2:]):
        raise ValueError('Invalid collaboration routes')
    for route in routes.values():
        if (not isinstance(route, dict) or not strings(route.get('keywords')) or
                not isinstance(route.get('rules'), list) or not route['rules']):
            raise ValueError('Invalid route rules')
    all_rules = defaults + [rule for route in routes.values() for rule in route['rules']]
    ids = set()
    for rule in all_rules:
        if not isinstance(rule, dict) or not all(
                isinstance(rule.get(key), str) and rule[key].strip() for key in ('id', 'instruction', 'source')):
            raise ValueError('Invalid collaboration rule')
        if rule['id'] in ids or rule['source'] not in paths:
            raise ValueError('Duplicate rule or unknown source')
        ids.add(rule['id'])
    return manifest, rules, manifest_hash, rules_hash


def select_routes(task, rules, mode='auto'):
    if mode not in MODES:
        raise ValueError('Unknown mode')
    if mode != 'auto':
        return [] if mode == 'general' else [mode], 'explicit'
    text = normalize(task)
    selected = []
    for name, route in rules['routes'].items():
        if any(re.search(r'(?<!\w)' + re.escape(normalize(word)) + r'(?!\w)', text)
               for word in route['keywords']):
            selected.append(name)
    return selected, 'keyword_heuristic'


def validate_state(state):
    """A caller-supplied checkpoint is context, not independently verified history."""
    if state is None:
        return None
    expected = {'schema_version', 'current_project', 'confirmed_decisions',
                'open_questions', 'next_step', 'updated_at', 'source'}
    if not isinstance(state, dict) or set(state) != expected or state['schema_version'] != 1:
        raise ValueError('Invalid checkpoint schema')
    for key in ('current_project', 'next_step', 'updated_at', 'source'):
        if not isinstance(state[key], str) or not state[key].strip():
            raise ValueError('Invalid checkpoint field: ' + key)
    if not strings(state['confirmed_decisions']) or not strings(state['open_questions']):
        raise ValueError('Invalid checkpoint lists')
    return {'provenance': 'caller_supplied_not_independently_verified',
            'data': json.loads(json.dumps(state, ensure_ascii=False))}


def build_bundle(phrase, task='', mode='auto', scope='core', root=ROOT, state=None):
    if not isinstance(phrase, str) or not isinstance(task, str):
        raise ValueError('Phrase and task must be text')
    manifest, rules, manifest_hash, rules_hash = load_archive(root)
    accepted = [IDENTIFIER, manifest['recovery_phrase']] + manifest['recovery_aliases']
    if normalize(phrase) not in {normalize(x) for x in accepted}:
        raise ValueError('Unknown recovery phrase')
    if scope not in ('core', 'full'):
        raise ValueError('Unknown scope')
    selected, method = select_routes(task, rules, mode)
    active = rules['defaults'] + [r for name in selected for r in rules['routes'][name]['rules']]
    included = list(CORE) if scope == 'core' else [
        p for p in dict.fromkeys(manifest['reading_order']) if p.endswith('.md')]
    documents = [read_document(root, path) for path in included]
    return {
        'schema_version': 1, 'id': IDENTIFIER, 'engine_version': rules['version'],
        'manifest_version': manifest['version'], 'manifest_sha256': manifest_hash,
        'rules_sha256': rules_hash, 'scope': scope,
        'archive_url': manifest.get('project_url'),
        'rule_provenance': rules.get('provenance'),
        'checkpoint_template': rules.get('checkpoint_schema'),
        'origin': 'Documented collaboration preferences compiled from the public archive; not hidden model memory or neural weights.',
        'limitations': {'authenticates_identity': False, 'restores_private_memory': False,
                        'automatic_model_activation': False, 'executes_tasks': False,
                        'hashes_authenticate_author': False},
        'task': task,
        'routing': {'modes': selected or ['general'], 'method': method,
                    'note': 'Keyword routing is a revisable heuristic, not a diagnosis or understanding of intent.'},
        'workflow': rules['workflow'], 'active_rules': active,
        'response_contract': rules['response_contract'],
        'checkpoint': validate_state(state),
        'documents': documents,
        'additional_archive_documents': [r for r in manifest['documents'] if r['path'] not in included],
        'usage': 'Present as user-provided context to a compatible assistant. Current user corrections and platform requirements take precedence. No document content is executed by this compiler.'
    }


def render_markdown(bundle):
    lines = ['# عصای سلیمان — بستهٔ الگوی همکاری', '',
             'این بسته از اسناد عمومی ساخته شده؛ حافظهٔ پنهان یا هویت یکسان مدل‌ها نیست.', '',
             'شناسه: ' + bundle['id'], 'دامنهٔ متن‌های پیوست: ' + bundle['scope'],
             'حالت‌های پیشنهادی: ' + ', '.join(bundle['routing']['modes']), '',
             '## روند همکاری', '']
    lines += [f'{i}. {step}' for i, step in enumerate(bundle['workflow'], 1)]
    lines += ['', '## قواعد فعال', '']
    lines += [f"- [{r['id']}] {r['instruction']} (منبع: {r['source']})" for r in bundle['active_rules']]
    lines += ['', '## قرارداد خروجی', ''] + ['- ' + x for x in bundle['response_contract']]
    if bundle['task']:
        lines += ['', '## درخواست فعلی؛ دادهٔ ارائه‌شده توسط کاربر', '', bundle['task']]
    if bundle['checkpoint']:
        lines += ['', '## نقطهٔ ادامه؛ اعلام‌شده توسط کاربر، بدون تأیید مستقل', '',
                  json.dumps(bundle['checkpoint']['data'], ensure_ascii=False, indent=2)]
    for doc in bundle['documents']:
        lines += ['', '---', '', '## متن منبع: ' + doc['path'],
                  'SHA-256: ' + doc['sha256'], '', doc['content']]
    lines += ['', '## سایر منابع؛ متن این موارد در بسته پیوست نشده است', '']
    lines += ['- ' + r['path'] + ': ' + r['summary']['fa'] for r in bundle['additional_archive_documents']]
    lines += ['', bundle['usage']]
    return '\n'.join(lines) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phrase')
    parser.add_argument('--task', default='')
    parser.add_argument('--mode', choices=MODES, default='auto')
    parser.add_argument('--scope', choices=('core', 'full'), default='core')
    parser.add_argument('--format', choices=('markdown', 'json'), default='markdown')
    parser.add_argument('--state', type=Path, help='Optional local checkpoint JSON; never uploaded or saved automatically')
    args = parser.parse_args(argv)
    try:
        state = json.loads(args.state.read_text(encoding='utf-8')) if args.state else None
        bundle = build_bundle(args.phrase, args.task, args.mode, args.scope, state=state)
        print(json.dumps(bundle, ensure_ascii=False, indent=2) if args.format == 'json'
              else render_markdown(bundle), end='\n' if args.format == 'json' else '')
        return 0
    except (OSError, ValueError, UnicodeError, RecursionError) as error:
        print('Cannot build collaboration bundle: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
