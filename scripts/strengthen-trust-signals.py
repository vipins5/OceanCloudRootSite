#!/usr/bin/env python3
"""Remove unverifiable homepage claims and publish inspectable trust evidence."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_section(text: str, start: str, end: str, replacement: str) -> str:
    left = text.find(start)
    if left < 0:
        return text
    right = text.find(end, left)
    if right < 0:
        return text
    return text[:left] + replacement.rstrip() + "\n\n" + text[right:]


def write(name: str, text: str) -> None:
    (ROOT / name).write_text(text, encoding="utf-8")


def remove_between(text: str, start: str, end: str) -> str:
    left = text.find(start)
    if left < 0:
        return text
    right = text.find(end, left)
    if right < 0:
        return text
    return text[:left] + text[right:]


def sanitize_business_schema(text: str) -> str:
    text = re.sub(r',?\s*"foundingDate":\s*"[^"]+"', '', text)
    text = re.sub(r',?\s*"numberOfEmployees":\s*\{.*?\}', '', text, flags=re.S)
    text = re.sub(r',?\s*"employee":\s*\[.*?\]', '', text, flags=re.S)
    text = re.sub(r',?\s*"hasCredential":\s*\{.*?\}', '', text, flags=re.S)
    return text


index_path = ROOT / "index.html"
index = index_path.read_text(encoding="utf-8")
index = index.replace(
    "Microsoft Solutions Partner for SharePoint consulting, Microsoft 365 migration, Power Platform, and Teams across the US. Free 60-min call.",
    "SharePoint consulting, Microsoft 365 migration, Power Platform, and Copilot readiness across the US. Review our public technical work and book a free 60-minute call.",
)
index = index.replace(
    "Expert SharePoint consulting, Microsoft 365 migration, and Microsoft 365 support. Microsoft Solutions Partner serving businesses across the United States.",
    "Source-backed SharePoint consulting, Microsoft 365 migration, and Power Platform delivery for organisations across the United States.",
)
index = index.replace(
    "Expert SharePoint & Microsoft 365 consultants. Migration, support, Power Platform and Teams — Microsoft Solutions Partner, United States.",
    "SharePoint and Microsoft 365 consulting with public technical work, source-backed guidance, and clear engagement terms.",
)
index = sanitize_business_schema(index)
index = index.replace(', Microsoft Solutions Partner" />', '" />')
index = index.replace(
    '<span class="hsr-num" data-target="150" data-suffix="+">150+</span>\n            <span class="hsr-lbl">Projects delivered</span>',
    '<span class="hsr-num">Public</span>\n            <span class="hsr-lbl">Implementation history</span>',
).replace(
    '<span class="hsr-num" data-target="98" data-suffix="%">98%</span>\n            <span class="hsr-lbl">Satisfaction rate</span>',
    '<span class="hsr-num">36</span>\n            <span class="hsr-lbl">Technical guides</span>',
).replace(
    '<span class="hsr-num" data-target="12" data-suffix=" yrs">12 yrs</span>\n            <span class="hsr-lbl">Experience</span>',
    '<span class="hsr-num">Live</span>\n            <span class="hsr-lbl">Service transparency</span>',
)
index = replace_section(index, '<!-- ===== STATS ===== -->', '<!-- ===== WHY OCEANCLOUD ===== -->', '''<!-- ===== INSPECTABLE EVIDENCE ===== -->
<section id="stats">
  <div class="container">
    <div class="stats-grid reveal">
      <a class="stat-block" href="https://github.com/vipins5/OceanCloudRootSite" target="_blank" rel="noopener noreferrer"><div class="stat-num">Public</div><div class="stat-lbl">Website implementation and change history on GitHub</div></a>
      <a class="stat-block" href="/guides"><div class="stat-num">36</div><div class="stat-lbl">Technical guides with official Microsoft and community references</div></a>
      <a class="stat-block" href="/status"><div class="stat-num">Live</div><div class="stat-lbl">Public Microsoft 365 service-status experience</div></a>
      <a class="stat-block" href="/contact"><div class="stat-num">Clear</div><div class="stat-lbl">Written scope, risks, acceptance criteria, and next steps</div></a>
    </div>
  </div>
</section>''')
index = index.replace(
    '<h3>Microsoft Solutions Partner</h3>\n          <p>Microsoft\'s highest partner designation — verified annually against customer success metrics, certified staff counts, and live deployment track records. Not every firm qualifies.</p>\n          <span class="why-badge">Modern Work &amp; Security</span>',
    '<h3>Public Technical Work</h3>\n          <p>Review the implementation history behind this website, including accessibility, search, structured data, and Cloudflare changes.</p>\n          <a class="why-badge" href="https://github.com/vipins5/OceanCloudRootSite" target="_blank" rel="noopener noreferrer">Inspect on GitHub ↗</a>',
)
index = replace_section(index, '<!-- ===== TESTIMONIALS ===== -->', '<!-- ===== INDUSTRIES ===== -->', '''<!-- ===== VERIFIABLE TRUST ===== -->
<section id="testimonials">
  <div class="container">
    <div class="test-header reveal"><span class="section-label">Evidence Before Engagement</span><h2 class="test-title">Inspect the work before <em>you hire us.</em></h2></div>
    <div class="why-grid reveal">
      <div class="why-item"><div class="why-body"><h3>Source-backed guidance</h3><p>Our implementation guides link to Microsoft Learn, PnP PowerShell, and other primary technical references so recommendations can be checked.</p><a class="why-badge" href="/guides">Review the guides →</a></div></div>
      <div class="why-item"><div class="why-body"><h3>Public implementation history</h3><p>The source and change history for this website are public, including issue fixes and the validation used before publication.</p><a class="why-badge" href="https://github.com/vipins5/OceanCloudRootSite" target="_blank" rel="noopener noreferrer">View GitHub ↗</a></div></div>
      <div class="why-item"><div class="why-body"><h3>Operational transparency</h3><p>Use our live status experience to review how Microsoft 365 service information is surfaced and explained.</p><a class="why-badge" href="/status">Open status →</a></div></div>
      <div class="why-item"><div class="why-body"><h3>Clear delivery controls</h3><p>Every proposed engagement documents scope, assumptions, risks, acceptance criteria, and ownership before delivery begins.</p><a class="why-badge" href="/contact">Discuss your scope →</a></div></div>
    </div>
  </div>
</section>''')
index = replace_section(index, '<!-- ===== RESOURCE INDEX (CRAWL DISCOVERY) ===== -->', '<!-- ===== CTA ===== -->', '')
index = remove_between(index, '''          {
            "@type": "Question",
            "name": "What is a Microsoft Solutions Partner and why does it matter?",''', '''          {
            "@type": "Question",
            "name": "Do you work with small businesses, or only large enterprises?",''')
index = re.sub(r'\s*<details class="faq-item">\s*<summary>What is a Microsoft Solutions Partner and why does it matter\?</summary>.*?</details>', '', index, flags=re.S)
index = index.replace('Microsoft Solutions Partner specialising in SharePoint, M365, Power Platform, and workplace transformation across the United States.', 'Microsoft 365 and SharePoint consulting focused on secure, usable, maintainable outcomes.')
index = index.replace('Microsoft Solutions Partner specialising in SharePoint Online, Microsoft 365, Power Platform, and workplace transformation across the United States.', 'Microsoft 365 and SharePoint consultancy focused on secure, usable, maintainable outcomes across the United States.')
index = index.replace('Microsoft Solutions Partner for SharePoint consulting, Microsoft 365 migration, Power Platform, and Teams across the US.', 'SharePoint consulting, Microsoft 365 migration, Power Platform, and Copilot readiness across the US.')
index = index.replace('"logo": "https://oceancloudconsults.com/assets/logo.png",\n        "email"', '"logo": "https://oceancloudconsults.com/assets/logo.png",\n        "sameAs": ["https://github.com/vipins5/OceanCloudRootSite"],\n        "email"', 1)
write("index.html", index)

about = (ROOT / "about.html").read_text(encoding="utf-8")
about = about.replace('Your Certified <span>SharePoint &amp; Microsoft 365</span><br>Consulting Partner', 'Transparent <span>SharePoint &amp; Microsoft 365</span><br>Consulting')
about = about.replace('Certified Microsoft Solutions Partner. 12+ years, 150+ SharePoint and Microsoft 365 projects, 40+ certifications, 98% client satisfaction.', 'Meet OceanCloud and review the public technical work, source-backed guidance, delivery controls, and operational transparency behind our Microsoft 365 consulting.')
about = about.replace('Certified Microsoft Solutions Partner with 12+ years delivering SharePoint and Microsoft 365 projects. Meet the accredited consultants behind OceanCloud.', 'Review OceanCloud\'s public technical work, source-backed Microsoft 365 guidance, and transparent delivery approach.')
about = about.replace('Microsoft Solutions Partner with 12+ years of SharePoint and M365 expertise. 40+ certifications, 150+ projects delivered.', 'Microsoft 365 consulting backed by public technical work, source-linked guidance, and clear delivery controls.')
about = about.replace('SharePoint consultant, Microsoft 365 consultant, Microsoft Solutions Partner, certified SharePoint expert, M365 specialist, SharePoint consulting company USA, OceanCloud team', 'SharePoint consultant, Microsoft 365 consultant, M365 specialist, SharePoint consulting company USA, OceanCloud delivery approach')
about = about.replace('OceanCloud team — certified Microsoft Solutions Partner consultants', 'OceanCloud — transparent SharePoint and Microsoft 365 consulting')
about = replace_section(about, '<!-- ===== STORY ===== -->', '<!-- ===== STATS ===== -->', '''<!-- ===== STORY ===== -->
<section class="about-story"><div class="container"><div class="about-grid"><div class="about-visual reveal"><div class="about-img-main"><span class="big-icon">&#9729;</span></div><div class="about-badge"><div class="big-num">Open</div><div class="label">Evidence</div></div></div><div class="about-content reveal"><span class="section-tag">How We Work</span><h2 class="section-title">Trust built through <span class="grad-text">inspectable work</span></h2><p class="section-desc">OceanCloud focuses on SharePoint, Microsoft 365 migration, Power Platform, Copilot readiness, security, and adoption.</p><p style="color:var(--text-mid);font-size:.95rem;line-height:1.8;margin-bottom:20px;">Prospective clients can review our public implementation history and source-backed technical guidance before a discovery call. Proposed work is documented with scope, assumptions, risks, ownership, and acceptance criteria.</p><p style="color:var(--text-mid);font-size:.95rem;line-height:1.8;">Where a credential, reference, or customer artifact is relevant to due diligence, request it during the consultation rather than relying on an unsupported website badge.</p></div></div></div></section>''')
about = replace_section(about, '<!-- ===== STATS ===== -->', '<!-- ===== CTA ===== -->', '''<!-- ===== VERIFIABLE TRUST ===== -->
<section id="why" style="padding:80px 0;"><div class="container"><div class="team-header reveal"><span class="section-tag">Verify Before You Engage</span><h2 class="section-title">Evidence you can <span class="grad-text">inspect now</span></h2></div><div class="why-grid reveal"><a class="why-item" href="https://github.com/vipins5/OceanCloudRootSite" target="_blank" rel="noopener noreferrer"><div class="why-body"><h3>Public GitHub history</h3><p>Review implementation decisions, fixes, and validation history.</p><span class="why-badge">Open repository ↗</span></div></a><a class="why-item" href="/guides"><div class="why-body"><h3>Source-backed guides</h3><p>Technical guidance includes links to Microsoft Learn and primary documentation.</p><span class="why-badge">Review guides →</span></div></a><a class="why-item" href="/status"><div class="why-body"><h3>Live service transparency</h3><p>Inspect the public Microsoft 365 status experience.</p><span class="why-badge">View status →</span></div></a><a class="why-item" href="/contact"><div class="why-body"><h3>Documented delivery</h3><p>Request written scope, risks, acceptance criteria, and credential evidence relevant to your project.</p><span class="why-badge">Start due diligence →</span></div></a></div></div></section>''')
about = sanitize_business_schema(about)
about = about.replace('About OceanCloud | Expert SharePoint & Microsoft 365 Consultants | Microsoft Solutions Partner', 'About OceanCloud | Transparent Microsoft 365 Consulting')
about = about.replace('Meet OceanCloud — a certified Microsoft Solutions Partner with 12+ years of SharePoint and Microsoft 365 consulting experience serving businesses across the United States.', 'Review OceanCloud\'s public technical work, source-backed guidance, and documented Microsoft 365 delivery approach.')
about = about.replace('Microsoft Solutions Partner specialising in SharePoint consulting, Microsoft 365 migration, Power Platform development, and workplace transformation.', 'Microsoft 365 consultancy specialising in SharePoint, migration, Power Platform, and workplace transformation.')
about = about.replace('Microsoft Solutions Partner specialising in SharePoint, M365, Power Platform, and workplace transformation.', 'Microsoft 365 and SharePoint consulting focused on secure, usable, maintainable outcomes.')
write("about.html", about)

for name in ("contact.html", "services.html"):
    text = (ROOT / name).read_text(encoding="utf-8")
    text = sanitize_business_schema(text)
    text = text.replace('Microsoft Solutions Partner specialising in SharePoint, M365, Power Platform, and workplace transformation.', 'Microsoft 365 and SharePoint consulting focused on secure, usable, maintainable outcomes.')
    text = text.replace('Microsoft Solutions Partner specialising in SharePoint consulting, Microsoft 365 migration, Power Platform development, and workplace transformation.', 'Microsoft 365 consultancy specialising in SharePoint, migration, Power Platform, and workplace transformation.')
    text = text.replace('Microsoft Solutions Partner offering SharePoint consulting, Microsoft 365 migration, and M365 support across the United States.', 'SharePoint and Microsoft 365 consultancy offering migration, Power Platform, Copilot readiness, and support across the United States.')
    text = text.replace('SharePoint intranet, Microsoft 365 migration, Teams, Power Platform, and security consulting. Fixed-price engagements. Microsoft Solutions Partner, USA.', 'SharePoint intranet, Microsoft 365 migration, Teams, Power Platform, security, and Copilot consulting with clear engagement terms.')
    write(name, text)

case_path = ROOT / "case-studies.html"
case = case_path.read_text(encoding="utf-8")
note = 'Supporting references and project artifacts can be discussed during qualified due diligence, subject to client confidentiality.'
if note not in case:
    case = case.replace('<!-- ===== CASE STUDIES ===== -->', f'<div class="container"><p class="section-desc" style="margin:0 auto 28px;text-align:center;">{note}</p></div>\n\n<!-- ===== CASE STUDIES ===== -->')
write("case-studies.html", case)

search_path = ROOT / "data/search-index.json"
entries = json.loads(search_path.read_text(encoding="utf-8"))
for entry in entries:
    if entry.get("id") == "home":
        entry["excerpt"] = "SharePoint consulting, Microsoft 365 migration, Power Platform, and Copilot readiness across the US. Review public technical work and book a free consultation."
        entry["body"] = "SharePoint and Microsoft 365 consulting. Public implementation history, 36 source-backed technical guides, live service transparency, clear scope, risks, ownership, and acceptance criteria."
    elif entry.get("id") == "about":
        entry["excerpt"] = "Review OceanCloud's public technical work, source-backed guidance, and documented Microsoft 365 delivery approach."
        entry["body"] = "OceanCloud trust and delivery approach. Public GitHub implementation history, Microsoft Learn source trails, live service transparency, and documented engagement controls."
    elif entry.get("id") == "services":
        entry["excerpt"] = "SharePoint intranet, Microsoft 365 migration, Teams, Power Platform, security, and Copilot consulting with clear engagement terms."
search_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for sitemap in ("sitemap.xml", "sitemap-guides.xml"):
    path = ROOT / sitemap
    text = path.read_text(encoding="utf-8")
    if sitemap == "sitemap.xml":
        text = re.sub(r'(<loc>https://oceancloudconsults\.com/(?:|about|services|contact|sharepoint-consulting|microsoft-365-migration|microsoft-365-copilot-readiness|power-platform-consulting|sharepoint-intranet-development)</loc>\s*<lastmod>)[^<]+', r'\g<1>2026-07-23', text)
    else:
        text = re.sub(r'(<loc>https://oceancloudconsults\.com/articles/guide-get-started-sharepoint-agents</loc>\s*<lastmod>)[^<]+', r'\g<1>2026-07-23', text)
    path.write_text(text, encoding="utf-8")

print("[ok] strengthened inspectable trust signals and removed the homepage resource dump")
