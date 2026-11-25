"""Update both Persian articles from the shared, source-backed assessment."""
from argparse import ArgumentParser
from pathlib import Path
from urllib.parse import urlsplit
from tempfile import TemporaryDirectory
import html
import os
import re
import subprocess

from markdown_it import MarkdownIt
from pypdf import PdfReader
from article_figures import EVALUATOR, FARAN, figure_destinations, figure_links

ROOT = Path(__file__).resolve().parents[1]
BROWSER = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
MARKDOWN = MarkdownIt("commonmark", {"html": True}).enable("table")
START = "<!-- BEGIN SYSTEM ASSESSMENT -->"
END = "<!-- END SYSTEM ASSESSMENT -->"
FIGURES = [
    ("verified-organization.jpg", "چارت سازمانی عمومی فاران در بوم Homelable"),
    ("verified-evaluation-lab.jpg", "محاسبهٔ سنجه‌ها از رد ثبت‌نام در آزمایشگاه ارزیابی"),
]
INTRO = {
    "faran": "جدول‌های این بخش، پوشش ساختار مؤسسه، مسئولیت سرویس‌ها و نتیجهٔ اجرای آزمایشی را در کنار شواهد قابل بازبینی ثبت می‌کنند.",
    "evaluator": "این بخش تعریف سنجه، آزمون حساسیت قواعد و مرز اعتبار هر نتیجه را کنار شاهد مربوط قرار می‌دهد.",
}
PRINT = """
@page { size:A4; margin:17mm 16mm 18mm;
  @bottom-center { content:"ارزیاب دکتر سلیمانی · " counter(page) " / " counter(pages); font:9pt Tahoma; }
}
body { margin:0 !important; font:10.5pt/1.8 Tahoma, sans-serif; color:#152b40; }
header,main,section { max-width:none !important; }
header nav, button, [download] { display:none !important; }
h2,h3 { break-after:avoid; }
figure { break-inside:avoid; }
figure img { width:auto; max-width:100%; max-height:106mm; object-fit:contain; }
table { border-collapse:collapse; }
thead { display:table-header-group; }
tr { break-inside:avoid; }
p { widows:3; orphans:3; }
"""
ARTICLE_CSS = """
#system-assessment table { width:100%; border-collapse:collapse; text-align:start; font-size:.88em; }
#system-assessment th,#system-assessment td { padding:.45em .55em; vertical-align:top; overflow-wrap:anywhere;
    border:1px solid #7990a073; }
#system-assessment th { background:#c3d6e233; }
#system-assessment figure img { max-width:100%; height:auto; }
.figure-source-links { font-size:.9em; }
.figure-source-links a { text-underline-offset:.18em; }
#system-assessment .assessment-outline { display:flex; gap:.75rem; flex-wrap:wrap; }
@media(max-width:650px) { #system-assessment table { font-size:.78em; } }
@media screen and (max-width:650px) {
    p, li { overflow-wrap:anywhere; }
    pre { max-width:100%; overflow-x:auto; }
}
"""


def replace_block(document, content):
    block = f"{START}\n{content}\n{END}"
    if START not in document:
        return document.rstrip() + "\n\n" + block + "\n"
    before, _, remainder = document.partition(START)
    _, matched, after = remainder.partition(END)
    assert matched and START not in remainder
    return before + block + after


def refresh_opening(current, manuscript, key):
    start = manuscript.index("## چکیده")
    end = manuscript.index("## نقشهٔ تعاملی", start)
    opening = MARKDOWN.render(manuscript[start:end])
    start = current.index("<h2>چکیده</h2>")
    boundary = '<h2 id="homelable">' if key == "faran" else '<h2 id="evaluation-lab">'
    end = current.index(boundary, start)
    current = current[:start] + opening + current[end:]
    current = re.sub(
        r'(<p><strong>نوع سند:</strong> )[^<]+',
        r'\g<1>مقالهٔ فنی و گزارش ارزیابی مبتنی بر شواهد، بازبینی ۲۵ نوامبر ۲۰۲۶',
        current, count=1,
    )
    current = re.sub(r'<p><strong>یادداشت ویراستاری:</strong>.*?</p>', '', current, count=1, flags=re.S)
    lecturer = re.search(r'^\*\*استاد:\*\* ([^\n]+)', manuscript, flags=re.M)
    if lecturer:
        current = re.sub(r'<p><strong>استاد(?: ارائه| تحویل)?:</strong>[^<]+</p>',
                         lambda _: f'<p><strong>استاد:</strong> {html.escape(lecturer[1])}</p>',
                         current, count=1)
    return current.replace("مطالعهٔ موردی دپارتمان‌های فاران", "آزمون مقدماتی واگذاری به چهار نقش", 1)


def link_figures(document, origin):
    def add_links(match):
        figure = match[0]
        image = re.search(r'<img\b[^>]*\bsrc="([^"]+)"', figure)
        if image is None:
            return figure
        filename = Path(urlsplit(image[1]).path).name
        figure = re.sub(r'<span class="figure-source-links">.*?</span>', '', figure, flags=re.S)
        assert figure.count("</figcaption>") == 1, filename
        return figure.replace("</figcaption>", figure_links(filename, origin) + "</figcaption>")
    return re.sub(r'<figure\b.*?</figure>', add_links, document, flags=re.S)


def link_markdown_figures(document, origin):
    def add_links(match):
        filename = Path(urlsplit(match[2]).path).name
        links = " · ".join(f"[{label}]({url})" for label, url in figure_destinations(filename, origin))
        return f"{match[1]}\n\n<!-- figure destinations -->{links}"
    return re.sub(
        r"^(!\[[^\n\]]*\]\(([^)\n]+)\))(?:\n\n(?:<!-- figure destinations -->[^\n]+|"
        r"\[(?:باز کردن نقشهٔ تعاملی|شواهد JSON)\]\([^\n]+\)))?",
        add_links, document, flags=re.M,
    )


def web_section(assessment, key, docdir, source_link):
    figures = []
    for filename, caption in FIGURES:
        asset = docdir / filename
        assert asset.stat().st_size > 1000
        label = html.escape(caption)
        figures.append(f'<figure><a href="{filename}"><img src="{filename}" alt="{label}"></a><figcaption>{label}</figcaption></figure>')
    return (
        f'<style>{ARTICLE_CSS}</style><section id="system-assessment" lang="fa" dir="rtl">'
        f'<p>{html.escape(INTRO[key])}</p>'
        + MARKDOWN.render(assessment)
        + "<h3>تصاویر نسخهٔ بررسی‌شده</h3>" + "".join(figures)
        + f'<p><a href="{source_link}">داده‌ها و منابع قابل بازبینی</a></p></section>'
    )


def make_pdf(source, destination):
    # Static HTML uses relative screenshots and leading-slash paths for site assets.
    # Resolve both before opening the A4 print template from a temporary directory.
    markup = source.read_text(encoding="utf-8-sig")
    root = source.parent.parent.as_uri()
    markup = re.sub(r'(?<=src=")/(?=[^/])', root + "/", markup)
    markup = re.sub(r'(?<=href=")/(?=[^/])', root + "/", markup)
    head = '<base href="' + source.parent.as_uri() + '/">'
    markup = markup.replace("</title>", "</title>" + head, 1) + "<style>" + PRINT + "</style>"
    assert "<base href=" in markup
    with TemporaryDirectory(prefix="evaluator-article-") as temporary:
        work = Path(temporary)
        document = work / "print.html"
        candidate = work / "article.pdf"
        document.write_text(markup, encoding="utf-8")
        subprocess.run([
            os.environ.get("FARAN_RENDER_BROWSER", str(BROWSER)), "--headless", "--disable-gpu",
            "--allow-file-access-from-files", "--no-pdf-header-footer", f"--user-data-dir={work / 'browser'}",
            f"--print-to-pdf={candidate}", document.as_uri(),
        ], check=True, timeout=120)
        reader = PdfReader(candidate)
        assert len(reader.pages) > 10 and sum(len(page.images) for page in reader.pages) >= 8
        destination.write_bytes(candidate.read_bytes())
        print("Evaluator article pages:", len(reader.pages))


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("evaluator", type=Path)
    parser.add_argument("--web-only", action="store_true", help="Update HTML and Markdown without rendering another PDF")
    args = parser.parse_args()
    assessment = (ROOT / "docs/SYSTEM-EVALUATION.md").read_text(encoding="utf-8")
    source_link = "https://faran-mu.vercel.app/docs/seminar-results.json"
    for key, root in (("faran", ROOT), ("evaluator", args.evaluator.resolve(strict=True))):
        docs = root / "docs"
        manuscript = docs / "ARTICLE.md"
        web = docs / "article.html"
        origin = FARAN if key == "faran" else EVALUATOR
        updated = replace_block(manuscript.read_text(encoding="utf-8-sig"), assessment)
        updated = link_markdown_figures(updated, origin)
        manuscript.write_text(updated, encoding="utf-8")
        current = web.read_text(encoding="utf-8-sig")
        intro = (
            '<p class="article-assessment-link"><strong>بازبینی ۲۵ نوامبر ۲۰۲۶.</strong> '
            'چارت منتشرشدهٔ مؤسسه و شواهد محیط آزمایشی در بخش ارزیابی نسخهٔ جاری بررسی شده‌اند. '
            '<a href="#system-assessment">رفتن به ارزیابی و جدول نتایج</a></p>'
        )
        old_intro = r'<p class="article-assessment-link">.*?</p>'
        if re.search(old_intro, current):
            current = re.sub(old_intro, lambda match: intro, current, count=1)
        else:
            current = current.replace("</h1>", "</h1>" + intro, 1)
        current = refresh_opening(current, updated, key)
        rendered = replace_block(current, web_section(assessment, key, docs, source_link))
        web.write_text(link_figures(rendered, origin), encoding="utf-8")
        if key == "evaluator" and not args.web_only:
            make_pdf(web, docs / "evaluation-article.pdf")


if __name__ == "__main__":
    main()
