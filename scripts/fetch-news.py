#!/usr/bin/env python3
"""
OceanCloud News Fetcher
=======================
Pulls the latest Microsoft SharePoint blog posts and M365 release
communications, rewrites each item in OceanCloud's consulting voice
using an AI API, then:
    1. Generates a standalone article page in articles/news-*.html for users
  2. Injects the latest cards into news.html (replaces each run)
  3. Appends new items to data/archive.json (cumulative, deduplicated)
  4. Regenerates archive.html from the full archive grouped by month
    5. Keeps short generated news detail pages out of sitemap.xml by default

Sources
-------
  Blog   : TechCommunity SharePoint Blog RSS
  Roadmap: Microsoft Release Communications RSS (official M365 release feed)

AI rewrite engines (tried in order, first available wins)
----------------------------------------------------------
    OPENAI_API_KEY    — ChatGPT gpt-4o-mini
    GEMINI_API_KEY    — Google Gemini 2.0 Flash
  None set          — uses truncated original RSS text

Add secrets at: GitHub repo → Settings → Secrets → Actions
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
from urllib.parse import urljoin

import requests
import feedparser

# ── Configuration ────────────────────────────────────────────────────────────

# Optional Gemini API key for AI rewriting fallback.
GEMINI_KEY      = os.environ.get("GEMINI_API_KEY", "")
# Gemini endpoint URL pre-bound with API key query parameter.
GEMINI_URL      = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent?key=" + GEMINI_KEY
)

# Optional OpenAI API key (preferred rewrite engine).
OPENAI_KEY      = os.environ.get("OPENAI_API_KEY", "")

# RSS source for official SharePoint blog announcements.
BLOG_RSS_URL    = (
    "https://techcommunity.microsoft.com"
    "/t5/s/gxcuf89792/rss/board?board.id=SPBlog"
)
# RSS source for Microsoft 365 release communications.
ROADMAP_RSS_URL = (
    "https://www.microsoft.com/releasecommunications/api/v2/m365/rss"
)

# Maximum SharePoint blog items fetched per run.
MAX_BLOG        = 6
# Maximum roadmap items fetched per run.
MAX_ROADMAP     = 6

# Topic terms used to filter relevant news content.
RELEVANT_TERMS  = {
    "sharepoint", "copilot", "teams", "viva", "onedrive",
    "power platform", "power apps", "power automate",
    "purview", "entra", "defender", "syntex", "loop",
    "microsoft 365", "m365"
}

# Repo root used for all generated content paths.
ROOT            = Path(__file__).parent.parent
# News landing page where latest cards are injected.
NEWS_HTML       = ROOT / "news.html"
# Archive landing page rebuilt from full archive data.
ARCHIVE_HTML    = ROOT / "archive.html"
# Canonical JSON archive store (deduplicated and cumulative).
ARCHIVE_JSON    = ROOT / "data" / "archive.json"
# Directory where generated article pages are written.
ARTICLES_DIR    = ROOT / "articles"
# Sitemap file updated with newly generated article URLs.
SITEMAP_XML     = ROOT / "sitemap.xml"
# Search index used for site-wide search discoverability.
SEARCH_INDEX    = ROOT / "data" / "search-index.json"
# Canonical public base URL for generated links/canonical tags.
SITE_BASE_URL   = "https://oceancloudconsults.com"
# Generated news detail pages are short recaps for human readers coming from the
# news/archive pages. Keep Google focused on the stronger hub and guide pages.
INDEX_NEWS_ARTICLES = False

# Marker comments delimiting auto-managed news block in news.html.
NEWS_BEGIN      = "<!-- BEGIN:NEWS-CONTENT -->"
NEWS_END        = "<!-- END:NEWS-CONTENT -->"
# Marker comments delimiting auto-managed archive block in archive.html.
ARCHIVE_BEGIN   = "<!-- BEGIN:ARCHIVE-CONTENT -->"
ARCHIVE_END     = "<!-- END:ARCHIVE-CONTENT -->"

# HTTP request headers for RSS and API fetches.
HEADERS         = {"User-Agent": "OceanCloudBot/1.0 (+https://oceancloudconsults.com)"}

# ── Helpers ───────────────────────────────────────────────────────────────────

def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
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


def iso_date(raw: str) -> str:
    """Return YYYY-MM-DD from an RSS date string."""
    if not raw:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    from email.utils import parsedate_to_datetime
    try:
        return parsedate_to_datetime(raw).strftime("%Y-%m-%d")
    except Exception:
        pass
    try:
        for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
            try:
                return datetime.strptime(raw[:len(fmt)], fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
    except Exception:
        pass
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


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


def slugify(title: str) -> str:
    """Convert a title to a URL-friendly slug (max 60 chars)."""
    s = title.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")[:60]


def article_slug(item: dict) -> str:
    """Generate a unique filename slug: news-YYYY-MM-<title-slug>."""
    sort_key, _ = month_parts(item["date"])
    return f"news-{sort_key}-{slugify(item['title'])}"


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

ARTICLE_IMAGE_FALLBACKS = {
    "copilot": {
        "url": "https://adoption.microsoft.com/wp-content/uploads/2026/05/preview-copilot-hub.jpg",
        "alt": "Microsoft 365 Copilot Hub preview from Microsoft Adoption",
        "caption": "Representative Microsoft 365 Copilot product image from Microsoft Adoption.",
        "source_url": "https://adoption.microsoft.com/en-us/copilot/",
        "source_label": "Microsoft Adoption",
    },
    "edge": {
        "url": "https://learn.microsoft.com/en-us/deployEdge/media/microsoft-edge-configure-the-copilot-new-tab-page/img1.png",
        "alt": "Microsoft Edge Copilot new tab page screenshot",
        "caption": "Representative Microsoft Edge Copilot new tab page screenshot.",
        "source_url": "https://learn.microsoft.com/en-us/deployEdge/microsoft-edge-management-configure-the-copilot-new-tab-page",
        "source_label": "Microsoft Learn",
    },
    "outlook": {
        "url": "https://support.microsoft.com/images/en-us/d42c7f8e-f190-488b-9c43-dd39755d72b5?format=png&w=900",
        "alt": "Microsoft Outlook for Windows toggle screenshot",
        "caption": "Representative Microsoft Outlook for Windows interface screenshot.",
        "source_url": "https://support.microsoft.com/en-us/office/start-using-new-outlook-for-windows-4395454d-cb2f-4c16-bb24-fa4bb36650ae",
        "source_label": "Microsoft Support",
    },
    "purview": {
        "url": "https://learn.microsoft.com/en-us/purview/media/insider-risk-triage.png",
        "alt": "Microsoft Purview Insider Risk Management triage screenshot",
        "caption": "Representative Microsoft Purview Insider Risk Management screenshot.",
        "source_url": "https://learn.microsoft.com/en-us/purview/insider-risk-management",
        "source_label": "Microsoft Learn",
    },
    "teams-bookable": {
        "url": "https://learn.microsoft.com/en-us/microsoftteams/rooms/media/bookable-desks/automatic-association-image.png",
        "alt": "Microsoft Teams bookable desks automatic association screenshot",
        "caption": "Representative Microsoft Teams bookable desks screenshot.",
        "source_url": "https://learn.microsoft.com/en-us/microsoftteams/rooms/bookable-desks",
        "source_label": "Microsoft Learn",
    },
    "teams-interpreter": {
        "url": "https://learn.microsoft.com/en-us/microsoftteams/media/interpreter-agent-diagram-small.png",
        "alt": "Microsoft Teams Interpreter agent architecture diagram",
        "caption": "Representative Microsoft Teams Interpreter agent diagram.",
        "source_url": "https://learn.microsoft.com/en-us/microsoftteams/interpreter-agent-teams",
        "source_label": "Microsoft Learn",
    },
    "teams": {
        "url": "https://support.microsoft.com/images/en-us/1966f017-c609-407a-9029-48624089e9b5?format=png&w=900",
        "alt": "Microsoft Teams product basics screenshot",
        "caption": "Representative Microsoft Teams product image.",
        "source_url": "https://support.microsoft.com/en-us/teams",
        "source_label": "Microsoft Support",
    },
    "sharepoint": {
        "url": "https://learn.microsoft.com/en-us/sharepoint/sharepointonline/media/teams-sharepoint-interactions.png",
        "alt": "Microsoft diagram showing how Microsoft Entra ID, Teams, and SharePoint relate",
        "caption": "Representative Microsoft SharePoint and Teams relationship diagram.",
        "source_url": "https://learn.microsoft.com/en-us/sharepoint/teams-connected-sites",
        "source_label": "Microsoft Learn",
    },
    "m365": {
        "url": "https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/3892600-work-iq-api-4x3?resMode=sharp2&op_usm=1.5,0.65,15,0&wid=1920&hei=1080&qlt=100&fit=constrain",
        "alt": "Microsoft 365 product image",
        "caption": "Representative Microsoft 365 product image.",
        "source_url": "https://www.microsoft.com/en-us/microsoft-365/roadmap",
        "source_label": "Microsoft 365 Roadmap",
    },
}


def image_for_item(item: dict) -> str:
    article_image = item.get("_article_image") or {}
    if article_image.get("url"):
        return article_image["url"]
    haystack = (item["title"] + " " + item.get("summary", "")).lower()
    for keyword, img_name in TOPIC_IMAGES:
        if keyword in haystack:
            return f"assets/news/{img_name}.svg"
    return "assets/news/m365-roadmap.svg" if item["css_tag"] == "tag-roadmap" else "assets/news/m365.svg"


def fetch_og_image(url: str) -> str:
    """Return a public Open Graph/Twitter image for a source article, if present."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        resp.raise_for_status()
    except Exception as exc:
        print(f"  [warn] Could not fetch source image: {exc}", file=sys.stderr)
        return ""

    html = resp.text
    patterns = [
        r'<meta[^>]+(?:property|name)=["\'](?:og:image|twitter:image)["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\'](?:og:image|twitter:image)["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, flags=re.IGNORECASE)
        if not match:
            continue
        image_url = urljoin(resp.url, unescape(match.group(1)))
        if image_url and "RE1Mu3b" not in image_url:
            return image_url
    return ""


def article_image_for_item(item: dict) -> dict:
    """Choose a real source image for a generated news article."""
    if item.get("css_tag") == "tag-blog":
        source_image = fetch_og_image(item.get("url", ""))
        if source_image:
            return {
                "url": source_image,
                "alt": f"Microsoft TechCommunity image for {item['title']}",
                "caption": "Original Microsoft TechCommunity image for this announcement.",
                "source_url": item["url"],
                "source_label": item.get("source", "Microsoft TechCommunity"),
            }

    haystack = (item.get("title", "") + " " + item.get("summary", "")).lower()
    if "edge" in haystack:
        return ARTICLE_IMAGE_FALLBACKS["edge"]
    if "outlook" in haystack:
        return ARTICLE_IMAGE_FALLBACKS["outlook"]
    if "purview" in haystack or "insider risk" in haystack:
        return ARTICLE_IMAGE_FALLBACKS["purview"]
    if "bookable desk" in haystack or "desk" in haystack:
        return ARTICLE_IMAGE_FALLBACKS["teams-bookable"]
    if "interpreter" in haystack:
        return ARTICLE_IMAGE_FALLBACKS["teams-interpreter"]
    if "teams" in haystack:
        return ARTICLE_IMAGE_FALLBACKS["teams"]
    if "sharepoint" in haystack:
        return ARTICLE_IMAGE_FALLBACKS["sharepoint"]
    if "copilot" in haystack:
        return ARTICLE_IMAGE_FALLBACKS["copilot"]
    return ARTICLE_IMAGE_FALLBACKS["m365"]


def topic_for_item(item: dict) -> str:
    haystack = (item["title"] + " " + item.get("summary", "")).lower()
    for keyword, img_name in TOPIC_IMAGES:
        if keyword in haystack:
            return img_name
    return "other"


def is_relevant(entry) -> bool:
    haystack = (
        entry.get("title", "") + " " + strip_html(entry.get("summary", ""))
    ).lower()
    return any(term in haystack for term in RELEVANT_TERMS)


# ── AI prompts ────────────────────────────────────────────────────────────────

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

ARTICLE_PROMPT = textwrap.dedent("""\
    You are a senior content writer for OceanCloud, a certified Microsoft 365
    consulting firm. Write a 380-450 word expert article about this Microsoft
    announcement for OceanCloud's website.

    Structure your response EXACTLY as follows (use these exact headings):

    ## What's Changing
    [2-3 sentences clearly explaining the feature or update]

    ## Business Impact
    [2-3 sentences on why this matters for IT teams and decision-makers]

    ## What You Should Do
    - [Specific action item]
    - [Specific action item]
    - [Specific action item]
    - [Specific action item]

    Rules:
    - Professional, confident, forward-looking tone
    - Practical advice for Microsoft 365 admins and business leaders
    - Do NOT repeat the title as a heading or first sentence
    - Output ONLY the structured content — nothing before ## What's Changing
""")


# ── AI rewrite (short commentary for news cards) ──────────────────────────────

def _truncate(summary: str) -> str:
    return (summary[:280] + "…") if len(summary) > 280 else summary


def _openai(title: str, summary: str, prompt: str, max_tokens: int) -> str | None:
    if not OPENAI_KEY:
        return None
    try:
        import openai
        client = openai.OpenAI(api_key=OPENAI_KEY)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=max_tokens,
            temperature=0.65,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Title: {title}\n\nOriginal text: {summary[:800]}"},
            ],
        )
        return resp.choices[0].message.content.strip()
    except Exception as exc:
        print(f"  [warn] ChatGPT error: {exc}", file=sys.stderr)
        return None


def _gemini(title: str, summary: str, prompt: str, max_tokens: int) -> str | None:
    if not GEMINI_KEY:
        return None
    body = f"Title: {title}\n\nOriginal text: {summary[:800]}"
    payload = {
        "contents": [{"parts": [{"text": prompt + "\n\n" + body}]}],
        "generationConfig": {"temperature": 0.65, "maxOutputTokens": max_tokens},
    }
    try:
        resp = requests.post(GEMINI_URL, json=payload, timeout=20)
        resp.raise_for_status()
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as exc:
        print(f"  [warn] Gemini error: {exc}", file=sys.stderr)
        return None


def ai_rewrite(title: str, summary: str) -> str:
    """Short 2-3 sentence commentary for news cards. ChatGPT → Gemini → text."""
    result = _openai(title, summary, SYSTEM_PROMPT, 220)
    if result:
        print("  [info] Used ChatGPT for card rewrite")
        return result
    result = _gemini(title, summary, SYSTEM_PROMPT, 220)
    if result:
        print("  [info] Used Gemini for card rewrite")
        return result
    print("  [warn] No AI key available — using original text", file=sys.stderr)
    return _truncate(summary)


def ai_article_body(title: str, summary: str) -> str:
    """Longer structured article body. ChatGPT → Gemini → fallback."""
    result = _openai(title, summary, ARTICLE_PROMPT, 700)
    if result:
        print("  [info] Used ChatGPT for article body")
        return result
    result = _gemini(title, summary, ARTICLE_PROMPT, 700)
    if result:
        print("  [info] Used Gemini for article body")
        return result
    return summary[:800]


# ── Markdown → HTML (for article body) ───────────────────────────────────────

def md_to_html(text: str) -> str:
    """Convert simple markdown (##, ###, -, *) to HTML."""
    lines = text.split("\n")
    parts = []
    in_ul = False
    for line in lines:
        line = line.rstrip()
        if line.startswith("## "):
            if in_ul:
                parts.append("</ul>")
                in_ul = False
            parts.append(f"<h2>{escape(line[3:])}</h2>")
        elif line.startswith("### "):
            if in_ul:
                parts.append("</ul>")
                in_ul = False
            parts.append(f"<h3>{escape(line[4:])}</h3>")
        elif line.startswith("- ") or line.startswith("* "):
            if not in_ul:
                parts.append("<ul>")
                in_ul = True
            parts.append(f"<li>{escape(line[2:])}</li>")
        elif line:
            if in_ul:
                parts.append("</ul>")
                in_ul = False
            parts.append(f"<p>{escape(line)}</p>")
    if in_ul:
        parts.append("</ul>")
    return "\n      ".join(parts)


# ── Article page generator ────────────────────────────────────────────────────

def generate_article_page(item: dict, commentary: str, body_md: str, slug: str) -> str:
    """Build a complete HTML article page for a news item."""
    date_str   = friendly_date(item["date"])
    pub_date   = iso_date(item["date"])
    title      = item["title"]
    ms_url     = item["url"]
    is_roadmap = item["css_tag"] == "tag-roadmap"
    tag_label  = "M365 Roadmap" if is_roadmap else "SharePoint Blog"
    tag_color  = "rgba(0,180,216,.12)" if is_roadmap else "rgba(59,130,246,.12)"
    tag_tc     = "#00b4d8" if is_roadmap else "#60a5fa"
    canonical  = f"{SITE_BASE_URL}/articles/{slug}"
    short      = title[:45] + ("…" if len(title) > 45 else "")
    body_html  = md_to_html(body_md)
    desc       = escape(commentary[:160])
    article_image = item.get("_article_image") or article_image_for_item(item)
    image_url = article_image.get("url", "")
    image_html = ""
    if image_url:
        image_html = f"""
      <figure class="article-image">
        <img src="{escape(image_url)}" alt="{escape(article_image.get('alt', title))}" loading="lazy" decoding="async" referrerpolicy="no-referrer" />
        <figcaption>{escape(article_image.get('caption', 'Microsoft product image.'))} <a href="{escape(article_image.get('source_url', ms_url))}" target="_blank" rel="noopener noreferrer">Source: {escape(article_image.get('source_label', item['source']))}</a>.</figcaption>
      </figure>
"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="theme-color" content="#0077b6" />
  <title>{escape(title)} | OceanCloud</title>
  <meta name="description" content="{desc}" />
    <meta name="robots" content="{'index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1' if INDEX_NEWS_ARTICLES else 'noindex, follow'}" />
  <meta name="author" content="OceanCloud" />
  <link rel="canonical" href="{canonical}" />
  <meta property="og:type"        content="article" />
  <meta property="og:site_name"   content="OceanCloud" />
  <meta property="og:title"       content="{escape(title)}" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:url"         content="{canonical}" />
  <meta property="og:image"       content="{SITE_BASE_URL}/assets/og-home.jpg" />
  <meta property="og:locale"      content="en_US" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="../css/style.css?v=3" />
  <link rel="stylesheet" href="../css/pages.css?v=11" />
  <link rel="stylesheet" href="../css/darkstar.css?v=3" />
  <link rel="stylesheet" href="../css/article.css?v=6" />
  <link rel="icon" type="image/svg+xml" href="../favicon.svg" />
  <link rel="alternate" type="application/rss+xml" title="OceanCloud M365 News" href="{SITE_BASE_URL}/feed.xml" />
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@graph": [
      {{
        "@type": "Article",
        "@id": "{canonical}#article",
        "headline": "{escape(title)}",
        "url": "{canonical}",
        "datePublished": "{pub_date}",
        "dateModified": "{pub_date}",
        "author": {{ "@id": "{SITE_BASE_URL}/#organization" }},
        "publisher": {{ "@id": "{SITE_BASE_URL}/#organization" }},
        "description": "{desc}"
      }},
      {{
        "@type": "BreadcrumbList",
        "itemListElement": [
          {{ "@type": "ListItem", "position": 1, "name": "Home",  "item": "{SITE_BASE_URL}" }},
          {{ "@type": "ListItem", "position": 2, "name": "News",  "item": "{SITE_BASE_URL}/news" }},
          {{ "@type": "ListItem", "position": 3, "name": "{escape(short)}", "item": "{canonical}" }}
        ]
      }}
    ]
  }}
  </script>
  <style>
  .article-section{{padding:60px 0 100px;}}
  .article-wrap{{max-width:800px;margin:0 auto;}}
  .article-meta{{display:flex;gap:14px;align-items:center;flex-wrap:wrap;margin-bottom:28px;padding-bottom:24px;border-bottom:1px solid rgba(255,255,255,.07);}}
  .art-tag{{font-size:.72rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:4px 12px;border-radius:50px;background:{tag_color};color:{tag_tc};}}
  .art-date,.art-read{{font-size:.8rem;color:var(--text-dim);}}
  .article-intro{{font-size:1.05rem;color:#b8cfe0;line-height:1.85;margin-bottom:24px;}}
  .article-wrap h2{{font-size:clamp(1.25rem,3vw,1.6rem);font-weight:800;margin:48px 0 14px;color:var(--white);letter-spacing:-.03em;}}
  .article-wrap h3{{font-size:1.05rem;font-weight:700;margin:30px 0 10px;color:#c8daea;}}
  .article-wrap p{{color:var(--text-mid);line-height:1.85;margin:0 0 18px;}}
  .article-wrap ul,.article-wrap ol{{color:var(--text-mid);line-height:1.85;padding-left:22px;margin:0 0 18px;}}
  .article-wrap li{{margin-bottom:7px;}}
  .article-wrap strong{{color:var(--white);}}
  .article-wrap a{{color:#00b4d8;}}
  .ms-source-ref{{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:12px;padding:18px 22px;margin-top:40px;font-size:.88rem;color:var(--text-dim);}}
  .ms-source-ref a{{color:#00b4d8;text-decoration:none;}}
  .ms-source-ref a:hover{{text-decoration:underline;}}
  .related-section{{margin-top:64px;padding-top:48px;border-top:1px solid rgba(255,255,255,.08);}}
  .related-label{{font-size:.72rem;font-weight:700;color:var(--text-dim);text-transform:uppercase;letter-spacing:.1em;margin-bottom:16px;}}
  .related-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;}}
  .related-card{{padding:18px 20px;border-radius:12px;text-decoration:none;display:flex;flex-direction:column;gap:6px;border:1px solid rgba(255,255,255,.07);transition:border-color .2s;}}
  .related-card:hover{{border-color:rgba(0,180,216,.3);}}
  .rc-topic{{font-size:.68rem;font-weight:700;color:#00b4d8;text-transform:uppercase;letter-spacing:.08em;}}
  .rc-title{{font-size:.88rem;font-weight:600;color:var(--white);line-height:1.4;}}
  .rc-read{{font-size:.78rem;color:var(--text-dim);margin-top:2px;}}
  .related-card:hover .rc-title{{color:#00b4d8;}}
  </style>
</head>
<body>

<a href="#main-content" class="skip-link">Skip to content</a>
<div id="c-dot"></div>
<div id="c-ring"></div>

<nav id="navbar">
  <div class="container nav-inner">
    <a href="/" class="nav-logo"><div class="logo-mark">OC</div><span class="logo-text">Ocean<span>Cloud</span></span></a>
    <ul class="nav-links" id="navLinks">
      <li><a href="/"><span class="nav-num">01</span>Home</a></li>
      <li><a href="../services"><span class="nav-num">02</span>Services</a></li>
      <li><a href="../about"><span class="nav-num">03</span>About</a></li>
      <li><a href="../case-studies"><span class="nav-num">04</span>Work</a></li>
      <li><a href="../news" class="active-link"><span class="nav-num">05</span>News</a></li>
      <li><a href="../guides"><span class="nav-num">06</span>Guides</a></li>
      <li><a href="../contact" class="nav-cta">Get In Touch</a></li>
    </ul>
    <a href="../search" class="nav-search-btn" aria-label="Search"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg></a>
    <button class="hamburger" id="hamburger" aria-label="Toggle navigation" aria-expanded="false"><span></span><span></span><span></span></button>
  </div>
</nav>

<section id="main-content" class="page-hero article-hero particle-hero">
  <canvas data-particles='{{"count":30,"color":"0,180,216","maxDist":90,"speed":0.15,"opacity":0.18}}'></canvas>
  <div class="orb orb-cyan" style="width:340px;height:340px;top:-80px;right:-60px;"></div>
  <div class="orb orb-purple" style="width:220px;height:220px;bottom:-40px;left:10%;"></div>
  <div class="container particle-hero-inner">
    <div class="page-hero-content">
      <nav class="breadcrumb"><a href="/">Home</a><span>/</span><a href="../news">News</a><span>/</span><span>{escape(short)}</span></nav>
      <h1>{escape(title)}</h1>
    </div>
  </div>
</section>

<section class="article-section">
  <div class="container">
    <div class="article-wrap">

      <div class="article-meta">
        <span class="art-tag">{escape(tag_label)}</span>
        {f'<span class="art-date">{escape(date_str)}</span>' if date_str else ""}
        <span class="art-read">3 min read</span>
      </div>

      <p class="article-intro">{escape(commentary)}</p>
{image_html}

      {body_html}

      <div class="ms-source-ref">
        <strong>Original announcement:</strong>
        <a href="{escape(ms_url)}" target="_blank" rel="noopener noreferrer">{escape(title)}</a>
        &mdash; {escape(item['source'])}
      </div>

      <div class="related-section">
        <p class="related-label">Related Guides</p>
        <div class="related-grid"></div>
      </div>

    </div>
  </div>
</section>

<footer class="site-footer">
  <div class="container footer-grid">
    <div class="footer-brand">
      <div class="nav-logo"><div class="logo-mark">OC</div><span class="logo-text">Ocean<span>Cloud</span></span></div>
      <p class="footer-tagline">Microsoft 365 &amp; SharePoint consultants helping businesses work smarter.</p>
    </div>
    <div class="footer-col">
      <h4>Company</h4>
      <ul>
        <li><a href="../about">About Us</a></li>
        <li><a href="../case-studies">Case Studies</a></li>
        <li><a href="../news">News</a></li>
        <li><a href="../archive">News Archive</a></li>
        <li><a href="../guides">Guides &amp; Tips</a></li>
        <li><a href="../faq">FAQ</a></li>
      </ul>
    </div>
    <div class="footer-col">
      <h4>Services</h4>
      <ul>
        <li><a href="../services">SharePoint Development</a></li>
        <li><a href="../services">Teams Configuration</a></li>
        <li><a href="../services">M365 Migration</a></li>
        <li><a href="../services">Power Platform</a></li>
      </ul>
    </div>
    <div class="footer-col">
      <h4>Legal</h4>
      <ul>
        <li><a href="../privacy">Privacy Policy</a></li>
        <li><a href="../terms">Terms of Service</a></li>
        <li><a href="../cookies">Cookie Policy</a></li>
        <li><a href="../contact">Contact Us</a></li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom"><div class="container"><p>&copy; 2026 OceanCloud Consultants. All rights reserved.</p></div></div>
</footer>

<button id="back-to-top" aria-label="Back to top"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"/></svg></button>

<script src="../js/main.js?v=9"></script>
<script src="../js/chat.js?v=7"></script>
<script src="../js/particles.js?v=6"></script>
<script src="../js/weather.js?v=6"></script>
<script src="../js/share.js?v=1"></script>
<script src="../js/article.js?v=5"></script>
<script src="../js/comments.js?v=7"></script>
</body>
</html>"""


# ── Sitemap updater ───────────────────────────────────────────────────────────

def update_sitemap(new_slugs: list[str]) -> None:
    """Append new article URLs to sitemap.xml if not already present."""
    if not INDEX_NEWS_ARTICLES:
        print("✓ sitemap.xml unchanged; generated news detail pages are noindex.")
        return
    if not SITEMAP_XML.exists() or not new_slugs:
        return
    content = SITEMAP_XML.read_text(encoding="utf-8")
    today   = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    entries = ""
    added   = 0
    for slug in new_slugs:
        url = f"{SITE_BASE_URL}/articles/{slug}"
        if url in content:
            continue
        entries += (
            f"\n  <url>\n"
            f"    <loc>{url}</loc>\n"
            f"    <lastmod>{today}</lastmod>\n"
            f"    <changefreq>monthly</changefreq>\n"
            f"    <priority>0.6</priority>\n"
            f"  </url>\n"
        )
        added += 1
    if not entries:
        return
    content = content.replace("</urlset>", entries + "</urlset>")
    SITEMAP_XML.write_text(content, encoding="utf-8")
    print(f"✓ sitemap.xml updated with {added} new article URL(s).")


# ── Search index updater ──────────────────────────────────────────────────────

def update_search_index(new_items: list[dict]) -> None:
    """Append new news article entries to data/search-index.json."""
    if not SEARCH_INDEX.exists() or not new_items:
        return
    try:
        index = json.loads(SEARCH_INDEX.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"  [warn] Could not read search-index.json: {exc}", file=sys.stderr)
        return

    existing_ids = {entry.get("id", "") for entry in index}
    added = 0
    for item in new_items:
        slug   = item.get("_slug", "")
        if not slug:
            continue
        entry_id = f"articles-{slug}"
        if entry_id in existing_ids:
            continue
        date_display = friendly_date(item["date"])
        commentary   = item.get("_commentary", item.get("summary", ""))[:300]
        body_text    = f"{item['title']} | OceanCloud {date_display} 3 min read {commentary}"
        index.append({
            "id":          entry_id,
            "type":        "article",
            "tag":         "Article",
            "title":       item["title"],
            "heading":     item["title"],
            "excerpt":     commentary,
            "body":        body_text,
            "url":         f"articles/{slug}",
            "dateDisplay": date_display,
            "dateSort":    "",
        })
        existing_ids.add(entry_id)
        added += 1

    if added:
        SEARCH_INDEX.write_text(
            json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"✓ search-index.json updated with {added} new article entry/entries.")


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
                "summary": strip_html(entry.get("summary", ""))[:800],
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
                "summary": strip_html(entry.get("summary", ""))[:800],
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
    img_alt     = (item.get("_article_image") or {}).get("alt", item["source"])
    source_slug = "roadmap" if item["css_tag"] == "tag-roadmap" else "blog"
    topic_slug  = topic_for_item(item)
    local_url   = item.get("_article_url", item["url"])
    ms_url      = item["url"]
    return f"""\
      <article class="news-card glass" data-source="{source_slug}" data-topic="{topic_slug}">
        <div class="nc-image-wrap">
          <img class="nc-image" src="{escape(img)}" alt="{escape(img_alt)}" loading="lazy" />
        </div>
        <div class="nc-meta">
          <span class="nc-tag {item['css_tag']}">{escape(item['source'])}</span>
          {f'<span class="nc-date">{escape(date_str)}</span>' if date_str else ''}
        </div>
        <h3 class="nc-title">
          <a href="{escape(local_url)}">
            {escape(item['title'])}
          </a>
        </h3>
        <p class="nc-body">{escape(commentary)}</p>
        <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
          <a class="nc-link" href="{escape(local_url)}">Read article &#8599;</a>
          <a class="nc-link" href="{escape(ms_url)}" target="_blank" rel="noopener noreferrer" style="opacity:.6;font-size:.75rem;">Microsoft &#8599;</a>
        </div>
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
    """Add new items to archive, deduped by URL. Stores article_slug for local page links."""
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
            "article_slug":  it.get("_slug", ""),
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

    groups: dict[str, dict] = {}
    order:  list[str]       = []
    for it in archive:
        key = it["month_sort"]
        if key not in groups:
            groups[key] = {"label": it["month_label"], "items": []}
            order.append(key)
        groups[key]["items"].append(it)

    parts = []
    for key in order:
        g     = groups[key]
        count = len(g["items"])
        rows  = ""
        for it in g["items"]:
            short      = "Blog" if "Blog" in it["source"] else "M365"
            art_slug   = it.get("article_slug", "")
            link_url   = f"/articles/{art_slug}" if art_slug else it["url"]
            link_attrs = "" if art_slug else ' target="_blank" rel="noopener noreferrer"'
            rows += (
                f'        <li class="am-item">\n'
                f'          <span class="nc-tag {escape(it["css_tag"])}">{short}</span>\n'
                f'          <a href="{escape(link_url)}"{link_attrs}>'
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

    ARTICLES_DIR.mkdir(exist_ok=True)

    blog_items    = fetch_blog()
    roadmap_items = fetch_roadmap()
    all_items     = blog_items + roadmap_items

    if not all_items:
        print("[warn] No content fetched — news.html not updated.", file=sys.stderr)
        sys.exit(1)

    # ── Rewrite short commentary + generate article pages ─────────────────────
    print(f"\nProcessing {len(all_items)} items…")
    new_article_slugs: list[str] = []

    for item in all_items:
        print(f"  • {item['title'][:70]}")

        # Short commentary for news card
        item["_commentary"] = ai_rewrite(item["title"], item["summary"])
        item["_article_image"] = article_image_for_item(item)
        time.sleep(0.3)

        # Standalone article page (only if file doesn't already exist)
        slug      = article_slug(item)
        art_path  = ARTICLES_DIR / f"{slug}.html"
        item["_slug"]        = slug
        item["_article_url"] = f"/articles/{slug}"

        if not art_path.exists():
            print(f"    → generating article page: {slug}.html")
            body_md = ai_article_body(item["title"], item["summary"])
            time.sleep(0.3)
            art_html = generate_article_page(item, item["_commentary"], body_md, slug)
            art_path.write_text(art_html, encoding="utf-8")
            new_article_slugs.append(slug)
        else:
            print(f"    → article page already exists, skipping")

    # ── Update sitemap ────────────────────────────────────────────────────────
    update_sitemap(new_article_slugs)

    # ── Update search index ───────────────────────────────────────────────────
    if INDEX_NEWS_ARTICLES:
        new_indexed = [it for it in all_items if it.get("_slug") in new_article_slugs]
        update_search_index(new_indexed)
    else:
        print("✓ search-index.json unchanged; generated news detail pages are noindex.")

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

    if new_article_slugs:
        print(f"\n✓ {len(new_article_slugs)} new article page(s) created in articles/")


if __name__ == "__main__":
    main()
