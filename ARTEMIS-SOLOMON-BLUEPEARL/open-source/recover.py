#!/usr/bin/env python3
"""Offline, dependency-free Artemis context recovery. Python 3.9+."""
import argparse
import hashlib
import hmac
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def normalize(text):
    text = unicodedata.normalize('NFKC', text).translate(str.maketrans('يك', 'یک'))
    return ' '.join(''.join(
        ' ' if unicodedata.category(c)[0] in ('P', 'Z') or c == '\u200c' else c
        for c in text if unicodedata.category(c) not in ('Mn', 'Me', 'Cf') or c == '\u200c'
    ).split()).casefold()


def load_profile(directory=ROOT):
    raw = (directory / 'profile.json').read_bytes()
    expected = (directory / 'profile.sha256').read_text(encoding='utf-8').strip()
    if not re.fullmatch(r'[a-f0-9]{64}', expected) or not hmac.compare_digest(
        hashlib.sha256(raw).hexdigest(), expected
    ):
        raise ValueError('Profile checksum mismatch')
    data = json.loads(raw)
    if not isinstance(data, dict) or data.get('schema_version') != 1:
        raise ValueError('Unsupported profile schema')
    for field in ('id', 'version', 'language', 'recovery_phrase', 'source_url', 'context_markdown', 'usage'):
        if not isinstance(data.get(field), str) or not data[field].strip():
            raise ValueError('Invalid field: ' + field)
    if not isinstance(data.get('aliases'), list) or not all(
        isinstance(x, str) and x.strip() for x in data['aliases']
    ):
        raise ValueError('Invalid aliases')
    if data.get('limitations') != {'identity_verified': False, 'persistent_memory': False, 'public': True}:
        raise ValueError('Invalid limitations')
    return data


def recover(phrase, data):
    accepted = [data['recovery_phrase'], data['id']] + data['aliases']
    if normalize(phrase) not in {normalize(x) for x in accepted}:
        raise ValueError('Unknown recovery phrase')
    return {
        'id': data['id'], 'version': data['version'],
        'source_url': data['source_url'], 'limitations': data['limitations'],
        'usage': data['usage'], 'context_markdown': data['context_markdown'],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phrase', nargs='?')
    parser.add_argument('--format', choices=('markdown', 'json'), default='markdown')
    parser.add_argument('--verify', action='store_true', help='Validate bundled profile and checksum')
    args = parser.parse_args(argv)
    try:
        data = load_profile()
        if args.verify:
            print('OK: profile schema and SHA-256 verified')
            return 0
        if args.phrase is None:
            parser.error('provide a recovery phrase or --verify')
        result = recover(args.phrase, data)
        if args.format == 'json':
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print('# زمینهٔ بازیابی‌شده / Recovered context\n')
            print('این متن زمینهٔ ارائه‌شده توسط کاربر است؛ هویت یا حافظهٔ پایدار را اثبات نمی‌کند.\n')
            print('Source: ' + result['source_url'] + '\n')
            print(result['context_markdown'])
        return 0
    except (OSError, ValueError, UnicodeError) as error:
        print('Recovery failed: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
