#!/usr/bin/env python3
"""
check-links.py
==============
Scans all HTML files in the repo for internal relative links and reports
any that point to a file that doesn't exist on disk.

Checks:
  - href="..." in <a> tags (skips absolute URLs, mailto:, tel:, #anchors)
  - src="..."  in <img>, <script>, <link> tags

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

ROOT = Path(__file__).parent.parent

HREF_RE = re.compile(r'href=["\']([^"\'#?]+)', re.IGNORECASE)
SRC_RE  = re.compile(r'src=["\']([^"\']+)',  re.IGNORECASE)

SKIP_SCHEMES = {"http", "https", "mailto", "tel", "javascript", "data"}

HTML_FILES = sorted(ROOT.glob("**/*.html"))


def resolve(base: Path, target: str) -> Path:
    """Resolve a relative URL against the HTML file's directory."""
    target = unquote(target.split("?")[0].split("#")[0])
    if target.startswith("/"):
        return ROOT / target.lstrip("/")
    return (base.parent / target).resolve()


def check_file(html: Path) -> list[str]:
    broken = []
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


def main(strict: bool = False) -> None:
    print(f"Checking {len(HTML_FILES)} HTML files for broken internal links…\n")
    all_broken: list[str] = []

    for html in HTML_FILES:
        broken = check_file(html)
        all_broken.extend(broken)

    if all_broken:
        print(f"⚠️  {len(all_broken)} broken link(s) found:\n")
        for line in all_broken:
            print(line)
    else:
        print("✓ No broken internal links found.")

    print(f"\nScanned {len(HTML_FILES)} files.")

    if strict and all_broken:
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true",
                        help="Exit 1 if any broken links are found")
    args = parser.parse_args()
    main(strict=args.strict)
