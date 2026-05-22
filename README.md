# OceanCloud — Microsoft 365 Consultancy Website

> A fast, fully static website for **OceanCloud** — a Microsoft Solutions Partner specialising in SharePoint Online, Microsoft 365, Power Platform, and workplace transformation.

---

## Overview

OceanCloud is built as a **pure HTML / CSS / JavaScript** site — no frameworks, no build step, no dependencies. Every page loads instantly and works without a server. AI and search features are powered by third-party APIs called directly from the browser.

**Live site:** [oceancloudconsults.com](https://oceancloudconsults.com)

---

## Pages

| File | Page | Description |
|---|---|---|
| `index.html` | Home | Hero, services overview, process, testimonials, CTA |
| `services.html` | Services | Full breakdown of 6 service categories |
| `about.html` | About | Story, team (6 members), values, certifications |
| `case-studies.html` | Case Studies | 6 case studies with category filters |
| `contact.html` | Contact | Contact form, phone/email, WhatsApp |
| `news.html` | News & Blog | Articles, blog posts, roadmap items |
| `archive.html` | Archive | Older articles and posts |
| `search.html` | Search | Three-mode search (Articles / Web / AI) |
| `privacy.html` | Privacy Policy | GDPR/CCPA privacy notice |
| `terms.html` | Terms of Service | Terms and conditions |
| `cookies.html` | Cookie Policy | Cookie usage policy |
| `404.html` | 404 | Custom not-found page |

---

## Features

### AI Chatbot (OceanBot)
Powered by **Groq + Llama 3.3 70B**. Appears on every page as a floating widget.

- Rule-based responses for common M365/SharePoint questions (instant, no API call)
- Automatic AI fallback for anything not matched by a rule
- Prefix bypass: start any message with `search`, `research`, or `find` to force AI
- Conversation history (last 6 turns sent to AI for context)
- Word-boundary keyword matching (prevents false rule triggers)

**File:** `js/chat.js`

---

### Three-Mode Search
A dedicated search page with three tabs:

| Tab | How it works |
|---|---|
| **Articles** | Client-side index of 24 pages/posts. Keyword scoring + `<mark>` term highlighting. No API needed. |
| **Web Search** | Google Custom Search Engine (CSE) — explicit rendering API, re-executes on each query without re-injecting the script. |
| **AI** | Redirects to Perplexity AI with the current query pre-filled. |

URL parameter support: `/search?q=your+query` pre-fills and runs the search automatically.

**Files:** `search.html`, `js/search.js`

---

### Cookie Consent
GDPR/CCPA compliant consent banner. Stores preference in `localStorage`. No tracking until consent is given.

**File:** `js/consent.js`

---

### Particle Background
Subtle animated particle canvas on hero sections.

**File:** `js/particles.js`

---

## Integrations

### Groq — Chatbot AI
| Detail | Value |
|---|---|
| Provider | [Groq](https://console.groq.com) |
| Model | `llama-3.3-70b-versatile` |
| Endpoint | `https://api.groq.com/openai/v1/chat/completions` |
| Auth | `Authorization: Bearer YOUR_KEY` |
| Free tier | 14,400 requests/day · 30 req/min · No credit card needed |

To update the key, edit line 7 of `js/chat.js`:
```js
const GROQ_API_KEY = 'gsk_...';
```

---

### Google Custom Search Engine — Web Search
| Detail | Value |
|---|---|
| Provider | [Google Programmable Search](https://programmablesearchengine.google.com) |
| CSE ID | `1245cccaad091448b` |
| Rendering | Explicit API (`parsetags: 'explicit'`) |

To update the CSE ID, edit line 1 of `js/search.js`:
```js
var GOOGLE_CSE_ID = '1245cccaad091448b';
```

---

### Perplexity AI — AI Search Tab
No API key needed. Queries are redirected to:
```
https://www.perplexity.ai/search?q=YOUR_QUERY
```

---

## File Structure

```
OceanCloud/
├── index.html
├── services.html
├── about.html
├── case-studies.html
├── contact.html
├── news.html
├── archive.html
├── search.html
├── privacy.html
├── terms.html
├── cookies.html
├── 404.html
├── coming-soon.html
├── sitemap.xml
├── robots.txt
├── CNAME                  ← GitHub Pages custom domain
│
├── css/
│   ├── style.css          ← Global styles, navbar, footer, design tokens
│   ├── pages.css          ← Inner-page styles (hero, cards, sections)
│   └── darkstar.css       ← Dark theme overrides
│
└── js/
    ├── main.js            ← Scroll effects, nav, counters, mobile menu
    ├── chat.js            ← OceanBot chatbot (Groq/Llama 3.3)
    ├── search.js          ← Three-mode search engine
    ├── particles.js       ← Hero particle animation
    └── consent.js         ← Cookie consent banner
```

---

## Design System

| Token | Value |
|---|---|
| `--ocean-dark` | `#071a2e` — page background |
| `--ocean-blue` | `#0077b6` — primary blue |
| `--ocean-bright` | `#00b4d8` — bright accent |
| `--accent-teal` | `#06d6a0` — teal highlight |
| Font | Inter (Google Fonts) |
| Animations | IntersectionObserver `.reveal` / `.visible` classes |
| Counters | `data-target` / `data-suffix` attributes |

---

## Deployment

Hosted on **GitHub Pages** with a custom domain via `CNAME`.

```
Repository  →  github.com/vipins5/OceanCloudRootSite
Branch      →  main
Domain      →  oceancloudconsults.com
```

Every `git push` to `main` deploys automatically.

---

## Cache Busting

JS files use `?v=N` query parameters on all `<script>` tags to force browsers to load updated files after deploys. Current versions:

| File | Version |
|---|---|
| `main.js` | `?v=7` |
| `particles.js` | `?v=3` |
| `consent.js` | `?v=3` |
| `chat.js` | `?v=6` |
| `search.js` | `?v=1` |

Increment the version number on all pages when updating a JS file.

---

## Microsoft Partner Details

| Detail | Value |
|---|---|
| Status | Microsoft Solutions Partner (Modern Work + Security) |
| Founded | 2013 |
| Team | 15 certified consultants |
| Projects | 150+ delivered |
| Satisfaction | 98% |
| Certifications | MS-102, MS-203, SC-300, SC-400, PL-400, PL-600, AZ-104 and 40+ more |

---

*Built and maintained by the OceanCloud team.*
