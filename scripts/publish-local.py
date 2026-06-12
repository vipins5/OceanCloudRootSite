#!/usr/bin/env python3
"""
Local publish helper for OceanCloud.

Run this from the repo root before committing a manual publish. It only updates:
  - sitemap.xml lastmod entries for files changed in the working tree
  - sitemap.xml entries for newly added HTML files
  - feed.xml lastBuildDate

It does not generate articles, fetch news, call AI APIs, create branches, or open PRs.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import format_datetime
from html import unescape
from pathlib import Path

# Repo root path used for git and content file operations.
ROOT = Path(__file__).parent.parent
# Target sitemap file that receives add/remove/lastmod updates.
SITEMAP = ROOT / "sitemap.xml"
# Target RSS feed whose lastBuildDate is refreshed on publish.
FEED = ROOT / "feed.xml"
# Canonical archive data used to map RSS items to local article pages.
ARCHIVE_JSON = ROOT / "data" / "archive.json"
# Canonical site base URL used in file-to-URL mapping.
BASE_URL = "https://oceancloudconsults.com"
# XML namespace for sitemap URL set parsing/writing.
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


def repo_path(path: str) -> Path:
    return (ROOT / path).resolve()


def file_to_url(file: Path) -> str | None:
    try:
        rel = file.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return None

    if not rel.endswith(".html"):
        return None
    if rel == "404.html":
        return None
    if rel.startswith("articles/news-"):
        return None
    if rel == "index.html":
        return f"{BASE_URL}/"
    return f"{BASE_URL}/{rel[:-5]}"


def url_to_file(loc: str) -> Path | None:
    path = loc.replace(BASE_URL, "").strip("/")
    if not path:
        return ROOT / "index.html"
    for candidate in (ROOT / f"{path}.html", ROOT / path, ROOT / path / "index.html"):
        if candidate.exists():
            return candidate
    return None


def changed_files() -> set[Path]:
    # Git porcelain output with tracked/untracked working-tree deltas.
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    # Unique set of changed file paths resolved to absolute filesystem paths.
    files: set[Path] = set()
    for line in result.stdout.splitlines():
        if not line:
            continue
        status = line[:2]
        path_text = line[3:]
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1]
        if status == "!!":
            continue
        files.add(repo_path(path_text.strip('"')))
    return files


def update_sitemap(changed: set[Path], dry_run: bool) -> int:
    if not SITEMAP.exists():
        print("[skip] sitemap.xml not found")
        return 0

    ET.register_namespace("", SITEMAP_NS)
    tree = ET.parse(SITEMAP)
    root = tree.getroot()
    # Local ISO date string written into lastmod fields for working-tree edits.
    today = datetime.now().astimezone().strftime("%Y-%m-%d")
    # Counter for total sitemap mutations performed in this run.
    changed_count = 0
    # Cache of existing loc values to avoid duplicate URL entries.
    existing_locs: set[str] = set()

    for url_el in list(root.findall(f"{{{SITEMAP_NS}}}url")):
        loc_el = url_el.find(f"{{{SITEMAP_NS}}}loc")
        if loc_el is None or not loc_el.text:
            continue
        loc = loc_el.text.strip()
        existing_locs.add(loc)
        if loc == f"{BASE_URL}/llms.txt":
            root.remove(url_el)
            changed_count += 1
            print(f"  [remove] {loc}")
            continue
        file = url_to_file(loc)
        if file is None:
            root.remove(url_el)
            changed_count += 1
            print(f"  [remove] {loc}")
            continue
        if file.resolve() in changed:
            lastmod_el = url_el.find(f"{{{SITEMAP_NS}}}lastmod")
            if lastmod_el is None:
                lastmod_el = ET.SubElement(url_el, f"{{{SITEMAP_NS}}}lastmod")
            if lastmod_el.text != today:
                print(f"  [lastmod] {loc} -> {today}")
                lastmod_el.text = today
                changed_count += 1

    for file in sorted(changed):
        loc = file_to_url(file)
        if loc is None or loc in existing_locs or not file.exists():
            continue
        url_el = ET.SubElement(root, f"{{{SITEMAP_NS}}}url")
        ET.SubElement(url_el, f"{{{SITEMAP_NS}}}loc").text = loc
        ET.SubElement(url_el, f"{{{SITEMAP_NS}}}lastmod").text = today
        ET.SubElement(url_el, f"{{{SITEMAP_NS}}}changefreq").text = "monthly"
        ET.SubElement(url_el, f"{{{SITEMAP_NS}}}priority").text = "0.7" if "/articles/" in loc else "0.8"
        changed_count += 1
        print(f"  [add] {loc}")

    if changed_count and not dry_run:
        ET.indent(root, space="  ")
        xml_str = ET.tostring(root, encoding="unicode", xml_declaration=False)
        SITEMAP.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str + "\n", encoding="utf-8")
    return changed_count


def update_feed(dry_run: bool) -> bool:
    if not FEED.exists():
        print("[skip] feed.xml not found")
        return False
    text = FEED.read_text(encoding="utf-8")
    # RFC 2822 timestamp required by RSS lastBuildDate.
    build_date = format_datetime(datetime.now(timezone.utc))
    start = text.find("<lastBuildDate>")
    end = text.find("</lastBuildDate>")
    if start == -1 or end == -1:
        print("[skip] feed.xml has no lastBuildDate")
        return False
    end += len("</lastBuildDate>")
    new_text = text[:start] + f"<lastBuildDate>{build_date}</lastBuildDate>" + text[end:]

    if ARCHIVE_JSON.exists():
        try:
            archive = json.loads(ARCHIVE_JSON.read_text(encoding="utf-8"))
            title_to_url = {
                item["title"]: f"{BASE_URL}/articles/{item['article_slug']}" if item.get("article_slug") else f"{BASE_URL}/archive"
                for item in archive.get("items", [])
                if item.get("title")
            }

            def localize_item(match: re.Match[str]) -> str:
                block = match.group(0)
                title_match = re.search(r"<title>(.*?)</title>", block, re.DOTALL)
                if not title_match:
                    return block
                local_url = title_to_url.get(unescape(title_match.group(1).strip()))
                if not local_url:
                    return block
                block = re.sub(r"<link>.*?</link>", f"<link>{local_url}</link>", block, count=1, flags=re.DOTALL)
                return re.sub(
                    r'<guid isPermaLink="true">.*?</guid>',
                    f'<guid isPermaLink="true">{local_url}</guid>',
                    block,
                    count=1,
                    flags=re.DOTALL,
                )

            new_text = re.sub(r"<item>.*?</item>", localize_item, new_text, flags=re.DOTALL)
        except (OSError, json.JSONDecodeError, KeyError) as exc:
            print(f"  [warn] Could not localize feed item links: {exc}")
    if new_text == text:
        return False
    print(f"  [feed] lastBuildDate -> {build_date}")
    if not dry_run:
        FEED.write_text(new_text, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    changed = changed_files()
    sitemap_changes = update_sitemap(changed, args.dry_run)
    feed_changed = update_feed(args.dry_run)

    if args.dry_run:
        print("Dry run complete; no files written.")
    else:
        print(f"Done. sitemap changes: {sitemap_changes}; feed updated: {feed_changed}.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f"[error] git command failed: {exc}", file=sys.stderr)
        sys.exit(1)
