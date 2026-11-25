"""Render the seminar manuscript and its compact evidence appendix as an A4 PDF."""

from collections import Counter
from pathlib import Path
from statistics import median
from tempfile import TemporaryDirectory
import argparse
import html
import json
import os
import re

from pypdf import PdfReader
from markdown_it import MarkdownIt
from playwright.sync_api import sync_playwright
from article_figures import FARAN, figure_links

DOCS = Path(__file__).resolve().parents[1] / "docs"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
REFERENCES = [
    ("Little, J. D. C. (1961). A Proof for the Queuing Formula L = λW. Operations Research 9(3), 383–387.",
     "https://doi.org/10.1287/opre.9.3.383"),
    ("Lamport, L. (1978). Time, Clocks, and the Ordering of Events in a Distributed System. Communications of the ACM 21(7), 558–565.",
     "https://lamport.org/pubs/time-clocks.pdf"),
    ("Van der Aalst, W. et al. (2012). Process Mining Manifesto. Business Process Management Workshops, LNCS 773, 169–194.",
     "https://doi.org/10.1007/978-3-642-28108-2_19"),
    ("Ewaschuk, R. (2016). Monitoring Distributed Systems. In Site Reliability Engineering.",
     "https://sre.google/sre-book/monitoring-distributed-systems/"),
    ("n8n Docs. Configuring queue mode.",
     "https://docs.n8n.io/hosting/scaling/queue-mode/"),
    ("Moodle Developer Resources. Enrolment API.",
     "https://moodledev.io/docs/5.0/apis/subsystems/enrol"),
    ("PostgreSQL documentation. Explicit Locking.",
     "https://www.postgresql.org/docs/current/explicit-locking.html"),
    ("Pouzor. (2026). Homelable v3.8.0. MIT-licensed software.",
     "https://github.com/Pouzor/homelable/tree/v3.8.0"),
]
IMAGE_NAMES = (
    ("service-graph.svg", "معماری ثبت‌نام و مرز مسئولیت سرویس‌ها"),
    ("semester-workflow.svg", "بازترسیم پنج گره از تعریف گردش‌کار نیمسال"),
    ("paperclip-console.png", "نمای مستقیم چهار نقش مدیریتی آزمایشی در Paperclip"),
    ("n8n-execution-19.jpg", "نمای مستقیم اجرای ۱۹ در n8n با وضعیت موفق و زمان ۸٫۳۲۴ ثانیه"),
    ("docker-desktop.jpg", "نمای مستقیم کانتینرهای روشن در Docker Desktop هنگام ثبت تصویر"),
    ("execution-evidence.png", "گزارش خروجی اجرای ۲۰۱۲ و تأیید عضویت فعال در درس ۴"),
    ("homelable-infrastructure.jpg", "نقشهٔ وابستگی سرویس‌ها در ویرایشگر مستقل Homelable [۸]"),
    ("verified-organization.jpg", "نمای عمومی چارت رسمی فاران، بازبینی ۲۵ نوامبر ۲۰۲۶"),
    ("verified-evaluation-lab.jpg", "آزمایشگاه عمومی هنگام محاسبه از رد اجرای ثبت‌نام"),
)
STYLE = """
@page {
  size:A4; margin:19mm 17mm 20mm;
  @bottom-center { content:"فاران · " counter(page) " / " counter(pages); font:9pt Tahoma,sans-serif; color:#395951 }
}
* { box-sizing:border-box }
body { margin:0; font:11pt/1.9 Tahoma,Arial,sans-serif; color:#182e29 }
p { margin:0 0 .72em; orphans:3; widows:3 }
h1 { font-size:23pt; line-height:1.5; margin:.25em 0 .5em }
h2 { font-size:15pt; line-height:1.6; margin:1.2em 0 .35em; border-bottom:1px solid #87a69b;
     break-after:avoid }
h3 { font-size:12pt; margin:1em 0 .3em; break-after:avoid }
a { color:#185c49; overflow-wrap:anywhere }
.byline { color:#395951; margin:0 0 1.25em; font-size:10.5pt }
ol { padding-inline-start:1.4em }
li { margin-block:.35em }
figure { margin:10pt auto; break-inside:avoid; text-align:center }
figure img { display:block; margin:auto; max-width:100%; max-height:115mm }
figcaption { font-size:9.5pt; margin-top:4pt }
table { border-collapse:collapse; width:100%; font-size:9pt; line-height:1.5; margin:.6em 0 1em }
thead { display:table-header-group }
tr { break-inside:avoid }
td,th { border:1px solid #b2c5bf; text-align:start; padding:4px 5px; vertical-align:top }
th { background:#e8f0ed }
tbody tr:nth-child(even) { background:#f6faf8 }
.bar { background:#d7eee5; border-inline-start:3px solid #176750; min-width:2%; height:11px; margin-block:2px }
.annex { break-before:page }
.role-ledger td { padding-block:6pt; font-size:10pt; }
.role-ledger .prefixes bdi { overflow-wrap:anywhere; }
@media screen { body{max-width:820px;margin:auto;padding:18px} }
"""

def escape(value):
    return html.escape(str(value))

def table(headers, rows):
    head = "".join(f"<th scope='col'>{escape(label)}</th>" for label in headers)
    body = "".join(
        "<tr>" + "".join(f"<td><bdi>{escape(value)}</bdi></td>" for value in row) + "</tr>"
        for row in rows
    )
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"

def manuscript():
    source = (DOCS / "SEMINAR-MANUSCRIPT.md").read_text(encoding="utf-8-sig")
    intro, *chapters = re.split(r"^## ", source, flags=re.M)
    heading, *metadata = intro.strip().splitlines()
    byline = " · ".join(line.replace("**", "").strip() for line in metadata if line.strip())
    result = [f"<h1>{escape(heading[2:])}</h1><p class='byline'>{escape(byline)}</p>"]
    for chapter in chapters:
        title, _, body = chapter.partition("\n")
        result.append(f"<h2>{escape(title.strip())}</h2>")
        for paragraph in re.split(r"\n\s*\n", body.strip()):
            result.append(f"<p>{escape(paragraph.replace('**',''))}</p>")
    return "".join(result)

def result_tables(evidence):
    roster = evidence["roster"]
    workers = evidence["worker_audit"]
    queue = evidence["queue"]
    stages = evidence["trace"]["stages"]
    race = evidence["race"]
    majors = Counter(row["major"] for row in roster)
    verified = Counter(row["major"] for row in roster if row["membership_verified"])
    managers = {"ceo":"مدیریت ارشد", "pm":"آموزش", "cto":"فناوری اطلاعات", "engineer":"مهندسی کامپیوتر"}
    out = ["<h2>جدول‌های نتایج و شواهد محاسبات</h2>",
           "<h3>تطبیق عضویت آزمایشی بر حسب رشته</h3>",
           table(["رشته","پرونده در برنامه","عضویت گروه تأییدشده"],
                 [(major, count, verified[major]) for major, count in majors.items()]),
           "<p>تأیید عضویت از بازخوانی گروه و وضعیت فعال در Moodle به دست آمد. شناسه‌های پروندهٔ ساختگی و رسیدهای تطبیق در پیوست آمده‌اند.</p>",
           "<h3>بازخوانی مستقل اجرای دسته‌ای از PostgreSQL</h3>",
           table(["سنجه","مقدار"],[
             ("گردش‌کار در نمونهٔ آزمایشی n8n",workers["workflow"]),
             ("بازهٔ شناسهٔ اجرا",f"{workers['first_execution']}–{workers['last_execution']}"),
             ("ردیف موفق مستقل در پایگاه داده",workers["successful_db_rows"]),
             ("شناسهٔ اجرا منطبق با دفتر",workers["matched_ledger_rows"]),
             ("شناسهٔ نقش متمایز در دفتر",workers["unique_roles"])]),
           table(["شاخهٔ مدیریتی","نقش بررسی‌شده"],
                 [(managers[key], count) for key,count in workers["managers"].items()]),
           "<h3>تجزیهٔ زمانی اجرای ۲۰</h3>",
           table(["مرحله","تحویل تا شروع (ms)","خدمت (ms)"],
                 [(s["name"],s["wait_ms"],s["service_ms"]) for s in stages]),
           "<p>فاصله‌های تحویل بین مراحل در جدول بالا نیامده‌اند. با افزودن ۲۳۵۶ و ۱۹۴ میلی‌ثانیه، جمع زمان سرتاسری به ۲۸۶۳۳ میلی‌ثانیه می‌رسد.</p>",
           "<h3>مشاهدات مقایسهٔ مسیرهای اجرا</h3>",
           table(["مسیر","شناسهٔ اجرا","تا نخستین گره (ms)","صف Redis (ms)","Moodle (ms)","عضو نمونه"],
                 [(r["mode"],r["execution"],r["dispatch_ms"],
                   "—" if r["redis_queue_ms"] is None else r["redis_queue_ms"],r["moodle_ms"],
                   "گرم‌کردن" if r["trace"]==queue["excluded_warmup"] else "تحلیل")
                  for r in queue["registrations"]])]
    modes = []
    for mode in ("cli","worker"):
        values = [r["dispatch_ms"] for r in queue["registrations"]
                  if r["mode"] == mode and r["trace"] != queue["excluded_warmup"]]
        modes.append((mode,min(values),median(values),max(values)))
    out += [table(["مسیر","کمینه (ms)","میانه (ms)","بیشینه (ms)"],modes),
            "<figure><div>",
            "".join(f'<div><bdi>{escape(mode)} · {middle:,} ms</bdi>'
                    f'<div class="bar" style="width:{100*middle/max(middle_value for _, _, middle_value, _ in modes):.2f}%"></div></div>'
                    for mode,_,middle,_ in modes),
            "</div><figcaption>میانهٔ زمان تحویل تا اولین گره. طول میله نسبت به بزرگ‌ترین میانه در همین نمونه است.</figcaption></figure>",
            "<h3>رقابت واقعی دو درخواست برای آخرین صندلی</h3>",
            table(["شناسهٔ درخواست","اجرا","عضویت مبدأ","عضویت مقصد"],
                  [(r["request_id"],r["execution"],"فعال" if r["origin"] else "حذف شد",
                    "فعال" if r["target"] else "تخصیص نیافت") for r in race["requests"]]),
            f"<p>تعداد اعضای مقصد بعد از آزمایش {race['occupancy']} نفر بود.</p>"]
    if "replay_checks" in evidence:
        labels = {
            "baseline": "مسیر سالم",
            "early-graduation": "فراغت هنگام اعتراض باز",
            "no-clearance": "حذف شاهد تسویه",
            "repeated-enrolment": "تخصیص تکراری با شناسهٔ تازه",
            "capacity-one": "آستانهٔ ظرفیت یک نفر",
            "duplicate-id": "شناسهٔ رویداد تکراری",
            "clock-regression": "عقب‌گرد ساعت رویداد",
        }
        out += ["<h3>بازپخش و آزمون حساسیت ارزیاب</h3>",
                table(["سناریو","نتیجه","شاهدها"],[
                    (labels[case["scenario"]],
                     "ورودی رد شد" if case["status"] == "invalid-input" else "تحلیل انجام شد",
                     "، ".join(f"{item['rule']} · {item['event']}" for item in case["findings"]) or "—")
                    for case in evidence["replay_checks"]]),
                '<p>ورودی عمومی برای بازپخش در <a href="https://faran-mu.vercel.app/docs/semester-web.json">دفتر نیمسال</a> و اعداد این گزارش در <a href="https://faran-mu.vercel.app/docs/seminar-results.json">فایل شواهد محاسبات</a> منتشر شده‌اند.</p>']
    return "".join(out)

def references():
    return "<h2>منابع علمی و فنی</h2><ol>" + "".join(
        f'<li dir="ltr">{escape(title)} <a href="{escape(url)}">نسخهٔ منبع</a></li>' for title,url in REFERENCES
    ) + "</ol>"

def figures():
    return '<h2>تصاویر محیط اجرا و معماری</h2>' + "".join(
        f'<figure><img src="{escape((DOCS / path).as_uri())}" alt="{escape(caption)}">'
        f'<figcaption>شکل {number}. {escape(caption)}{figure_links(path, FARAN)}</figcaption></figure>'
        for number,(path,caption) in enumerate(IMAGE_NAMES,1)
    )

def appendix(roster):
    description = (
        "<section class='annex'><h2>پیوست الف ـ خلاصهٔ رسیدهای ثبت‌نام آزمایشی</h2>"
        "<p>ستون گروه آموزشی از برنامهٔ نیمسال می‌آید. ستون درس و گروه Moodle شناسهٔ ذخیره‌شده در سامانه است. "
        "نتیجهٔ هر ردیف به عضویت فعال همان پروندهٔ ساختگی در گروه مورد انتظار اشاره دارد.</p>"
    )
    rows = [(r["id"],r["major"],r["group"],r["instructor"],r["courseid"],r["groupid"],
             "تأیید" if r["receipt_matches"] and r["membership_verified"] else "نیازمند بررسی") for r in roster]
    return description + table(["پرونده","رشته","گروه آموزشی","مدرس","درس Moodle","گروه Moodle","نتیجه"],rows) + "</section>"

def role_appendix(catalog):
    records = catalog["records"]
    assert len(records) == len({row["agent_id"] for row in records}) == 2000
    managers = {"ceo": "مدیریت ارشد", "pm": "آموزش", "cto": "فناوری اطلاعات", "engineer": "مهندسی کامپیوتر"}
    prefixes = {}
    rows = []
    for record in records:
        prefix, role = record["task_id"].rsplit("/", 1)
        assert role == record["agent_id"]
        manager = record["manager"]
        assert prefixes.setdefault(manager, prefix) == prefix
        date, time = record["occurred_at"].split("T", 1)
        status = "تکمیل" if record["status"] == "completed" else record["status"]
        rows.append((role, managers[manager], record["execution"], date, time, status))
    return (
        '<section class="annex role-ledger"><h2>پیوست ب ـ دفتر اجرای تک‌تک نقش‌ها</h2>'
        '<p>هر ردیف یک شناسهٔ متمایز نقش و ارجاع به اجرای بایگانی‌شدهٔ n8n دارد. دادهٔ نیمسال و نقش‌ها آزمایشی است. '
        'زمان در قالب ISO و با مبدأ زمانی ثبت‌شده نگه داشته شده تا با رد اصلی تطبیق داده شود. '
        'برای بازسازی شناسهٔ وظیفه، پیشوند شاخه و شناسهٔ نقش را با / به هم وصل کنید. '
        '<a href="https://dr-soleimani-evaluator.vercel.app/lab/catalog.json">نسخهٔ ماشین‌خوان دفتر</a></p>'
        + '<div class="prefixes">' + table(["شاخه", "پیشوند دقیق شناسهٔ وظیفه"],
           [(managers[key], prefix) for key, prefix in prefixes.items()]) + "</div>"
        + table(["نقش", "شاخهٔ مدیریت", "اجرای n8n", "تاریخ ISO", "ساعت و منطقه", "وضعیت"], rows) + "</section>"
    )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--body-only", action="store_true", help="Render the main report without the raw receipt table")
    parser.add_argument("--catalog", type=Path, help="Public evaluator catalog for the per-role evidence appendix")
    args = parser.parse_args()
    evidence = json.loads((DOCS / "seminar-results.json").read_text(encoding="utf8"))
    evaluation = (DOCS / "SYSTEM-EVALUATION.md").read_text(encoding="utf-8")
    body = manuscript() + MarkdownIt().enable("table").render(evaluation) + result_tables(evidence) + figures() + references()
    if not args.body_only:
        body += appendix(evidence["roster"])
        if args.catalog:
            body += role_appendix(json.loads(args.catalog.read_text(encoding="utf-8")))
    document = (f'<!doctype html><html lang="fa" dir="rtl"><meta charset="utf-8">'
                f'<title>گزارش سمینار دانشگاه دیجیتال فاران</title><style>{STYLE}</style>'
                f'<main>{body}</main></html>')
    with TemporaryDirectory(prefix="faran-seminar-") as temporary:
        folder = Path(temporary)
        source = folder / "print.html"
        source.write_text(document,encoding="utf8")
        candidate = folder / "rendered.pdf"
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                executable_path=os.environ.get("FARAN_RENDER_BROWSER", str(EDGE)),
                args=["--allow-file-access-from-files"],
            )
            try:
                page = browser.new_page()
                page.set_default_timeout(120_000)
                page.goto(source.as_uri(), wait_until="load")
                page.pdf(path=candidate, prefer_css_page_size=True, print_background=True)
            finally:
                browser.close()
        pdf = PdfReader(candidate)
        assert len(pdf.pages) > 1
        assert sum(len(page.images) for page in pdf.pages) >= 4, "Screenshot evidence missing"
        if not args.body_only:
            (DOCS / "faran-seminar.pdf").write_bytes(candidate.read_bytes())
        print("Body pages" if args.body_only else "Total pages",len(pdf.pages))

if __name__ == "__main__":
    main()
