"""Add google-adsense-account verification meta to all indexable pages."""
from pathlib import Path
import re

PUB_ID = "ca-pub-9926554564611983"
META = f'<meta name="google-adsense-account" content="{PUB_ID}" />'

EXCLUDE = {
    "coming-soon.html", "comments-admin.html", "search.html",
    "404.html", "archive.html", "message-center.html", "status.html",
}

targets = list(Path(".").glob("*.html")) + list(Path("articles").glob("guide-*.html"))

updated = skipped = already = warn = 0
for p in targets:
    if p.name in EXCLUDE:
        skipped += 1
        continue
    html = p.read_text("utf-8")
    if "noindex" in html:
        skipped += 1
        continue
    if "google-adsense-account" in html:
        already += 1
        continue
    # Insert after robots meta
    new = re.sub(r'(<meta name="robots"[^>]*/?>)', r"\1\n  " + META, html, count=1)
    if new == html:
        # fallback: after canonical link
        new = re.sub(r'(<link rel="canonical"[^>]*/?>)', r"\1\n  " + META, html, count=1)
    if new != html:
        p.write_text(new, "utf-8")
        updated += 1
    else:
        print(f"WARNING: no insertion point in {p}")
        warn += 1

print(f"Added: {updated}, Already present: {already}, Skipped (noindex/excluded): {skipped}, Warnings: {warn}")
