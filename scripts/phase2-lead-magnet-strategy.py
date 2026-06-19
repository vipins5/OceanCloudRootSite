#!/usr/bin/env python3
"""Phase 2: Lead Magnet Strategy & Mapping

Maps 28 guides to lead magnet types and creates a conversion funnel.
Lead magnets are downloadable resources that capture email + convert guide readers to leads.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
REPORTS_DIR = DATA_DIR / "reports"

# Lead magnet strategy: Map guides to lead magnets
LEAD_MAGNET_STRATEGY = {
    "assessment_tools": {
        "category": "Interactive Assessments",
        "description": "Self-assessment tools that score readiness and identify gaps",
        "guides": [
            ("guide-sharepoint-copilot-ready.html", "Copilot Readiness Assessment"),
            ("guide-m365-migration-checklist.html", "Migration Complexity Scorer"),
            ("guide-sharepoint-external-sharing-complete-admin-guide.html", "External Sharing Risk Matrix"),
            ("guide-sharepoint-permissions.html", "Permissions Audit Checklist"),
            ("guide-sharepoint-intranet.html", "Intranet Maturity Assessment"),
        ],
        "format": "Interactive PDF + Excel Spreadsheet",
        "value": "Identify gaps, prioritize next steps, compare to peer benchmarks",
        "cta": "Get Your Assessment & Benchmark Score",
    },
    "templates": {
        "category": "Ready-to-Use Templates",
        "description": "Copy-paste templates for immediate implementation",
        "guides": [
            ("guide-sharepoint-otp-retirement-entra-b2b.html", "OTP Retirement Migration Template"),
            ("guide-power-automate-sharepoint.html", "Power Automate Workflow Templates (10+)"),
            ("guide-teams-automation.html", "Teams Bot Flow Templates"),
            ("guide-sharepoint-site-provisioning-automation.html", "Site Provisioning Script Templates"),
            ("guide-power-apps-sharepoint.html", "Power Apps Canvas App Templates"),
            ("guide-sharepoint-approval-workflow.html", "Approval Workflow JSON Export"),
        ],
        "format": "ZIP file with .json, .json, PowerShell scripts",
        "value": "Copy templates into your environment, customize, deploy",
        "cta": "Download Templates (Ready to Deploy)",
    },
    "governance_frameworks": {
        "category": "Policy & Governance Frameworks",
        "description": "Pre-built policy documents and governance playbooks",
        "guides": [
            ("guide-sharepoint-permissions-best-practices.html", "Permissions Governance Policy"),
            ("guide-sharepoint-external-sharing-complete-admin-guide.html", "External Sharing Policy"),
            ("guide-sharepoint-workflow-migration.html", "Workflow Governance Playbook"),
            ("guide-sharepoint-vs-teams.html", "SharePoint vs Teams Usage Policy"),
        ],
        "format": "Word templates + PDF guide (12-15 pages)",
        "value": "Editable policies you can present to stakeholders immediately",
        "cta": "Get Governance Framework",
    },
    "implementation_guides": {
        "category": "Step-by-Step Implementation Guides",
        "description": "PDF guides that expand on web articles with screenshots",
        "guides": [
            ("guide-m365-migration-checklist.html", "Complete M365 Migration Playbook (PDF)"),
            ("guide-sharepoint-pnp-site-migration.html", "PnP Site Migration Workbook"),
            ("guide-power-automate-triggers-actions.html", "Power Automate Decision Matrix"),
            ("guide-sharepoint-intranet.html", "Intranet Planning Workbook"),
            ("guide-teams-automation.html", "Teams Automation Cookbook"),
        ],
        "format": "PDF (20-30 pages) + downloadable workbook",
        "value": "Printable guides + interactive worksheets for your team",
        "cta": "Download PDF + Workbook",
    },
    "quick_reference": {
        "category": "Quick Reference Checklists",
        "description": "1-2 page checklists for at-a-glance reference",
        "guides": [
            ("guide-sharepoint-permissions.html", "SharePoint Permission Levels Quick Ref"),
            ("guide-sharepoint-approval-multiple-approvers.html", "Multi-Approver Workflow Checklist"),
            ("guide-sharepoint-classic-calendar-to-modern-view.html", "Migration Checklist (Classic→Modern)"),
            ("guide-power-automate-triggers-actions.html", "Common Triggers & Actions Reference"),
            ("guide-microsoft-graph-sharepoint.html", "Microsoft Graph Query Builder Quick Ref"),
        ],
        "format": "PDF (1-2 pages), laminate-friendly",
        "value": "Print and post in office, keep on desk for daily reference",
        "cta": "Download Quick Reference",
    },
}

# Lead magnet conversion funnel
CONVERSION_FUNNEL = {
    "step_1_awareness": {
        "phase": "On-Guide CTA",
        "tactic": "All 28 guides have consultation CTA",
        "goal": "Collect email for lead magnet offer",
    },
    "step_2_consideration": {
        "phase": "Lead Magnet Download",
        "tactic": "User downloads lead magnet, provides email",
        "goal": "Move from anonymous reader to known contact",
    },
    "step_3_nurture": {
        "phase": "Email Sequence (5 emails over 2 weeks)",
        "tactic": "Automated nurture based on lead magnet type",
        "goal": "Establish OceanCloud expertise, introduce services",
    },
    "step_4_decision": {
        "phase": "Consultation Offer",
        "tactic": "Email #5 offers free 60-min consultation",
        "goal": "Convert nurtured lead to consultation booking",
    },
}

# Email nurture sequences (per lead magnet type)
EMAIL_SEQUENCES = {
    "assessment_tools": [
        {
            "day": 0,
            "subject": "Your Assessment Is Ready + What Your Score Means",
            "content": "Thank you for downloading [Assessment Name]. Your assessment score compared to peer orgs is [SCORE]. Here's what it means...",
        },
        {
            "day": 2,
            "subject": "3 Quick Wins You Can Implement This Week (Based on Your Assessment)",
            "content": "Based on your assessment results, here are 3 improvements you can make immediately without budget approval...",
        },
        {
            "day": 4,
            "subject": "Why Organizations Like Yours Choose OceanCloud for [Topic]",
            "content": "In our 5-year track record, we've helped [X] organizations improve their [metric] by [Y]%. Here's how we do it...",
        },
        {
            "day": 7,
            "subject": "Common Mistakes in [Topic] (And How to Avoid Them)",
            "content": "We've seen the same mistakes repeatedly in orgs your size. Here's what typically goes wrong and how OceanCloud helps...",
        },
        {
            "day": 10,
            "subject": "Let's Talk: Free 60-Min Consultation (No Sales Pitch)",
            "content": "Based on your assessment, we see an opportunity to help. Let's schedule a quick call to discuss your specific situation. [BOOK NOW]",
        },
    ],
    "templates": [
        {
            "day": 0,
            "subject": "Your Templates Are Ready - Plus 3 Implementation Tips",
            "content": "You now have [X] templates ready to deploy. Here's the fastest path to implementation...",
        },
        {
            "day": 2,
            "subject": "Template Pro Tip: How to Customize [Template] for Your Environment",
            "content": "The most common customization question is... here's the exact process...",
        },
        {
            "day": 4,
            "subject": "Why These Templates Work (And The Mistakes We See in Custom Builds)",
            "content": "Before you build from scratch, understand why template-based approaches outperform custom in [X]% of cases...",
        },
        {
            "day": 7,
            "subject": "[Case Study] How [Company] Used These Templates to Save [Cost/Time]",
            "content": "Real example from a org similar to yours: they deployed templates and achieved [result]...",
        },
        {
            "day": 10,
            "subject": "Stuck on Implementation? Let's Get You Unstuck (Free 60-Min Call)",
            "content": "We can walk you through customization, troubleshooting, or advanced scenarios. [BOOK NOW]",
        },
    ],
    "governance_frameworks": [
        {
            "day": 0,
            "subject": "Your Governance Framework Is Ready - Use This for Your Next Leadership Presentation",
            "content": "You have a complete policy template ready for stakeholder review. Here's how to present it...",
        },
        {
            "day": 2,
            "subject": "Governance Best Practice: How Other Organizations Use This Framework",
            "content": "Here's how similar-sized organizations have adapted this framework for their culture...",
        },
        {
            "day": 4,
            "subject": "Why Governance Fails (And How to Avoid It)",
            "content": "We've seen governance initiatives fail. Here are the top 3 failure modes and how to prevent them...",
        },
        {
            "day": 7,
            "subject": "Stakeholder Buy-In Strategy: Getting Adoption of Your New Governance",
            "content": "You have the policy. Now you need adoption. Here's the exact playbook OceanCloud uses...",
        },
        {
            "day": 10,
            "subject": "Help Implement Your Governance (Free 60-Min Kickoff Call)",
            "content": "We specialize in governance implementation and change management. Let's discuss your specific challenges. [BOOK NOW]",
        },
    ],
}

def generate_strategy_report():
    """Generate lead magnet strategy report."""
    report = {
        "phase": "Phase 2: Lead Magnet Strategy",
        "date": "2026-06-20",
        "objective": "Convert 28 guides into lead magnets for email capture and consultation booking",
        
        "lead_magnet_categories": {},
        "total_lead_magnets": 0,
        "conversion_funnel": CONVERSION_FUNNEL,
        "email_sequences": EMAIL_SEQUENCES,
        
        "implementation_timeline": {
            "week_1": "Design and create assessment tools (5 lead magnets)",
            "week_2": "Build templates package and governance frameworks (10 lead magnets)",
            "week_3": "Create implementation guides and quick reference (9 lead magnets)",
            "week_4": "Set up landing pages, email automation, analytics",
        },
        
        "projected_metrics": {
            "guide_traffic_monthly": 500,  # assumes 500 guide page views/month
            "lead_magnet_download_rate": 0.20,  # 20% of guide readers
            "email_capture_monthly": 100,
            "consultation_booking_rate": 0.15,  # 15% of nurtured leads
            "monthly_consultations": 15,
        },
    }
    
    # Build category summary
    for category, details in LEAD_MAGNET_STRATEGY.items():
        report["lead_magnet_categories"][category] = {
            "category_name": details["category"],
            "description": details["description"],
            "format": details["format"],
            "count": len(details["guides"]),
            "guides": details["guides"],
            "cta": details["cta"],
        }
        report["total_lead_magnets"] += len(details["guides"])
    
    return report

def main():
    print("=" * 70)
    print("PHASE 2: LEAD MAGNET STRATEGY GENERATION")
    print("=" * 70)
    
    report = generate_strategy_report()
    
    # Create reports directory
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save report
    report_path = REPORTS_DIR / "phase2-lead-magnet-strategy.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Strategy Report: {report_path}")
    print(f"\n📊 LEAD MAGNET SUMMARY:")
    print(f"   Total magnets planned: {report['total_lead_magnets']}")
    
    for category, details in report["lead_magnet_categories"].items():
        print(f"\n   {details['category_name']}: {details['count']} magnets")
        print(f"   Format: {details['format']}")
        for guide, magnet in details["guides"]:
            print(f"     • {magnet}")
    
    print(f"\n💧 CONVERSION FUNNEL:")
    for step, details in CONVERSION_FUNNEL.items():
        print(f"   {details['phase']}: {details['goal']}")
    
    print(f"\n📧 EMAIL SEQUENCES:")
    for seq_type, emails in EMAIL_SEQUENCES.items():
        print(f"   {seq_type}: {len(emails)} emails over {emails[-1]['day']} days")
    
    print(f"\n📈 PROJECTED MONTHLY METRICS:")
    for metric, value in report["projected_metrics"].items():
        print(f"   {metric}: {value}")
    
    print("\n" + "=" * 70)
    print("Phase 2 Strategy Complete - Ready for Implementation")
    print("=" * 70)

if __name__ == "__main__":
    main()
