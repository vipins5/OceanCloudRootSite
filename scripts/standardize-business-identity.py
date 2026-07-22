#!/usr/bin/env python3
"""Standardize OceanCloud's public identity and structured contact data."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ORG_ID = "https://oceancloudconsults.com/#organization"
LEGAL_NAME = "OceanCloud Consultants"

LD_JSON_RE = re.compile(
    r'(<script\s+type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)',
    re.IGNORECASE | re.DOTALL,
)


def business_kind(value: dict) -> str | None:
    value_type = value.get("@type")
    types = set(value_type if isinstance(value_type, list) else [value_type])
    if (
        (value.get("@id") == ORG_ID and "Organization" in types)
        or "ProfessionalService" in types
        or "LocalBusiness" in types
    ):
        return "primary"
    if (
        "Organization" in types
        and (
            value.get("name") in {"OceanCloud", LEGAL_NAME}
            or str(value.get("url", "")).rstrip("/") == "https://oceancloudconsults.com"
        )
    ):
        return "publisher"
    return None


def standardize_schema(value):
    if isinstance(value, dict):
        for key in list(value):
            value[key] = standardize_schema(value[key])

        value_type = value.get("@type")
        types = set(value_type if isinstance(value_type, list) else [value_type])
        if value.get("@id") == ORG_ID and not any(types):
            return {"@id": ORG_ID}
        if "WebSite" in types:
            value["name"] = "OceanCloud"
            for key in ("alternateName", "legalName", "telephone", "email", "address", "areaServed", "contactPoint"):
                value.pop(key, None)

        kind = business_kind(value)
        if kind:
            value["name"] = LEGAL_NAME
            value["alternateName"] = "OceanCloud"
            value["legalName"] = LEGAL_NAME
        if kind == "publisher":
            for key in ("telephone", "email", "address", "areaServed", "contactPoint"):
                value.pop(key, None)
        if kind == "primary":
            address = value.get("address") if isinstance(value.get("address"), dict) else {}
            address.update(
                {
                    "@type": "PostalAddress",
                    "addressLocality": "Dallas",
                    "addressRegion": "TX",
                    "addressCountry": "US",
                }
            )
            value.update(
                {
                    "telephone": "+1-469-809-4053",
                    "email": "oceancloudconsults@gmail.com",
                    "address": address,
                    "areaServed": {"@type": "Country", "name": "United States"},
                    "contactPoint": [
                        {
                            "@type": "ContactPoint",
                            "name": "Main phone",
                            "telephone": "+1-469-809-4053",
                            "contactType": "sales and customer service",
                            "availableLanguage": "English",
                            "description": "Available Monday-Friday, 9:00 AM-6:00 PM Eastern Time.",
                        },
                        {
                            "@type": "ContactPoint",
                            "name": "WhatsApp",
                            "telephone": "+1-917-675-3126",
                            "contactType": "customer support",
                            "contactOption": "WhatsApp",
                            "availableLanguage": "English",
                            "description": "Available Monday-Friday, 9:00 AM-6:00 PM Eastern Time.",
                        },
                    ],
                }
            )
        return value
    if isinstance(value, list):
        return [standardize_schema(item) for item in value]
    return value


def rewrite_ld_json(html: str) -> str:
    def replace(match: re.Match[str]) -> str:
        payload = json.loads(match.group(2))
        payload = standardize_schema(payload)
        return f"{match.group(1)}\n  {json.dumps(payload, ensure_ascii=False, indent=2)}\n  {match.group(3)}"

    return LD_JSON_RE.sub(replace, html)


def update_html(path: Path) -> bool:
    html = path.read_text(encoding="utf-8")
    original = html
    html = rewrite_ld_json(html)
    html = html.replace("OceanCloud LLC", LEGAL_NAME)
    html = html.replace(
        '<meta name="author" content="OceanCloud" />',
        f'<meta name="author" content="{LEGAL_NAME}" />',
    )
    html = html.replace(
        '<meta property="og:site_name" content="OceanCloud" />',
        f'<meta property="og:site_name" content="{LEGAL_NAME}" />',
    )
    html = re.sub(
        r'(<meta\s+property=["\']og:site_name["\']\s+content=["\'])OceanCloud(["\'])',
        rf'\1{LEGAL_NAME}\2',
        html,
        flags=re.IGNORECASE,
    )
    html = html.replace(
        '<li><a href="tel:+14698094053">+1 (469) 809-4053</a></li>',
        '<li><a href="tel:+14698094053">Main: +1 (469) 809-4053</a></li>',
    )
    html = re.sub(
        r'(<li><a href="https://wa\.me/19176753126"[^>]*>)WhatsApp(?:\s*&#8599;|\s*↗)?(</a></li>)',
        r'\1WhatsApp: +1 (917) 675-3126 &#8599;\2',
        html,
    )
    if html != original:
        path.write_text(html, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = 0
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in {".git", "node_modules", ".venv"} for part in path.parts):
            continue
        changed += update_html(path)
    search_index = ROOT / "data" / "search-index.json"
    search_text = search_index.read_text(encoding="utf-8")
    search_text = search_text.replace("OceanCloud LLC", LEGAL_NAME)
    search_text = search_text.replace("Microsoft Solutions Partner", "Microsoft 365 consultancy")
    search_index.write_text(search_text, encoding="utf-8")
    print(f"[ok] standardized identity in {changed} HTML files")


if __name__ == "__main__":
    main()
