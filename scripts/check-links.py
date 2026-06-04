#!/usr/bin/env python3
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
"""
check-links.py
==============
Scans all HTML files in the repo for internal relative links and reports
any that point to a file that doesn't exist on disk. Also verifies that
article pages include the standard shared script bundle, and all HTML pages
include the consent-gated Google Analytics loader.

Checks:
  - href="..." in <a> tags (skips absolute URLs, mailto:, tel:, #anchors)
  - src="..."  in <img>, <script>, <link> tags
    - required shared scripts in articles/*.html
    - required consent analytics loader in every HTML page

Usage:
    python scripts/check-links.py [--strict]

Exit codes:
  0  no broken links
  1  broken links found (only when --strict)
"""

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlparse, unquote

# Repo root used to resolve relative links from HTML files.
ROOT = Path(__file__).parent.parent

# Regex to capture href values while ignoring inline anchors and query strings.
HREF_RE = re.compile(r'href=["\']([^"\'#?]+)', re.IGNORECASE)
# Regex to capture src values for assets (scripts, images, stylesheets).
SRC_RE  = re.compile(r'src=["\']([^"\']+)',  re.IGNORECASE)

# URI schemes that should never be validated as local filesystem paths.
SKIP_SCHEMES = {"http", "https", "mailto", "tel", "javascript", "data"}
# Required script bundle that must appear in article pages for consistent UX/features.
REQUIRED_ARTICLE_SCRIPTS = (
    "../js/main.js",
    "../js/consent.js",
    "../js/chat.js",
    "../js/particles.js",
    "../js/weather.js",
    "../js/article.js",
    "../js/comments.js",
)

# Google Analytics is intentionally loaded only through js/consent.js after the
# visitor accepts cookies. Every HTML page should include that loader.
ROOT_CONSENT_SCRIPT = "js/consent.js"
ARTICLE_CONSENT_SCRIPT = "../js/consent.js"

# Folders to exclude from HTML scans.
IGNORED_PARTS = {".git", "node_modules", ".wrangler", "dist", "build"}

# Precomputed list of HTML files that are in scope for link checks.
HTML_FILES = sorted(
    path for path in ROOT.glob("**/*.html")
    if not any(part in IGNORED_PARTS for part in path.relative_to(ROOT).parts)
)


def resolve(base: Path, target: str) -> Path:
    """Resolve a relative URL against the HTML file's directory."""
    target = unquote(target.split("?")[0].split("#")[0])
    if target.startswith("/"):
        return ROOT / target.lstrip("/")
    return (base.parent / target).resolve()


def check_file(html: Path) -> list[str]:
    # Accumulates unresolved local links found in this specific HTML file.
    broken = []
    # Raw HTML content being scanned with regex patterns.
    text   = html.read_text(encoding="utf-8", errors="ignore")

    for pattern in (HREF_RE, SRC_RE):
        for m in pattern.finditer(text):
            raw = m.group(1).strip()
            if not raw:
                continue
            parsed = urlparse(raw)
            if parsed.scheme in SKIP_SCHEMES or parsed.scheme:
                continue        # absolute or special — skip
            if raw.startswith("#"):
                continue        # anchor — skip

            target = resolve(html, raw)

            # If the path has no suffix, try .html
            if not target.suffix and not target.exists():
                target = target.with_suffix(".html")

            if not target.exists():
                rel_html = html.relative_to(ROOT)
                broken.append(f"  {rel_html}  →  {raw}")

    return broken


def check_article_scripts(html: Path) -> list[str]:
    rel = html.relative_to(ROOT)
    if len(rel.parts) < 2 or rel.parts[0] != "articles":
        return []

    text = html.read_text(encoding="utf-8", errors="ignore")
    missing = [script for script in REQUIRED_ARTICLE_SCRIPTS if script not in text]
    if not missing:
        return []

    return [f"  {rel}  missing standard script(s): {', '.join(missing)}"]


def check_analytics_loader(html: Path) -> list[str]:
    rel = html.relative_to(ROOT)
    text = html.read_text(encoding="utf-8", errors="ignore")
    required = ARTICLE_CONSENT_SCRIPT if len(rel.parts) > 1 and rel.parts[0] == "articles" else ROOT_CONSENT_SCRIPT

    if required in text:
        return []

    return [f"  {rel}  missing analytics consent loader: {required}"]


def main(strict: bool = False) -> None:
    print(f"Checking {len(HTML_FILES)} HTML files for broken internal links…\n")
    # Global list of broken link findings across all scanned files.
    all_broken: list[str] = []
    # Global list of missing required article script bundle entries.
    all_script_issues: list[str] = []
    # Global list of missing consent-gated Google Analytics loader entries.
    all_analytics_issues: list[str] = []

    for html in HTML_FILES:
        broken = check_file(html)
        all_broken.extend(broken)
        all_script_issues.extend(check_article_scripts(html))
        all_analytics_issues.extend(check_analytics_loader(html))

    if all_broken:
        print(f"⚠️  {len(all_broken)} broken link(s) found:\n")
        for line in all_broken:
            print(line)
    else:
        print("✓ No broken internal links found.")

    if all_script_issues:
        print(f"\n⚠️  {len(all_script_issues)} article script issue(s) found:\n")
        for line in all_script_issues:
            print(line)
    else:
        print("✓ All article pages include the standard script bundle.")

    if all_analytics_issues:
        print(f"\n⚠️  {len(all_analytics_issues)} analytics loader issue(s) found:\n")
        for line in all_analytics_issues:
            print(line)
    else:
        print("✓ All HTML pages include the analytics consent loader.")

    print(f"\nScanned {len(HTML_FILES)} files.")

    if strict and (all_broken or all_script_issues or all_analytics_issues):
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true",
                        help="Exit 1 if any broken links are found")
    args = parser.parse_args()
    main(strict=args.strict)
