---
Document: Backlink Outreach Tracker (executable version of backlink-outreach-strategy.md)
Date created: 2026-07-20
Status: Not started - 0 of 12 actions sent/claimed
---

# Backlink Outreach Tracker

This turns `backlink-outreach-strategy.md` into things that can actually be sent/claimed
this week. Update the Status column as you go — Sent / Replied / Live / Declined.

Best guides to lead with (technical, evergreen, solve one specific problem — the kind
of thing communities actually link to, not the broad marketing guides):

- `guide-sharepoint-pnp-site-migration` — https://oceancloudconsults.com/articles/guide-sharepoint-pnp-site-migration
- `guide-powershell-self-signed-certificate-entra-app-registration` — https://oceancloudconsults.com/articles/guide-powershell-self-signed-certificate-entra-app-registration (already ranking #2 in GSC for its exact-match query — good proof point to cite in pitches)
- `guide-pnp-entra-app-registration` — https://oceancloudconsults.com/articles/guide-pnp-entra-app-registration
- `guide-sharepoint-anonymous-links-report-remove-pnp-powershell` — https://oceancloudconsults.com/articles/guide-sharepoint-anonymous-links-report-remove-pnp-powershell
- `guide-infopath-forms-services-pdf-archive` — https://oceancloudconsults.com/articles/guide-infopath-forms-services-pdf-archive (timely: hard July 14 2026 deadline, high genuine search interest)

---

## Tier 0 — Zero outreach needed, highest authority, do these first

These are self-serve profile claims, not cold outreach. No one to convince — just fill
out a form under the business's real identity. Requires you (real business owner),
not something I can do on your behalf.

| # | Action | Why it matters | Status |
|---|--------|-----------------|--------|
| 1 | Claim/verify listing on **Microsoft "Find a Solutions Partner" directory** (partner.microsoft.com) — requires your real MPN ID | Highest-authority possible backlink (microsoft.com), and directly substantiates the "Microsoft Solutions Partner" claim made throughout the site | ☐ Not started |
| 2 | Create/claim **Google Business Profile** for the real business address | The site currently just embeds a generic "Dallas, TX" map query (`contact.html`), not a real GBP listing — there's no verified local business entity behind it yet | ☐ Not started |
| 3 | Create a real **LinkedIn Company Page** | I found the link on `coming-soon.html` pointed to an unrelated German company by name coincidence — removed it. There is currently no verified OceanCloud LinkedIn presence at all. | ☐ Not started (link removed pending real page) |
| 4 | Verify the **X/@oceancloud_x** account referenced in `twitter:site` meta tags sitewide is real and belongs to this business | Couldn't verify via automated fetch (X blocks it). Low SEO impact either way (Twitter Card meta isn't a backlink signal), but worth a manual check for brand consistency. | ☐ Not verified |

---

## Tier 1 — Microsoft-owned properties (draft ready to send)

**Target:** Microsoft Tech Community (techcommunity.microsoft.com) — SharePoint/Viva or
Microsoft 365 forum sections.

**Action:** Post as a genuine community contribution (not a link-drop) — answer an open
question in the SharePoint forum, and where truly relevant, mention the guide.

Draft post (for the InfoPath deadline guide, since it's genuinely time-sensitive):

```
Subject: InfoPath Forms Services retirement in SharePoint Online — practical PDF archive runbook

Publishing was blocked May 18, 2026; full service removal hits July 14, 2026 with no
extensions. If anyone's still working through their InfoPath inventory, I put together
a runbook for rendering the remaining XML forms to PDF before the cutoff, including the
Edge headless print-to-pdf approach and a metadata capture step so submissions stay
searchable after the forms are gone:
https://oceancloudconsults.com/articles/guide-infopath-forms-services-pdf-archive

Happy to compare notes if anyone hit different edge cases during their migration.
```

Status: ☐ Not sent

---

## Tier 2 — Microsoft MVP blogs (personalize before sending — do not mass-send this verbatim)

| MVP / Blog | URL | Best-fit guide to reference | Status |
|---|---|---|---|
| Paul Bullock | https://www.pkbullock.com/ | `guide-sharepoint-pnp-site-migration` | ☐ Not sent |
| Leon Finkelman | https://www.leonfinkelman.com/ | `guide-pnp-entra-app-registration` | ☐ Not sent |
| Brent Ericks | https://www.ms365support.com/microsoft-365-blog/ | `guide-infopath-forms-services-pdf-archive` | ☐ Not sent |

Draft (adjust the specific-post reference before sending — do not send without reading
their actual recent post first, generic pitches get ignored/flagged):

```
Subject: Following up on your [specific recent post title] post

Hi [Name],

Read your recent piece on [specific topic] — the [specific detail] point matched
something I ran into recently while writing up [our guide topic]:
[guide URL]

No ask here beyond a look, but if it's useful to your readers or you've hit different
edge cases, I'd genuinely like to compare notes.

[Your name]
OceanCloud
```

Status: ☐ Not sent (0/3)

---

## Tier 3 — Directories (self-serve, no outreach, but need real business verification)

| Directory | URL | Notes | Status |
|---|---|---|---|
| Clutch | https://clutch.co/ | Needs real client reviews to be worth claiming — premature until case studies are verifiably real clients | ☐ Not started |
| G2 | https://www.g2.com/ | Same caveat as Clutch | ☐ Not started |
| DesignRush (Dallas SharePoint category) | https://www.designrush.com/agency/it-services/microsoft-sharepoint/texas/dallas | Competitors already listed here — free listing plausible | ☐ Not started |

**Caution on case studies:** `case-studies.html` currently lists named clients (Meridian
Group, Hartwell NHS Trust, BrightCore Finance, etc.) with specific metrics. Before using
these in any directory submission or outreach, confirm these are real, disclosable
engagements — directories and MVP contacts will sometimes check, and unverifiable claims
damage credibility (and are a legitimate E-E-A-T risk with Google too).

---

## What actually needs your action

Everything above with a ☐ requires a human to send an email, post to a community, or
verify a business identity — none of that is something I have tools to do (no email
send, no account creation/login access). What I already did:

- Removed the incorrect LinkedIn link from `coming-soon.html`.
- Built this tracker with real guide URLs and ready-to-personalize drafts so sending is
  copy/paste + a few minutes of personalization, not a research project.

Update the Status column as you work through it so the next check-in has real signal
instead of a re-read of the strategy doc.
