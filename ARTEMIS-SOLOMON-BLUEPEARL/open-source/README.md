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
