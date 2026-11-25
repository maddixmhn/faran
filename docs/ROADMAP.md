# Faran roadmap

## First local slice

Journey: seed synthetic university roles → create a mock hardening course task → run its offline exercise → independently evaluate deterministic output → save a JSON report.

Acceptance: Python standard library only; deterministic idempotent 2,000-role seed; 12 sample active roles; repeatable task ID and result; independent evaluator flags invalid output; no real student/HR/finance data; schedule disabled; Paperclip disconnected; marketing copy remains draft.

Visual direction: temporary, accessible Persian-first RTL command-line output and JSON reports. No final dashboard design is claimed until the owner supplies the Chrome bookmark references.

## Dependencies and later work

1. Local mock core (this slice): CLI, seed, task execution, evaluation, JSON report.
2. Reliability: durable leases, retry, crash recovery, budget and concurrency limits.
3. Paperclip adapter: pin a release and exercise real create/read/execute integration.
4. Dashboard: accessible RTL states for organization, tasks, runs, costs, evaluations, and schedules.
5. Load and recovery evaluation: measure 2,000 mock identities and staged concurrency.
6. Deployment package: only after destination, budget, secrets, and operations are specified.

## درگاه دانشگاه

مسیرهای عمومی مؤسسه و معیار آزمون صفحه‌های فارسی در [مستند ساختار فاران](FARAN-INSTITUTION.md#بازآرایی-درگاه-دانشگاه) ثبت شده‌اند. خانه به خدمات دانشجو و دانشکده‌ها اولویت می‌دهد. آزمایشگاه و شواهد در صفحهٔ پروژه در دسترس‌اند.

## بازطراحی درگاه و داشبورد

مسیرهای دانشگاه و نمایش نمونهٔ کار از خانه قابل‌دسترسی‌اند. داخل داشبورد، فهرست جست‌وجوشدنی ابزارها دسترسی به ارائه، سندها، برنامهٔ Android، شواهد و نقشه را کنار کنترل‌های موجود می‌دهد. موبایل از چیدمان تک‌ستونه و همان ناوبری استفاده می‌کند. ورودی سند در ارزیاب روی مرورگر تحلیل می‌شود. داشبورد وضعیت خلاصهٔ شاهد را از API خواندنی می‌گیرد و هنگام اختلال شبکه به نسخهٔ همراه بسته برمی‌گردد. دادهٔ نمایشی به عنوان شاهد آرشیوی معرفی می‌شود.

برای بازاستفاده، قالب Python، رابط HTML/CSS، قرارداد رویداد و سازوکار بسته‌بندی کنونی حفظ شدند. فهرست ستاره‌ها و mcp.so بررسی شدند. Pico CSS با مجوز MIT، پشتیبانی RTL و اجرای مرورگری بررسی شد. مخزن آن آرشیو شده و CSS عمومی آن نیاز به بازبینی فرم‌ها و جدول‌های موجود در دو پروژه دارد. پوستهٔ محدود به صفحه و API استاندارد Vercel مسیر انتخابی‌اند. هیچ بستهٔ تازه‌ای وارد مسیر اجرا نمی‌شود. ورودی API به فایل‌های عمومی ثبت‌شده در مخزن محدود است. [Pico](https://github.com/picocss/pico) · [Vercel Build Output](https://vercel.com/docs/build-output-api/primitives)

آزمون پذیرش شامل مسیر ورود نمونه، حفظ پیوندهای قبلی، جست‌وجوی ابزار، لینک دانلود APK، خلاصهٔ API، نمایش جایگزین بدون API و عرض موبایل است.
