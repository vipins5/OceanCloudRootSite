# OceanCloud — Microsoft 365 Consultancy Website

> A fast, fully static website for **OceanCloud** — a Microsoft Solutions Partner specialising in SharePoint Online, Microsoft 365, Power Platform, and workplace transformation.

---

## Overview

OceanCloud is built as a **pure HTML / CSS / JavaScript** site — no frameworks, no build step, no runtime dependencies. Core AI and search features are integrated through external services and a Cloudflare Worker backend.

**Live site:** [oceancloudconsults.com](https://oceancloudconsults.com)

---

## Pages

| File | Page | Description |
|---|---|---|
| `index.html` | Home | Hero, services overview, process, testimonials, CTA |
| `services.html` | Services | Full breakdown of 6 service categories |
| `about.html` | About | Story, team, values, certifications |
| `case-studies.html` | Case Studies | Case studies with category filters |
| `contact.html` | Contact | Contact form, phone/email, WhatsApp |
| `news.html` | News & Blog | News feed and updates |
| `archive.html` | Archive | Historical news archive |
| `guides.html` | Guides | Guide hub for implementation content |
| `faq.html` | FAQ | Frequently asked questions |
| `search.html` | Search | Three-mode search (Articles / Web / AI) |
| `status.html` | Status | Service and operations status |
| `message-center.html` | Message Center | Public status messages and communications |
| `comments-admin.html` | Comments Admin | Internal moderation/admin page |
| `privacy.html` | Privacy Policy | GDPR/CCPA privacy notice |
| `terms.html` | Terms of Service | Terms and conditions |
| `cookies.html` | Cookie Policy | Cookie usage policy |
| `404.html` | 404 | Custom not-found page |

---

## Features

### AI Chatbot (OceanBot)
Powered by **Groq + Llama 3.3 70B** with a Cloudflare Worker proxy.

- Rule-based responses for common M365/SharePoint questions
- Automatic AI fallback
- Prefix bypass: `search`, `research`, `find`
- Conversation history context window
- Word-boundary keyword matching

**File:** `js/chat.js`

### Three-Mode Search

| Tab | How it works |
|---|---|
| **Articles** | Client-side index of guides, articles, and key pages; keyword scoring + `<mark>` highlighting |
| **Web Search** | Google Programmable Search (CSE) with explicit render mode |
| **AI** | Redirects to Perplexity with query prefill |

URL parameter support: `/search?q=your+query` pre-fills and runs automatically.

**Files:** `search.html`, `js/search.js`

### Cookie Consent
Consent banner with `localStorage` preference handling.

**File:** `js/consent.js`

### Particle Background
Subtle animated hero canvas effect.

**File:** `js/particles.js`

---

## Integrations

### Groq — Chatbot AI via Cloudflare Worker

| Detail | Value |
|---|---|
| Model | `llama-3.3-70b-versatile` |
| Endpoint | `https://oceancloud-ai-proxy.oceancloud-ai-proxy.workers.dev/chat` |
| Worker folder | `oceancloud-ai-proxy/` |
| Secret | `GROQ_API_KEY` |

### Microsoft 365 Service Health via Cloudflare Worker

| Detail | Value |
|---|---|
| Endpoint | `https://oceancloud-ai-proxy.oceancloud-ai-proxy.workers.dev/m365/service-health` |
| Required Graph permission | `ServiceHealth.Read.All` (application) |
| Secrets | `M365_HEALTH_TENANT_ID`, `M365_HEALTH_CLIENT_ID`, `M365_HEALTH_CLIENT_SECRET` |

### Consultation Requests via Cloudflare Worker

The contact page submits once to `POST /contact`, validates Cloudflare
Turnstile on the server, stores the request in D1, and optionally sends a
SendGrid notification. New requests are available alongside comment moderation
in `comments-admin.html`.

Required deployment steps:

```powershell
cd oceancloud-ai-proxy
npx wrangler d1 migrations apply oceancloud-comments --remote
npx wrangler secret put SENDGRID_API_KEY
npx wrangler secret put SENDGRID_FROM_EMAIL
npx wrangler secret put CONTACT_NOTIFICATION_EMAIL
```

### Google Programmable Search (Web tab)

| Detail | Value |
|---|---|
| CSE ID | `1245cccaad091448b` |
| Config file | `js/search.js` |

### Perplexity (AI tab)
Redirect target: `https://www.perplexity.ai/search?q=YOUR_QUERY`

---

## File Structure

```text
OceanCloud/
├── index.html
├── services.html
├── about.html
├── case-studies.html
├── contact.html
├── news.html
├── archive.html
├── guides.html
├── faq.html
├── search.html
├── status.html
├── message-center.html
├── comments-admin.html
├── privacy.html
├── terms.html
├── cookies.html
├── 404.html
├── coming-soon.html
├── sitemap.xml
├── sitemap-index.xml
├── sitemap-mc.xml
├── feed.xml
├── llms.txt
├── robots.txt
├── CNAME
├── articles/
├── assets/
├── css/
│   ├── style.css
│   ├── pages.css
│   ├── article.css
│   ├── code.css
│   └── darkstar.css
├── js/
│   ├── main.js
│   ├── chat.js
│   ├── search.js
│   ├── particles.js
│   └── consent.js
├── scripts/
├── data/
├── mc/
└── oceancloud-ai-proxy/
```

---

## Deployment

Hosted on GitHub Pages with custom domain via `CNAME`.

```text
Repository: github.com/vipins5/OceanCloudRootSite
Branch:     main
Domain:     oceancloudconsults.com
```

Every push to `main` auto-deploys.

### Local Publishing Workflow

```powershell
python scripts/publish-local.py
```

Updates `sitemap.xml` and `feed.xml` based on local guide/article changes.

### Google Recrawl Workflow

Use the submitted XML sitemaps for site-wide discovery. For a small number of
materially updated pages, request indexing through Search Console URL
Inspection. The Google Indexing API is intentionally not used because these
pages are neither job postings nor livestream events.

### Local Pre-Push Hook

```powershell
git config core.hooksPath .githooks
```

The pre-push hook runs:

- `python scripts/check-links.py --strict`
- `python scripts/content-qa-report.py`
- `npm --prefix oceancloud-ai-proxy run -s test -- --run`
- `npm --prefix oceancloud-ai-proxy run -s typecheck`

---

## Secrets & Safety

- `.secrets/` is git-ignored.
- Never commit API tokens, `.env`, or secret helper files.
- Keep service-account key files such as `oceancloud-comments-*.json` local-only.

---

## Microsoft Partner Details

| Detail | Value |
|---|---|
| Status | Microsoft Solutions Partner (Modern Work + Security) |
| Founded | 2013 |
| Team | 15 certified consultants |
| Projects | 150+ delivered |
| Satisfaction | 98% |

---

*Built and maintained by the OceanCloud team.*
