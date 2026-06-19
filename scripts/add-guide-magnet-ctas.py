#!/usr/bin/env python3
"""Add Lead Magnet CTAs to Guides

Adds contextual "Download Resource" CTAs to each guide that link to lead magnet landing pages.
CTAs are positioned after final consultation CTA but before footer.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTICLES = ROOT / "articles"

# Complete map: all 28 guides to lead magnets
GUIDE_MAGNET_MAP = {
    "guide-get-started-sharepoint-agents.html": {
        "magnet_title": "Copilot Agents Implementation Guide",
        "magnet_link": "/lead-magnets/landing-agents-guide.html",
        "magnet_description": "Getting started guide with step-by-step setup and prompt engineering tips.",
    },
    "guide-m365-copilot.html": {
        "magnet_title": "M365 Copilot Adoption Playbook",
        "magnet_link": "/lead-magnets/landing-m365-copilot.html",
        "magnet_description": "Adoption strategy, rollout timeline, and change management playbook.",
    },
    "guide-m365-migration-checklist.html": {
        "magnet_title": "Complete M365 Migration Playbook",
        "magnet_link": "/lead-magnets/landing-migration-playbook.html",
        "magnet_description": "Comprehensive 30-page guide covering all 5 migration phases.",
    },
    "guide-microsoft-graph-sharepoint.html": {
        "magnet_title": "Microsoft Graph Developer Reference",
        "magnet_link": "/lead-magnets/landing-graph-guide.html",
        "magnet_description": "Developer guide with common queries, endpoints, and error handling.",
    },
    "guide-pnp-entra-app-registration.html": {
        "magnet_title": "PnP App Registration & Auth Guide",
        "magnet_link": "/lead-magnets/landing-pnp-auth.html",
        "magnet_description": "Complete walkthrough for Azure AD app registration and PnP setup.",
    },
    "guide-power-apps-sharepoint.html": {
        "magnet_title": "Power Apps Development Best Practices",
        "magnet_link": "/lead-magnets/landing-powerapps-guide.html",
        "magnet_description": "Performance, delegation, and UX guide for building Power Apps.",
    },
    "guide-power-automate-sharepoint.html": {
        "magnet_title": "Power Automate for SharePoint Best Practices",
        "magnet_link": "/lead-magnets/landing-pa-guide.html",
        "magnet_description": "Common patterns, error handling, and performance tuning guide.",
    },
    "guide-power-automate-triggers-actions.html": {
        "magnet_title": "Power Automate Advanced Patterns Playbook",
        "magnet_link": "/lead-magnets/landing-pa-advanced.html",
        "magnet_description": "Advanced patterns for complex workflows and integrations.",
    },
    "guide-powershell-self-signed-certificate-entra-app-registration.html": {
        "magnet_title": "PowerShell Certificate Management Guide",
        "magnet_link": "/lead-magnets/landing-powershell-certs.html",
        "magnet_description": "Self-signed certificate creation and renewal procedures.",
    },
    "guide-sharepoint-anonymous-links-report-remove-pnp-powershell.html": {
        "magnet_title": "Anonymous Links Audit & Remediation",
        "magnet_link": "/lead-magnets/landing-anon-links-audit.html",
        "magnet_description": "PnP PowerShell scripts to audit and clean anonymous links.",
    },
    "guide-sharepoint-approval-multiple-approvers.html": {
        "magnet_title": "Multi-Approver Workflow Checklist",
        "magnet_link": "/lead-magnets/landing-approval-qr.html",
        "magnet_description": "Step-by-step checklist for multi-stage approval configuration.",
    },
    "guide-sharepoint-approval-workflow.html": {
        "magnet_title": "Approval Workflow JSON Library",
        "magnet_link": "/lead-magnets/landing-approval-json.html",
        "magnet_description": "Pre-built approval flow templates as JSON imports.",
    },
    "guide-sharepoint-automation-ideas.html": {
        "magnet_title": "SharePoint Automation Ideas & Use Cases",
        "magnet_link": "/lead-magnets/landing-automation-ideas.html",
        "magnet_description": "30+ automation ideas with complexity and ROI assessment.",
    },
    "guide-sharepoint-classic-calendar-to-modern-view.html": {
        "magnet_title": "Classic to Modern Migration Checklist",
        "magnet_link": "/lead-magnets/landing-classic-modern-qr.html",
        "magnet_description": "Printable checklist for classic to modern migrations.",
    },
    "guide-sharepoint-copilot-agents.html": {
        "magnet_title": "Copilot Agents Implementation Guide",
        "magnet_link": "/lead-magnets/landing-agents-guide.html",
        "magnet_description": "Step-by-step guide for building and deploying Copilot agents.",
    },
    "guide-sharepoint-copilot-ready.html": {
        "magnet_title": "Copilot Readiness Assessment",
        "magnet_link": "/lead-magnets/landing-copilot-readiness.html",
        "magnet_description": "5-question interactive assessment with adoption timeline.",
    },
    "guide-sharepoint-external-sharing-complete-admin-guide.html": {
        "magnet_title": "External Sharing Risk Matrix",
        "magnet_link": "/lead-magnets/landing-sharing-risk.html",
        "magnet_description": "Risk assessment and compliance gap analysis tool.",
    },
    "guide-sharepoint-integrations.html": {
        "magnet_title": "SharePoint Integration Architecture Guide",
        "magnet_link": "/lead-magnets/landing-integrations-guide.html",
        "magnet_description": "Best practices for integrating SharePoint with other systems.",
    },
    "guide-sharepoint-intranet.html": {
        "magnet_title": "Intranet Planning & Launch Workbook",
        "magnet_link": "/lead-magnets/landing-intranet-workbook.html",
        "magnet_description": "20-page workbook with planning templates and launch timeline.",
    },
    "guide-sharepoint-otp-retirement-entra-b2b.html": {
        "magnet_title": "OTP Retirement Migration Template",
        "magnet_link": "/lead-magnets/landing-otp-template.html",
        "magnet_description": "Ready-to-use migration scripts and templates.",
    },
    "guide-sharepoint-permissions-best-practices.html": {
        "magnet_title": "Permissions Governance Policy Template",
        "magnet_link": "/lead-magnets/landing-permissions-policy.html",
        "magnet_description": "Editable Word policy template with enforcement checklist.",
    },
    "guide-sharepoint-permissions.html": {
        "magnet_title": "Permission Levels Quick Reference",
        "magnet_link": "/lead-magnets/landing-permission-levels-qr.html",
        "magnet_description": "Printable one-page guide to all permission levels.",
    },
    "guide-sharepoint-pnp-site-migration.html": {
        "magnet_title": "PnP Site Migration Templates",
        "magnet_link": "/lead-magnets/landing-pnp-migration.html",
        "magnet_description": "Complete export/import workflow with customization examples.",
    },
    "guide-sharepoint-recycle-bin-restore-pnp-powershell.html": {
        "magnet_title": "Recycle Bin Management & Restore Guide",
        "magnet_link": "/lead-magnets/landing-recycle-bin-guide.html",
        "magnet_description": "PowerShell techniques for recovery and automation.",
    },
    "guide-sharepoint-site-provisioning-automation.html": {
        "magnet_title": "Site Provisioning Script Templates",
        "magnet_link": "/lead-magnets/landing-provisioning-templates.html",
        "magnet_description": "PnP PowerShell and REST API templates for automation.",
    },
    "guide-sharepoint-vs-teams.html": {
        "magnet_title": "SharePoint vs Teams Usage Policy",
        "magnet_link": "/lead-magnets/landing-sp-teams-policy.html",
        "magnet_description": "Policy document with decision matrix and guidance.",
    },
    "guide-sharepoint-workflow-migration.html": {
        "magnet_title": "Workflow Migration Playbook",
        "magnet_link": "/lead-magnets/landing-workflow-migration.html",
        "magnet_description": "Step-by-step guide for 2013/2010 to Cloud migration.",
    },
    "guide-teams-automation.html": {
        "magnet_title": "Teams Bot & Automation Templates",
        "magnet_link": "/lead-magnets/landing-teams-templates.html",
        "magnet_description": "Adaptive cards, notification flows, and bot starters.",
    },
}

# Default CTA for guides without specific magnet (generic offer)
DEFAULT_MAGNET_CTA = {
    "magnet_title": "OceanCloud Resource Guide",
    "magnet_link": "/contact",
    "magnet_description": "Explore resources and book a consultation to discuss your specific scenario.",
}

def create_magnet_cta_section(magnet_title: str, magnet_link: str, magnet_description: str) -> str:
    """Create HTML section for lead magnet CTA."""
    return f'''      <section class="guide-lead-magnet">
        <div class="container">
          <div class="lm-content">
            <div class="lm-icon">📥</div>
            <div class="lm-text">
              <h3>Get This Free Resource</h3>
              <p>{magnet_description}</p>
            </div>
          </div>
          <a href="{magnet_link}" class="btn-secondary">Download {magnet_title.split()[0]} →</a>
        </div>
      </section>
'''

def add_magnet_cta_to_guide(guide_path: Path) -> tuple[bool, str]:
    """Add lead magnet CTA to a guide."""
    content = guide_path.read_text(encoding='utf-8')
    guide_name = guide_path.name
    
    # Check if already has lead-magnet section
    if 'class="guide-lead-magnet"' in content:
        return False, "Already has lead magnet CTA"
    
    # Get magnet mapping for this guide
    if guide_name not in GUIDE_MAGNET_MAP:
        return False, "No magnet mapped for this guide"
    
    magnet_data = GUIDE_MAGNET_MAP[guide_name]
    
    # Find insertion point: before closing </footer> tag (most reliable)
    footer_close = content.rfind('</footer>')
    if footer_close < 0:
        return False, "Could not find closing footer tag"
    
    insert_pos = footer_close
    
    # Create CTA section
    cta_section = '\n' + create_magnet_cta_section(
        magnet_data["magnet_title"],
        magnet_data["magnet_link"],
        magnet_data["magnet_description"]
    ) + '\n'
    
    # Insert CTA
    new_content = content[:insert_pos] + cta_section + content[insert_pos:]
    
    guide_path.write_text(new_content, encoding='utf-8')
    return True, f"Added CTA for {magnet_data['magnet_title']}"

def main():
    guides = sorted(ARTICLES.glob("guide-*.html"))
    
    print("=" * 70)
    print("ADDING LEAD MAGNET CTAs TO GUIDES")
    print("=" * 70)
    
    added = 0
    skipped = 0
    
    for guide in guides:
        success, msg = add_magnet_cta_to_guide(guide)
        status = "✅" if success else "⏭️"
        print(f"{status} {guide.name:60} {msg}")
        if success:
            added += 1
        else:
            skipped += 1
    
    print("\n" + "=" * 70)
    print(f"Result: {added} guides updated, {skipped} skipped")
    print("=" * 70)

if __name__ == "__main__":
    main()
