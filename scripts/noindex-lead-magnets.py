"""One-off: add noindex, follow, noarchive to all lead-magnet landing pages."""
from pathlib import Path
import re

TAG = '<meta name="robots" content="noindex, follow, noarchive" />'
pages = list(Path("assets/lead-magnets").glob("*.html"))
updated = skipped = warn = 0

for p in pages:
    html = p.read_text("utf-8")
    if "noindex" in html:
        skipped += 1
        continue
    new = re.sub(r'(<meta name="viewport"[^>]*/?>)', r"\1\n  " + TAG, html, count=1)
    if new == html:
        new = re.sub(r"(<meta charset=[^>]*/?>)", r"\1\n  " + TAG, html, count=1)
    if new != html:
        p.write_text(new, "utf-8")
        updated += 1
    else:
        print(f"WARNING: no insertion point in {p.name}")
        warn += 1

print(f"Updated: {updated}, Already noindex: {skipped}, Warnings: {warn}")
