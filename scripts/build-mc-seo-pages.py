#!/usr/bin/env python3
"""
Generate crawlable Message Center SEO pages for MC IDs.

Outputs:
- mc/<MCID>.html            (one page per message)
- mc/index.html             (listing page)
- sitemap-mc.xml            (sitemap for MC pages)

This improves discoverability when users search Google for specific MC IDs.
"""

from __future__ import annotations

import datetime as dt
import html
import json
import pathlib
import re
import urllib.request
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
MC_DIR = ROOT / "mc"
SITEMAP_PATH = ROOT / "sitemap-mc.xml"
SEEDS_PATH = ROOT / "data" / "mc-id-seeds.txt"
SITE = "https://oceancloudconsults.com"
API = "https://oceancloud-ai-proxy.oceancloud-ai-proxy.workers.dev/m365/message-center"


def esc(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def strip_tags(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def fetch_messages() -> list[dict[str, Any]]:
    req = urllib.request.Request(
        API,
        headers={
            "Origin": SITE,
            "User-Agent": "OceanCloud-MC-SEO-Builder/1.0",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        payload = json.loads(resp.read().decode("utf-8", errors="ignore"))
    msgs = payload.get("messages") or []
    return [m for m in msgs if isinstance(m, dict) and re.fullmatch(r"MC\d+", str(m.get("id", "")).upper())]


def fetch_message_by_id(mcid: str) -> dict[str, Any] | None:
    req = urllib.request.Request(
        f"{API}?id={mcid}",
        headers={
            "Origin": SITE,
            "User-Agent": "OceanCloud-MC-SEO-Builder/1.0",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        payload = json.loads(resp.read().decode("utf-8", errors="ignore"))
    msgs = payload.get("messages") or []
    for m in msgs:
        if isinstance(m, dict) and str(m.get("id", "")).upper() == mcid:
            return m
    return None


def load_seed_ids() -> list[str]:
    if not SEEDS_PATH.exists():
        return []
    ids: list[str] = []
    for line in SEEDS_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        candidate = line.strip().upper()
        if re.fullmatch(r"MC\d+", candidate):
            ids.append(candidate)
    return ids


def existing_ids() -> list[str]:
    ids: list[str] = []
    if not MC_DIR.exists():
        return ids
    for p in MC_DIR.glob("MC*.html"):
        mcid = p.stem.upper()
        if re.fullmatch(r"MC\d+", mcid):
            ids.append(mcid)
    return ids


def page_html(m: dict[str, Any]) -> str:
    mcid = str(m.get("id", "")).upper()
    title = strip_tags(str(m.get("title", "Microsoft 365 Message Center update")))
    service = ", ".join(m.get("services") or []) or "Microsoft 365"
    updated = str(m.get("lastModifiedDateTime") or "")
    published = str(m.get("startDateTime") or "")
    body = strip_tags(str(m.get("body") or ""))
    if len(body) > 700:
        body = body[:700].rstrip() + "..."
    desc = f"{mcid}: {title}. Service: {service}. Latest Microsoft 365 Message Center notification surfaced by OceanCloud."
    url = f"{SITE}/mc/{mcid}.html"
    app_url = f"{SITE}/message-center?id={mcid}"

    json_ld = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": f"{mcid} | {title}",
        "mainEntityOfPage": url,
        "datePublished": published or None,
        "dateModified": updated or None,
        "publisher": {
            "@type": "Organization",
            "name": "OceanCloud",
            "url": SITE,
        },
        "description": desc,
        "articleBody": body,
    }
    # Drop None values for cleaner JSON-LD.
    json_ld = {k: v for k, v in json_ld.items() if v}

    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{esc(mcid)} | {esc(title)} | OceanCloud Message Center</title>
  <meta name=\"description\" content=\"{esc(desc)}\" />
  <meta name=\"robots\" content=\"index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1\" />
  <link rel=\"canonical\" href=\"{esc(url)}\" />
  <meta property=\"og:type\" content=\"article\" />
  <meta property=\"og:title\" content=\"{esc(mcid)} | {esc(title)}\" />
  <meta property=\"og:description\" content=\"{esc(desc)}\" />
  <meta property=\"og:url\" content=\"{esc(url)}\" />
  <meta property=\"og:site_name\" content=\"OceanCloud\" />
  <meta name=\"twitter:card\" content=\"summary\" />
  <meta name=\"twitter:title\" content=\"{esc(mcid)} | {esc(title)}\" />
  <meta name=\"twitter:description\" content=\"{esc(desc)}\" />
  <script type=\"application/ld+json\">{json.dumps(json_ld, ensure_ascii=True)}</script>
  <style>
    :root {{ --bg:#070d17; --panel:#0f1828; --text:#d6e3f5; --muted:#8ea7c7; --acc:#00b4d8; --line:rgba(120,160,220,.25); }}
    html,body {{ margin:0; padding:0; background:var(--bg); color:var(--text); font-family:Inter,Segoe UI,Arial,sans-serif; }}
    main {{ max-width:860px; margin:48px auto; padding:0 18px; }}
    .card {{ border:1px solid var(--line); background:var(--panel); border-radius:10px; padding:20px; box-shadow:0 12px 36px rgba(0,0,0,.35); }}
    .id {{ color:var(--acc); font-weight:800; letter-spacing:.04em; text-transform:uppercase; font-size:.86rem; }}
    h1 {{ margin:.4rem 0 1rem; font-size:1.7rem; line-height:1.2; }}
    dl {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; margin:0 0 16px; }}
    dt {{ color:var(--muted); text-transform:uppercase; letter-spacing:.06em; font-size:.68rem; font-weight:800; }}
    dd {{ margin:4px 0 0; font-size:.93rem; color:var(--text); overflow-wrap:anywhere; }}
    p {{ line-height:1.75; color:var(--text); }}
    .muted {{ color:var(--muted); font-size:.9rem; }}
    .btn {{ display:inline-block; margin-top:14px; border:1px solid rgba(0,180,216,.45); color:#00111c; background:var(--acc); padding:10px 14px; border-radius:999px; font-weight:800; text-decoration:none; }}
    .btn-secondary {{ margin-left:8px; background:transparent; color:var(--acc); }}
    @media (max-width:640px) {{ dl {{ grid-template-columns:1fr; }} h1 {{ font-size:1.3rem; }} }}
  </style>
</head>
<body>
  <main>
    <div class=\"card\">
      <div class=\"id\">Microsoft 365 Message Center</div>
      <h1>{esc(mcid)} | {esc(title)}</h1>
      <dl>
        <div><dt>Service</dt><dd>{esc(service)}</dd></div>
        <div><dt>Last Updated</dt><dd>{esc(updated or '-')}</dd></div>
        <div><dt>Published</dt><dd>{esc(published or '-')}</dd></div>
        <div><dt>Message ID</dt><dd>{esc(mcid)}</dd></div>
      </dl>
      <p>{esc(body or 'Open in Message Center to read the complete notification.')}</p>
      <a class=\"btn\" rel=\"nofollow\" href=\"{esc(app_url)}\">Open Full Notification</a>
      <a class=\"btn btn-secondary\" href=\"{SITE}/message-center\">Browse Message Center</a>
      <p class=\"muted\">This page is an SEO landing page for discoverability of Message Center ID {esc(mcid)}.</p>
    </div>
  </main>
    <script src=\"/js/consent.js\"></script>
</body>
</html>
"""


def write_index(messages: list[dict[str, Any]]) -> None:
    items = []
    for m in messages:
        mcid = str(m.get("id", "")).upper()
        title = strip_tags(str(m.get("title", "Message Center notification")))
        items.append(f'<li><a href="/mc/{esc(mcid)}.html">{esc(mcid)}</a> - {esc(title)}</li>')
    html_doc = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Microsoft 365 Message Center IDs | OceanCloud</title>
  <meta name=\"description\" content=\"Index of Microsoft 365 Message Center IDs tracked by OceanCloud.\" />
  <meta name=\"robots\" content=\"index,follow\" />
  <link rel=\"canonical\" href=\"{SITE}/mc/index.html\" />
  <style>
    body {{ margin:0; background:#070d17; color:#d6e3f5; font-family:Inter,Segoe UI,Arial,sans-serif; }}
    main {{ max-width:880px; margin:48px auto; padding:0 18px; }}
    .card {{ border:1px solid rgba(120,160,220,.25); background:#0f1828; border-radius:10px; padding:20px; }}
    h1 {{ margin:0 0 12px; }}
    a {{ color:#00b4d8; }}
    li {{ margin:8px 0; line-height:1.45; }}
  </style>
</head>
<body>
  <main>
    <div class=\"card\">
      <h1>Microsoft 365 Message Center IDs</h1>
      <p>Direct landing pages for crawl/index support.</p>
      <ul>{''.join(items)}</ul>
      <p><a href=\"/message-center\">Open live Message Center</a></p>
    </div>
  </main>
  <script src=\"/js/consent.js\"></script>
</body>
</html>
"""
    (MC_DIR / "index.html").write_text(html_doc, encoding="utf-8")


def write_sitemap(messages: list[dict[str, Any]]) -> None:
    rows = []
    today = dt.date.today().isoformat()
    for m in messages:
        mcid = str(m.get("id", "")).upper()
        mod_raw = str(m.get("lastModifiedDateTime") or "")
        lastmod = mod_raw[:10] if re.fullmatch(r"\d{4}-\d{2}-\d{2}.*", mod_raw) else today
        rows.append(
            f"  <url>\n"
            f"    <loc>{SITE}/mc/{mcid}.html</loc>\n"
            f"    <lastmod>{lastmod}</lastmod>\n"
            f"    <changefreq>daily</changefreq>\n"
            f"    <priority>0.7</priority>\n"
            f"  </url>"
        )

    sitemap = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n"
        f"{chr(10).join(rows)}\n"
        "</urlset>\n"
    )
    SITEMAP_PATH.write_text(sitemap, encoding="utf-8")


def main() -> int:
    messages = fetch_messages()
    by_id: dict[str, dict[str, Any]] = {
        str(m.get("id", "")).upper(): m
        for m in messages
        if re.fullmatch(r"MC\d+", str(m.get("id", "")).upper())
    }

    # Union current feed IDs with previously generated and explicit seed IDs.
    wanted_ids = set(by_id.keys())
    wanted_ids.update(existing_ids())
    wanted_ids.update(load_seed_ids())

    # For IDs not in the current feed, try direct lookup one-by-one.
    for mcid in sorted(wanted_ids):
        if mcid in by_id:
            continue
        try:
            found = fetch_message_by_id(mcid)
            if found:
                by_id[mcid] = found
        except Exception:
            # Keep generator resilient; skip IDs that cannot be resolved now.
            continue

    messages = list(by_id.values())

    MC_DIR.mkdir(parents=True, exist_ok=True)

    for m in messages:
        mcid = str(m.get("id", "")).upper()
        (MC_DIR / f"{mcid}.html").write_text(page_html(m), encoding="utf-8")

    write_index(messages)
    write_sitemap(messages)

    print(f"Generated {len(messages)} MC SEO pages in {MC_DIR}")
    print(f"Generated sitemap: {SITEMAP_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
