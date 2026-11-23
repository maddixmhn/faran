from pathlib import Path
from shutil import copy2

root = Path(__file__).resolve().parent.parent
output = root / "pages-dist"
(output / "docs").mkdir(parents=True, exist_ok=True)
for filename in ("index.html", "app.js", "site.css", "style.css", "core.mjs", "sw.js", "manifest.webmanifest", "icon.svg"):
    source = root / filename
    if source.is_file():
        copy2(source, output / filename)
for source in (root / "docs").iterdir():
    if source.suffix in {".html", ".md", ".json"}:
        copy2(source, output / "docs" / source.name)
