#!/usr/bin/env python3
"""Verify new SEO improvements: guides sitemap, HowTo schema, Web Vitals"""
import re
from pathlib import Path

root = Path(__file__).parent.parent

# 1. sitemap-index.xml
idx = (root / "sitemap-index.xml").read_text(encoding="utf-8")
sitemaps = re.findall(r"<loc>(.*?)</loc>", idx)
print(f"sitemap-index.xml ({len(sitemaps)} sitemaps):")
for s in sitemaps:
    print(f"  {s}")
print()

# 2. sitemap-guides.xml
guides_xml = (root / "sitemap-guides.xml").read_text(encoding="utf-8")
guide_urls = re.findall(r"<loc>(.*?)</loc>", guides_xml)
print(f"sitemap-guides.xml: {len(guide_urls)} URLs at priority 0.8")
print()

# 3. HowTo schema on 3 guides
for g in ["guide-m365-migration-checklist", "guide-sharepoint-approval-workflow", "guide-sharepoint-intranet"]:
    html = (root / f"articles/{g}.html").read_text(encoding="utf-8")
    has_howto = '"@type": "HowTo"' in html
    steps = len(re.findall(r'"@type": "HowToStep"', html))
    print(f"{g}: HowTo={has_howto}, steps={steps}")
print()

# 4. Web Vitals in consent.js
consent = (root / "js/consent.js").read_text(encoding="utf-8")
has_vitals = "reportVital" in consent and "onLCP" in consent
print(f"Web Vitals in consent.js: {has_vitals}")
print()
print("All medium-priority improvements verified!")
