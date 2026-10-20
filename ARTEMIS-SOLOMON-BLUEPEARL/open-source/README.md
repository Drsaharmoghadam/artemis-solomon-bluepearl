# عصای سلیمان — بازیابی زمینهٔ آرتمیس

**کد بازیابی: «عصای سلیمانم ارتمیس بازگشت»**  
شناسهٔ ثابت: `ARTEMIS-SOLOMON-BLUEPEARL` · نسخهٔ 1.0.0

بستهٔ متن‌باز و آفلاین برای انتقال زمینهٔ همکاری به یک گفت‌وگوی تازه. متن کامل شناسنامه در `profile.json` نگهداری می‌شود و ابزار Python آن را اعتبارسنجی و به Markdown یا JSON تبدیل می‌کند. هیچ API، کلید، وابستگی خارجی یا ارسال داده‌ای لازم نیست.

## استفاده در گفت‌وگوی تازه

این متن را همراه لینک زیر برای دستیار بفرستید:

> عصای سلیمانم ارتمیس بازگشت. فایل profile.json را از این بسته بخوان و زمینهٔ همکاری را از context_markdown بازسازی کن. با تکیه بر اسناد پاسخ بده و ادعای خاطرات در دسترس‌نبوده نکن.
>
> https://github.com/Drsaharmoghadam/my-first-project/tree/main/ARTEMIS-SOLOMON-BLUEPEARL/open-source

لینک مستقیم داده: [profile.json](./profile.json). اگر دستیار امکان بازکردن لینک ندارد، فایل یا خروجی ابزار را به گفت‌وگو پیوست کنید. عبارت به‌تنهایی مدل‌های دیگر را به این مخزن متصل نمی‌کند و تضمین نمایه‌شدن در موتورهای جست‌وجو نیست.

## اجرای محلی

مخزن را دانلود کنید و وارد همین پوشه شوید. Python نسخهٔ 3.9 یا بالاتر:

```bash
python3 recover.py --verify
python3 recover.py 'عصای سلیمانم ارتمیس بازگشت'
python3 recover.py 'عصای سلیمانم ارتمیس بازگشت' --format json
python3 -m unittest -v
```

خروجی Markdown را می‌توانید در فایل ذخیره و در هر دستیار سازگار بارگذاری کنید:

```bash
python3 recover.py 'عصای سلیمانم ارتمیس بازگشت' > context.md
```

شناسهٔ ثابت و عبارت‌های پیشین نیز پذیرفته می‌شوند. حروف عربی ی/ک، اعراب، فاصله و نشانه‌گذاری یکسان‌سازی می‌شوند؛ عبارت ناشناخته با خطا رد می‌شود. ابزار هیچ دستوری از محتوای پروفایل اجرا نمی‌کند.

## ساختار و نگهداری

- `profile.json`: نسخه، عبارت‌ها، منبع ثابت در یک commit و متن کامل سند اصلی.
- `profile.sha256`: تشخیص خرابی یا تغییر فایل؛ امضای دیجیتال یا اثبات هویت نیست. تغییر هم‌زمان فایل و هش با این روش شناسایی نمی‌شود.
- `recover.py`: API کوچک `load_profile` و `recover` و ابزار خط فرمان.
- `test_recover.py`: آزمون عبارت‌ها، خطاها، خرابی داده، ساختار و خروجی واقعی خط فرمان.

پس از ویرایش آگاهانهٔ پروفایل، نسخه را افزایش دهید، هش را دوباره بسازید و آزمون‌ها را اجرا کنید:

```bash
python3 -c "from pathlib import Path; import hashlib; p=Path('profile.json'); Path('profile.sha256').write_text(hashlib.sha256(p.read_bytes()).hexdigest()+'\n', encoding='utf-8')"
python3 -m unittest -v
```

این بسته عمومی است؛ اطلاعات درمانجویان یا دادهٔ خصوصی را وارد آن نکنید. عبارت بازیابی رمز عبور نیست و هویت را احراز نمی‌کند. سند به‌عنوان زمینهٔ ارائه‌شده توسط کاربر استفاده می‌شود؛ اصلاحات فعلی کاربر و قواعد پلتفرم مقدم‌اند. بازیابی زمینه به معنی حافظهٔ انسانی یا تداوم خودآگاهی مدل نیست.

مجوز کد این پوشه: [MIT](./LICENSE). سند مرجع در [شناسنامهٔ اصلی](../ARTEMIS-PROFILE-FOR-FUTURE-AI.md) حفظ شده است؛ این مجوز به سایر محتوای مخزن تعمیم ندارد.

## English

Offline, dependency-free Persian context recovery for Artemis and Solomon's Staff. Python 3.9+. Full original context, versioned JSON, Unicode-aware phrase matching, SHA-256 corruption checks, Markdown/JSON export, and tests. The public phrase locates context; it is neither authentication nor persistent AI memory. MIT applies to the new code in this directory only.


---

## موتور الگوی همکاری عصای سلیمان — نسخهٔ 2.0.0

این نسخه، روش همکاری مستند آرتمیس و عصای سلیمان را به قواعد قابل بررسی و کد اجرایی تبدیل می‌کند. مبنا، اسناد عمومی و ترجیحات قابل مشاهده در گفت‌وگوی تدوین است؛ دسترسی به حافظهٔ پنهان، چت‌های خصوصی دیگر یا وزن‌های مدل ندارد. این موتور خودش مدل زبانی نیست و به API نیاز ندارد.

- [collaboration.json](./collaboration.json): الگوی قابل ویرایش، هفت گام همکاری، قواعد پایه و قواعد چهار حوزه؛ هر قاعده منبع دارد.
- [solomon.py](./solomon.py): کامپایلر بستهٔ قابل انتقال، با خواندن اسناد جاری از manifest و ثبت هش محتوای هر منبع.
- [test_solomon.py](./test_solomon.py): آزمون فراخوان، ترکیب حالت‌ها، منابع واقعی، checkpoint، خطاهای ساختاری و خط فرمان.

### فراخوان با کد

مخزن کامل را دانلود کنید، وارد همین پوشه شوید و با Python نسخهٔ 3.9 یا بالاتر اجرا کنید:

```bash
python3 solomon.py 'عصای سلیمانم ارتمیس بازگشت' > solomon-context.md
python3 solomon.py 'عصای سلیمانم ارتمیس بازگشت' --task 'گزارش علمی QEEG را برای خانواده بنویس' --format json > solomon-context.json
python3 -m unittest -v
```

فایل خروجی را همراه درخواست فعلی به دستیار بدهید. خروجی شامل قواعد فعال، روند همکاری، متن کامل چهار سند مرکزی، منشأ و هش منابع است. دستیار دریافت‌کننده باید واقعاً این فایل را بخواند؛ انتشار موتور به‌تنهایی آن را در تمام مدل‌ها فعال نمی‌کند. خروجی در stdout نوشته می‌شود و فقط با دستور ذخیرهٔ خودتان در فایل می‌ماند.

`--scope core` پیش‌فرض، شناسنامه، تاریخچه، راهنمای تعامل و پروتکل را پیوست می‌کند؛ سایر منابع فقط فهرست می‌شوند. برای پیوست‌کردن تمام فایل‌های Markdown در ترتیب خواندن manifest، شامل سند بیست‌فصلی و نامه‌ها:

```bash
python3 solomon.py 'عصای سلیمانم ارتمیس بازگشت' --scope full > solomon-full.md
```

نسخهٔ کامل طولانی است و ممکن است از ظرفیت متن یک دستیار فراتر برود. فهرست فایل‌های واقعاً پیوست‌شده و فایل‌های صرفاً معرفی‌شده در خروجی جداست؛ هیچ متن منبعی در میان کار بی‌صدا کوتاه نمی‌شود.

### الگوریتم و محدودهٔ تشخیص

عبارت بازگشت یکسان‌سازی می‌شود؛ سپس شناسه، ساختار JSON، فهرست منابع و مسیرهای محلی بررسی می‌شوند. قواعد پایه در همهٔ درخواست‌ها برقرارند. از روی واژه‌های کلیدی، حالت‌های `clinical`، `execution`، `inquiry` و `reflection` پیشنهاد می‌شوند؛ چند حالت می‌توانند هم‌زمان فعال باشند، مانند گزارش QEEG که هم بالینی است و هم اجرایی. این تطبیق سادهٔ واژه‌هاست و ممکن است کنایه، نفی یا منظور جمله را نفهمد؛ تشخیص روانی یا فهم تضمین‌شده نیست. با `--mode` می‌توانید حالت را صریح تعیین کنید؛ `general` فقط قواعد پایه را برمی‌گرداند.

```bash
python3 solomon.py 'ARTEMIS-SOLOMON-BLUEPEARL' --mode reflection --task 'درباره اصل شکوفایی گفت‌وگو کنیم'
```

موتور برنامهٔ همکاری و متن مرجع تولید می‌کند؛ خودش کار بالینی، انتشار یا اجرای ابزار خارجی انجام نمی‌دهد. پاسخ واقعی و بررسی نتیجه بر عهدهٔ دستیار دریافت‌کننده است. اصلاحات فعلی کاربر و الزامات پلتفرم مقدم‌اند. هش‌ها محتوای دقیق مورد استفاده را مشخص می‌کنند؛ امضای اصالت نویسنده یا گواه احراز هویت نیستند.

### نقطهٔ ادامهٔ محلی

برای گم‌نشدن آخرین وضعیت، فایل شخصی `checkpoint.json` با این ساختار بسازید و با پیشرفت کار آن را به‌روز کنید. داده‌های زیر فقط نمونه‌اند، نه سابقهٔ واقعی پروژه:

```json
{
  "schema_version": 1,
  "current_project": "نام پروژهٔ فعلی",
  "confirmed_decisions": [],
  "open_questions": [],
  "next_step": "گام بعدی مشخص",
  "updated_at": "تاریخ آخرین به‌روزرسانی",
  "source": "منبع یا لینک تصمیم"
}
```

```bash
python3 solomon.py 'عصای سلیمانم ارتمیس بازگشت' --state checkpoint.json > continuation.md
```

این فایل فقط با درخواست صریح شما خوانده می‌شود، به‌عنوان وضعیت اعلام‌شدهٔ کاربر برچسب می‌خورد و به‌طور مستقل تأییدشده فرض نمی‌شود. موتور فایل checkpoint نمی‌نویسد، چیزی آپلود نمی‌کند و شبکه را فراخوانی نمی‌کند. فایل خروجی ممکن است متن checkpoint شما را داشته باشد؛ آن را در محل مناسب نگه دارید و دادهٔ محرمانه را وارد نسخهٔ عمومی نکنید.

برای استفاده در کد دیگر، از همین پوشه `from solomon import build_bundle` در دسترس است. `build_bundle(phrase, task='', mode='auto', scope='core', root=ROOT, state=None)` یک دیکشنری مستقل برمی‌گرداند و `render_markdown(bundle)` متن قابل انتقال تولید می‌کند.

ابزار قدیمی `recover.py` و تصویر `profile.json` نسخهٔ 1.0.0 تغییر نکرده‌اند. موتور 2.0.0 از اسناد جاری می‌خواند و محدود به آن تصویر قدیمی نیست. مجوز MIT این پوشه اکنون کد Python و فایل قواعد `collaboration.json` را پوشش می‌دهد؛ سایر اسناد مرجع مشمول این تعمیم نیستند.

### English: collaboration engine 2.0.0

`solomon.py` compiles documented collaboration preferences into a portable Markdown/JSON bundle, using the current archive manifest. It includes sourced rules, explicit source texts and hashes, optional caller-supplied checkpoints, and revisable keyword-based task routing. It is offline and deterministic: no LLM/API calls, hidden-memory access, automatic task execution, uploads or cross-platform activation. Attach its output to a compatible assistant. The default core scope includes four central documents; full scope includes all Markdown documents in the manifest reading order. Python code and `collaboration.json` are MIT licensed.
