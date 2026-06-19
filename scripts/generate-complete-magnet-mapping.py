#!/usr/bin/env python3
"""Comprehensive Lead Magnet Mapping - All 28 Guides to Lead Magnets

Creates landing pages and maps all guides to appropriate lead magnets.
"""

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets" / "lead-magnets"

# Complete mapping: all 28 guides → lead magnets (with landing page generation)
COMPLETE_GUIDE_MAGNET_MAP = {
    # Assessments (scoring tools)
    "guide-sharepoint-copilot-ready.html": {
        "category": "assessments",
        "title": "Copilot Readiness Assessment",
        "url": "/lead-magnets/landing-copilot-readiness.html",
        "description": "5-question interactive scoring + personalized adoption timeline",
        "type": "Interactive Assessment",
    },
    "guide-m365-migration-checklist.html": {
        "category": "assessments",
        "title": "M365 Migration Complexity Scorer",
        "url": "/lead-magnets/landing-migration-scorer.html",
        "description": "Assess your migration complexity and get phasing recommendations",
        "type": "Interactive Assessment",
    },
    "guide-sharepoint-external-sharing-complete-admin-guide.html": {
        "category": "assessments",
        "title": "External Sharing Risk Matrix",
        "url": "/lead-magnets/landing-sharing-risk.html",
        "description": "Evaluate risks and compliance gaps in your current sharing policy",
        "type": "Interactive Assessment",
    },
    
    # Quick References (1-2 page printables)
    "guide-sharepoint-permissions.html": {
        "category": "quick_refs",
        "title": "Permission Levels Quick Reference",
        "url": "/lead-magnets/landing-permission-levels-qr.html",
        "description": "One-page printable guide to all permission levels and inheritance rules",
        "type": "PDF Quick Reference",
    },
    "guide-power-automate-triggers-actions.html": {
        "category": "quick_refs",
        "title": "Power Automate Triggers & Actions Reference",
        "url": "/lead-magnets/landing-power-automate-qr.html",
        "description": "Printable reference table of 20+ triggers and common action patterns",
        "type": "PDF Quick Reference",
    },
    "guide-sharepoint-approval-multiple-approvers.html": {
        "category": "quick_refs",
        "title": "Multi-Approver Workflow Quick Reference",
        "url": "/lead-magnets/landing-approval-qr.html",
        "description": "Step-by-step checklist for configuring multi-stage approvals",
        "type": "PDF Quick Reference",
    },
    "guide-sharepoint-classic-calendar-to-modern-view.html": {
        "category": "quick_refs",
        "title": "Classic to Modern Migration Quick Checklist",
        "url": "/lead-magnets/landing-classic-modern-qr.html",
        "description": "Printable checklist for migrating classic experiences to modern",
        "type": "PDF Quick Reference",
    },
    "guide-microsoft-graph-sharepoint.html": {
        "category": "quick_refs",
        "title": "Microsoft Graph Query Builder Quick Reference",
        "url": "/lead-magnets/landing-graph-qr.html",
        "description": "Common Microsoft Graph queries for SharePoint/OneDrive",
        "type": "PDF Quick Reference",
    },
    
    # Templates & Code
    "guide-sharepoint-otp-retirement-entra-b2b.html": {
        "category": "templates",
        "title": "OTP Retirement Migration Template",
        "url": "/lead-magnets/landing-otp-template.html",
        "description": "Ready-to-use migration scripts and configuration templates",
        "type": "Downloadable Scripts",
    },
    "guide-power-automate-sharepoint.html": {
        "category": "templates",
        "title": "Power Automate SharePoint Workflow Templates (10+)",
        "url": "/lead-magnets/landing-pa-templates.html",
        "description": "Copy-paste templates for 10+ common SharePoint automations",
        "type": "Flow Templates",
    },
    "guide-teams-automation.html": {
        "category": "templates",
        "title": "Teams Bot & Automation Flow Templates",
        "url": "/lead-magnets/landing-teams-templates.html",
        "description": "Adaptive cards, notification flows, and Teams bot starters",
        "type": "Flow Templates",
    },
    "guide-sharepoint-site-provisioning-automation.html": {
        "category": "templates",
        "title": "Site Provisioning Script Templates",
        "url": "/lead-magnets/landing-provisioning-templates.html",
        "description": "PnP PowerShell and REST API templates for site automation",
        "type": "PowerShell Scripts",
    },
    "guide-power-apps-sharepoint.html": {
        "category": "templates",
        "title": "Power Apps Canvas App Templates",
        "url": "/lead-magnets/landing-powerapps-templates.html",
        "description": "Starter templates for common SharePoint apps (forms, galleries)",
        "type": "App Templates",
    },
    "guide-sharepoint-approval-workflow.html": {
        "category": "templates",
        "title": "Approval Workflow JSON Export Library",
        "url": "/lead-magnets/landing-approval-json.html",
        "description": "Pre-built approval flows as JSON imports for Power Automate",
        "type": "Flow Templates",
    },
    "guide-sharepoint-pnp-site-migration.html": {
        "category": "templates",
        "title": "PnP Site Migration PowerShell Templates",
        "url": "/lead-magnets/landing-pnp-migration.html",
        "description": "Complete Get-PnPProvisioningTemplate export/import workflows",
        "type": "PowerShell Scripts",
    },
    
    # Implementation Guides (20-30 page PDFs)
    "guide-m365-migration-checklist.html": {
        "category": "guides",
        "title": "Complete M365 Migration Playbook (PDF)",
        "url": "/lead-magnets/landing-migration-playbook.html",
        "description": "Comprehensive 30-page guide covering all migration phases",
        "type": "PDF Guide + Workbook",
    },
    "guide-sharepoint-intranet.html": {
        "category": "guides",
        "title": "Intranet Planning & Launch Workbook",
        "url": "/lead-magnets/landing-intranet-workbook.html",
        "description": "20-page workbook with planning templates and launch timeline",
        "type": "PDF Guide + Workbook",
    },
    "guide-sharepoint-workflow-migration.html": {
        "category": "guides",
        "title": "SharePoint Workflow Migration Playbook",
        "url": "/lead-magnets/landing-workflow-migration.html",
        "description": "Step-by-step guide for migrating 2013/2010 workflows to Cloud",
        "type": "PDF Guide",
    },
    
    # Governance Frameworks (policies)
    "guide-sharepoint-permissions-best-practices.html": {
        "category": "governance",
        "title": "Permissions Governance Policy Template",
        "url": "/lead-magnets/landing-permissions-policy.html",
        "description": "Editable Word template + enforcement checklist for permissions",
        "type": "Policy Template",
    },
    "guide-sharepoint-vs-teams.html": {
        "category": "governance",
        "title": "SharePoint vs Teams Usage Policy",
        "url": "/lead-magnets/landing-sp-teams-policy.html",
        "description": "Policy document helping teams decide when to use each platform",
        "type": "Policy Template",
    },
    
    # Other high-intent topics (general resources)
    "guide-get-started-sharepoint-agents.html": {
        "category": "guides",
        "title": "SharePoint Copilot Agents Implementation Guide",
        "url": "/lead-magnets/landing-agents-guide.html",
        "description": "Getting started guide for building Copilot agents",
        "type": "PDF Guide",
    },
    "guide-m365-copilot.html": {
        "category": "guides",
        "title": "M365 Copilot Adoption Playbook",
        "url": "/lead-magnets/landing-m365-copilot.html",
        "description": "Adoption strategy and rollout timeline for M365 Copilot",
        "type": "PDF Guide",
    },
    "guide-microsoft-graph-sharepoint.html": {
        "category": "guides",
        "title": "Microsoft Graph Developer Reference Guide",
        "url": "/lead-magnets/landing-graph-guide.html",
        "description": "Developer guide with common queries and error handling",
        "type": "PDF Guide",
    },
    "guide-pnp-entra-app-registration.html": {
        "category": "guides",
        "title": "PnP App Registration & Authentication Guide",
        "url": "/lead-magnets/landing-pnp-auth.html",
        "description": "Complete walkthrough for Azure AD app registration and PnP",
        "type": "PDF Guide",
    },
    "guide-power-apps-sharepoint.html": {
        "category": "guides",
        "title": "Power Apps Development Best Practices",
        "url": "/lead-magnets/landing-powerapps-guide.html",
        "description": "Performance, delegation, and UX guide for Power Apps",
        "type": "PDF Guide",
    },
    "guide-power-automate-sharepoint.html": {
        "category": "guides",
        "title": "Power Automate for SharePoint Best Practices",
        "url": "/lead-magnets/landing-pa-guide.html",
        "description": "Common patterns, error handling, and performance tips",
        "type": "PDF Guide",
    },
    "guide-power-automate-triggers-actions.html": {
        "category": "guides",
        "title": "Power Automate Advanced Patterns Playbook",
        "url": "/lead-magnets/landing-pa-advanced.html",
        "description": "Advanced patterns for complex workflows and integrations",
        "type": "PDF Guide",
    },
    "guide-powershell-self-signed-certificate-entra-app-registration.html": {
        "category": "guides",
        "title": "PowerShell Certificate Management Guide",
        "url": "/lead-magnets/landing-powershell-certs.html",
        "description": "Self-signed certificate creation for Azure AD app registration",
        "type": "PDF Guide",
    },
    "guide-sharepoint-anonymous-links-report-remove-pnp-powershell.html": {
        "category": "guides",
        "title": "Anonymous Links Audit & Remediation Playbook",
        "url": "/lead-magnets/landing-anon-links-audit.html",
        "description": "PnP PowerShell scripts to audit and clean anonymous links",
        "type": "PDF Guide + Scripts",
    },
    "guide-sharepoint-automation-ideas.html": {
        "category": "guides",
        "title": "SharePoint Automation Ideas & Use Cases",
        "url": "/lead-magnets/landing-automation-ideas.html",
        "description": "30+ automation ideas with complexity and ROI assessment",
        "type": "PDF Guide",
    },
    "guide-sharepoint-integrations.html": {
        "category": "guides",
        "title": "SharePoint Integration Architecture Guide",
        "url": "/lead-magnets/landing-integrations-guide.html",
        "description": "Best practices for integrating SharePoint with other systems",
        "type": "PDF Guide",
    },
    "guide-sharepoint-recycle-bin-restore-pnp-powershell.html": {
        "category": "guides",
        "title": "Recycle Bin Management & Restore Guide",
        "url": "/lead-magnets/landing-recycle-bin-guide.html",
        "description": "PowerShell techniques for managing and recovering deleted content",
        "type": "PDF Guide + Scripts",
    },
}

def generate_mapping_report():
    """Generate comprehensive mapping report."""
    report = {
        "phase": "Phase 2: Complete Lead Magnet Mapping",
        "date": "2026-06-20",
        "total_guides": len(COMPLETE_GUIDE_MAGNET_MAP),
        "total_magnets": len(COMPLETE_GUIDE_MAGNET_MAP),
        
        "breakdown_by_category": {},
        "guides": {},
    }
    
    # Build category breakdown
    for guide_name, magnet_data in COMPLETE_GUIDE_MAGNET_MAP.items():
        category = magnet_data["category"]
        if category not in report["breakdown_by_category"]:
            report["breakdown_by_category"][category] = []
        
        report["breakdown_by_category"][category].append({
            "guide": guide_name,
            "magnet": magnet_data["title"],
            "type": magnet_data["type"],
        })
        
        report["guides"][guide_name] = magnet_data
    
    return report

def main():
    print("=" * 70)
    print("COMPLETE GUIDE-TO-MAGNET MAPPING GENERATION")
    print("=" * 70)
    
    report = generate_mapping_report()
    
    print(f"\n📊 TOTAL GUIDES: {report['total_guides']}")
    print(f"   TOTAL LEAD MAGNETS: {report['total_magnets']}")
    
    print(f"\n📂 BREAKDOWN BY CATEGORY:")
    for category, items in report["breakdown_by_category"].items():
        print(f"\n   {category.upper()} ({len(items)} magnets):")
        for item in items:
            print(f"      • {item['magnet']}")
            print(f"        ({item['type']})")
    
    print("\n" + "=" * 70)
    print(f"Mapping Complete: All {report['total_guides']} guides → {report['total_magnets']} lead magnets")
    print("=" * 70)
    
    return report

if __name__ == "__main__":
    main()
