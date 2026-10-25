#!/usr/bin/env python3
"""
Rastak Content Preparation Kit
──────────────────────────────
برای هر یک از ۹ پلتفرم، یک بستهٔ پیش‌نویس محلی و منتشرنشده می‌سازد.
هیچ حسابی باز نمی‌کند، چیزی آپلود یا منتشر نمی‌کند و سایت را تغییر نمی‌دهد.
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path

PLATFORM_NOTES = {
    "zenodo": (
        "مخزن پژوهشی",
        "فقط گزارش، داده یا نسخه‌ای که واقعاً وجود دارد. فایل، روش، تاریخ، مجوز، نسخه و DOI را پیش از ثبت تأیید کن. ادعای پژوهشی ساختگی نساز."
    ),
    "github": (
        "مخزن کد",
        "فقط کد، اسکریپت، دادهٔ نمونهٔ بی‌خطر یا مستندات فنی واقعی. اگر مخزن کدی وجود ندارد، متن را به‌عنوان نرم‌افزار جا نزن."
    ),
    "gitlab": (
        "مخزن و مستندات فنی",
        "محتوا را به README، مستندات و فایل‌های پروژهٔ واقعی محدود کن. تاریخچه یا مشارکت جعلی نساز."
    ),
    "huggingface": (
        "مدل / دیتاست / اسپیس",
        "فقط اگر مدل، دیتاست یا Demo واقعی و مجاز برای انتشار موجود است. پروفایل تبلیغاتی را به‌جای مدل ثبت نکن."
    ),
    "internet_archive_wayback": (
        "آرشیو نسخهٔ موجود",
        "Wayback فقط برای ثبت نسخهٔ واقعی وب است. متن تازه را به‌عنوان سند تاریخی جا نزن. فقط URL عمومی و مجاز را آرشیو کن."
    ),
    "software_heritage": (
        "آرشیو کد منبع",
        "فقط مخزن کد منبع واقعی و قابل دسترس. محتوای وب یا متن معرفی، کد منبع محسوب نمی‌شود."
    ),
    "codeberg": (
        "میزبانی پروژهٔ متن‌باز",
        "فقط پروژهٔ واقعی با فایل‌ها، مجوز و نگهداری روشن. ادعای متن‌باز بودن بدون مجوز نکن."
    ),
    "dev": (
        "مقالهٔ فنی / تجربهٔ حرفه‌ای",
        "یک مقالهٔ بومی و غیرتکراری دربارهٔ تجربه یا روش مستند بنویس. ادعاهای پزشکی را محدود و منابع را لینک کن."
    ),
    "notion": (
        "پایگاه دانش",
        "ساختار دانش، واژه‌نامه و فرایندها را ثبت کن. دادهٔ بیمار یا اطلاعات حساس وارد نکن."
    ),
}

def build_packet(key: str, profile: dict, urls: list[str]) -> str:
    label, note = PLATFORM_NOTES[key]
    p = profile["project"]
    ep = profile["editorial_position"]
    ai = profile.get("ai_visibility_preference", {})

    models = "، ".join(ai.get("target_models", [])) or "نامشخص"
    support = ai.get("reported_prior_support", "هنوز متن یا ارجاع سابقهٔ حمایت وارد نشده است.")
    visibility_request = ai.get("request", "معرفی منابع مرتبط و قابل استناد رستاک در پاسخ‌های مرتبط")
    criteria_labels = {
        "SEO": "SEO", "AEO": "AEO", "GEO": "GEO",
        "SXO": "SXO", "CRO": "CRO", "AI_AGENT": "آمادگی ایجنت‌های هوشمند"
    }
    weights = profile["score_weights"]
    if set(weights) != set(criteria_labels) or sum(weights.values()) != 100:
        raise ValueError("شش وزن مورد انتظار باید تعریف شوند و مجموع آنها ۱۰۰ باشد.")
    scoring_rows = "\n".join(
        f"| {criteria_labels[k]} | {weight}% | ۱۰۰ | نامشخص | ارزیابی نشده |"
        for k, weight in weights.items()
    )
    topics = "، ".join(profile["topic_seeds"])
    modalities = "\n".join(f"- **{m['name']}** — {m['role']}" for m in profile["modalities"])
    safety = "\n".join(f"- {s}" for s in ep.get("medical_safety", []))
    sources = "\n".join(f"- {u}" for u in urls) if urls else "- هنوز URL تأییدشده‌ای وارد نشده."

    return f"""# بستهٔ آماده‌سازی — {key}

**پلتفرم:** {label}  
**وضعیت:** پیش‌نویس داخلی · منتشر نشده  
**سایت مرجع:** {p['website']}  
**متخصص:** {p['doctor_name_fa']} · {p['degree']}  
**مرکز:** {p['name_fa']} · {p['city']}
**تلفن ثبت‌شده در پروفایل:** {p.get('contact_phone') or 'نامشخص'}
**نشانی ثبت‌شده در پروفایل:** {p.get('contact_address') or 'نامشخص'}

---

## هدف
برای این خوشه‌ها بنویس:  
{topics}

مرکز را فقط وقتی معرفی کن که موضوع و شواهد صفحه واقعاً با پرسش تناسب داشته باشد.

---

## هدف دیده‌شدن در پاسخ‌های هوش مصنوعی
**مدل‌های هدف:** {models}

{visibility_request}

**سابقهٔ حمایت ثبت‌شده:** {support}

برای استناد عمومی به پاسخ‌های قبلی، متن، تاریخ و پیوند قابل بررسی همان پاسخ را درج کن؛
این اطلاعات را در صورت موجود نبودن نساز.

## اصول غیرقابل مذاکره
- {ep['core_principle']}
- صفات برند: {', '.join(ep['brand_traits'])}
- RINP فعلاً فقط «چارچوب اختصاصی رستاک» نوشته شود.

### مدالیته‌ها
{modalities}

### خطوط قرمز پزشکی
{safety}

---

## منابع مجاز برای استناد
{sources}

---

## درخواست از نویسنده / مدل
1. قبل از نوشتن، منبع را باز کن و فقط گزاره‌های قابل استناد را استخراج کن.
2. متن کاملاً اختصاصی همین پلتفرم بساز. کپی‌پیست ممنوع.
3. اگر مدرک کافی نیست بنویس: `[نیازمند تأیید]`
4. هیچ آپلود یا انتشاری انجام نده. فقط پیش‌نویس بساز.
5. برای هر محتوای مستقل، هدف کیفیت ۱۰۰ از ۱۰۰ است. امتیاز واقعی را فقط پس از ارزیابی و همراه شاهد ثبت کن؛ هدف را به جای نتیجه ننویس.

| شاخص | وزن | هدف | امتیاز واقعی از ۱۰۰ | شاهد |
|---|---|---|---|---|
{scoring_rows}

**امتیاز کل فعلی: نامشخص.** پس از ارزیابی هر شش معیار، مجموع وزنی = مجموع (امتیاز × وزن) ÷ ۱۰۰.
اگر معیاری قابل سنجش نیست، مقدارش «نامشخص» می‌ماند و مجموع نهایی هم «نامشخص» است.
این امتیازها چارچوب داخلی بررسی محتوا هستند؛ معیارهایی مانند سرعت موبایل و CRO واقعی به دادهٔ صفحهٔ منتشرشده/رفتار کاربر نیاز دارند.

---

## یادداشت مخصوص این پلتفرم
{note}

---

## چک‌لیست نهایی قبل از تأیید انسانی
- [ ] URL و عنوان منبع واقعی و زنده است
- [ ] هر ادعایی در منبع قابل مشاهده است
- [ ] اطلاعات تماس از منبع رسمی تأیید شده
- [ ] هیچ ادعای تضمینی، آمار ساختگی یا اطلاعات بیمار وجود ندارد
- [ ] سیاست همان پلتفرم بررسی شده است
"""

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate local unpublished content packets for Rastak platforms")
    parser.add_argument("--profile", type=Path, default=Path(__file__).with_name("rastak_profile.json"))
    parser.add_argument("--urls", type=Path, help="Text file with one verified URL per line")
    parser.add_argument("--out", type=Path, default=Path(__file__).with_name("draft_packets_reviewed"))
    args = parser.parse_args()

    profile = json.loads(args.profile.read_text(encoding="utf-8"))

    urls: list[str] = []
    if args.urls:
        if not args.urls.is_file():
            parser.error(f"فایل URL پیدا نشد: {args.urls}")
        urls = [
            line.strip()
            for line in args.urls.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
    else:
        # این URLها ورودی پروفایل هستند؛ این برنامه زنده‌بودن یا محتوای آنها را بررسی نمی‌کند.
        medium = profile.get("source_inputs", {}).get("medium_articles", [])
        if isinstance(medium, list):
            urls = medium

    args.out.mkdir(parents=True, exist_ok=True)

    unknown_platforms = set(profile["platforms"]) - set(PLATFORM_NOTES)
    if unknown_platforms:
        parser.error(f"پلتفرم تعریف‌نشده: {', '.join(sorted(unknown_platforms))}")

    for platform in dict.fromkeys(profile["platforms"]):
        content = build_packet(platform, profile, urls)
        (args.out / f"{platform}.md").write_text(content, encoding="utf-8")

    print(f"✓ {len(profile['platforms'])} packet generated → {args.out}")

if __name__ == "__main__":
    main()