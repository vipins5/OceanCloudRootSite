#!/usr/bin/env python3
"""
update-sitemap.py
=================
Updates <lastmod> dates in sitemap.xml to match the last git commit date
for each page's corresponding file. Preserves all other sitemap fields.

Usage:
    python scripts/update-sitemap.py [--dry-run]

Run from the repo root. Requires git history (use fetch-depth: 0 in Actions).
"""

import argparse
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

# Repo root used for git lookups and URL-to-file resolution.
ROOT     = Path(__file__).parent.parent
# Sitemap file that will receive refreshed lastmod values.
SITEMAP  = ROOT / "sitemap.xml"
# Canonical domain prefix stripped from loc entries before path mapping.
BASE_URL = "https://oceancloudconsults.com"

# Map URL path → local file (relative to repo root)
# Paths without .html extension are tried with .html appended
def url_to_file(path: str) -> Path | None:
    path = path.strip("/")

    if path == "":
        return ROOT / "index.html"

    candidates = [
        ROOT / f"{path}.html",
        ROOT / path,
        ROOT / f"{path}/index.html",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def git_last_modified(file: Path) -> str:
    """Return ISO date (YYYY-MM-DD) of the last git commit touching `file`."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%aI", "--", str(file)],
            capture_output=True, text=True, check=True,
            cwd=ROOT
        )
        raw = result.stdout.strip()
        if raw:
            return raw[:10]          # YYYY-MM-DD
    except subprocess.CalledProcessError:
        pass
    # Fallback: file mtime
    if file.exists():
        mtime = datetime.fromtimestamp(file.stat().st_mtime, tz=timezone.utc)
        return mtime.strftime("%Y-%m-%d")
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def main(dry_run: bool = False) -> None:
    if not SITEMAP.exists():
        print(f"[error] {SITEMAP} not found.", file=sys.stderr)
        sys.exit(1)

    ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    tree = ET.parse(SITEMAP)
    root = tree.getroot()
    # Namespace URI used to query sitemap XML elements.
    ns   = "http://www.sitemaps.org/schemas/sitemap/0.9"

    # URL entries updated with a new lastmod value.
    updated = 0
    # URL entries that were already in sync.
    unchanged = 0
    # URL entries with no local file mapping.
    missing = 0

    for url_el in root.findall(f"{{{ns}}}url"):
        loc_el     = url_el.find(f"{{{ns}}}loc")
        lastmod_el = url_el.find(f"{{{ns}}}lastmod")
        if loc_el is None:
            continue

        # Absolute URL from <loc>.
        loc  = loc_el.text or ""
        # Repo-relative URL path segment derived from loc.
        path = loc.replace(BASE_URL, "").strip("/")
        # Filesystem path inferred from URL path.
        file = url_to_file(path)

        if file is None:
            print(f"  [skip] No file found for: /{path}")
            missing += 1
            continue

        # Proposed lastmod value based on latest git commit touching this file.
        new_date = git_last_modified(file)
        # Existing lastmod value currently present in sitemap.
        old_date = (lastmod_el.text or "").strip() if lastmod_el is not None else ""

        if new_date == old_date:
            unchanged += 1
            continue

        if lastmod_el is None:
            lastmod_el = ET.SubElement(url_el, f"{{{ns}}}lastmod")
        lastmod_el.text = new_date
        print(f"  {'[dry]' if dry_run else '[set]'} /{path}  {old_date or '(none)'} → {new_date}")
        updated += 1

    print(f"\nResult: {updated} updated, {unchanged} unchanged, {missing} no-file.")

    if updated > 0 and not dry_run:
        # Write back preserving declaration + xmlns
        xml_str = ET.tostring(root, encoding="unicode", xml_declaration=False)
        SITEMAP.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str + "\n",
            encoding="utf-8"
        )
        print(f"✓ {SITEMAP} written.")
    elif dry_run:
        print("Dry-run mode — sitemap not written.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    main(dry_run=args.dry_run)
