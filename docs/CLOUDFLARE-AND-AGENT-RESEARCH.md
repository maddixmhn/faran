# ارزیابی Cloudflare و مخزن‌های ایجنتی

**تاریخ بررسی:** ۱۴۰۵/۰۹/۰۲ (۲۰۲۶-۱۱-۲۳)  
**وضعیت:** تحقیق و تصمیم معماری؛ هیچ مخزن بیرونی نصب یا اجرا نشده و هیچ سرویس Cloudflare ساخته/منتشر نشده است.

## آیا پلن رایگان جای Docker را می‌گیرد؟

برای داشبورد، API سبک و هماهنگی کارهای کوتاه/رویدادمحور: تا حد زیادی بله. برای اجرای همان Paperclip و n8n فعلی به‌صورت کانتینرهای دائمی: خیر. Workers/Pages میزبان عمومی فرانت و API هستند؛ Workers Workflows و Queues می‌توانند کارهای مرحله‌ای و صف را مدیریت کنند؛ D1 یا SQLite-backed Durable Objects وضعیت کوچک و رویدادهای پالایش‌شده را نگه می‌دارند. هیچ‌کدام به‌تنهایی معادل Docker host دائمی با دیتابیس‌ها، فایل‌سیستم و محیط اجرایی Paperclip/n8n نیستند.

Workers Containers طبق مستندات Cloudflare فقط در Workers Paid ارائه می‌شود؛ Free برای این مسیر Container، CPU، حافظه و دیسک تخصیص نمی‌دهد. حتی با Containers، اجرای همیشگی سرویس‌ها و نگهداری وضعیت Paperclip باید جداگانه از نظر هزینه، حجم دیسک و مدل اجرای sleep/scale-to-zero ارزیابی شود. ارزان‌ترین طرح ترکیبی فعلی: داشبورد استاتیک روی Workers/Pages، API محافظت‌شده برای دادهٔ پالایش‌شده، اجرای Paperclip/n8n روی میزبان Docker و اتصال فقط از راه Cloudflare Tunnel + Access؛ این طرح همچنان به میزبان روشن نیاز دارد.

### سقف‌های پلن رایگان که در طراحی باید رعایت شوند

| قابلیت | محدودیت درج‌شده در مستندات فعلی | اثر بر فاران |
|---|---:|---|
| Workers | ۱۰۰٬۰۰۰ درخواست در روز، ۱۰ ms CPU در هر درخواست، ۵۰ subrequest، ۱۲۸ MB حافظه، ۵ Cron Trigger در هر حساب | برای API سبک کافی، برای تبدیل Worker به اجرای پردازشی/agent runtime مناسب نیست. |
| Pages Functions | درخواست‌ها در سهمیهٔ Workers شمرده می‌شوند؛ فایل‌های استاتیک رایگان و نامحدود هستند. | صفحات داشبورد ارزان؛ backend را برای عبور از سهمیه fail-closed تنظیم کنیم. |
| Cron | ۱۰ ms CPU برای هر فراخوانی Free، حداکثر wall time زمان‌بندی‌شده ۱۵ دقیقه طبق limits | فقط پایش/dispatch سبک و محدود؛ نه session طولانی agent. |
| Workers Workflows | موجود در Free؛ ۳٬۰۰۰ step/day، ۱ GB-month state، ۱۰ ms CPU/invocation؛ وضعیت پیش‌فرض Free سه روز نگه‌داری می‌شود. | برای orchestration کوتاه، retry کنترل‌شده و human approval مناسب؛ step و storage سهمیه دارند. |
| Queues | ۱۰٬۰۰۰ operation/day، ماندگاری پیام ۲۴ ساعت در Free | صف رویدادهای سبک؛ برای backlog طولانی یا audit archive کافی نیست. |
| SQLite Durable Objects | ۱۰۰٬۰۰۰ درخواست/day، ۱۳٬۰۰۰ GB-s/day، ۵ GB storage، تا ۱۰۰٬۰۰۰ write/day | مناسب وضعیت زندهٔ کوچک/هماهنگی؛ event history کامل را در آن نگه نداریم. |
| Containers | Free در دسترس نیست؛ Workers Paid شامل اعتبار پایه است و مصرف اضافه هزینه دارد. | برای اجرای واقعی کانتینر و ابزارهای لینوکسی، پلن رایگان کافی نیست. |

**جمع‌بندی Cloudflare:** با Free می‌شود داشبورد و control-plane نمایشی/رویدادمحور را بالا آورد و یک نمونهٔ سبک از workflowهای فاران ساخت؛ نمی‌توان بدون میزبان دیگری، Docker فعلی، n8n و Paperclip را با حفظ رفتار و ماندگاری‌شان جایگزین کرد. برای ۲۴/۷ واقعی، به origin همیشه‌روشن نیاز است. Cloudflare Tunnel فقط origin را امن route می‌کند و میزبان ایجاد نمی‌کند.

## مخزن‌های پیشنهادی کاربر

| مخزن و منبع بررسی‌شده | مجوز/سازگاری/نگه‌داری | ارزش محتمل | تصمیم امنیتی و کاری |
|---|---|---|---|
| [N1nEmAn/sapper-v2](https://github.com/N1nEmAn/sapper-v2), README, MIT link, disclaimer link, Docker/Kali quick start, competition environment notes | MIT به‌همراه disclaimer مستقل. خودش pentest legion رقابتی با coordinator/worker/watchdog چندایجنتی است؛ README می‌گوید endpoint محیط مسابقه (`BENCHMARK_BASE_URL`) اجباری است و بیرون آن باید interface سازگار ساخت. Docker image تبلیغ‌شده حدود ۱٫۲ GB و Kali toolchain دارد. ادعاهای برد مسابقه، ارزیابی مستقل این پروژه نیستند. در این بررسی commit hash/نسخهٔ release از API GitHub تثبیت نشد. | می‌تواند ایده‌های تقسیم نقش، handoff، memory و post-mortem برای یک محیط آزمایشگاهیِ مجاز بدهد؛ خودش معماری مناسب بهره‌برداری از دانشگاه نیست. | **به Paperclip وصل یا اجرا نمی‌کنم.** این repo ابزار و harness تهاجمی چندایجنتی است. فقط می‌توان ایده‌های غیرتهاجمی را پس از بازبینی کد/مجوز وابستگی‌ها در CTF محلیِ ایزوله و مجاز یا برای شبیه‌سازی دفاعی بررسی کرد. هیچ target اینترنتی/سازمانی به آن ندهیم. |
| [alishahryar1/free-claude-code](https://github.com/alishahryar1/free-claude-code), GitHub README/license | `AGPL-3.0-only`; چند harness/model/provider را از proxy محلی عبور می‌دهد. README صراحتاً می‌گوید سهمیهٔ رایگان هر provider متغیر است و تابع Terms همان provider است. دستورات quick start کد نصب دوردست را در PowerShell اجرا می‌کنند؛ اینجا اجرا نشده‌اند. در این بررسی commit hash تثبیت نشد. | ممکن است برای توسعهٔ محلی، انتخاب providerهای متعدد و adapterهای سازگار کمک کند؛ orchestration اصلی ما را جایگزین نمی‌کند. | **برای runtime دانشگاه استفاده نشود فعلاً.** providerها، OAuth، proxy-auth و قوانین استفاده/حریم خصوصی باید جدا بررسی شوند؛ tokenهای دانشجو/پروژه نباید از proxy نامعلوم عبور کنند. AGPL برای ادغام/ارائهٔ شبکه‌ای نیازمند بررسی مجوز است. |
| [kalil0321/reverse-api-engineer](https://github.com/kalil0321/reverse-api-engineer), README, installation and license sections | MIT؛ 594 commits در نمای GitHub هنگام بررسی و README سازگاری Python 3.11+ را می‌گوید. Agent mode می‌خواهد traffic را از مرورگر بگیرد و از HAR برای ساخت typed client استفاده کند؛ manual mode Playwright دارد. API key مدل در agent mode لازم است. | برای سامانه‌ای که فقط API را از traffic وب می‌شود شناخت، ساخت client اولیه را سریع می‌کند. | **برای Paperclip/n8n کاربردی نیست** چون API رسمی/OpenAPI خود سرویس را داریم؛ برای سایت ثالث فقط با اجازهٔ روشن مالک و HAR پاک‌سازی‌شده، چون cookie، token و دادهٔ شخصی ممکن است داخل HAR باشد. نصب نشده است. |

منبع اصلیِ بررسی هر مخزن، صفحهٔ GitHub و README/license همان مخزن بود. ستاره‌ها، ادعاهای عملکرد و badgeها به‌عنوان شواهد کیفیت/امنیت تلقی نشده‌اند. نسخه/commit دقیق برای دو مخزن اول از صفحهٔ قابل دسترس تأیید نشد؛ به همین دلیل dependency جدیدی pin یا نصب نشده است.

## طرح محصول داشبورد و workflow canvas

نمودار اجرای دقیق باید از n8n بماند تا node status واقعی حفظ شود. برای تجربهٔ جامع شبیه editor، داشبورد فاران می‌تواند یک canvas مدیریتی React Flow بسازد که Agent، Department، Workflow، Trigger، Approval، Task و Connector را نشان دهد؛ هر run node از APIهای n8n/Paperclip خوانده و به detail بومی همان سامانه لینک شود. این canvas تا زمان اتصال API read-only است؛ تغییر workflow، فعال‌سازی trigger، approve agent، wakeup، اجرای ابزار امنیتی یا dispatch مدل پشت gate تأیید انسانی می‌ماند.

### تصمیم reuse برای canvas

| گزینهٔ بررسی‌شده | منبع/نسخهٔ مشاهده‌شده | مجوز، runtime و نگه‌داری | تصمیم |
|---|---|---|---|
| n8n editor | نمونهٔ محلی n8n 2.46.4 و workflow/executionهای واقعی همین مخزن | رابط رسمی و node status واقعی را دارد؛ صفحهٔ اجرا را از بیرون با auth نشان می‌دهد؛ n8n با Sustainable Use License است. | مرجع دقیق مشاهدهٔ run و execution بماند؛ Faran آن را clone نکند. |
| React Flow از xyflow | مخزن رسمی `https://github.com/xyflow/xyflow`, README و صفحهٔ package، نسخهٔ `@xyflow/react 13.0.2` دیده‌شده در npm در 2026-11-23 | MIT، React/TypeScript، Node >=20؛ نگه‌داری فعال در GitHub با update مورخ 2026-11-10. اپ فعلی Vanilla JS/PWA است و React/Vite ندارد؛ استفاده نیازمند build step مستقل و اضافه‌کردن React است. | گزینهٔ برگزیده برای **نقشهٔ مدیریتی و رابطهٔ کل سیستم**، نه جعل اجرای n8n. ابتدا dependency/security review و build بررسی، سپس pin دقیق و import با lockfile. |
| custom DOM/SVG canvas | کد فعلی Faran | بدون dependency، اما باید drag, zoom, keyboard navigation, minimap, layout, handles, viewport و accessibility را خودمان بسازیم. | رد: قابلیت تکراری نسبت به کتابخانهٔ maintained و هزینهٔ نگه‌داری بی‌دلیل. |

**جهت طراحی:** ابزار عملیات دانشگاهی روزانه برای مدیران/ارزیاب‌ها؛ فضای کم‌ازدحام، دقیق و data-dense با Persian RTL، منوی کناری پایدار، نوار وضعیت اتصال، مرکز canvas و پنل inspector راست/چپ متناسب RTL. accent محدود به سبز فاران و رنگ وضعیت؛ بدون نمای قهرمان/کارت‌های تزئینی. target: desktop 1440×900 برای ویرایش/inspect، تبلت 768×1024 برای انتخاب عامل، موبایل 390×844 فقط مرور و تاییدهای کم‌خطر. Interactionهای canvas keyboard reachable و touch target ≥44 px.

**مسیر و حالت‌ها:** (۱) سازمان/دپارتمان → انتخاب ایجنت → skill/evidence/permission در inspector؛ (۲) انتخاب workflow → گراف → اجرای انتخابی → native n8n execution؛ (۳) task → Paperclip issue → runهای فعال/تاریخی → ارزیابی/گزارش؛ (۴) پیشنهاد ارزیاب → شواهد و confidence → ارسال برای بازبینی انسانی. Loading: اسکلت canvas و آخرین زمان داده؛ Empty: node group نمونه و دکمهٔ import docs، نه «موفق» ساختگی؛ Error/stale: زمان آخرین نمونه، منبع down و retry؛ Partial: Paperclip/n8n هرکدام status مستقل؛ Permission: پنهان‌کردن token و controlهای ممنوع. Local mock mode را از connected runtime جدا و با label همیشگی نشان دهیم.

فازهای محصول: (۱) design system و RTL dashboard responsive، (۲) API backend با auth و role policy، (۳) adapterهای Paperclip/n8n server-side و event stream، (۴) canvas و drill-down روی اجرای واقعی، (۵) ارزیابی/گزارش روند و پیش‌بینی با provenance، (۶) deploy روی Free با dataهای synthetic و مشاهدهٔ سهمیه، (۷) انتقال runtime به میزبان ماندگار فقط وقتی منبع هزینه/میزبان مشخص شد. موبایل PWA همان پنل مانیتورینگ است؛ dispatch حساس از موبایل نیز به تأیید و audit trail نیاز دارد.

## منابع اولیهٔ Cloudflare که بررسی شدند

- Workers limits/pricing: https://developers.cloudflare.com/workers/platform/limits/ و https://developers.cloudflare.com/workers/platform/pricing/
- Workflows overview/pricing/limits: https://developers.cloudflare.com/workflows/ ، https://developers.cloudflare.com/workflows/reference/pricing/ ، https://developers.cloudflare.com/workflows/reference/limits/
- Pages Functions: https://developers.cloudflare.com/pages/functions/pricing/ و https://developers.cloudflare.com/pages/platform/limits/
- Queues: https://developers.cloudflare.com/queues/platform/pricing/ و https://developers.cloudflare.com/queues/platform/limits/
- Durable Objects: https://developers.cloudflare.com/durable-objects/platform/pricing/
- Containers: https://developers.cloudflare.com/containers/ و https://developers.cloudflare.com/containers/platform/pricing/
