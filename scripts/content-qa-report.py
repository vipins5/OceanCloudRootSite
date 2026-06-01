#!/usr/bin/env python3
"""
Generate a content QA report for OceanCloud.

Hard-fail checks:
- XML parseability for sitemap.xml and feed.xml
- JSON parseability for key data index files
- Sitemap URLs must not point at pages with a robots noindex directive

Advisory checks (warnings only):
- Missing <title>
- Missing <meta name="description">
- Missing canonical link tag
"""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

# Repo root path used for file discovery and relative output paths.
ROOT = Path(__file__).resolve().parent.parent
# Output markdown report for QA pipeline artifacts.
REPORT = ROOT / "data" / "reports" / "content-qa-report.md"

# XML files that must parse successfully (hard-fail checks).
XML_FILES = [
    ROOT / "sitemap.xml",
    ROOT / "feed.xml",
]

# JSON files that must parse successfully (hard-fail checks).
JSON_FILES = [
    ROOT / "data" / "search-index.json",
    ROOT / "data" / "archive.json",
    ROOT / "data" / "guide-topics.json",
]

# Regex that detects a valid HTML title element.
TITLE_RE = re.compile(r"<title\b[^>]*>.*?</title>", re.IGNORECASE | re.DOTALL)
# Regex that detects the meta description tag.
DESC_RE = re.compile(
    r"<meta\s+[^>]*name=[\"']description[\"'][^>]*>",
    re.IGNORECASE,
)
# Regex that detects canonical link markup.
CANONICAL_RE = re.compile(
    r"<link\s+[^>]*rel=[\"']canonical[\"'][^>]*>",
    re.IGNORECASE,
)
# Regex that extracts page-level robots directives.
ROBOTS_RE = re.compile(
    r"<meta\s+[^>]*name=[\"']robots[\"'][^>]*content=[\"']([^\"']*)[\"'][^>]*>",
    re.IGNORECASE,
)

# Public URL prefix used in sitemap.xml.
BASE_URL = "https://oceancloudconsults.com"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def check_xml(files: list[Path]) -> list[str]:
    errors: list[str] = []
    for file_path in files:
        if not file_path.exists():
            errors.append(f"Missing XML file: {rel(file_path)}")
            continue
        try:
            ET.parse(file_path)
        except ET.ParseError as exc:
            errors.append(f"Invalid XML in {rel(file_path)}: {exc}")
    return errors


def check_json(files: list[Path]) -> list[str]:
    errors: list[str] = []
    for file_path in files:
        if not file_path.exists():
            errors.append(f"Missing JSON file: {rel(file_path)}")
            continue
        try:
            json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSON in {rel(file_path)}: {exc}")
    return errors


def sitemap_url_to_file(loc: str) -> Path | None:
    path = loc.replace(BASE_URL, "", 1).strip("/")
    if not path:
        return ROOT / "index.html"

    candidates = [
        ROOT / f"{path}.html",
        ROOT / path,
        ROOT / f"{path}/index.html",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def check_sitemap_noindex(sitemap_file: Path) -> list[str]:
    errors: list[str] = []
    if not sitemap_file.exists():
        return errors

    try:
        tree = ET.parse(sitemap_file)
    except ET.ParseError:
        return errors

    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    for loc_el in tree.findall(".//sm:loc", ns):
        loc = (loc_el.text or "").strip()
        file_path = sitemap_url_to_file(loc)
        if file_path is None or file_path.suffix.lower() != ".html":
            continue

        content = file_path.read_text(encoding="utf-8", errors="ignore")
        robots_match = ROBOTS_RE.search(content)
        robots = robots_match.group(1).lower() if robots_match else ""
        if "noindex" in robots:
            errors.append(f"Sitemap URL points to noindex page: {loc} ({rel(file_path)})")

    return errors


def scan_metadata(html_files: list[Path]) -> dict[str, list[str]]:
    missing_title: list[str] = []
    missing_description: list[str] = []
    missing_canonical: list[str] = []

    for file_path in html_files:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        r = rel(file_path)
        if TITLE_RE.search(content) is None:
            missing_title.append(r)
        if DESC_RE.search(content) is None:
            missing_description.append(r)
        if CANONICAL_RE.search(content) is None:
            missing_canonical.append(r)

    return {
        "title": missing_title,
        "description": missing_description,
        "canonical": missing_canonical,
    }


def format_samples(items: list[str], max_items: int = 12) -> list[str]:
    if not items:
        return ["- none"]
    sample = items[:max_items]
    lines = [f"- {item}" for item in sample]
    if len(items) > max_items:
        lines.append(f"- ... and {len(items) - max_items} more")
    return lines


def build_report(
    html_count: int,
    xml_errors: list[str],
    json_errors: list[str],
    metadata: dict[str, list[str]],
) -> str:
    # UTC timestamp shown in the generated report header.
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    # Hard failures determine process exit code for CI behavior.
    hard_fail_count = len(xml_errors) + len(json_errors)

    lines = [
        "# Content QA Report",
        "",
        f"Generated: {now}",
        f"HTML files scanned: {html_count}",
        f"Hard-fail issues: {hard_fail_count}",
        "",
        "## Hard Checks",
        "",
        "### XML validation",
    ]

    if xml_errors:
        lines.extend([f"- {err}" for err in xml_errors])
    else:
        lines.append("- OK")

    lines.extend(["", "### JSON validation"])
    if json_errors:
        lines.extend([f"- {err}" for err in json_errors])
    else:
        lines.append("- OK")

    lines.extend([
        "",
        "## Advisory SEO Checks",
        "",
        f"Missing title tag: {len(metadata['title'])}",
    ])
    lines.extend(format_samples(metadata["title"]))

    lines.extend([
        "",
        f"Missing meta description: {len(metadata['description'])}",
    ])
    lines.extend(format_samples(metadata["description"]))

    lines.extend([
        "",
        f"Missing canonical link: {len(metadata['canonical'])}",
    ])
    lines.extend(format_samples(metadata["canonical"]))

    return "\n".join(lines) + "\n"


def main() -> int:
    # Scope of HTML files checked for advisory metadata quality.
    html_files = sorted(ROOT.glob("*.html")) + sorted((ROOT / "articles").glob("*.html"))

    xml_errors = check_xml(XML_FILES)
    xml_errors.extend(check_sitemap_noindex(ROOT / "sitemap.xml"))
    json_errors = check_json(JSON_FILES)
    metadata = scan_metadata(html_files)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        build_report(len(html_files), xml_errors, json_errors, metadata),
        encoding="utf-8",
    )

    hard_fail_count = len(xml_errors) + len(json_errors)
    print(f"[ok] wrote QA report: {rel(REPORT)}")
    print(f"[ok] hard-fail issues: {hard_fail_count}")

    return 1 if hard_fail_count else 0


if __name__ == "__main__":
    sys.exit(main())
