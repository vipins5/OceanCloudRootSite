---
Document: CRM & Email Automation Integration Guide
Date: 2026-06-23
Platforms: HubSpot, Marketo, ActiveCampaign, Klaviyo
Purpose: Connect lead-magnet landing pages to email nurture sequences
---

# Lead Capture Automation Setup Guide

## Overview
This guide walks through connecting landing pages to CRM platforms for automated email sequences. Once configured, leads filling out landing pages automatically receive nurture sequences.

---

## Platform-Specific Setup

### HubSpot (Most Popular for B2B SaaS)

**Step 1: Create HubSpot Form**
1. Go to HubSpot > Marketing > Lead Capture > Forms
2. Create new form with fields:
   - First Name (required)
   - Email (required)
   - Company (required)
   - Role (required)
   - Company Size (dropdown)
   - [For Cowork] Teams Deploying (number input)
   - [For Scout] Adoption Phase (dropdown)

3. Configure form actions:
   - Submit button text: "Download My [Resource]"
   - Post-submit action: "Redirect to thank you page"
   - Thank you page URL: (prepare static HTML file)

4. Copy HubSpot form embed code

**Step 2: Embed Form on Landing Page**
```html
<!-- Add this inside <head> section of landing page -->
<script charset="utf-8" src="//js.hsforms.net/forms/embed/v2.js"></script>

<!-- Add this where form should appear -->
<div id="hubspot-form"></div>
<script>
  hbspt.forms.create({
    region: "na1",
    portalId: "YOUR_PORTAL_ID",
    formId: "YOUR_FORM_ID",
    target: "#hubspot-form"
  });
</script>
```

**Step 3: Create Nurture Workflow**
1. HubSpot > Marketing > Workflows > Create workflow
2. Trigger: "Form submitted" (select landing page form)
3. Actions:
   - Add to contact list (e.g., "Cowork-Interested")
   - Send email: Email 1 of sequence (template below)
   - Wait 3 days
   - Send email: Email 2
   - Wait 3 days
   - Send email: Email 3
   - [continue for 5-email sequence]

4. Create email templates for each sequence step:
   - Subject line
   - Sender name (your team)
   - Email body (from email-sequences-cowork-nurture.md / email-sequences-scout-nurture.md)
   - CTA link
   - Unsubscribe footer

**Step 4: Set Up Tracking**
- Enable email open tracking
- Enable link click tracking
- Create segments: "Opened Email 1", "Clicked Email 2 CTA", etc.
- Create trigger: "If clicked consultation CTA" → Assign to sales team

**Step 5: Connect to Slack / Salesforce**
- Notify sales in Slack when lead books consultation
- Auto-create Salesforce lead/contact with HubSpot sync

---

### ActiveCampaign (Affordable, Powerful)

**Step 1: Create Signup Form**
1. ActiveCampaign > Forms > Create Form
2. Form type: "Embedded" (embeds on your page)
3. Add fields:
   - First Name, Email, Company, Role, Company Size, etc.

4. Click "Generate code" to get embed script

**Step 2: Add Form to Landing Page**
```html
<!-- Paste this in <body> where form should appear -->
<form action="https://oceancloud.activehosted.com/f/1" method="post" id="_form_1">
  <!-- Form will auto-populate from ActiveCampaign -->
</form>
<script src="https://oceancloud.activehosted.com/f/embed.js"></script>
```

**Step 3: Create Automation**
1. ActiveCampaign > Automations > Create Automation
2. Trigger: "Contact submits this form"
3. Add steps:
   - Add tag: "cowork-lead" (for segmentation)
   - Send email series:
     - Immediate: "Welcome" email
     - +3 days: Email 2
     - +6 days: Email 3
     - +10 days: Email 4
     - +14 days: Email 5

4. Create branch: "If clicked consultation link" → Tag "consultation-interested"

**Step 4: Add Email Templates**
1. Create 5 email templates (one per sequence email)
2. Link templates into automation
3. Enable tracking: Opens, clicks, bounces

---

### Marketo (Enterprise)

**Step 1: Create Marketo Form**
1. Marketo > Design Studio > Forms > New Form
2. Form name: "Cowork Implementation Checklist"
3. Add fields:
   - First Name, Email, Company, Role, Company Size, Teams Deploying

4. Configure submission behaviors:
   - Show follow-up page ✓
   - Visit thank you page

**Step 2: Add Form to Landing Page**
```html
<!-- Add Marketo Munchkin code to site first (site setup) -->
<script src="//munchkin.marketo.net/munchkin.js"></script>
<script>
  Munchkin.init('YOUR_ACCOUNT_ID');
</script>

<!-- Add this where form should go -->
<form id="mktoForm_1"></form>
<script src="//app-abc.marketo.com/js/forms2/js/forms2.min.js"></script>
<script>
  MktoForms2.loadForm("//app-abc.marketo.com", "YOUR_ORG_ID", "1", function(form) {
    form.render("#mktoForm_1");
  });
</script>
```

**Step 3: Create Lead Flow Campaign**
1. Marketo > Marketing > Email > Create Email
   - Email 1: Thank you + resource download
   - Email 2-5: Nurture sequence

2. Create Smart Campaign:
   - Trigger: "Form filled out" (select your form)
   - Flow: Add to list + Send email sequence

3. Configure email sends:
   - Email 1: Immediate
   - Email 2: 3 days later
   - Email 3: 6 days later
   - Email 4: 10 days later
   - Email 5: 14 days later

4. Set up scoring:
   - Open email: +1 point
   - Click link: +5 points
   - Visit pricing page: +10 points
   - Request consultation: +50 points

---

### Klaviyo (E-commerce / Transactional)

**Step 1: Create Email Form**
1. Klaviyo > Website > Create Form
2. Form type: "Embedded" or "Pop-up"
3. Fields: First Name, Email, Company, Role

**Step 2: Add Form to Landing Page**
```html
<script src="https://a.klaviyo.com/media/js/onsite/onsite.js"></script>
<div id="klaviyo-form-TaBcDeFg"></div>
```

**Step 3: Create Email Flow**
1. Klaviyo > Flows > Create Flow
2. Trigger: "Subscribed to list 'Cowork-Leads'"
3. Flow steps:
   - Email 1 (immediate): Welcome
   - Delay 3 days
   - Email 2: Quick wins
   - Delay 3 days
   - Email 3: Case study
   - Delay 3 days
   - Email 4: Advanced techniques
   - Delay 3 days
   - Email 5: Consultation CTA

4. Add conditional split:
   - If clicked consultation link → Send SMS/SMS notification
   - If unopened after 24 hours → Send reminder

---

## Universal Setup Steps (All Platforms)

### Landing Page HTML Structure
```html
<!DOCTYPE html>
<html>
<head>
  <title>Download [Resource] | OceanCloud</title>
  <meta name="description" content="Get [Resource]...">
  <!-- CRM platform script goes here -->
</head>
<body>
  <header>
    <h1>Get [Resource Name]</h1>
    <p>Step-by-step implementation guide for...</p>
  </header>

  <main>
    <section class="form-container">
      <!-- FORM EMBED GOES HERE -->
      <!-- Platform-specific form code inserted here -->
    </section>

    <section class="benefits">
      <h2>What You'll Get</h2>
      <ul>
        <li>Checklist item 1</li>
        <li>Checklist item 2</li>
        <li>Checklist item 3</li>
      </ul>
    </section>
  </main>

  <!-- Analytics tracking -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXX"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-XXXXXXX');
    
    // Track form submission
    gtag('event', 'lead_form_submit', {
      'resource': 'Cowork Checklist'
    });
  </script>
</body>
</html>
```

### Thank You Page Setup
1. Create simple "Thank You" page
2. Include:
   - Confirmation message
   - Download link (if offering downloadable PDF)
   - Next steps (e.g., "You'll receive Email 1 in 5 minutes")
   - Link to email nurture expectation ("5 emails over 14 days")
   - CTA: "Book a consultation call"

### Email Template Structure (All Sequences)
```
From: [Consultant Name] <name@oceancloudconsults.com>
Subject: [Email Subject from sequences]
Reply-To: [Consultant Email]

[Email 1 Body from email-sequences-cowork-nurture.md]

---

[CTA Button]

[Signature]
[Unsubscribe link - required by law]
```

---

## Integration Checklist

### Pre-Launch
- [ ] Landing page created and hosted
- [ ] CRM account set up with billing verified
- [ ] Form embedded on landing page
- [ ] Form submission tested (fill out test form)
- [ ] Email sequence created (all 5 emails)
- [ ] Email templates reviewed for spelling/links
- [ ] CTA links point to correct URLs
- [ ] Thank you page configured
- [ ] Analytics tracking installed
- [ ] CRM connected to Slack/sales notification system

### Launch Day
- [ ] Landing page live and publicly accessible
- [ ] Link added to guide content (CTA section)
- [ ] Link added to guides.html navigation
- [ ] Social media announcement scheduled
- [ ] Email notification sent to team
- [ ] Monitor first 24 hours for form submissions

### Post-Launch Monitoring
- [ ] Check daily: Form submissions received?
- [ ] Check daily: Emails being sent?
- [ ] Week 1: Review email open rates (target: 25-30%)
- [ ] Week 1: Review email click rates (target: 8-10%)
- [ ] Week 2: First consultation bookings coming in?
- [ ] Week 2: Refine subject lines if needed based on open rates

---

## Segmentation & Conditional Logic

### Sample Segments for Reporting
1. **"Cowork-Downloaded"** - Downloaded checklist
2. **"Cowork-Engaged"** - Opened 3+ emails
3. **"Cowork-High-Intent"** - Clicked consultation CTA
4. **"Cowork-Contacted"** - Booked consultation call

### Conditional Flows
**If lead shows high intent:**
- Move from nurture sequence to sales sequence
- Add to "Hot Lead" list in CRM
- Notify sales team immediately
- Trigger personalized follow-up email

**If lead goes quiet:**
- After Email 5, wait 7 days
- If no engagement, add to re-engagement campaign
- Send "Last chance" email on day 30
- If still no response, move to long-term nurture (low frequency)

---

## Analytics & ROI Tracking

### Metrics to Monitor
| Metric | Target | Actual |
|--------|--------|--------|
| Landing page views | - | TBD |
| Form submissions | 5% of page views | TBD |
| Email open rate | 25-30% | TBD |
| Email click rate | 8-10% | TBD |
| Consultation bookings | 3-5% of emails | TBD |
| Consultation to engagement rate | 15-20% | TBD |

### ROI Calculation
```
Total consulting revenue from lead magnet leads
÷ Cost of setup + CRM subscription + effort
= ROI %

Example:
$50K revenue / $5K cost = 1000% ROI
```

---

## Troubleshooting

### Forms Not Submitting
- Check form code is properly embedded
- Check CRM API is enabled
- Check for browser console errors
- Test in incognito mode (privacy blocker issue?)

### Emails Not Sending
- Check email templates are published
- Check sender email verified in CRM
- Check automation is "active" (not paused)
- Check leads not already on suppression list

### Low Form Submission Rate
- Test form UX on mobile (mobile-responsive?)
- Reduce number of form fields (3-4 required fields ideal)
- Make CTA more prominent
- A/B test different headlines

### Low Email Open Rate
- Test different subject lines
- Vary send time
- Check from name (personal > company)
- Monitor for spam folder delivery

---

## Security & Compliance

- [ ] Forms are HTTPS (encrypted)
- [ ] Privacy statement links to privacy policy
- [ ] Unsubscribe link in every email
- [ ] GDPR: "Double opt-in" enabled (confirm email address)
- [ ] CAN-SPAM: Company address in email footer
- [ ] Lead data backed up weekly
- [ ] CRM access limited to authorized users
- [ ] Password manager for CRM credentials
