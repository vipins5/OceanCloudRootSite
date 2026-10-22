#!/usr/bin/env python3
"""
update-sitemap.py
=================
Updates <lastmod> dates in the URL sitemaps to match the last git commit date
for each page's corresponding file, then rolls those dates up into
sitemap-index.xml. Preserves all other sitemap fields.

The index rollup matters: Google reads the index's <lastmod> to decide whether
a child sitemap is worth re-fetching. An index that still advertises an old
date hides every fresh URL underneath it.

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
# URL sitemaps that receive refreshed lastmod values.
SITEMAPS = [ROOT / "sitemap.xml", ROOT / "sitemap-guides.xml"]
# Sitemap index whose lastmod values are derived from the sitemaps above.
INDEX    = ROOT / "sitemap-index.xml"
# Canonical domain prefix stripped from loc entries before path mapping.
BASE_URL = "https://oceancloudconsults.com"
# Namespace URI used to query sitemap XML elements.
NS       = "http://www.sitemaps.org/schemas/sitemap/0.9"

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
        status = subprocess.run(
            ["git", "status", "--porcelain", "--", str(file)],
            capture_output=True, text=True, check=True,
            cwd=ROOT
        )
        if status.stdout.strip() and file.exists():
            mtime = datetime.fromtimestamp(file.stat().st_mtime).astimezone()
            return mtime.strftime("%Y-%m-%d")

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
        mtime = datetime.fromtimestamp(file.stat().st_mtime).astimezone()
        return mtime.strftime("%Y-%m-%d")
    return datetime.now().astimezone().strftime("%Y-%m-%d")


def register_namespaces() -> None:
    """Keep the default and xsi prefixes intact on write-back."""
    ET.register_namespace("", NS)
    ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")


def write_xml(path: Path, root: ET.Element) -> None:
    xml_str = ET.tostring(root, encoding="unicode", xml_declaration=False)
    path.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str + "\n",
        encoding="utf-8"
    )
    print(f"[ok] {path.name} written.")


def update_sitemap(sitemap: Path, dry_run: bool) -> str | None:
    """Refresh every <lastmod> in `sitemap`. Returns the newest date seen."""
    print(f"\n{sitemap.name}")
    tree = ET.parse(sitemap)
    root = tree.getroot()

    # URL entries updated with a new lastmod value.
    updated = 0
    # URL entries that were already in sync.
    unchanged = 0
    # URL entries with no local file mapping.
    missing = 0
    # Newest lastmod across all entries — becomes this sitemap's index date.
    newest = None

    for url_el in root.findall(f"{{{NS}}}url"):
        loc_el     = url_el.find(f"{{{NS}}}loc")
        lastmod_el = url_el.find(f"{{{NS}}}lastmod")
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
            # A stale entry still contributes its date to the index rollup.
            old_date = (lastmod_el.text or "").strip() if lastmod_el is not None else ""
            if old_date and (newest is None or old_date > newest):
                newest = old_date
            continue

        # Proposed lastmod value based on latest git commit touching this file.
        new_date = git_last_modified(file)
        # Existing lastmod value currently present in sitemap.
        old_date = (lastmod_el.text or "").strip() if lastmod_el is not None else ""

        if newest is None or new_date > newest:
            newest = new_date

        if new_date == old_date:
            unchanged += 1
            continue

        if lastmod_el is None:
            lastmod_el = ET.SubElement(url_el, f"{{{NS}}}lastmod")
        lastmod_el.text = new_date
        print(f"  {'[dry]' if dry_run else '[set]'} /{path}  {old_date or '(none)'} -> {new_date}")
        updated += 1

    print(f"  Result: {updated} updated, {unchanged} unchanged, {missing} no-file.")

    if updated > 0 and not dry_run:
        write_xml(sitemap, root)

    return newest


def update_index(dates: dict[str, str], dry_run: bool) -> None:
    """Point each <sitemap> entry in the index at its child's newest lastmod."""
    print(f"\n{INDEX.name}")
    if not INDEX.exists():
        print(f"  [skip] {INDEX.name} not found.")
        return

    tree = ET.parse(INDEX)
    root = tree.getroot()
    updated = 0

    for sm_el in root.findall(f"{{{NS}}}sitemap"):
        loc_el     = sm_el.find(f"{{{NS}}}loc")
        lastmod_el = sm_el.find(f"{{{NS}}}lastmod")
        if loc_el is None:
            continue

        # Child sitemap filename, used to look up its computed newest date.
        name     = (loc_el.text or "").rstrip("/").split("/")[-1]
        new_date = dates.get(name)
        if new_date is None:
            print(f"  [skip] No local sitemap for: {name}")
            continue

        old_date = (lastmod_el.text or "").strip() if lastmod_el is not None else ""
        if new_date == old_date:
            continue

        if lastmod_el is None:
            lastmod_el = ET.SubElement(sm_el, f"{{{NS}}}lastmod")
        lastmod_el.text = new_date
        print(f"  {'[dry]' if dry_run else '[set]'} {name}  {old_date or '(none)'} -> {new_date}")
        updated += 1

    print(f"  Result: {updated} updated.")

    if updated > 0 and not dry_run:
        write_xml(INDEX, root)


def main(dry_run: bool = False) -> None:
    register_namespaces()

    # Newest lastmod per child sitemap filename, fed into the index rollup.
    dates = {}
    for sitemap in SITEMAPS:
        if not sitemap.exists():
            print(f"[error] {sitemap} not found.", file=sys.stderr)
            sys.exit(1)
        newest = update_sitemap(sitemap, dry_run)
        if newest:
            dates[sitemap.name] = newest

    update_index(dates, dry_run)

    if dry_run:
        print("\nDry-run mode — nothing written.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    main(dry_run=args.dry_run)
