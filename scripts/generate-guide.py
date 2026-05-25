#!/usr/bin/env python3
"""
OceanCloud Guide Generator
==========================
Picks the next pending topic from data/guide-topics.json and generates
a manual guide article scaffold. Writes:
  - articles/{slug}.html        new guide page
  - guides.html                 new card injected before END marker
  - js/article.js               GUIDES array entry
  - data/search-index.json      new search entry
  - sitemap.xml                 new URL entry

Outputs slug and title to $GITHUB_OUTPUT for the workflow.
Exits cleanly with no output if no pending topics exist.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from html import escape
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

ROOT          = Path(__file__).parent.parent
ARTICLES_DIR  = ROOT / "articles"
GUIDES_HTML   = ROOT / "guides.html"
ARTICLE_JS    = ROOT / "js" / "article.js"
SEARCH_INDEX  = ROOT / "data" / "search-index.json"
SITEMAP_XML   = ROOT / "sitemap.xml"
TOPICS_JSON   = ROOT / "data" / "guide-topics.json"
SITE_BASE_URL = "https://www.oceancloudconsults.com"

GUIDES_BEGIN  = "<!-- BEGIN:GUIDES-GRID -->"
GUIDES_END    = "<!-- END:GUIDES-GRID -->"
JS_ARRAY_END  = "    // END:GUIDES-ARRAY"

# ── Topic metadata ────────────────────────────────────────────────────────────

TAG_MAP = {
    "sharepoint":     "SharePoint",
    "migration":      "Migration",
    "power-platform": "Power Platform",
    "copilot":        "Copilot",
    "teams":          "Teams",
    "integration":    "Integration",
    "admin":          "Admin & Automation",
}

ICON_MAP = {
    "sharepoint":     "&#128274;",
    "migration":      "&#128640;",
    "power-platform": "&#9889;",
    "copilot":        "&#129302;",
    "teams":          "&#128101;",
    "integration":    "&#128257;",
    "admin":          "&#128736;",
}

CSS_TAG_MAP = {
    "sharepoint":     "tag-sharepoint",
    "migration":      "tag-migration",
    "power-platform": "tag-power-platform",
    "copilot":        "tag-copilot",
    "teams":          "tag-teams",
    "integration":    "tag-integration",
    "admin":          "tag-admin",
}

# ── Helpers ────────────────────────────────────────────────────────────────────

def slugify(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s)
    s = s.strip("-")
    slug = f"guide-{s}"
    return slug[:60].rstrip("-")


def word_count(html: str) -> int:
    return len(re.sub(r"<[^>]+>", " ", html).split())


def read_time(body_html: str) -> str:
    mins = max(6, round(word_count(body_html) / 200))
    return f"{mins} min read"


def html_to_text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def extract_intro(body_html: str) -> str:
    m = re.search(r'<p class="article-intro">(.*?)</p>', body_html, re.DOTALL)
    if m:
        return html_to_text(m.group(1))[:220]
    return html_to_text(body_html)[:220]


def h1_html(title: str) -> str:
    if ":" in title:
        main, rest = title.split(":", 1)
        return f'{escape(main.strip())}: <span class="grad-text">{escape(rest.strip())}</span>'
    words = title.rsplit(" ", 2)
    if len(words) >= 3:
        return (
            f'{escape(" ".join(words[:-2]))} '
            f'<span class="grad-text">{escape(" ".join(words[-2:]))}</span>'
        )
    return escape(title)


def branch_exists(branch: str) -> bool:
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--heads", "origin", branch],
            capture_output=True, text=True, timeout=15,
        )
        return bool(result.stdout.strip())
    except Exception:
        return False


def generate_content(title: str, tag: str) -> dict:
    esc_title = escape(title)
    esc_tag = escape(tag)
    meta_description = f"Manual draft scaffold for {title}. Complete and review before publishing."
    hero_subtitle = f"A manually prepared scaffold for completing {title}."
    body_html = f"""
      <p class="article-intro">This is a manual draft scaffold for <strong>{esc_title}</strong>. Replace this introduction with a concise explanation of the problem, the audience, and the outcome the reader will achieve.</p>

      <div class="art-callout warning"><p><strong>Draft note:</strong> This guide was generated as a no-API manual scaffold. Complete every placeholder section and review technical accuracy before merging.</p></div>

      <h2>Overview</h2>
      <p>Summarise what {esc_title} means for Microsoft 365 administrators, business stakeholders, and end users. Explain why this topic matters now and where it typically appears in real-world {esc_tag} projects.</p>
      <p>Add the key definitions, assumptions, and prerequisites a reader needs before following the rest of the guide.</p>

      <h2>Business Scenario</h2>
      <p>Describe the common business situation that leads teams to search for this guide. Include the symptoms, operational risks, governance concerns, and expected benefits of solving the problem well.</p>
      <p>Connect the scenario to practical OceanCloud consulting work such as SharePoint architecture, Teams governance, Power Platform automation, migration planning, or Microsoft 365 security.</p>

      <h2>Planning Checklist</h2>
      <p>List the decisions that should be made before implementation, including ownership, permissions, lifecycle management, communication, rollback planning, and success measures.</p>
      <div class="art-table-wrap"><table class="art-table">
      <thead><tr><th>Planning area</th><th>Decision to document</th><th>Owner</th></tr></thead>
      <tbody>
      <tr><td>Scope</td><td>Which sites, teams, users, or workloads are included?</td><td>Project lead</td></tr>
      <tr><td>Governance</td><td>Which policies, naming standards, and approval rules apply?</td><td>M365 admin</td></tr>
      <tr><td>Security</td><td>Which permissions, labels, retention, or sharing controls are required?</td><td>Security owner</td></tr>
      <tr><td>Adoption</td><td>How will users be trained and supported after launch?</td><td>Business owner</td></tr>
      </tbody>
      </table></div>

      <h2>Implementation Steps</h2>
      <p>Replace this section with the ordered steps for completing the work. Keep the instructions practical, tested, and specific to Microsoft 365 admin centers, SharePoint, Teams, Power Platform, or PnP.PowerShell as appropriate.</p>
      <p>Include screenshots or exact navigation paths where they would reduce ambiguity for the reader.</p>

      <h2>PowerShell Validation</h2>
      <p>Add any safe validation commands here. Avoid destructive commands and confirm all examples work with current PnP.PowerShell parameters before publishing.</p>
      <div class="code-label">PowerShell 7 &mdash; validate site connectivity</div>
      <div class="code-block"><pre>$siteUrl = "https://contoso.sharepoint.com/sites/Example"
Connect-PnPOnline -Url $siteUrl -Interactive
Get-PnPWeb | Select-Object Title, Url</pre></div>

      <div class="art-callout tip"><p><strong>Tip:</strong> Keep implementation commands separate from validation commands so readers can test access and assumptions before making changes.</p></div>

      <h2>Governance and Security</h2>
      <p>Explain the policies, permissions, audit requirements, data protection controls, and lifecycle considerations that should be reviewed before rollout.</p>
      <p>Call out tenant-level settings that may override site-level or team-level configuration.</p>

      <h2>Common Pitfalls</h2>
      <p>Document the mistakes that commonly delay projects in this area, such as unclear ownership, over-permissioned sites, missing communication plans, untested automation, or incomplete rollback steps.</p>
      <div class="art-callout"><p><strong>Note:</strong> Replace this note with a topic-specific caveat that would help an administrator avoid a real support issue.</p></div>

      <h2>Final Review Checklist</h2>
      <p>Before publishing, confirm the guide includes accurate product names, current admin center navigation, tested PowerShell, clear business value, and a concrete next step for readers who need expert help.</p>
    """.strip()
    return {
        "meta_description": meta_description[:160],
        "hero_subtitle": hero_subtitle,
        "body_html": body_html,
    }


# ── Page builder ──────────────────────────────────────────────────────────────

def build_page(
    slug: str, title: str, topic: str, tag: str,
    date_str: str, iso_str: str, read_str: str,
    meta_desc: str, hero_sub: str, body_html: str,
) -> str:
    canonical  = f"{SITE_BASE_URL}/articles/{slug}"
    h1         = h1_html(title)
    esc_title  = escape(title)
    esc_desc   = escape(meta_desc[:160])
    esc_sub    = escape(hero_sub)
    bc_label   = escape(title[:50] + ("…" if len(title) > 50 else ""))
    css_tag    = CSS_TAG_MAP.get(topic, "tag-sharepoint")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="theme-color" content="#0077b6" />
  <title>{esc_title} | OceanCloud</title>
  <meta name="description" content="{esc_desc}" />
  <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1" />
  <meta name="author" content="OceanCloud" />
  <link rel="canonical" href="{canonical}" />
  <meta property="og:type"        content="article" />
  <meta property="og:site_name"   content="OceanCloud" />
  <meta property="og:title"       content="{esc_title}" />
  <meta property="og:description" content="{esc_desc}" />
  <meta property="og:url"         content="{canonical}" />
  <meta property="og:image"       content="{SITE_BASE_URL}/assets/og-home.jpg" />
  <meta property="og:locale"      content="en_US" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="../css/style.css?v=3" />
  <link rel="stylesheet" href="../css/pages.css?v=11" />
  <link rel="stylesheet" href="../css/darkstar.css?v=3" />
  <link rel="stylesheet" href="../css/code.css?v=1" />
  <link rel="stylesheet" href="../css/article.css?v=1" />
  <link rel="icon" type="image/svg+xml" href="../favicon.svg" />
  <link rel="alternate" type="application/rss+xml" title="OceanCloud M365 News" href="{SITE_BASE_URL}/feed.xml" />
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@graph": [
      {{
        "@type": "Article",
        "@id": "{canonical}#article",
        "headline": "{esc_title}",
        "url": "{canonical}",
        "datePublished": "{iso_str}",
        "dateModified": "{iso_str}",
        "author": {{ "@id": "{SITE_BASE_URL}/#organization" }},
        "publisher": {{ "@id": "{SITE_BASE_URL}/#organization" }},
        "description": "{esc_desc}"
      }},
      {{
        "@type": "BreadcrumbList",
        "itemListElement": [
          {{ "@type": "ListItem", "position": 1, "name": "Home",   "item": "{SITE_BASE_URL}" }},
          {{ "@type": "ListItem", "position": 2, "name": "Guides", "item": "{SITE_BASE_URL}/guides" }},
          {{ "@type": "ListItem", "position": 3, "name": "{bc_label}", "item": "{canonical}" }}
        ]
      }}
    ]
  }}
  </script>
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
      <li><a href="../news"><span class="nav-num">05</span>News</a></li>
      <li><a href="../guides" class="active-link"><span class="nav-num">06</span>Guides</a></li>
      <li><a href="../contact" class="nav-cta">Get In Touch</a></li>
    </ul>
    <a href="../search" class="nav-search-btn" aria-label="Search"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg></a>
    <button class="hamburger" id="hamburger" aria-label="Toggle navigation" aria-expanded="false"><span></span><span></span><span></span></button>
  </div>
</nav>

<section id="main-content" class="page-hero article-hero particle-hero">
  <canvas data-particles='{{"count":40,"color":"59,130,246","maxDist":100,"speed":0.15,"opacity":0.22}}'></canvas>
  <div class="orb" style="width:400px;height:400px;top:-100px;right:-80px;background:radial-gradient(circle,rgba(59,130,246,.18) 0%,rgba(59,130,246,0) 70%);position:absolute;border-radius:50%;"></div>
  <div class="orb orb-cyan" style="width:260px;height:260px;bottom:-40px;left:10%;"></div>
  <div class="container particle-hero-inner">
    <div class="page-hero-content">
      <nav class="breadcrumb"><a href="/">Home</a><span>/</span><a href="../guides">Guides</a><span>/</span><span>{bc_label}</span></nav>
      <h1>{h1}</h1>
      <p>{esc_sub}</p>
    </div>
  </div>
</section>

<section class="article-section">
  <div class="container">
    <div class="article-wrap">

      <div class="article-meta">
        <span class="art-tag">{escape(tag)}</span>
        <span class="art-date">{date_str}</span>
        <span class="art-read">{read_str}</span>
      </div>

      {body_html}

      <div class="art-cta-box">
        <h3>Need expert Microsoft 365 help?</h3>
        <p>OceanCloud's certified consultants design, implement, and optimise Microsoft 365 environments — SharePoint architecture, Power Platform automation, Teams governance, and Copilot readiness. Free 60-minute scoping call.</p>
        <a href="../contact" class="btn btn-primary">Book a Free Call</a>
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
<script src="../js/code.js?v=2"></script>
<script src="../js/article.js?v=3"></script>
</body>
</html>"""


# ── File updaters ─────────────────────────────────────────────────────────────

def update_guides_html(slug: str, title: str, topic: str, tag: str, read_str: str, intro: str) -> None:
    content = GUIDES_HTML.read_text(encoding="utf-8")
    if f'href="articles/{slug}"' in content:
        print("  Guide card already in guides.html — skipping")
        return
    if GUIDES_END not in content:
        print("[warn] guides.html END marker missing — skipping card", file=sys.stderr)
        return

    icon    = ICON_MAP.get(topic, "&#128203;")
    css_tag = CSS_TAG_MAP.get(topic, "tag-sharepoint")
    tag_amp = tag.replace("&", "&amp;")
    card = (
        f"\n      <article class=\"guide-card glass\" data-topic=\"{topic}\">\n"
        f"        <div class=\"gc-icon\">{icon}</div>\n"
        f"        <div class=\"gc-meta\">\n"
        f"          <span class=\"gc-tag {css_tag}\">{tag_amp}</span>\n"
        f"          <span class=\"gc-read\">{read_str}</span>\n"
        f"        </div>\n"
        f"        <h2 class=\"gc-title\">\n"
        f"          <a href=\"articles/{slug}\">{escape(title)}</a>\n"
        f"        </h2>\n"
        f"        <p class=\"gc-body\">{escape(intro[:180])}</p>\n"
        f"        <a class=\"gc-link\" href=\"articles/{slug}\">Read guide &#8599;</a>\n"
        f"      </article>\n"
    )
    content = content.replace(GUIDES_END, card + "    " + GUIDES_END)
    content = re.sub(
        r"(\d+) guides available",
        lambda m: f"{int(m.group(1)) + 1} guides available",
        content,
    )
    GUIDES_HTML.write_text(content, encoding="utf-8")
    print("  ✓ guides.html updated")


def update_article_js(slug: str, title: str, topic: str, tag: str, read_str: str) -> None:
    content = ARTICLE_JS.read_text(encoding="utf-8")
    if f"url:'{slug}'" in content:
        print("  GUIDES entry already in article.js — skipping")
        return
    if JS_ARRAY_END not in content:
        print("[warn] article.js END marker missing — skipping GUIDES update", file=sys.stderr)
        return

    tag_js   = tag.replace("'", "\\'")
    title_js = title.replace("'", "\\'")
    entry = (
        f"    {{ topic:'{topic}', tag:'{tag_js}', url:'{slug}', "
        f"title:'{title_js}', read:'{read_str}' }},\n"
    )
    content = content.replace(JS_ARRAY_END, entry + JS_ARRAY_END)
    content = re.sub(
        r"/\* ── All (\d+) guide articles",
        lambda m: f"/* ── All {int(m.group(1)) + 1} guide articles",
        content,
    )
    ARTICLE_JS.write_text(content, encoding="utf-8")
    print("  ✓ js/article.js updated")


def update_search_index(slug: str, title: str, tag: str, date_str: str, body_html: str, intro: str) -> None:
    entry_id = f"articles-{slug}"
    try:
        index = json.loads(SEARCH_INDEX.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"  [warn] Could not read search-index.json: {exc}", file=sys.stderr)
        return
    if any(e.get("id") == entry_id for e in index):
        print("  Search index entry already exists — skipping")
        return

    body_text = f"{title} | OceanCloud {date_str} {html_to_text(body_html)}"
    index.append({
        "id":          entry_id,
        "type":        "guide",
        "tag":         "Guide",
        "title":       title,
        "heading":     title,
        "excerpt":     intro,
        "body":        body_text[:4000],
        "url":         f"articles/{slug}",
        "dateDisplay": date_str,
        "dateSort":    "",
    })
    SEARCH_INDEX.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    print("  ✓ data/search-index.json updated")


def update_sitemap(slug: str, iso_str: str) -> None:
    url = f"{SITE_BASE_URL}/articles/{slug}"
    content = SITEMAP_XML.read_text(encoding="utf-8")
    if url in content:
        print("  Sitemap entry already exists — skipping")
        return
    entry = (
        f"\n  <url>\n"
        f"    <loc>{url}</loc>\n"
        f"    <lastmod>{iso_str}</lastmod>\n"
        f"    <changefreq>monthly</changefreq>\n"
        f"    <priority>0.7</priority>\n"
        f"  </url>\n"
    )
    content = content.replace("</urlset>", entry + "</urlset>")
    SITEMAP_XML.write_text(content, encoding="utf-8")
    print("  ✓ sitemap.xml updated")


def write_pr_body(slug: str, title: str) -> Path:
    body = (
    f"## New Manual Guide Scaffold\n\n"
        f"**Title:** {title}\n"
        f"**File:** `articles/{slug}.html`\n\n"
    f"This PR contains a no-API scaffold. Complete the article manually before merging.\n\n"
        f"### Before merging — review checklist\n"
    f"- [ ] Replace every scaffold paragraph with final content\n"
    f"- [ ] Introduction and section headings read naturally\n"
        f"- [ ] Any PowerShell code blocks use correct PnP.PowerShell 2.x cmdlets and parameters\n"
        f"- [ ] Tables and callout boxes look right\n"
        f"- [ ] No obvious factual errors\n"
        f"- [ ] Reading time estimate is reasonable\n\n"
        f"### To publish\n"
        f"Merge this PR — the guide goes live on the site immediately.\n\n"
        f"### To discard\n"
        f"Close this PR without merging.\n\n"
        f"> Auto-generated by OceanCloud Guide Bot\n"
    )
    runner_temp = Path(os.environ.get("RUNNER_TEMP", "/tmp"))
    pr_file = runner_temp / "pr-body.md"
    pr_file.write_text(body, encoding="utf-8")
    return pr_file


def emit_output(slug: str, title: str, pr_body_path: Path) -> None:
    gh_output = os.environ.get("GITHUB_OUTPUT", "")
    if gh_output:
        with open(gh_output, "a", encoding="utf-8") as f:
            f.write(f"slug={slug}\n")
            f.write(f"title={title}\n")
            f.write(f"pr_body={pr_body_path}\n")
    else:
        print(f"GUIDE_SLUG={slug}")
        print(f"GUIDE_TITLE={title}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    if not TOPICS_JSON.exists():
        print("No guide-topics.json found — nothing to do.")
        return

    try:
        topics = json.loads(TOPICS_JSON.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[error] Cannot parse guide-topics.json: {exc}", file=sys.stderr)
        sys.exit(1)

    if not topics:
        print("guide-topics.json is empty — no topics queued. Add topics to generate a draft.")
        return

    # Find first topic that has no article and no open draft branch
    chosen = None
    for t in topics:
        title = t.get("title", "").strip()
        if not title:
            continue
        slug = slugify(title)
        if (ARTICLES_DIR / f"{slug}.html").exists():
            print(f"  → skip (article exists): {slug}")
            continue
        if branch_exists(f"draft/{slug}"):
            print(f"  → skip (draft branch open): draft/{slug}")
            continue
        chosen = t
        break

    if not chosen:
        print("All queued topics already have articles or open draft branches — nothing to do.")
        return

    title  = chosen["title"].strip()
    topic  = chosen.get("topic", "sharepoint")
    tag    = TAG_MAP.get(topic, "SharePoint")
    slug   = slugify(title)
    today  = datetime.now(timezone.utc)
    date_str = today.strftime("%B %d, %Y")
    iso_str  = today.strftime("%Y-%m-%d")

    print(f"\nGenerating manual guide scaffold: {title}")
    print(f"  Slug : {slug}")
    print(f"  Topic: {topic} ({tag})")

    content = generate_content(title, tag)

    body_html = content["body_html"]
    meta_desc = content["meta_description"] or f"Expert guide to {title} for Microsoft 365 admins and IT professionals."
    hero_sub  = content["hero_subtitle"] or "A practical guide for Microsoft 365 administrators."
    read_str  = read_time(body_html)
    intro     = extract_intro(body_html)

    ARTICLES_DIR.mkdir(exist_ok=True)
    art_html = build_page(slug, title, topic, tag, date_str, iso_str, read_str, meta_desc, hero_sub, body_html)
    (ARTICLES_DIR / f"{slug}.html").write_text(art_html, encoding="utf-8")
    print(f"  ✓ articles/{slug}.html written ({read_str})")

    update_guides_html(slug, title, topic, tag, read_str, intro)
    update_article_js(slug, title, topic, tag, read_str)
    update_search_index(slug, title, tag, date_str, body_html, intro)
    update_sitemap(slug, iso_str)

    pr_path = write_pr_body(slug, title)
    emit_output(slug, title, pr_path)
    print(f"\n✓ Done — {slug}")


if __name__ == "__main__":
    main()
