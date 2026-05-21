#!/usr/bin/env python3
"""
OceanCloud News Fetcher
=======================
Pulls the latest Microsoft SharePoint blog posts and M365 release
communications, rewrites each item in OceanCloud's consulting voice
using the Gemini API, then:
  1. Injects the latest cards into news.html (replaces each week)
  2. Appends new items to data/archive.json (cumulative, deduplicated)
  3. Regenerates archive.html from the full archive grouped by month

Sources
-------
  Blog   : TechCommunity SharePoint Blog RSS
  Roadmap: Microsoft Release Communications RSS (official M365 release feed)

Required environment variable
------------------------------
  GEMINI_API_KEY  — add as a GitHub Repository Secret
"""

import json
import os
import re
import sys
import time
import textwrap
from datetime import datetime, timezone
from html import escape, unescape
from pathlib import Path

import requests
import feedparser

# ── Configuration ────────────────────────────────────────────────────────────

GEMINI_KEY      = os.environ.get("GEMINI_API_KEY", "")
GEMINI_URL      = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent?key=" + GEMINI_KEY
)

BLOG_RSS_URL    = (
    "https://techcommunity.microsoft.com"
    "/t5/s/gxcuf89792/rss/board?board.id=SPBlog"
)
ROADMAP_RSS_URL = (
    "https://www.microsoft.com/releasecommunications/api/v2/m365/rss"
)

MAX_BLOG        = 6
MAX_ROADMAP     = 6

RELEVANT_TERMS  = {
    "sharepoint", "copilot", "teams", "viva", "onedrive",
    "power platform", "power apps", "power automate",
    "purview", "entra", "defender", "syntex", "loop",
    "microsoft 365", "m365"
}

ROOT            = Path(__file__).parent.parent
NEWS_HTML       = ROOT / "news.html"
ARCHIVE_HTML    = ROOT / "archive.html"
ARCHIVE_JSON    = ROOT / "data" / "archive.json"

NEWS_BEGIN      = "<!-- BEGIN:NEWS-CONTENT -->"
NEWS_END        = "<!-- END:NEWS-CONTENT -->"
ARCHIVE_BEGIN   = "<!-- BEGIN:ARCHIVE-CONTENT -->"
ARCHIVE_END     = "<!-- END:ARCHIVE-CONTENT -->"

HEADERS         = {"User-Agent": "OceanCloudBot/1.0 (+https://oceancloudconsults.com)"}

# ── Helpers ───────────────────────────────────────────────────────────────────

def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)          # convert &nbsp; &amp; &#x27; etc. to real chars
    return re.sub(r"\s+", " ", text).strip()


def friendly_date(raw: str) -> str:
    if not raw:
        return ""
    from email.utils import parsedate_to_datetime
    try:
        return parsedate_to_datetime(raw).strftime("%B %d, %Y")
    except Exception:
        pass
    try:
        for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
            try:
                return datetime.strptime(raw[:len(fmt)], fmt).strftime("%B %d, %Y")
            except ValueError:
                continue
    except Exception:
        pass
    return raw[:10]


def month_parts(raw: str) -> tuple[str, str]:
    """Return (sort_key '2026-05', label 'May 2026') from an RSS date string."""
    from email.utils import parsedate_to_datetime
    try:
        dt = parsedate_to_datetime(raw)
        return dt.strftime("%Y-%m"), dt.strftime("%B %Y")
    except Exception:
        pass
    try:
        for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(raw[:len(fmt)], fmt)
                return dt.strftime("%Y-%m"), dt.strftime("%B %Y")
            except ValueError:
                continue
    except Exception:
        pass
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m"), now.strftime("%B %Y")


# Keyword → SVG thumbnail mapping (checked in order, first match wins)
TOPIC_IMAGES: list[tuple[str, str]] = [
    ("copilot",        "copilot"),
    ("viva",           "viva"),
    ("onedrive",       "onedrive"),
    ("power automate", "power-platform"),
    ("power apps",     "power-platform"),
    ("power platform", "power-platform"),
    ("purview",        "purview"),
    ("entra",          "purview"),
    ("defender",       "purview"),
    ("teams",          "teams"),
    ("loop",           "teams"),
    ("syntex",         "sharepoint"),
    ("intranet",       "sharepoint"),
    ("sharepoint",     "sharepoint"),
    ("document",       "sharepoint"),
]


def image_for_item(item: dict) -> str:
    haystack = (item["title"] + " " + item.get("summary", "")).lower()
    for keyword, img_name in TOPIC_IMAGES:
        if keyword in haystack:
            return f"assets/news/{img_name}.svg"
    return "assets/news/m365-roadmap.svg" if item["css_tag"] == "tag-roadmap" else "assets/news/m365.svg"


def topic_for_item(item: dict) -> str:
    haystack = (item["title"] + " " + item.get("summary", "")).lower()
    for keyword, img_name in TOPIC_IMAGES:
        if keyword in haystack:
            return img_name  # e.g. "sharepoint", "teams", "copilot", "power-platform" …
    return "other"


def is_relevant(entry) -> bool:
    haystack = (
        entry.get("title", "") + " " + strip_html(entry.get("summary", ""))
    ).lower()
    return any(term in haystack for term in RELEVANT_TERMS)


# ── Gemini rewrite ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = textwrap.dedent("""\
    You are a senior content writer for OceanCloud, a certified Microsoft 365
    consulting firm in Dallas, TX. OceanCloud specialises in SharePoint, Teams,
    Power Platform, Copilot, and M365 security.

    Rewrite the Microsoft announcement below as a 2-3 sentence expert commentary
    for OceanCloud's news page. Rules:
    - Explain the business impact clearly.
    - Mention how organisations can take advantage (link to OceanCloud's
      expertise where natural, e.g. "migration", "governance", "Copilot rollout").
    - Confident, authoritative, slightly forward-looking tone.
    - Do NOT start with "OceanCloud". Do NOT use bullet points.
    - Output ONLY the 2-3 sentence commentary, nothing else.
""")


def gemini_rewrite(title: str, summary: str) -> str:
    if not GEMINI_KEY:
        print("  [warn] GEMINI_API_KEY not set — using original text", file=sys.stderr)
        return (summary[:280] + "…") if len(summary) > 280 else summary

    body = f"Title: {title}\n\nOriginal text: {summary[:600]}"
    payload = {
        "contents": [{"parts": [{"text": SYSTEM_PROMPT + "\n\n" + body}]}],
        "generationConfig": {"temperature": 0.65, "maxOutputTokens": 220},
    }
    try:
        resp = requests.post(GEMINI_URL, json=payload, timeout=20)
        resp.raise_for_status()
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as exc:
        print(f"  [warn] Gemini error: {exc}", file=sys.stderr)
        return (summary[:280] + "…") if len(summary) > 280 else summary


# ── Fetchers ──────────────────────────────────────────────────────────────────

def fetch_blog() -> list[dict]:
    print("Fetching SharePoint blog RSS…")
    print(f"  URL: {BLOG_RSS_URL}")
    try:
        feed = feedparser.parse(BLOG_RSS_URL, request_headers=HEADERS)
        status = getattr(feed, "status", "unknown")
        bozo   = getattr(feed, "bozo", False)
        print(f"  HTTP status: {status}  |  bozo: {bozo}  |  entries: {len(feed.entries)}")
        if bozo and not feed.entries:
            print(f"  [warn] bozo_exception: {getattr(feed, 'bozo_exception', '')}", file=sys.stderr)
        posts = []
        for entry in feed.entries[:MAX_BLOG]:
            posts.append({
                "title":   entry.get("title", "Untitled"),
                "url":     entry.get("link", "#"),
                "date":    entry.get("published", ""),
                "summary": strip_html(entry.get("summary", ""))[:600],
                "source":  "SharePoint Blog",
                "css_tag": "tag-blog",
            })
        print(f"  → {len(posts)} blog posts selected")
        return posts
    except Exception as exc:
        print(f"  [error] Blog fetch failed: {exc}", file=sys.stderr)
        return []


def fetch_roadmap() -> list[dict]:
    print("Fetching M365 Release Communications RSS…")
    print(f"  URL: {ROADMAP_RSS_URL}")
    try:
        feed = feedparser.parse(ROADMAP_RSS_URL, request_headers=HEADERS)
        status = getattr(feed, "status", "unknown")
        bozo   = getattr(feed, "bozo", False)
        print(f"  HTTP status: {status}  |  bozo: {bozo}  |  entries: {len(feed.entries)}")
        if bozo and not feed.entries:
            print(f"  [warn] bozo_exception: {getattr(feed, 'bozo_exception', '')}", file=sys.stderr)
        items, matched = [], 0
        for entry in feed.entries:
            if is_relevant(entry):
                matched += 1
            else:
                continue
            items.append({
                "title":   entry.get("title", "Untitled"),
                "url":     entry.get("link", "https://www.microsoft.com/en-us/microsoft-365/roadmap"),
                "date":    entry.get("published", ""),
                "summary": strip_html(entry.get("summary", ""))[:600],
                "source":  "M365 Roadmap",
                "css_tag": "tag-roadmap",
            })
            if len(items) >= MAX_ROADMAP:
                break
        print(f"  → {len(items)} roadmap items (relevance matched {matched}/{len(feed.entries)})")
        return items
    except Exception as exc:
        print(f"  [error] Roadmap fetch failed: {exc}", file=sys.stderr)
        return []


# ── News HTML ─────────────────────────────────────────────────────────────────

def card_html(item: dict, commentary: str) -> str:
    date_str    = friendly_date(item["date"])
    img         = image_for_item(item)
    source_slug = "roadmap" if item["css_tag"] == "tag-roadmap" else "blog"
    topic_slug  = topic_for_item(item)
    return f"""\
      <article class="news-card glass" data-source="{source_slug}" data-topic="{topic_slug}">
        <div class="nc-image-wrap">
          <img class="nc-image" src="{escape(img)}" alt="{escape(item['source'])}" loading="lazy" />
        </div>
        <div class="nc-meta">
          <span class="nc-tag {item['css_tag']}">{escape(item['source'])}</span>
          {f'<span class="nc-date">{escape(date_str)}</span>' if date_str else ''}
        </div>
        <h3 class="nc-title">
          <a href="{escape(item['url'])}" target="_blank" rel="noopener noreferrer">
            {escape(item['title'])}
          </a>
        </h3>
        <p class="nc-body">{escape(commentary)}</p>
        <a class="nc-link" href="{escape(item['url'])}" target="_blank" rel="noopener noreferrer">
          Read on Microsoft &#8599;
        </a>
      </article>"""


def build_news_block(items: list[dict]) -> str:
    now = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    cards = "\n".join(card_html(it, it["_commentary"]) for it in items)
    return (
        f"{NEWS_BEGIN}\n"
        f'    <div class="news-grid" id="news-grid">\n'
        f"{cards}\n"
        f"    </div>\n"
        f'    <p class="news-updated">Last updated: {now} &nbsp;&middot;&nbsp; '
        f'Sources: <a href="https://techcommunity.microsoft.com/category/content_management/blog/spblog" '
        f'target="_blank" rel="noopener">Microsoft TechCommunity SharePoint Blog</a> &amp; '
        f'<a href="https://www.microsoft.com/en-us/microsoft-365/roadmap" '
        f'target="_blank" rel="noopener">M365 Roadmap</a> &nbsp;&middot;&nbsp; '
        f'<a href="archive">View full archive &#8594;</a></p>\n'
        f"{NEWS_END}"
    )


# ── Archive ───────────────────────────────────────────────────────────────────

def load_archive() -> list[dict]:
    if not ARCHIVE_JSON.exists():
        return []
    try:
        return json.loads(ARCHIVE_JSON.read_text(encoding="utf-8")).get("items", [])
    except Exception:
        return []


def save_archive(items: list[dict]) -> None:
    ARCHIVE_JSON.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "items":        items,
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }
    ARCHIVE_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def merge_archive(archive: list[dict], new_items: list[dict]) -> tuple[list[dict], int]:
    """Add new items to archive, deduped by URL. Returns (updated, added_count)."""
    seen = {it["url"] for it in archive}
    added = 0
    for it in new_items:
        if it["url"] in seen:
            continue
        sort_key, label = month_parts(it["date"])
        archive.append({
            "title":         it["title"],
            "url":           it["url"],
            "date_friendly": friendly_date(it["date"]) or label,
            "month_sort":    sort_key,
            "month_label":   label,
            "source":        it["source"],
            "css_tag":       it["css_tag"],
        })
        seen.add(it["url"])
        added += 1
    archive.sort(key=lambda x: (x.get("month_sort", ""), x.get("date_friendly", "")), reverse=True)
    return archive, added


def build_archive_block(archive: list[dict]) -> str:
    if not archive:
        return (
            f"{ARCHIVE_BEGIN}\n"
            "    <p class=\"archive-empty\">No archived articles yet — check back after the next weekly update.</p>\n"
            f"{ARCHIVE_END}"
        )

    # Group by month_sort preserving newest-first order
    groups: dict[str, dict] = {}
    order: list[str] = []
    for it in archive:
        key = it["month_sort"]
        if key not in groups:
            groups[key] = {"label": it["month_label"], "items": []}
            order.append(key)
        groups[key]["items"].append(it)

    parts = []
    for key in order:
        g = groups[key]
        count = len(g["items"])
        rows = ""
        for it in g["items"]:
            short = "Blog" if "Blog" in it["source"] else "M365"
            rows += (
                f'        <li class="am-item">\n'
                f'          <span class="nc-tag {escape(it["css_tag"])}">{short}</span>\n'
                f'          <a href="{escape(it["url"])}" target="_blank" rel="noopener noreferrer">'
                f'{escape(it["title"])}</a>\n'
                f'          <span class="am-date">{escape(it["date_friendly"])}</span>\n'
                f'        </li>\n'
            )
        parts.append(
            f'    <div class="archive-month reveal">\n'
            f'      <h3 class="am-heading">\n'
            f'        <span class="grad-text">{escape(g["label"])}</span>\n'
            f'        <span class="am-count">{count} item{"s" if count != 1 else ""}</span>\n'
            f'      </h3>\n'
            f'      <ul class="am-list">\n'
            f'{rows}'
            f'      </ul>\n'
            f'    </div>\n'
        )

    now = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    return (
        f"{ARCHIVE_BEGIN}\n"
        + "".join(parts)
        + f'    <p class="news-updated">Archive updated: {now} &nbsp;&middot;&nbsp; {len(archive)} total items</p>\n'
        + f"{ARCHIVE_END}"
    )


def inject(html: str, begin: str, end: str, block: str) -> tuple[str, int]:
    pattern = re.escape(begin) + r".*?" + re.escape(end)
    return re.subn(pattern, block, html, flags=re.DOTALL)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    if not NEWS_HTML.exists():
        print(f"[error] {NEWS_HTML} not found.", file=sys.stderr)
        sys.exit(1)

    blog_items    = fetch_blog()
    roadmap_items = fetch_roadmap()
    all_items     = blog_items + roadmap_items

    if not all_items:
        print("[warn] No content fetched — news.html not updated.", file=sys.stderr)
        sys.exit(1)

    print(f"\nRewriting {len(all_items)} items with Gemini…")
    for item in all_items:
        print(f"  • {item['title'][:70]}")
        item["_commentary"] = gemini_rewrite(item["title"], item["summary"])
        time.sleep(0.4)

    # ── Update news.html ──────────────────────────────────────────────────────
    html = NEWS_HTML.read_text(encoding="utf-8")
    updated, n = inject(html, NEWS_BEGIN, NEWS_END, build_news_block(all_items))
    if n == 0:
        print(f"[error] News markers not found in news.html", file=sys.stderr)
        sys.exit(1)
    NEWS_HTML.write_text(updated, encoding="utf-8")
    print(f"\n✓ news.html updated with {len(all_items)} items.")

    # ── Update archive ────────────────────────────────────────────────────────
    print("\nUpdating archive…")
    archive = load_archive()
    archive, added = merge_archive(archive, all_items)
    save_archive(archive)
    print(f"  → {added} new items added ({len(archive)} total in archive)")

    if ARCHIVE_HTML.exists():
        arc_html = ARCHIVE_HTML.read_text(encoding="utf-8")
        updated_arc, m = inject(arc_html, ARCHIVE_BEGIN, ARCHIVE_END, build_archive_block(archive))
        if m == 0:
            print("[warn] Archive markers not found in archive.html", file=sys.stderr)
        else:
            ARCHIVE_HTML.write_text(updated_arc, encoding="utf-8")
            print(f"✓ archive.html updated with {len(archive)} total items.")
    else:
        print("[warn] archive.html not found — skipping.", file=sys.stderr)


if __name__ == "__main__":
    main()
