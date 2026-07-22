#!/usr/bin/env python3
"""Apply deterministic search-recovery and trust cleanup changes."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDE_DIR = ROOT / "articles"
FAKE_AUTHOR_ID = "https://oceancloudconsults.com/#james-whitfield"
FAKE_PEOPLE = {"James Whitfield", "Sara Okafor", "Ben Marchetti"}
ORG_ID = "https://oceancloudconsults.com/#organization"
TODAY = "2026-07-23"

LD_JSON_RE = re.compile(
    r'(<script\s+type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)',
    re.IGNORECASE | re.DOTALL,
)

PRIORITY_LINKS = {
    "guide-sharepoint-pnp-site-migration.html": (
        "/microsoft-365-migration",
        "Microsoft 365 migration services",
        "Use this runbook with a documented migration scope, pilot, cutover, and source-to-target validation plan.",
    ),
    "guide-sharepoint-external-sharing-complete-admin-guide.html": (
        "/sharepoint-consulting",
        "SharePoint governance support",
        "Connect the tenant settings in this guide to named owners, exception handling, and a recurring access-review process.",
    ),
    "guide-power-automate-triggers-actions.html": (
        "/power-platform-consulting",
        "Power Platform consulting",
        "Move from individual flows to governed environments, documented ownership, monitoring, and deployment controls.",
    ),
    "guide-sharepoint-approval-multiple-approvers.html": (
        "/power-platform-consulting",
        "Power Platform consulting",
        "Choose the approval pattern alongside audit, delegation, timeout, exception, and support requirements.",
    ),
    "guide-sharepoint-copilot-ready.html": (
        "/microsoft-365-copilot-readiness",
        "Microsoft 365 Copilot readiness",
        "Turn the checklist into an evidence-backed remediation backlog with owners and rollout gates.",
    ),
    "guide-get-started-sharepoint-agents.html": (
        "/microsoft-365-copilot-readiness",
        "Microsoft 365 Copilot readiness",
        "Validate permissions, knowledge scope, answer quality, lifecycle, and monitoring before publishing an agent broadly.",
    ),
    "guide-sharepoint-intranet.html": (
        "/sharepoint-intranet-development",
        "SharePoint intranet development",
        "Apply the planning framework with user research, publishing ownership, measurable findability, and adoption criteria.",
    ),
    "guide-power-apps-sharepoint.html": (
        "/power-platform-consulting",
        "Power Platform consulting",
        "Plan delegation, environments, data policy, application lifecycle, ownership, and support before production rollout.",
    ),
    "guide-powershell-self-signed-certificate-entra-app-registration.html": (
        "/sharepoint-consulting",
        "SharePoint automation support",
        "Use certificate authentication with least privilege, documented ownership, expiry monitoring, and a tested rotation procedure.",
    ),
    "guide-m365-migration-checklist.html": (
        "/microsoft-365-migration",
        "Microsoft 365 migration services",
        "Translate the checklist into workload waves, acceptance criteria, rollback decisions, and post-cutover evidence.",
    ),
}


def clean_schema(value, *, update_article_date: bool):
    if isinstance(value, dict):
        graph = value.get("@graph")
        if isinstance(graph, list):
            value["@graph"] = [
                clean_schema(item, update_article_date=update_article_date)
                for item in graph
                if not (
                    isinstance(item, dict)
                    and (
                        item.get("@id") == FAKE_AUTHOR_ID
                        or item.get("name") in FAKE_PEOPLE
                    )
                )
            ]
        if value.get("@id") == FAKE_AUTHOR_ID:
            return {"@id": ORG_ID}
        if value.get("@type") == "Organization":
            for unsupported in ("employee", "numberOfEmployees", "award", "foundingDate"):
                value.pop(unsupported, None)
        for key in list(value):
            if key != "@graph":
                value[key] = clean_schema(value[key], update_article_date=update_article_date)
        if value.get("@type") == "Article":
            if update_article_date:
                value["dateModified"] = TODAY
            value["author"] = {"@id": ORG_ID}
        return value
    if isinstance(value, list):
        return [
            clean_schema(item, update_article_date=update_article_date)
            for item in value
            if not (isinstance(item, dict) and item.get("name") in FAKE_PEOPLE)
        ]
    if value == FAKE_AUTHOR_ID:
        return ORG_ID
    if value == "https://oceancloudconsults.com/about#team":
        return "https://oceancloudconsults.com/editorial-policy"
    return value


def rewrite_ld_json(html: str, *, update_article_date: bool) -> str:
    def replace(match: re.Match[str]) -> str:
        payload = json.loads(match.group(2))
        cleaned = clean_schema(payload, update_article_date=update_article_date)
        return f'{match.group(1)}\n  {json.dumps(cleaned, ensure_ascii=False, indent=2)}\n  {match.group(3)}'

    return LD_JSON_RE.sub(replace, html)


def add_visible_publisher(html: str) -> str:
    if 'href="/editorial-policy"' in html:
        return html
    pattern = re.compile(r'(<div class="article-meta">)(.*?)(</div>)', re.DOTALL)
    match = pattern.search(html)
    if not match:
        return html
    replacement = (
        match.group(1)
        + match.group(2)
        + '\n        <span class="art-read">Published by <a href="/editorial-policy">OceanCloud</a></span>\n      '
        + match.group(3)
    )
    return html[: match.start()] + replacement + html[match.end() :]


def add_priority_path(html: str, filename: str) -> str:
    if filename not in PRIORITY_LINKS or 'data-recovery-path="true"' in html:
        return html
    href, label, explanation = PRIORITY_LINKS[filename]
    block = (
        '\n      <div class="art-callout" data-recovery-path="true">\n'
        f'        <p><strong>Implementation path:</strong> {explanation} '
        f'<a href="{href}">{label} &rarr;</a></p>\n'
        '      </div>\n\n'
    )
    marker = '<div class="related-section">'
    index = html.find(marker)
    if index < 0:
        return html
    return html[:index] + block + html[index:]


def update_guide(path: Path) -> None:
    html = path.read_text(encoding="utf-8")
    html = rewrite_ld_json(html, update_article_date=True)
    html = html.replace("https://oceancloudconsults.com/about#team", "/editorial-policy")
    html = html.replace('href="/about#team"', 'href="/editorial-policy"')
    html = html.replace("James Whitfield", "OceanCloud")
    html = add_visible_publisher(html)
    html = add_priority_path(html, path.name)
    if '<li><a href="/editorial-policy">Editorial Policy</a></li>' not in html:
        html = html.replace(
            '<li><a href="/about">About Us</a></li>',
            '<li><a href="/about">About Us</a></li>\n        <li><a href="/editorial-policy">Editorial Policy</a></li>',
        )
    html = re.sub(r"[ \t]+(?=\r?$)", "", html, flags=re.MULTILINE)
    path.write_text(html, encoding="utf-8")


def clean_sitewide_trust_claims() -> int:
    changed = 0
    replacements = {
        "Microsoft Solutions Partner specialising in SharePoint consulting, Microsoft 365 migration, Power Platform development, and workplace transformation.":
            "Microsoft 365 consultancy focused on SharePoint, migration, Power Platform, Copilot readiness, and workplace transformation.",
        "Microsoft Solutions Partner specialising in SharePoint, M365, Power Platform, and workplace transformation across the United States.":
            "Microsoft 365 consultancy focused on SharePoint, migration, Power Platform, Copilot readiness, and workplace transformation.",
        "Microsoft Solutions Partner specialising in SharePoint, M365, Power Platform, and workplace transformation.":
            "Microsoft 365 consultancy focused on SharePoint, migration, Power Platform, Copilot readiness, and workplace transformation.",
        "OceanCloud — Microsoft Solutions Partner.": "OceanCloud.",
        "OceanCloud's certified Microsoft 365 consultants": "OceanCloud",
        "OceanCloud's certified consultants": "OceanCloud",
        "OceanCloud&#x27;s certified consultants": "OceanCloud",
        "our certified consultants": "OceanCloud",
        "a certified M365 consultant": "an M365 consultant",
        "We are a Microsoft Solutions Partner providing SharePoint and Microsoft 365 consultancy services.":
            "We provide SharePoint and Microsoft 365 consultancy services.",
        "curated weekly by OceanCloud since May 2026": "curated by OceanCloud with links to original sources",
        "Updated every week.": "Updated when a reviewed digest is published.",
        "Updated weekly.": "Updated when a reviewed digest is published.",
        "Weekly roundup of what matters for your business.": "A source-linked digest of what matters for your business.",
        "Weekly SharePoint and Microsoft 365 updates": "SharePoint and Microsoft 365 updates",
    }
    for path in sorted(ROOT.rglob("*.html")):
        html = path.read_text(encoding="utf-8")
        original = html
        if any(name in html for name in FAKE_PEOPLE):
            html = rewrite_ld_json(html, update_article_date=False)
        for source, replacement in replacements.items():
            html = html.replace(source, replacement)
        if html != original:
            path.write_text(html, encoding="utf-8")
            changed += 1
    return changed


def update_sitemaps() -> None:
    guide_sitemap = ROOT / "sitemap-guides.xml"
    text = guide_sitemap.read_text(encoding="utf-8")
    text = re.sub(r"<lastmod>[^<]+</lastmod>", f"<lastmod>{TODAY}</lastmod>", text)
    guide_sitemap.write_text(text, encoding="utf-8")

    sitemap_index = ROOT / "sitemap-index.xml"
    text = sitemap_index.read_text(encoding="utf-8")
    text = re.sub(r"<lastmod>[^<]+</lastmod>", f"<lastmod>{TODAY}</lastmod>", text)
    sitemap_index.write_text(text, encoding="utf-8")


def update_search_index() -> None:
    path = ROOT / "data" / "search-index.json"
    entries = json.loads(path.read_text(encoding="utf-8"))
    entries = [entry for entry in entries if entry.get("id") != "editorial-policy"]
    entries.append(
        {
            "id": "editorial-policy",
            "type": "page",
            "tag": "Company",
            "title": "Editorial Policy and Technical Review",
            "heading": "Accountable technical publishing",
            "excerpt": "How OceanCloud sources, reviews, updates, and corrects Microsoft 365 and SharePoint guidance.",
            "body": "Primary sources practical scope original value automation disclosure corrections public change history.",
            "url": "editorial-policy",
            "dateDisplay": "",
            "dateSort": "",
        }
    )
    path.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    trust_pages = clean_sitewide_trust_claims()
    guides = sorted(GUIDE_DIR.glob("guide-*.html"))
    for guide in guides:
        update_guide(guide)
    update_search_index()
    update_sitemaps()
    print(f"[ok] updated {len(guides)} guides, {trust_pages} trust pages, search index, and sitemaps")


if __name__ == "__main__":
    main()
