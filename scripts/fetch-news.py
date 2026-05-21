#!/usr/bin/env python3
"""
OceanCloud News Fetcher
=======================
Pulls the latest Microsoft SharePoint blog posts and M365 release
communications, rewrites each item in OceanCloud's consulting voice
using the Gemini API, then injects the generated cards into news.html
between the <!-- BEGIN:NEWS-CONTENT --> / <!-- END:NEWS-CONTENT --> markers.

Sources
-------
  Blog  : TechCommunity SharePoint Blog RSS
  Roadmap: Microsoft Release Communications RSS (official M365 release feed)

Required environment variable
------------------------------
  GEMINI_API_KEY  — add as a GitHub Repository Secret
                    (Settings → Secrets and variables → Actions)
"""

import os
import re
import sys
import time
import textwrap
from datetime import datetime, timezone
from html import escape
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

MAX_BLOG        = 6     # how many blog posts to show
MAX_ROADMAP     = 6     # how many roadmap items to show

# Keywords used to filter roadmap RSS for items relevant to an M365 consultancy
RELEVANT_TERMS  = {
    "sharepoint", "copilot", "teams", "viva", "onedrive",
    "power platform", "power apps", "power automate",
    "purview", "entra", "defender", "syntex", "loop",
    "microsoft 365", "m365"
}

NEWS_HTML       = Path(__file__).parent.parent / "news.html"
BEGIN_MARKER    = "<!-- BEGIN:NEWS-CONTENT -->"
END_MARKER      = "<!-- END:NEWS-CONTENT -->"
HEADERS         = {"User-Agent": "OceanCloudBot/1.0 (+https://oceancloudconsults.com)"}

# ── Helpers ───────────────────────────────────────────────────────────────────

def strip_html(text: str) -> str:
    """Remove HTML tags and collapse whitespace."""
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def friendly_date(raw: str) -> str:
    """Return a human-readable date string, or the raw value on failure."""
    if not raw:
        return ""
    from email.utils import parsedate_to_datetime
    try:
        return parsedate_to_datetime(raw).strftime("%B %d, %Y")
    except Exception:
        pass
    try:
        from datetime import datetime
        for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
            try:
                return datetime.strptime(raw[:len(fmt)], fmt).strftime("%B %d, %Y")
            except ValueError:
                continue
    except Exception:
        pass
    return raw[:10]


def is_relevant(entry) -> bool:
    """Return True if a roadmap RSS entry touches our core service areas."""
    haystack = (
        entry.get("title", "") + " " + strip_html(entry.get("summary", ""))
    ).lower()
    return any(term in haystack for term in RELEVANT_TERMS)


# ── Gemini rewrite ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = textwrap.dedent("""\
    You are a senior content writer for OceanCloud, a certified Microsoft 365
    consulting firm in Dallas, TX. OceanCloud specialises in SharePoint, Teams,
    Power Platform, Copilot, and M365 security.

    Rewrite the Microsoft announcement below as a 2–3 sentence expert commentary
    for OceanCloud's news page. Rules:
    • Explain the business impact clearly.
    • Mention how organisations can take advantage (link to OceanCloud's
      expertise where natural, e.g. "migration", "governance", "Copilot rollout").
    • Confident, authoritative, slightly forward-looking tone.
    • Do NOT start with "OceanCloud". Do NOT use bullet points.
    • Output ONLY the 2–3 sentence commentary — nothing else.
""")


def gemini_rewrite(title: str, summary: str) -> str:
    """Call Gemini to rewrite a news item. Falls back to truncated original."""
    if not GEMINI_KEY:
        print("  [warn] GEMINI_API_KEY not set — using original text", file=sys.stderr)
        return (summary[:280] + "…") if len(summary) > 280 else summary

    body = f"Title: {title}\n\nOriginal text: {summary[:600]}"
    payload = {
        "contents": [
            {"parts": [{"text": SYSTEM_PROMPT + "\n\n" + body}]}
        ],
        "generationConfig": {
            "temperature": 0.65,
            "maxOutputTokens": 220,
        },
    }
    try:
        resp = requests.post(GEMINI_URL, json=payload, timeout=20)
        resp.raise_for_status()
        return (
            resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        )
    except Exception as exc:
        print(f"  [warn] Gemini error: {exc}", file=sys.stderr)
        return (summary[:280] + "…") if len(summary) > 280 else summary


# ── Fetchers ──────────────────────────────────────────────────────────────────

def fetch_blog() -> list[dict]:
    """Fetch the latest SharePoint TechCommunity blog posts via RSS."""
    print("Fetching SharePoint blog RSS…")
    try:
        feed = feedparser.parse(BLOG_RSS_URL)
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
        print(f"  → {len(posts)} blog posts")
        return posts
    except Exception as exc:
        print(f"  [error] Blog fetch failed: {exc}", file=sys.stderr)
        return []


def fetch_roadmap() -> list[dict]:
    """Fetch relevant M365 roadmap items from the official Release Comms RSS."""
    print("Fetching M365 Release Communications RSS…")
    try:
        feed = feedparser.parse(ROADMAP_RSS_URL)
        items = []
        for entry in feed.entries:
            if not is_relevant(entry):
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
        print(f"  → {len(items)} roadmap items (after relevance filter)")
        return items
    except Exception as exc:
        print(f"  [error] Roadmap fetch failed: {exc}", file=sys.stderr)
        return []


# ── HTML generation ───────────────────────────────────────────────────────────

def card_html(item: dict, commentary: str) -> str:
    """Return the HTML for one news card."""
    date_str = friendly_date(item["date"])
    return f"""\
      <article class="news-card glass">
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


def build_content(items: list[dict]) -> str:
    """Wrap cards in the injectable content block."""
    now = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    cards = "\n".join(card_html(it, it["_commentary"]) for it in items)
    return (
        f"{BEGIN_MARKER}\n"
        f'    <div class="news-grid stagger-grid" id="news-grid">\n'
        f"{cards}\n"
        f"    </div>\n"
        f'    <p class="news-updated">Last updated: {now} &nbsp;&middot;&nbsp; '
        f'Sources: <a href="https://techcommunity.microsoft.com/category/content_management/blog/spblog" '
        f'target="_blank" rel="noopener">Microsoft TechCommunity SharePoint Blog</a> &amp; '
        f'<a href="https://www.microsoft.com/en-us/microsoft-365/roadmap" '
        f'target="_blank" rel="noopener">M365 Roadmap</a></p>\n'
        f"{END_MARKER}"
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    if not NEWS_HTML.exists():
        print(f"[error] {NEWS_HTML} not found. Create the page first.", file=sys.stderr)
        sys.exit(1)

    blog_items     = fetch_blog()
    roadmap_items  = fetch_roadmap()
    all_items      = blog_items + roadmap_items

    if not all_items:
        print("No content fetched — skipping update.")
        sys.exit(0)

    print(f"\nRewriting {len(all_items)} items with Gemini…")
    for item in all_items:
        print(f"  • {item['title'][:70]}")
        item["_commentary"] = gemini_rewrite(item["title"], item["summary"])
        time.sleep(0.4)   # stay well under Gemini free-tier rate limits

    new_block = build_content(all_items)

    html = NEWS_HTML.read_text(encoding="utf-8")
    pattern = re.escape(BEGIN_MARKER) + r".*?" + re.escape(END_MARKER)
    updated, n = re.subn(pattern, new_block, html, flags=re.DOTALL)

    if n == 0:
        print(f"[error] Could not find {BEGIN_MARKER!r} in news.html", file=sys.stderr)
        sys.exit(1)

    NEWS_HTML.write_text(updated, encoding="utf-8")
    print(f"\n✓ news.html updated with {len(all_items)} items.")


if __name__ == "__main__":
    main()
