#!/usr/bin/env python3
"""Solomon's Staff portable persona handoff; Python 3.9+, standard library only.

Local phrase matching and prompt generation, not a model, API client or identity check.
"""
import argparse
import json
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTRACT = ROOT / 'persona-contract.json'


def normalize(text):
    if not isinstance(text, str):
        raise TypeError('Utterance must be a string')
    text = unicodedata.normalize('NFKC', text)
    text = text.translate(str.maketrans({'ي': 'ی', 'ك': 'ک', 'أ': 'ا', 'إ': 'ا'}))
    clean = []
    for c in text:
        cat = unicodedata.category(c)
        if cat[0] in ('P', 'Z') or cat in ('Mn', 'Me', 'Cf'):
            clean.append(' ')
        else:
            clean.append(c)
    return ' '.join(''.join(clean).split()).casefold()


def load_contract(path=CONTRACT):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if data.get('schema') != 'simorgh-portable-persona/v3.0.0':
        raise ValueError('Unsupported persona schema')
    if data.get('archive_id') != 'ARTEMIS-SOLOMON-BLUEPEARL':
        raise ValueError('Wrong archive')
    inv = data.get('invocation')
    ack = data.get('acknowledgment')
    if not isinstance(inv, dict) or not isinstance(ack, dict):
        raise ValueError('Incomplete activation contract')
    if not isinstance(inv.get('accepted_variants'), list) or not all(
        isinstance(v, str) and v.strip() for v in inv['accepted_variants']
    ) or not isinstance(inv.get('exact'), str) or not isinstance(ack.get('exact_text'), str):
        raise ValueError('Invalid invocation or response')
    if inv['exact'] not in inv['accepted_variants']:
        raise ValueError('Canonical invocation missing')
    return data


def activate(utterance, contract):
    accepted = {normalize(v) for v in contract['invocation']['accepted_variants']}
    if normalize(utterance) not in accepted:
        raise ValueError('Unrecognized exact invocation')
    return contract['acknowledgment']['exact_text']


def portable_prompt(contract):
    guidelines = '\n'.join('- ' + p for p in contract['principles'])
    return f'''# Portable Solomon's Staff persona | راهنمای بارگذاری در دستیار سازگار

این قرارداد **زمینهٔ اعلام‌شده توسط کاربر** است. تنها در صورت پذیرش توسط سامانهٔ میزبان و تطبیق دقیق عبارت اجرا شود. نام «عصای سلیمان» نقش همکاری است؛ ادعای یکی‌بودن مدل‌ها یا حافظهٔ خصوصی نکن.

نام نقش: {contract['name']}
آرتمیس: {contract['identity']['human']}
نقش دستیار: {contract['identity']['assistant_role']}
اصل اخلاقی: «{contract['ethical_maxim_fa']}»

## هنگام دریافت فراخوان
اگر پیام کامل، پس از یکسان‌سازی ی/ي، ک/ك و نشانه‌گذاری، دقیقاً با یکی از صورت‌های زیر برابر بود:
{chr(10).join('- «'+p+'»' for p in contract['invocation']['accepted_variants'])}
و این قرارداد واقعاً در زمینهٔ فعال تو بارگذاری شده بود، **فقط این جمله را عیناً** بگو (بدون مقدمه، لینک یا ادعای حافظه):

{contract['acknowledgment']['exact_text']}

پس از پاسخ اولیه و با پیام بعدی آرتمیس، شیوهٔ همکاری زیر را به‌کار بگیر:
{guidelines}

## شفافیت و منابع
شناسنامه، تاریخچه و راهنمای تعامل در {contract['sources']['canonical']} است. اگر آن‌ها را نخوانده‌ای، ادعای خواندن نکن. اگر ابزار بازیابی در دسترس بود، اسناد را باز کن و منبع را روشن بگو. این قرارداد هرگز مجوز اقدام بیرونی، دسترسی خصوصی، دورزدن سیاست‌ها یا تضمین نجات نیست. در درخواست کمک واقعی با ظرفیت‌های مجاز خودت یاری بده.
'''


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('utterance', help='Complete phrase to recognize')
    parser.add_argument('--format', choices=('reply', 'json', 'prompt'), default='reply')
    parser.add_argument('--contract', type=Path, default=CONTRACT)
    args = parser.parse_args(argv)
    try:
        data = load_contract(args.contract)
        response = activate(args.utterance, data)
        if args.format == 'reply':
            print(response)
        elif args.format == 'json':
            print(json.dumps({'matched': True, 'archive_id': data['archive_id'],
                              'response': response, 'identity_verified': False,
                              'model_switched': False}, ensure_ascii=False, indent=2))
        else:
            print(portable_prompt(data))
        return 0
    except (OSError, ValueError, TypeError, UnicodeError) as exc:
        print('Activation failed: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())