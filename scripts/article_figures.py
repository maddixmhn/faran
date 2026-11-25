"""Public destinations for the figures shared by the seminar and evaluator articles."""
import html

FARAN = "https://faran-mu.vercel.app"
EVALUATOR = "https://dr-soleimani-evaluator.vercel.app"


def figure_destinations(filename, origin):
    infrastructure = "faran-infrastructure" if origin == FARAN else "evaluator-evidence"
    topology = f"{origin}/topology/index.html?design={infrastructure}"
    workflow = EVALUATOR + "/lab/index.html#university"
    archived = origin + "/docs/"
    links = {
        "homelable-infrastructure.jpg": [("باز کردن نقشهٔ تعاملی زیرساخت", FARAN + "/topology/index.html?design=faran-infrastructure")],
        "homelable-evidence.jpg": [("باز کردن نقشهٔ تعاملی شواهد", EVALUATOR + "/topology/index.html?design=evaluator-evidence")],
        "verified-organization.jpg": [("باز کردن همین چارت تعاملی", origin + "/topology/index.html?design=faran-official-structure")],
        "verified-evaluation-lab.jpg": [("باز کردن آزمایشگاه ارزیابی", EVALUATOR + "/lab/index.html"),
                                        ("دادهٔ نمونهٔ ثبت‌نام", EVALUATOR + "/docs/registration-trace.json")],
        "faculty-home.png": [("باز کردن صفحهٔ عمومی فعلی", origin + "/")],
        "faculty-semester.png": [("باز کردن دفتر نیمسال در وب", archived + "semester-web.html")],
        "service-graph.svg": [("نقشهٔ تعاملی مرتبط", topology), ("نسخهٔ کامل نمودار", archived + filename)],
        "semester-workflow.svg": [("مرور گردش‌کارها و دفتر اجرا در وب", workflow),
                                  ("نسخهٔ کامل نمودار", archived + filename)],
        "execution-evidence.png": [("رسید بایگانی‌شدهٔ اجرای ثبت‌نام", archived + "execution-evidence.json")],
        "docker-desktop.jpg": [("تصویر کامل بایگانی‌شدهٔ Docker Desktop", archived + filename),
                              ("فایل شواهد این محیط محلی", archived + "execution-evidence.json")],
        "n8n-execution-19.jpg": [("تصویر کامل بایگانی‌شدهٔ اجرای ۱۹", archived + filename),
                                ("نمودار گردش‌کار نیمسال", archived + "semester-workflow.svg")],
        "paperclip-console.png": [("تصویر کامل بایگانی‌شدهٔ Paperclip", archived + filename),
                                  ("بوم عمومی نقش‌های آزمایشی", FARAN + "/topology/index.html?design=faran-university")],
    }
    return links[filename]


def figure_links(filename, origin):
    anchors = " · ".join(f'<a href="{html.escape(url)}">{html.escape(label)}</a>'
                         for label, url in figure_destinations(filename, origin))
    return f'<span class="figure-source-links"><br>{anchors}</span>'
