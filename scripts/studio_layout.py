"""Render the public landing page and dashboard directory from studio-menu.json."""
import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def link(title, href, css=""):
    attrs = f' class="{escape(css)}"' if css else ""
    return f'<a href="{escape(href, quote=True)}"{attrs}>{escape(title)}</a>'

def cards(items):
    return '<div class="studio-services">' + "".join(
        f'<a class="studio-card" data-studio-tool href="{escape(url, quote=True)}">'
        f'<strong>{escape(title)}</strong><span>{escape(description)}</span><small>{escape(kind)} <span aria-hidden="true">↗</span></small></a>'
        for title, description, url, kind in items
    ) + '</div>'

def summary():
    return '''<section class="studio-summary" data-project-status aria-label="آخرین شواهد منتشرشده">
      <h3>شواهد ثبت‌شده</h3><p data-studio-message role="status">در حال خواندن خلاصهٔ شواهد…</p>
      <dl data-studio-metrics hidden></dl>
      <noscript><p>برای دیدن خلاصه، جاوااسکریپت را فعال کنید یا رد خام را باز کنید.</p></noscript>
      <a href="/docs/registration-trace.json">باز کردن رد ثبت‌نام ↗</a>
    </section>'''

def menu():
    return json.loads((ROOT / "studio-menu.json").read_text("utf-8-sig"))

def render_home():
    m = menu()
    buttons = "".join(link(title, url, "studio-link") for title, url in m["primary"])
    nav = "".join(link(title, url) for title, url in m["nav"])
    services = f'''<section class="studio-content" id="services"><h2>خدمات دانشگاه</h2>{cards(m["services"])}</section>''' if m["services"] else ""
    legacy = """const anchors = ['#overview','#agents','#forecast','#evidence','#about','#registration-trace']; if (anchors.includes(location.hash)) location.replace('/dashboard.html'+location.hash);""" if m["theme"]=="evaluator" else ""
    return f'''<!doctype html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta name="description" content="{escape(m["intro"],quote=True)}">
  <meta name="theme-color" content="#{ '0c2929' if m["theme"] == "faran" else "1f1b3c"}">
  <title>{escape(m["name"])}</title>
  <link rel="icon" href="/icon.svg">
  <link rel="manifest" href="/manifest.webmanifest">
  <link rel="stylesheet" href="/studio.css">
  <script src="/studio.js" defer></script>
  <script>{legacy} if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(() => {{}});</script>
</head>
<body class="studio-page studio-{m["theme"]}">
  <header class="studio-nav"><div class="studio-wrap">
    <a class="studio-ident" href="/"><span class="studio-mark" aria-hidden="true">{m["mark"]}</span>{escape(m["name"])}</a>
    <nav aria-label="منوی اصلی">{nav}{link("ورود به داشبورد", "/login.html", "studio-btn")}</nav>
  </div></header>
  <main class="studio-wrap">
    <section class="studio-hero">
      <div><p class="studio-eyebrow">{escape(m["course"])}</p>
        <h1>{escape(m["headline"])}</h1><p>{escape(m["intro"])}</p>
        <div class="studio-actions">{link("ورود به داشبورد آزمایشی", "/login.html", "studio-btn")}{buttons}</div>
      </div>
      <figure class="studio-media">
        <a href="{escape(m["preview"],quote=True)}"><img src="{escape(m["image"],quote=True)}" alt="{escape(m["imageAlt"],quote=True)}" fetchpriority="high" width="720" height="450"></a>
        <figcaption><span>{escape(m["imageAlt"])}</span>{link(m["previewLabel"],m["preview"])}</figcaption>
      </figure>
    </section>
    {summary()}
    {services}
    <section class="studio-content" id="tools"><h2>ابزارها و میزکار</h2>{cards(m["tools"])}</section>
    <section class="studio-content" id="downloads"><h2>نسخه‌ها و ارائهٔ درس</h2>{cards(m["downloads"])}</section>
  </main>
  <footer class="studio-footer"><div class="studio-wrap"><strong>{escape(m["name"])}</strong>
    <nav aria-label="پیوندهای پروژه">{link(m["peerName"],m["peer"])}{link("گیت‌هاب",m["github"])}</nav>
    <span class="publisher-credit" dir="ltr"><bdi lang="en">Powered by</bdi> <a href="https://github.com/maddixmhn" rel="me"><bdi dir="rtl">محمد مهرانی</bdi></a></span>
  </div></footer>
</body>
</html>
'''

def dashboard_directory():
    m = menu()
    tools = m["tools"]
    downloads = m["downloads"]
    featured = [tools[0], tools[1], downloads[0], downloads[1]]
    rest = [item for item in tools + downloads if item not in featured] + m["services"]
    return f'''<section class="studio-hub" data-studio-directory aria-label="دسترسی سریع و شواهد">
      <div class="studio-hub-head"><div><h2>دسترسی سریع</h2><p class="studio-sub">ابزارها، فایل ارائه و نسخهٔ اندروید</p></div>
      <label class="studio-filter" hidden data-studio-search>جست‌وجوی ابزار<input type="search" placeholder="مثلاً ظرفیت یا اندروید"></label></div>
      {cards(featured)}
      <details data-studio-more><summary>همهٔ ابزارها و فایل‌ها</summary>{cards(rest)}</details>
      <p data-studio-empty role="status" hidden>ابزاری با این عبارت پیدا نشد.</p>
      {summary()}
    </section>'''

def main():
    (ROOT / "index.html").write_text(render_home(), encoding="utf-8")
    path = ROOT / "dashboard.html"
    text = path.read_text("utf-8-sig")
    block = "<!-- studio-hub:start -->\n" + dashboard_directory() + "\n<!-- studio-hub:end -->"
    text, count = re.subn(r"<!-- studio-hub:start -->.*?<!-- studio-hub:end -->", lambda _: block, text, count=1, flags=re.S)
    if count != 1:
        raise ValueError("Dashboard does not have a studio directory placeholder")
    path.write_text(text, encoding="utf-8")

if __name__ == "__main__":
    main()
