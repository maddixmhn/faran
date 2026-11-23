# Moodle برای دانشگاه فاران

پنل فاران عملیات دانشگاه و وضعیت عامل‌ها را نمایش می‌دهد. Moodle دوره، تکلیف، آزمون و نمره را مدیریت می‌کند. منوی پنل روی میزبان محلی Moodle را در پنجرهٔ جدا باز می‌کند. همگام‌سازی داده و ورود یکپارچه هنوز پیاده‌سازی نشده‌اند.

از [Moodle](https://github.com/moodle/moodle) با مجوز GPL-3.0 و شاخهٔ نگهداری ۴٫۵ استفاده می‌شود. [محیط PHP رسمی MoodleHQ](https://github.com/moodlehq/moodle-php-apache) برای PHP ۸٫۳ و نصب محلی مناسب است. [moodle-docker](https://github.com/moodlehq/moodle-docker) برای توسعه و آزمون است. از تصویر PHP همان مجموعه استفاده می‌کنیم و Compose کوچک فقط PostgreSQL و فضای پایدار موردنیاز این نصب را اضافه می‌کند. تصویر Bitnami بررسی نشد چون صفحهٔ منبع در دسترس نبود. بستهٔ متفرقه‌ای به Moodle افزوده نشده است. جست‌وجوی مرتبط در D:/OB یادداشت اختصاصی Moodle پیدا نکرد.

## نصب محلی

پایگاه PostgreSQL و کانتینر وب Moodle روی این میزبان راه افتاده‌اند. Docker Hub برای تصویر PHP پاسخ ۴۰۳ داد. تصویر اجرای محلی از رجیستری واسط با digest ثبت‌شده دریافت شد. این digest با رجیستری اصلی تطبیق داده نشده است.

از ریشهٔ مخزن فاران اجرا کنید. سورس دریافت‌شده در این میزبان از commit `159ab15527329473770aefdf864499ce764752af` است. برای به‌روزرسانی، نسخهٔ نگهداری‌شده و سازگاری آن را پیش از تغییر بررسی کنید.

```powershell
git clone --depth 1 --branch MOODLE_405_STABLE https://github.com/moodle/moodle.git infra/workflow/data/lms/moodle
powershell -NoProfile -File infra/workflow/scripts/start-local-lms.ps1 -Install
```

گزینهٔ `-Install` حساب مدیر محلی با نام `admin` می‌سازد و رمز را در `infra/workflow/data/lms/moodle-admin.env` ذخیره می‌کند. برای راه‌اندازی مجدد همین نصب، از همان تصویر اولیه استفاده کنید. تصویر محلی این میزبان `registry.docker.ir/moodlehq/moodle-php-apache@sha256:514011c7f2cf58feb8f6bb8cbaabaaac74c52548b87e37202eadd167e5febc8f` است و با گزینهٔ `-Image` انتخاب می‌شود.

راه‌انداز رمز تصادفی PostgreSQL را در فایل محلی و خارج از Git در مسیر `infra/workflow/data/lms/compose.env` نگه می‌دارد. در http://localhost:8700 نصب را با PostgreSQL، میزبان `db`، نام پایگاه و کاربر `moodle` و مسیر دادهٔ `/var/www/moodledata` انجام دهید. اگر نصب‌کننده فایل `config.php` را برای دانلود پیشنهاد کرد، آن را در پوشهٔ محلی Moodle ذخیره کنید. برای نمونهٔ محلی فقط درس‌ها و کاربران ساختگی بسازید. پورت پایگاه داده به میزبان متصل نمی‌شود.

توکن n8n جای اعتبارنامهٔ Moodle را نمی‌گیرد. توکن ارسال‌شده در چت را از تنظیمات n8n باطل کنید. کلید جایگزین فقط در تنظیمات محرمانهٔ backend نگهداری شود. تا وقتی سایت عمومی به backend خصوصی دسترسی مجاز ندارد، از همان مسیر محلی برای دیدن اجرای workflow استفاده کنید.
