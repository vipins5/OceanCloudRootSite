#!/usr/bin/env python3
"""
Generate a content QA report for OceanCloud.

Hard-fail checks:
- XML parseability for sitemap.xml and feed.xml
- JSON parseability for key data index files
- Sitemap URLs must not point at pages with a robots noindex directive

Advisory checks (warnings only):
- Missing <title>
- Missing <meta name="description"> on indexable pages
- Missing canonical link tag on indexable pages
- Overlong title or meta description snippets on indexable pages
- Missing Open Graph or Twitter preview tags on indexable pages
- Article JSON-LD missing mainEntityOfPage
- Search index URLs pointing at missing local pages or noindex pages
"""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html import unescape
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
# Regex that extracts the text inside the first HTML title element.
TITLE_TEXT_RE = re.compile(r"<title\b[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
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
# Regex that extracts JSON-LD script bodies.
JSON_LD_RE = re.compile(
    r"<script\s+[^>]*type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
    re.IGNORECASE | re.DOTALL,
)

OG_REQUIRED = ("og:title", "og:description", "og:url", "og:image")
TWITTER_REQUIRED = (
    "twitter:card",
    "twitter:title",
    "twitter:description",
    "twitter:image",
)
ARTICLE_TYPES = {"article", "newsarticle", "blogposting"}
MAX_TITLE_CHARS = 70
MAX_DESCRIPTION_CHARS = 180

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


def local_url_to_file(url: str) -> Path | None:
    if not url or url.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    if url.startswith(("http://", "https://")) and not url.startswith(BASE_URL):
        return None

    path = url.replace(BASE_URL, "", 1).split("#", 1)[0].split("?", 1)[0].strip("/")
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
    return ROOT / f"{path}.html" if Path(path).suffix == "" else ROOT / path


def page_is_noindex(file_path: Path) -> bool:
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    robots_match = ROBOTS_RE.search(content)
    robots = robots_match.group(1).lower() if robots_match else ""
    return "noindex" in robots


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

        if page_is_noindex(file_path):
            errors.append(f"Sitemap URL points to noindex page: {loc} ({rel(file_path)})")

    return errors


def extract_meta_content(content: str, attr_name: str, attr_value: str) -> str | None:
    key = re.escape(attr_value)
    before_content = re.search(
        rf"<meta\s+[^>]*{attr_name}=[\"']{key}[\"'][^>]*content=[\"']([^\"']*)[\"'][^>]*>",
        content,
        re.IGNORECASE,
    )
    if before_content:
        return unescape(before_content.group(1)).strip()

    after_content = re.search(
        rf"<meta\s+[^>]*content=[\"']([^\"']*)[\"'][^>]*{attr_name}=[\"']{key}[\"'][^>]*>",
        content,
        re.IGNORECASE,
    )
    if after_content:
        return unescape(after_content.group(1)).strip()

    return None


def has_meta(content: str, attr_name: str, attr_value: str) -> bool:
    return extract_meta_content(content, attr_name, attr_value) is not None


def normalized_len(value: str) -> int:
    return len(" ".join(unescape(value).split()))


def flatten_jsonld(node: object) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    if isinstance(node, dict):
        items.append(node)
        for child in node.values():
            items.extend(flatten_jsonld(child))
    elif isinstance(node, list):
        for child in node:
            items.extend(flatten_jsonld(child))
    return items


def scan_article_jsonld(file_path: Path, content: str) -> list[str]:
    missing_main_entity: list[str] = []
    if not rel(file_path).startswith("articles/"):
        return missing_main_entity

    article_nodes: list[dict[str, object]] = []
    for match in JSON_LD_RE.finditer(content):
        try:
            data = json.loads(unescape(match.group(1)).strip())
        except json.JSONDecodeError:
            continue
        for node in flatten_jsonld(data):
            node_type = node.get("@type")
            node_types = node_type if isinstance(node_type, list) else [node_type]
            if any(str(item).lower() in ARTICLE_TYPES for item in node_types):
                article_nodes.append(node)

    if article_nodes and any("mainEntityOfPage" not in node for node in article_nodes):
        missing_main_entity.append(rel(file_path))
    return missing_main_entity


def scan_metadata(html_files: list[Path]) -> dict[str, list[str]]:
    missing_title: list[str] = []
    missing_description: list[str] = []
    missing_canonical: list[str] = []
    long_title: list[str] = []
    long_description: list[str] = []
    missing_og: list[str] = []
    missing_twitter: list[str] = []
    missing_article_main_entity: list[str] = []

    for file_path in html_files:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        r = rel(file_path)
        if TITLE_RE.search(content) is None:
            missing_title.append(r)
        robots_match = ROBOTS_RE.search(content)
        robots = robots_match.group(1).lower() if robots_match else ""
        missing_article_main_entity.extend(scan_article_jsonld(file_path, content))
        if "noindex" in robots:
            continue
        title_match = TITLE_TEXT_RE.search(content)
        title = title_match.group(1) if title_match else ""
        if title_match and normalized_len(title) > MAX_TITLE_CHARS:
            long_title.append(r)
        if DESC_RE.search(content) is None:
            missing_description.append(r)
        else:
            description = extract_meta_content(content, "name", "description") or ""
            if normalized_len(description) > MAX_DESCRIPTION_CHARS:
                long_description.append(r)
        if CANONICAL_RE.search(content) is None:
            missing_canonical.append(r)
        missing_og.extend(
            f"{r} ({tag})" for tag in OG_REQUIRED if not has_meta(content, "property", tag)
        )
        missing_twitter.extend(
            f"{r} ({tag})" for tag in TWITTER_REQUIRED if not has_meta(content, "name", tag)
        )

    return {
        "title": missing_title,
        "description": missing_description,
        "canonical": missing_canonical,
        "long_title": long_title,
        "long_description": long_description,
        "og": missing_og,
        "twitter": missing_twitter,
        "article_main_entity": missing_article_main_entity,
    }


def scan_search_index(search_index_file: Path) -> dict[str, list[str]]:
    missing_local_urls: list[str] = []
    noindex_urls: list[str] = []
    if not search_index_file.exists():
        return {"missing": missing_local_urls, "noindex": noindex_urls}

    try:
        entries = json.loads(search_index_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"missing": missing_local_urls, "noindex": noindex_urls}

    if not isinstance(entries, list):
        return {"missing": missing_local_urls, "noindex": noindex_urls}

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        url = str(entry.get("url", "")).strip()
        file_path = local_url_to_file(url)
        if file_path is None:
            continue
        if not file_path.exists():
            missing_local_urls.append(url)
            continue
        if file_path.suffix.lower() == ".html" and page_is_noindex(file_path):
            noindex_urls.append(url)

    return {"missing": missing_local_urls, "noindex": noindex_urls}


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
    search_index: dict[str, list[str]],
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
        f"Missing meta description on indexable pages: {len(metadata['description'])}",
    ])
    lines.extend(format_samples(metadata["description"]))

    lines.extend([
        "",
        f"Missing canonical link on indexable pages: {len(metadata['canonical'])}",
    ])
    lines.extend(format_samples(metadata["canonical"]))

    lines.extend([
        "",
        f"Overlong title tag on indexable pages: {len(metadata['long_title'])}",
    ])
    lines.extend(format_samples(metadata["long_title"]))

    lines.extend([
        "",
        f"Overlong meta description on indexable pages: {len(metadata['long_description'])}",
    ])
    lines.extend(format_samples(metadata["long_description"]))

    lines.extend([
        "",
        f"Missing Open Graph preview tags on indexable pages: {len(metadata['og'])}",
    ])
    lines.extend(format_samples(metadata["og"]))

    lines.extend([
        "",
        f"Missing Twitter preview tags on indexable pages: {len(metadata['twitter'])}",
    ])
    lines.extend(format_samples(metadata["twitter"]))

    lines.extend([
        "",
        f"Article JSON-LD missing mainEntityOfPage: {len(metadata['article_main_entity'])}",
    ])
    lines.extend(format_samples(metadata["article_main_entity"]))

    lines.extend([
        "",
        f"Search index URLs missing local files: {len(search_index['missing'])}",
    ])
    lines.extend(format_samples(search_index["missing"]))

    lines.extend([
        "",
        f"Search index URLs pointing to noindex pages: {len(search_index['noindex'])}",
    ])
    lines.extend(format_samples(search_index["noindex"]))

    return "\n".join(lines) + "\n"


def main() -> int:
    # Scope of HTML files checked for advisory metadata quality.
    html_files = sorted(ROOT.glob("*.html")) + sorted((ROOT / "articles").glob("*.html"))

    xml_errors = check_xml(XML_FILES)
    xml_errors.extend(check_sitemap_noindex(ROOT / "sitemap.xml"))
    json_errors = check_json(JSON_FILES)
    metadata = scan_metadata(html_files)
    search_index = scan_search_index(ROOT / "data" / "search-index.json")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        build_report(len(html_files), xml_errors, json_errors, metadata, search_index),
        encoding="utf-8",
    )

    hard_fail_count = len(xml_errors) + len(json_errors)
    print(f"[ok] wrote QA report: {rel(REPORT)}")
    print(f"[ok] hard-fail issues: {hard_fail_count}")

    return 1 if hard_fail_count else 0


if __name__ == "__main__":
    sys.exit(main())
