"""Render the public Faran directory with no network or build dependencies."""
from html import escape
from pathlib import Path

from studio_layout import render_home

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = "https://faran.ac.ir/"
GITHUB = "https://github.com/maddixmhn/faran"
MAP = "/topology/index.html?design=faran-official-structure"
PROGRAMS = OFFICIAL + "عنوان-رشتهها/"
LMS = "https://faranlms.com/"
TEACHERS = OFFICIAL + "teachers-portal/"
REGULATIONS = OFFICIAL + "آیین-نامه-و-مقررات/"
TUITION = OFFICIAL + "jadval-shahrieh/"
VIDEOS = OFFICIAL + "video-1403/"
CONTACT = OFFICIAL + "contact-us/"
ASSOCIATIONS = {"law": "law-ass/", "engineering": "regs-engineering/", "languages": "regi-language/", "social": "reg-social/", "economics": "regs-accounting/", "management": "reg-management/"}
LIBRARY = OFFICIAL + "digital-library/"

def route(slug):
    return f"/university/{slug}.html"

# Faculty names and degree groups follow the public academic navigation.
faculties = {
    "law": ("حقوق", "حقوق", "حقوق خصوصی، حقوق بین‌الملل، حقوق جزا و جرم‌شناسی"),
    "languages": ("زبان‌های خارجی", "آموزش زبان انگلیسی، مترجمی زبان انگلیسی، مترجمی زبان انگلیسی (ناپیوسته)", "آموزش زبان انگلیسی"),
    "engineering": ("مهندسی", "مهندسی کامپیوتر، مهندسی حرفه‌ای کامپیوتر نرم‌افزار (ناپیوسته)", "شبکه‌های کامپیوتری، تجارت الکترونیکی، یادگیری الکترونیکی"),
    "economics": ("اقتصاد و حسابداری", "اقتصاد، حسابداری، حسابداری (ناپیوسته)", "حسابداری، اقتصاد انرژی"),
    "management": ("مدیریت", "مدیریت امور بانکی، مدیریت بازرگانی، مدیریت صنعتی، مدیریت کسب‌وکار، مدیریت مالی", "مدیریت بازرگانی (کارآفرینی)، مدیریت تکنولوژی (انتقال تکنولوژی)، مدیریت فناوری (همکاری‌ها و انتقال فناوری)"),
    "social": ("خدمات اجتماعی", "مددکاری اجتماعی", ""),
}

def item(name, description, url):
    return name, description, url

pages = {
    "about": ("دربارهٔ فاران", "معرفی مؤسسهٔ آموزش عالی فاران مهر دانش و مسیرهای دسترسی به ساختار سازمانی آن.",
        [item("معرفی مؤسسه", "پیشینه و مأموریت آموزش مجازی در معرفی منتشرشدهٔ فاران.", OFFICIAL + "faran/"),
         item("چارت سازمانی", "بررسی واحدهای آموزش، پژوهش، اداری و مالی، فناوری و امور دانشجویی.", MAP),
         item("تصویر رسمی چارت", "تصویر منتشرشده توسط مؤسسه، مرجع بازخوانی ساختار.", OFFICIAL + "faran-chart/"),
         item("ریاست مؤسسه", "صفحهٔ رسمی ریاست مؤسسه و معرفی مسئولیت آن.", OFFICIAL + "hi/")]),
    "admissions": ("راهنمای پذیرش", "مقطع را انتخاب کنید و شرایط، مدارک و مهلت ثبت‌نام را از اطلاعیهٔ همان ورودی بخوانید.",
        [item("کارشناسی پیوسته", "راهنمای ثبت‌نام ورودی‌های کارشناسی پیوسته.", OFFICIAL + "karshenasi-peyvasteh/"),
         item("کارشناسی ناپیوسته", "راهنمای ثبت‌نام ورودی‌های کارشناسی ناپیوسته.", OFFICIAL + "karshenasi-napeyvasteh/"),
         item("کارشناسی ارشد", "راهنمای ثبت‌نام ورودی‌های تحصیلات تکمیلی.", OFFICIAL + "karshenasi-arshad/"),
         item("فهرست رسمی رشته‌ها", "عناوین منتشرشده از سوی مؤسسه.", PROGRAMS),
         item("اطلاعیه‌های مؤسسه", "مهلت‌ها و جزئیات اعلام‌شده برای هر ورودی.", OFFICIAL)]),
    "education": ("آموزش", "مسیرهای انتخاب واحد، کلاس مجازی، امتحان و پیگیری امور آموزشی از آغاز تا پایان نیمسال.",
        [item("پرتال آموزشی دانشجویان", "ورود برای دسترسی به کلاس‌ها و خدمات آموزشی حساب دانشجو.", LMS),
         item("آیین‌نامه و مقررات", "مقررات آموزشی و مدارک مرجع مؤسسه.", REGULATIONS),
         item("تقویم و اطلاعیه‌ها", "به‌روزترین زمان‌بندی منتشرشده در صفحهٔ اصلی مؤسسه.", OFFICIAL),
         item("آموزش شرکت در آزمون", "آموزش منتشرشده برای شرکت در آزمون مجازی.", OFFICIAL + "amnazmoon"),
         item("پرسش‌های کارشناسی", "پاسخ‌های مؤسسه دربارهٔ امور آموزشی دورهٔ کارشناسی.", OFFICIAL + "shareholder-faq/"),
         item("پرسش‌های کارشناسی ارشد", "پاسخ‌های مؤسسه دربارهٔ تحصیلات تکمیلی و وضعیت آموزشی.", OFFICIAL + "سوالات-متداول-کارشناسی/")]),
    "finance": ("امور اداری و مالی", "مرجع مشاهدهٔ جدول شهریه و پیگیری پرسش‌های مالی از مؤسسه.",
        [item("جدول شهریه", "جدول منتشرشدهٔ شهریه و مدارک مالی مرتبط با دوره‌های تحصیلی.", TUITION),
         item("پرتال آموزشی", "برای مشاهدهٔ خدمات حساب دانشجویی وارد سامانهٔ رسمی شوید.", LMS),
         item("ارتباط با مؤسسه", "برای پیگیری جزئیات پرداخت یا وضعیت پرونده با مرجع مؤسسه تماس بگیرید.", route("contact"))]),
    "research": ("پژوهش و کتابخانه", "دسترسی به معاونت پژوهشی، منابع کتابخانه‌ای و اطلاعات همایش‌ها.",
        [item("معاونت پژوهشی", "صفحهٔ معرفی معاونت در سایت مؤسسه.", OFFICIAL + "r-assistant/"),
         item("کتابخانهٔ دیجیتال", "منابع و راه‌های دسترسی مندرج در راهنمای کتابخانه.", LIBRARY),
         item("همایش‌ها", "فراخوان و اطلاع‌رسانی همایش‌های مؤسسه.", OFFICIAL + "همایش/"),
         item("گزارش پژوهشی پروژهٔ سمینار", "مقاله و شواهد آزمایش این پروژهٔ درسی.", route("project"))]),
    "student-services": ("خدمات دانشجویی", "برای دریافت کارت دانشجویی، کلاس مجازی و راهنمای کار با سامانه از این مسیرها استفاده کنید.",
        [item("کارت دانشجویی", "فرم و دستورالعمل رسمی درخواست کارت.", OFFICIAL + "stu-form/"),
         item("سامانهٔ آموزش مجازی", "کلاس‌ها و خدمات آموزشی دانشجویان.", LMS),
         item("ویدئوهای آموزشی", "راهنمای تصویری خدمات و سامانه‌های مؤسسه.", VIDEOS),
         item("انجمن‌های علمی", "در صفحهٔ هر دانشکده، پیوند انجمن علمی همان حوزه آمده است.", route("faculties")),
         item("آموزش و پرسش‌های متداول", "مقررات، آزمون و پیگیری آموزشی در طول نیمسال.", route("education"))]),
    "technology": ("فناوری و آموزش مجازی", "پرتال‌های آموزشی دانشجویان و استادان و راهنمای استفاده از کلاس مجازی.",
        [item("پرتال دانشجویان", "سامانهٔ رسمی ورود دانشجویان.", LMS),
         item("پرتال استادان", "خدمات آموزشی اعضای هیئت علمی و مدرسان.", TEACHERS),
         item("رزرو زمان کلاس استادان", "سامانهٔ رزرو زمان از منوی مؤسسه.", OFFICIAL + "ocr/"),
         item("راهنمای سامانه", "ویدئوهای آموزشی منتشرشده برای کار با خدمات مجازی.", VIDEOS)]),
    "contact": ("تماس با فاران", "برای اطلاعات تماس به صفحهٔ رسمی مؤسسه مراجعه کنید.",
        [item("راه‌های تماس", "نشانی، شماره‌ها و کانال‌های معرفی‌شده از سوی مؤسسه.", CONTACT),
         item("اطلاعیه‌ها", "اخبار، زمان‌بندی‌ها و راه‌های تماس در صفحهٔ اصلی مؤسسه.", OFFICIAL),
         item("راهنمای مراجعه", "انتخاب مسیر متناسب با موضوع آموزش، پذیرش یا امور مالی.", "/#services")]),
    "project": ("پروژهٔ دانشگاه دیجیتال", "ارائهٔ درس سمینار، دانشجو محمد مهرانی، استاد دکتر سعید شکراللهی. داشبورد پژوهشی عملکرد چند فرایند آموزشی را در محیط آزمایشی نمایش می‌دهد.",
        [item("صفحهٔ ارائهٔ سمینار", "فرمول‌ها، کد، نتیجه و جزوهٔ آمادهٔ دفاع.", "/docs/presentation.html"),
         item("داشبورد آزمایشی", "مشاهدهٔ گردش‌کارها و شواهد ثبت‌نام در محیط نمونه.", "/dashboard.html"),
         item("مقالهٔ سمینار", "مسئله، معماری، روش آزمایش، نتایج و منابع.", "/docs/article.html"),
         item("دانلود گزارش سمینار", "نسخهٔ صفحه‌بندی‌شدهٔ گزارش و پیوست‌ها (PDF).", "/docs/faran-seminar.pdf"),
         item("ارائهٔ سمینار", "نسخهٔ وب گزارش و مستندات ارائه.", "/docs/seminar.html"),
         item("مدیریت نیمسال", "فرایندها و شواهد الکترونیکی سناریوی آموزشی.", "/docs/semester-web.html"),
         item("نقشهٔ زیرساخت آزمایش", "نقشهٔ سرویس‌ها و ارتباط میان مؤلفه‌ها.", "/topology/index.html?design=faran-infrastructure"),
         item("ورود به نمونهٔ آزمایشی", "دسترسی به پنل محلی پروژه با حساب نمونه.", "/login.html"),
         item("پروژهٔ ارزیابی سیستم", "پروژهٔ درس ارزیابی کارایی سیستم‌های کامپیوتری، استاد دکتر علی سلیمانی.", "https://dr-soleimani-evaluator.vercel.app/"),
         item("مخزن پروژه", "کد، مستندات و راهنمای راه‌اندازی فارسی.", GITHUB)]),
}

faculty_cards = [item(name, undergraduate, route(slug))
                 for slug, (name, undergraduate, _) in faculties.items()]
pages["faculties"] = ("دانشکده‌ها", "رشته‌ها بر اساس گروه‌بندی منتشرشدهٔ مؤسسه آمده‌اند. برای ظرفیت و پذیرش سال جاری، اطلاعیهٔ همان ورودی را بخوانید.", faculty_cards)
for slug, (name, undergraduate, graduate) in faculties.items():
    details = [item("فهرست رسمی رشته‌ها", "عنوان رشته و مقطع را در مرجع مؤسسه بررسی کنید.", PROGRAMS),
               item("پذیرش و ثبت‌نام", "اطلاعیه‌های ورودی به تفکیک مقطع.", route("admissions")),
               item("انجمن علمی", "صفحهٔ انجمن این حوزه در پایگاه مؤسسه.", OFFICIAL + ASSOCIATIONS[slug]),
               item("آیین‌نامه و مقررات", "شرایط عمومی و منابع مرتبط با آموزش.", REGULATIONS)]
    pages[slug] = (name, "رشته‌های این گروه در منوی رسمی فاران به تفکیک مقطع درج شده‌اند.", details)

NAV = [("خانه", "/"), ("دربارهٔ فاران", route("about")), ("دانشکده‌ها", route("faculties")),
       ("پذیرش", route("admissions")), ("آموزش", route("education")),
       ("پژوهش", route("research")), ("خدمات دانشجویی", route("student-services")),
       ("تماس", route("contact"))]

def link(name, url, attrs=""):
    return f'<a href="{escape(url, quote=True)}"{attrs}>{escape(name)}</a>'

def cards(items, grouped=False):
    parts = []
    for name, description, url in items:
        external = url.startswith("https://")
        caption = "مرجع بیرونی" if external else "مشاهده"
        parts.append(f'<li><a class="service" href="{escape(url, quote=True)}">'
                     f'<strong>{escape(name)}</strong><span>{escape(description)}</span>'
                     f'<small>{caption} <span aria-hidden="true">{"↗" if external else "←"}</span></small></a></li>')
    return f'<ul class="cards {"grouped" if grouped else ""}">{"".join(parts)}</ul>'

def frame(title, intro, current, body):
    menu = "".join(link(name, url, ' aria-current="page"' if url == current else "") for name, url in NAV)
    return f'''<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} | درگاه فاران</title>
<meta name="description" content="{escape(intro, quote=True)}">
<meta name="theme-color" content="#102d3b">
<link rel="icon" href="/icon.svg">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="stylesheet" href="/university.css">
</head>
<body><a class="skip" href="#main">رفتن به محتوا</a>
<header>
  <div class="utilities"><div class="wrap">
    {link("سایت رسمی مؤسسه ↗", OFFICIAL)}{link("پرتال دانشجویان ↗", LMS)}{link("پرتال استادان ↗", TEACHERS)}
  </div></div>
  <div class="wrap identity-nav">
    <a class="identity" href="/"><img src="/topology/brand/faran-reference.webp" width="48" height="48" alt="">
      <span><strong>درگاه دانشگاهی فاران</strong><small>پروژهٔ آموزشی بر پایهٔ ساختار فاران مهر دانش</small></span>
    </a>
    <nav aria-label="منوی اصلی">{menu}</nav>
  </div>
</header>
<main id="main" tabindex="-1">{body}</main>
<footer><div class="wrap footer-row"><div><strong>درگاه دانشگاهی فاران</strong><p>پروژهٔ درس سمینار · محمد مهرانی</p></div>
  <nav aria-label="پیوندهای پایین صفحه">{link("صفحهٔ پروژه", route("project"))}{link("نمودار سازمانی", MAP)}{link("سایت رسمی مؤسسه ↗", OFFICIAL)}{link("گیت‌هاب ↗", GITHUB)}</nav>
</div><div class="publisher-credit" dir="ltr" style="grid-column:1/-1;flex:1 0 100%;text-align:center;padding:.5rem .75rem;font-size:.875rem"><bdi lang="en" dir="ltr">Powered by</bdi> <a href="https://github.com/maddixmhn" rel="me" style="color:inherit;text-decoration:underline"><bdi dir="rtl">محمد مهرانی</bdi></a></div></footer>
<script>if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(() => {{}});</script>
</body></html>
'''

def page(slug, title, intro, items):
    current = route(slug)
    faculty_ancestor = link("دانشکده‌ها", route("faculties")) + "<span>/</span>" if slug in faculties else ""
    degree_list = ""
    if slug in faculties:
        _, undergraduate, graduate = faculties[slug]
        degree_list = f'<div class="degree"><h2>کارشناسی</h2><p>{escape(undergraduate)}</p>'
        if graduate:
            degree_list += f'<h2>کارشناسی ارشد</h2><p>{escape(graduate)}</p>'
        degree_list += '</div>'
    body = f'''
    <section class="page-intro"><div class="wrap">
      <nav class="trail" aria-label="مسیر صفحه">{link("خانه", "/")}<span>/</span>{faculty_ancestor}<span aria-current="page">{escape(title)}</span></nav>
      <h1>{escape(title)}</h1><p>{escape(intro)}</p>
    </div></section>
    <section class="wrap shelf">{degree_list}<h2>{"دانشکده‌ها و گروه‌ها" if slug == "faculties" else "پیوندهای مرتبط"}</h2>{cards(items, slug == "faculties")}</section>
    '''
    return frame(title, intro, route("faculties") if slug in faculties else current, body)

def main():
    (ROOT / "university").mkdir(exist_ok=True)
    (ROOT / "index.html").write_text(render_home(), encoding="utf-8")
    for slug, (title, intro, items) in pages.items():
        (ROOT / "university" / f"{slug}.html").write_text(page(slug, title, intro, items), encoding="utf-8")
    print(f"Rendered {len(pages) + 1} public university pages.")

if __name__ == "__main__":
    main()
