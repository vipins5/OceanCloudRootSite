#!/usr/bin/env python3
"""Generate focused, indexable commercial service landing pages."""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://oceancloudconsults.com"

SERVICES = [
    {
        "slug": "sharepoint-consulting",
        "title": "SharePoint Consulting Services | OceanCloud",
        "description": "SharePoint consulting for intranets, governance, permissions, SPFx and migration. Review our public technical work and fixed-price delivery approach.",
        "kicker": "SharePoint consulting",
        "h1": "Build a SharePoint environment <span>people can trust.</span>",
        "intro": "Plan, repair, govern, and extend SharePoint Online with a delivery team that connects technical architecture to measurable adoption.",
        "service": "SharePoint Consulting",
        "query_service": "SharePoint Consulting",
        "proof": [("Fixed-price delivery", "A written scope and price before implementation starts."), ("Security by design", "Permissions, lifecycle, and governance built into the solution."), ("12-month hypercare", "Post-launch support from a consultant who knows the environment.")],
        "outcomes": ["A scalable site and hub architecture", "Clear ownership, lifecycle, and sharing controls", "Faster content discovery and lower support demand", "Custom solutions that stay maintainable"],
        "deliverables": [("Architecture and governance", "Tenant assessment, information architecture, content types, metadata, permissions, and lifecycle controls."), ("Modern intranet delivery", "Communication sites, hubs, navigation, search, branded page patterns, and Viva Connections integration."), ("Custom development", "SPFx components, Microsoft Graph integrations, list experiences, and Power Platform extensions."), ("Health and remediation", "Permission audits, site cleanup, performance review, technical debt reduction, and an improvement roadmap.")],
        "faqs": [("What does a SharePoint consultant do?", "A SharePoint consultant turns business requirements into a secure site architecture, governance model, migration plan, and usable employee experience."), ("Can you improve an existing SharePoint environment?", "Yes. We can assess existing sites, permissions, search, navigation, content sprawl, and customisations before delivering a prioritised remediation plan."), ("How long does a SharePoint engagement take?", "Focused assessments usually take one to two weeks. Intranet builds and broader transformations commonly run for eight to twelve weeks, depending on scope.")],
        "guides": [("SharePoint permissions guide", "/articles/guide-sharepoint-permissions"), ("SharePoint intranet planning guide", "/articles/guide-sharepoint-intranet"), ("External sharing administration", "/articles/guide-sharepoint-external-sharing-complete-admin-guide")],
    },
    {
        "slug": "microsoft-365-migration",
        "title": "Microsoft 365 Migration Services | OceanCloud",
        "description": "Plan and deliver Microsoft 365 migrations for Exchange, SharePoint, OneDrive and tenant-to-tenant moves with tested cutover and validation.",
        "kicker": "Microsoft 365 migration",
        "h1": "Move to Microsoft 365 with <span>less risk.</span>",
        "intro": "Migrate mail, files, SharePoint, OneDrive, and collaboration workloads through a controlled programme with inventory, pilot, cutover, and validation built in.",
        "service": "Microsoft 365 Migration",
        "query_service": "M365 Migration",
        "proof": [("Workload inventory", "Know the volume, permissions, dependencies, and exceptions first."), ("Tested cutover", "Pilot users and rehearsed runbooks reduce go-live uncertainty."), ("Validation evidence", "Source-to-target checks confirm data and access after migration.")],
        "outcomes": ["A migration plan with owners and decision gates", "Preserved permissions, metadata, and business continuity", "A rehearsed cutover and rollback approach", "Clear post-migration validation and adoption support"],
        "deliverables": [("Discovery and assessment", "Inventory users, sites, mailboxes, file shares, permissions, customisations, and unsupported content."), ("Migration architecture", "Select tooling, target information architecture, identity approach, coexistence needs, waves, and cutover criteria."), ("Pilot and migration waves", "Run representative pilots, remediate exceptions, communicate with users, and migrate in controlled batches."), ("Validation and closure", "Compare counts, permissions, mail flow, sharing, search, and user access before decommissioning source systems.")],
        "faqs": [("How long does a Microsoft 365 migration take?", "A 100–500 user migration commonly takes four to eight weeks. Larger or highly customised environments need additional discovery and migration waves."), ("Can users keep working during migration?", "Usually yes. Coexistence, delta synchronisation, and planned cutover windows keep disruption low for most workloads."), ("Do you support tenant-to-tenant migrations?", "Yes. We plan identity, Exchange, OneDrive, SharePoint, and Teams migrations for mergers, acquisitions, divestitures, and rebrands.")],
        "guides": [("Microsoft 365 migration checklist", "/articles/guide-m365-migration-checklist"), ("PnP SharePoint site migration", "/articles/guide-sharepoint-pnp-site-migration"), ("Replace legacy SharePoint workflows", "/articles/guide-sharepoint-workflow-migration")],
    },
    {
        "slug": "microsoft-365-copilot-readiness",
        "title": "Microsoft 365 Copilot Readiness | OceanCloud",
        "description": "Prepare Microsoft 365 Copilot safely with oversharing assessment, permissions remediation, Purview controls, pilot governance and adoption measurement.",
        "kicker": "Copilot readiness",
        "h1": "Make your Microsoft 365 data <span>ready for Copilot.</span>",
        "intro": "Identify oversharing, strengthen governance, align information protection, and launch a measured Copilot pilot before expanding licences across the organisation.",
        "service": "Microsoft 365 Copilot Readiness",
        "query_service": "Microsoft 365 Copilot",
        "proof": [("Oversharing baseline", "Find broad access, anonymous links, and high-risk sites."), ("Governed pilot", "Define users, use cases, acceptable use, and success measures."), ("Actionable scorecard", "Prioritised remediation with owners and rollout gates.")],
        "outcomes": ["Visibility into SharePoint and OneDrive oversharing", "Aligned sensitivity labels, DLP, and retention controls", "A controlled pilot with measurable use cases", "A governance model for agents and Copilot Studio"],
        "deliverables": [("Data exposure assessment", "Review sharing links, broad groups, inactive sites, sensitive content, and search exposure across SharePoint and OneDrive."), ("Security and compliance alignment", "Map sensitivity labels, DLP, retention, audit, and identity controls to Copilot risks and use cases."), ("Pilot design", "Select pilot personas, prioritise scenarios, prepare communications, build prompt guidance, and define support routes."), ("Measurement and scale plan", "Track adoption, time saved, answer quality, risk events, and business outcomes before wider licensing.")],
        "faqs": [("Why does SharePoint oversharing matter for Copilot?", "Copilot can surface content a user already has permission to access. Excessive permissions therefore become a data exposure and answer-quality problem."), ("Should we buy licences before a readiness assessment?", "A small pilot can be useful, but a readiness assessment should precede a broad purchase so security and content issues do not scale with licence deployment."), ("Does this include Copilot Studio agents?", "Yes. The same governance principles extend to knowledge sources, actions, authentication, testing, publishing, and agent lifecycle management.")],
        "guides": [("SharePoint Copilot readiness checklist", "/articles/guide-sharepoint-copilot-ready"), ("Copilot Agent for SharePoint", "/articles/guide-get-started-sharepoint-agents"), ("Copilot Studio with SharePoint", "/articles/guide-copilot-studio-sharepoint-integration")],
    },
    {
        "slug": "power-platform-consulting",
        "title": "Power Platform Consulting Services | OceanCloud",
        "description": "Build governed Power Apps, Power Automate workflows and Power BI solutions with secure architecture, ALM, adoption and measurable business outcomes.",
        "kicker": "Power Platform consulting",
        "h1": "Automate work without creating <span>low-code sprawl.</span>",
        "intro": "Design and deliver Power Apps, Power Automate, Dataverse, and Power BI solutions that are usable, governed, supportable, and ready to scale.",
        "service": "Power Platform Consulting",
        "query_service": "Power Platform",
        "proof": [("Outcome-led scope", "Start with the process, users, controls, and measurable result."), ("Governed environments", "DLP, ownership, ALM, and support are part of delivery."), ("Maintainable build", "Documented components and handover reduce long-term dependence.")],
        "outcomes": ["Less manual work and fewer spreadsheet handoffs", "Secure connectors, environments, and data policies", "Reliable deployment through development, test, and production", "Clear ownership, monitoring, and support documentation"],
        "deliverables": [("Process discovery", "Map the current workflow, exceptions, approvals, data sources, controls, and business measures."), ("Power Apps and Dataverse", "Build responsive canvas or model-driven apps with appropriate data modelling, roles, and validation."), ("Power Automate", "Deliver cloud or desktop flows with error handling, monitoring, approvals, and operational ownership."), ("Governance and ALM", "Establish environments, DLP policies, solutions, pipelines, naming, inventory, and support standards.")],
        "faqs": [("When should we use Power Apps instead of custom software?", "Power Apps is a strong fit for internal business processes that integrate with Microsoft 365 or Dataverse and need rapid, governed iteration."), ("Can you repair unreliable Power Automate flows?", "Yes. We review triggers, concurrency, connector limits, error handling, ownership, environment variables, and monitoring before stabilising the workflow."), ("Do you provide source and documentation?", "Yes. Handover includes solution packages, architecture notes, support guidance, and administrator or maker training appropriate to the engagement.")],
        "guides": [("Power Apps with SharePoint", "/articles/guide-power-apps-sharepoint"), ("Power Automate triggers and actions", "/articles/guide-power-automate-triggers-actions"), ("Multiple-approver workflow patterns", "/articles/guide-sharepoint-approval-multiple-approvers")],
    },
    {
        "slug": "sharepoint-intranet-development",
        "title": "SharePoint Intranet Development | OceanCloud",
        "description": "Plan and build a modern SharePoint intranet with research-led navigation, governance, search, Viva Connections, adoption and measurable outcomes.",
        "kicker": "SharePoint intranet development",
        "h1": "Launch an intranet employees <span>can actually navigate.</span>",
        "intro": "Create a modern SharePoint intranet around employee tasks, trusted publishing, findability, and governance—not around an organisational chart alone.",
        "service": "SharePoint Intranet Development",
        "query_service": "SharePoint Consulting",
        "proof": [("User-centred discovery", "Research tasks, audiences, publishing needs, and pain points."), ("Governed publishing", "Ownership, approvals, lifecycle, and analytics are built in."), ("Adoption plan", "Launch communications, champions, training, and measures support uptake.")],
        "outcomes": ["Task-based navigation and an evidence-led site structure", "Consistent page, news, and departmental publishing patterns", "Improved enterprise search and content findability", "A sustainable ownership and governance operating model"],
        "deliverables": [("Research and information architecture", "Stakeholder interviews, content inventory, card sorting, audience needs, navigation, taxonomy, and search planning."), ("Experience design and build", "Home, department, news, resource, and campaign patterns using modern SharePoint and accessible design."), ("Viva Connections", "Surface intranet content in Teams with an audience-aware dashboard, resources, and mobile experience."), ("Launch and adoption", "Publisher training, governance playbook, champions, communications, analytics baseline, and optimisation backlog.")],
        "faqs": [("How long does a SharePoint intranet take to build?", "A focused intranet commonly takes eight to twelve weeks. Content readiness, number of departments, integrations, and governance decisions affect the timeline."), ("Can you migrate content from an existing intranet?", "Yes. We inventory and classify existing content, assign owners, archive low-value material, and migrate approved content into the new structure."), ("Will the intranet work inside Microsoft Teams?", "Yes. Viva Connections can bring SharePoint news, navigation, dashboard cards, and resources into Teams for desktop and mobile users.")],
        "guides": [("SharePoint intranet guide", "/articles/guide-sharepoint-intranet"), ("SharePoint integrations guide", "/articles/guide-sharepoint-integrations"), ("SharePoint permissions guide", "/articles/guide-sharepoint-permissions")],
    },
]


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def render(service: dict) -> str:
    canonical = f"{SITE}/{service['slug']}"
    proof = "".join(f'<div class="service-proof-item"><strong>{esc(a)}</strong><span>{esc(b)}</span></div>' for a, b in service["proof"])
    outcomes = "".join(f'<div class="service-outcome">{esc(item)}</div>' for item in service["outcomes"])
    deliverables = "".join(f'<article class="service-card"><h3>{esc(a)}</h3><p>{esc(b)}</p></article>' for a, b in service["deliverables"])
    steps = [("Discover", "Confirm goals, users, constraints, risks, and measures."), ("Design", "Agree the architecture, controls, delivery plan, and acceptance criteria."), ("Deliver", "Build iteratively, demonstrate progress, test, and document."), ("Adopt", "Launch, train, measure, and support continuous improvement.")]
    process = "".join(f'<article class="service-step"><div class="service-step-num">0{i}</div><h3>{a}</h3><p>{b}</p></article>' for i, (a, b) in enumerate(steps, 1))
    faqs = "".join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in service["faqs"])
    faq_schema = [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in service["faqs"]]
    guides = "".join(f'<a class="btn-outline" href="{href}">{esc(label)} →</a>' for label, href in service["guides"])
    schema = {"@context": "https://schema.org", "@graph": [
        {"@type": "Service", "@id": canonical + "#service", "name": service["service"], "url": canonical, "description": service["description"], "provider": {"@id": SITE + "/#organization"}, "areaServed": {"@type": "Country", "name": "United States"}},
        {"@type": "WebPage", "@id": canonical + "#webpage", "url": canonical, "name": service["title"], "description": service["description"], "inLanguage": "en-US", "about": {"@id": canonical + "#service"}},
        {"@type": "FAQPage", "mainEntity": faq_schema},
    ]}
    return f'''<!DOCTYPE html>
<html lang="en"><head>
  <meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" /><meta name="theme-color" content="#0077b6" />
  <title>{esc(service['title'])}</title>
  <meta name="description" content="{esc(service['description'])}" />
  <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1" />
  <link rel="canonical" href="{canonical}" /><link rel="alternate" hreflang="en-US" href="{canonical}" />
  <meta property="og:type" content="website" /><meta property="og:site_name" content="OceanCloud" /><meta property="og:title" content="{esc(service['title'])}" /><meta property="og:description" content="{esc(service['description'])}" /><meta property="og:url" content="{canonical}" /><meta property="og:image" content="{SITE}/assets/og-services.jpg" />
  <meta name="twitter:card" content="summary_large_image" /><meta name="twitter:title" content="{esc(service['title'])}" /><meta name="twitter:description" content="{esc(service['description'])}" /><meta name="twitter:image" content="{SITE}/assets/og-services.jpg" />
  <link rel="preconnect" href="https://fonts.googleapis.com" /><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin /><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="css/style.css?v=3" /><link rel="stylesheet" href="css/pages.css?v=12" /><link rel="stylesheet" href="css/service-detail.css?v=1" /><link rel="stylesheet" href="css/darkstar.css?v=3" /><link rel="icon" type="image/svg+xml" href="favicon.svg" />
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
</head><body>
<a href="#main-content" class="skip-link">Skip to content</a><div id="c-dot"></div><div id="c-ring"></div>
<nav id="navbar"><div class="container nav-inner"><a href="/" class="nav-logo"><div class="logo-mark">OC</div><span class="logo-text">Ocean<span>Cloud</span></span></a><ul class="nav-links" id="navLinks"><li><a href="/"><span class="nav-num">01</span>Home</a></li><li><a href="/services" class="active-link"><span class="nav-num">02</span>Services</a></li><li><a href="/about"><span class="nav-num">03</span>About</a></li><li><a href="/case-studies"><span class="nav-num">04</span>Work</a></li><li><a href="/news"><span class="nav-num">05</span>News</a></li><li><a href="/guides"><span class="nav-num">06</span>Guides</a></li><li><a href="/contact" class="nav-cta">Get In Touch</a></li></ul><a href="/search" class="nav-search-btn" aria-label="Search">⌕</a><button class="hamburger" id="hamburger" aria-label="Toggle navigation" aria-expanded="false"><span></span><span></span><span></span></button></div></nav>
<main id="main-content"><section class="service-detail-hero"><div class="container"><nav class="service-breadcrumb"><a href="/">Home</a><span>/</span><a href="/services">Services</a><span>/</span><span>{esc(service['service'])}</span></nav><span class="service-kicker">{esc(service['kicker'])}</span><h1>{service['h1']}</h1><p>{esc(service['intro'])}</p><div class="service-hero-actions"><a class="btn-primary" href="/contact?service={esc(service['query_service'])}">Book a free consultation →</a><a class="btn-outline" href="#deliverables">See deliverables</a></div></div></section>
<section class="service-proof">{proof}</section>
<section class="service-section"><div class="container"><div class="service-section-head"><span class="section-label">Business outcomes</span><h2>What this engagement changes.</h2><p>Every workstream is tied to a practical operational, security, adoption, or delivery outcome.</p></div><div class="service-outcomes">{outcomes}</div></div></section>
<section class="service-section alt" id="deliverables"><div class="container"><div class="service-section-head"><span class="section-label">Scope</span><h2>What we can deliver.</h2><p>The final scope is shaped around your current environment and priorities—not a generic package.</p></div><div class="service-card-grid">{deliverables}</div></div></section>
<section class="service-section"><div class="container"><div class="service-section-head"><span class="section-label">Delivery model</span><h2>From discovery to adoption.</h2></div><div class="service-process">{process}</div></div></section>
<section class="service-section alt"><div class="container"><div class="service-section-head"><span class="section-label">Related guidance</span><h2>Prepare before the first call.</h2></div><div class="service-hero-actions">{guides}</div></div></section>
<section class="service-section"><div class="container"><div class="service-section-head"><span class="section-label">Evidence before engagement</span><h2>Inspect how we work.</h2><p>Review public implementation history, source-backed guidance, and live service transparency before discussing a scope.</p></div><div class="service-card-grid"><article class="service-card"><h3>Public implementation history</h3><p>This website's source and change history are available for technical review.</p><a href="https://github.com/vipins5/OceanCloudRootSite" target="_blank" rel="noopener noreferrer">Open GitHub ↗</a></article><article class="service-card"><h3>Source-backed guidance</h3><p>Our guides link to Microsoft Learn, PnP PowerShell, and other primary technical references.</p><a href="/guides">Review guides →</a></article><article class="service-card"><h3>Operational transparency</h3><p>Review the live Microsoft 365 service-status experience and our documented delivery approach.</p><a href="/status">View status →</a></article></div></div></section>
<section class="service-section"><div class="container service-faq"><div class="service-section-head"><span class="section-label">FAQ</span><h2>Common questions.</h2></div>{faqs}</div></section>
<section class="service-cta"><div class="container"><h2>Get a clear next step.</h2><p>Book a free 60-minute consultation. We will discuss the current environment, desired outcome, risks, and a realistic delivery approach.</p><a class="btn-primary" href="/contact?service={esc(service['query_service'])}">Book your free consultation →</a></div></section></main>
<footer><div class="container"><div class="footer-grid"><div class="footer-brand"><div class="logo-text"><div class="logo-mark">OC</div>Ocean<span>Cloud</span></div><p>Microsoft 365 and SharePoint consulting focused on secure, usable, maintainable outcomes.</p></div><div class="footer-col"><h4>Services</h4><ul><li><a href="/sharepoint-consulting">SharePoint Consulting</a></li><li><a href="/microsoft-365-migration">M365 Migration</a></li><li><a href="/microsoft-365-copilot-readiness">Copilot Readiness</a></li><li><a href="/power-platform-consulting">Power Platform</a></li><li><a href="/sharepoint-intranet-development">Intranet Development</a></li></ul></div><div class="footer-col"><h4>Company</h4><ul><li><a href="/about">About</a></li><li><a href="/editorial-policy">Editorial Policy</a></li><li><a href="/case-studies">Case Studies</a></li><li><a href="/guides">Guides</a></li><li><a href="/contact">Contact</a></li></ul></div><div class="footer-col"><h4>Contact</h4><ul><li><a href="mailto:oceancloudconsults@gmail.com">oceancloudconsults@gmail.com</a></li><li><a href="tel:+14698094053">+1 (469) 809-4053</a></li></ul></div></div><div class="footer-bottom"><div class="footer-bottom-inner"><span class="fb-copy">&copy; 2026 OceanCloud LLC</span><div class="fb-right"><a href="/privacy">Privacy</a><span class="fb-sep">·</span><a href="/terms">Terms</a></div></div></div></div></footer>
<a href="#" id="back-top" aria-label="Back to top">⇧</a>
<div id="oc-cookie-banner" role="dialog" aria-label="Cookie consent"><div class="ccb-inner"><div class="ccb-text"><strong>🍪 We use cookies</strong><span>Google Analytics helps us improve this site. No personal data is sold or shared. <a href="/cookies">Cookie policy</a></span></div><div class="ccb-btns"><button id="ccb-decline">Decline</button><button id="ccb-accept">Accept</button></div></div></div>
<script src="js/main.js?v=8"></script><script src="js/chat.js?v=7"></script><script src="js/consent.js?v=5"></script><script src="js/weather.js?v=6"></script>
</body></html>'''


def update_search_index() -> None:
    path = ROOT / "data" / "search-index.json"
    entries = json.loads(path.read_text(encoding="utf-8"))
    for entry in entries:
        if entry.get("id") == "home":
            entry["body"] = "SharePoint and Microsoft 365 consulting. Public implementation history, source-backed guides, live service transparency, and documented delivery controls."
        if entry.get("id") == "about":
            entry["body"] = "OceanCloud trust and delivery approach. Public GitHub history, Microsoft Learn source trails, live service transparency, and clear scope and acceptance criteria."
    ids = {f"service-{service['slug']}" for service in SERVICES}
    entries = [entry for entry in entries if entry.get("id") not in ids]
    new_entries = []
    for service in SERVICES:
        plain_h1 = service["h1"].replace("<span>", "").replace("</span>", "")
        new_entries.append({
            "id": f"service-{service['slug']}", "type": "page", "tag": "Service",
            "title": service["title"].replace(" | OceanCloud", ""), "heading": plain_h1,
            "excerpt": service["description"],
            "body": " ".join(service["outcomes"] + [text for pair in service["deliverables"] for text in pair]),
            "url": service["slug"], "dateDisplay": "", "dateSort": "",
        })
    insert_at = next((i + 1 for i, entry in enumerate(entries) if entry.get("id") == "services"), 1)
    entries[insert_at:insert_at] = new_entries
    path.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    for service in SERVICES:
        (ROOT / f"{service['slug']}.html").write_text(render(service), encoding="utf-8")
        print(f"[ok] {service['slug']}.html")
    update_search_index()
    print("[ok] data/search-index.json")


if __name__ == "__main__":
    main()
