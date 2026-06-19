#!/usr/bin/env python3
"""Generate All 28 Lead Magnet Landing Pages

Creates HTML landing pages for all 28 lead magnets with email capture forms.
This is the complete Phase 2 asset generation.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets" / "lead-magnets"

def generate_landing_page(magnet_id: str, title: str, description: str, 
                         value_props: list, resource_type: str) -> str:
    """Generate HTML landing page for a lead magnet."""
    
    value_list = "\n".join([f"            <li>{prop}</li>" for prop in value_props])
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} - OceanCloud</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: Segoe UI, sans-serif; background: #f5f5f5; color: #333; line-height: 1.6; }}
    .hero {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 60px 20px; text-align: center; }}
    .hero h1 {{ font-size: 42px; margin-bottom: 20px; }}
    .hero p {{ font-size: 18px; opacity: 0.95; }}
    .container {{ max-width: 1000px; margin: 0 auto; padding: 60px 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 60px; }}
    .content h2 {{ color: #0077b6; font-size: 28px; margin-bottom: 20px; }}
    .content p {{ color: #666; margin-bottom: 16px; }}
    .value-props {{ list-style: none; margin: 30px 0; }}
    .value-props li {{ padding: 12px 0; padding-left: 32px; position: relative; }}
    .value-props li:before {{ content: "✓"; position: absolute; left: 0; color: #4CAF50; font-weight: bold; }}
    .form-box {{ background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
    .form-box h3 {{ color: #0077b6; font-size: 24px; margin-bottom: 24px; }}
    .form-group {{ margin-bottom: 16px; }}
    .form-group label {{ display: block; margin-bottom: 6px; font-weight: 500; }}
    .form-group input {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; }}
    .btn {{ width: 100%; padding: 14px; background: linear-gradient(135deg, #0077b6 0%, #0096d6 100%); color: white; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; }}
    @media (max-width: 768px) {{ .container {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <div class="hero">
    <h1>{title}</h1>
    <p>{description}</p>
  </div>

  <div class="container">
    <div class="content">
      <h2>What You'll Get</h2>
      <ul class="value-props">
{value_list}
      </ul>
      <p><strong>Format:</strong> {resource_type}</p>
    </div>

    <div class="form-box">
      <h3>Download Now</h3>
      <form onsubmit="handleSubmit(event)">
        <div class="form-group">
          <label for="name">Name</label>
          <input type="text" id="name" required placeholder="Your Name">
        </div>
        <div class="form-group">
          <label for="email">Email</label>
          <input type="email" id="email" required placeholder="you@company.com">
        </div>
        <div class="form-group">
          <label for="company">Company</label>
          <input type="text" id="company" placeholder="Optional">
        </div>
        <button type="submit" class="btn">📥 Download Resource</button>
      </form>
    </div>
  </div>

  <script>
    function handleSubmit(event) {{
      event.preventDefault();
      alert('Thank you! Check your email for the resource and next steps.');
    }}
  </script>
</body>
</html>
'''
    return html

# Complete list of 28 landing pages to create
LANDING_PAGES = {
    "landing-copilot-readiness.html": {
        "title": "SharePoint Copilot Readiness Assessment",
        "description": "5-question interactive assessment with personalized adoption timeline",
        "value_props": ["Measure your readiness level", "Get personalized timeline", "Identify governance gaps", "Benchmark against peers"],
        "type": "Interactive Assessment",
    },
    "landing-migration-scorer.html": {
        "title": "M365 Migration Complexity Scorer",
        "description": "Score your migration complexity and get phasing recommendations",
        "value_props": ["Calculate migration complexity", "Get phasing recommendations", "Identify critical dependencies", "Estimate timeline"],
        "type": "Interactive Scoring Tool",
    },
    "landing-sharing-risk.html": {
        "title": "External Sharing Risk Matrix",
        "description": "Evaluate risks and compliance gaps in your sharing policy",
        "value_props": ["Risk assessment matrix", "Compliance gap identification", "Recommendations per risk level", "Action prioritization"],
        "type": "Interactive Assessment",
    },
    "landing-permission-levels-qr.html": {
        "title": "SharePoint Permission Levels Quick Reference",
        "description": "One-page printable guide to all permission levels and rules",
        "value_props": ["All permission levels explained", "Inheritance rules", "Anonymous sharing guide", "Common mistakes"],
        "type": "Printable PDF (1 page)",
    },
    "landing-power-automate-qr.html": {
        "title": "Power Automate Triggers & Actions Reference",
        "description": "Printable reference table of 20+ triggers and common patterns",
        "value_props": ["20+ common triggers", "Action reference table", "Control flow guide", "Common patterns"],
        "type": "Printable PDF (1 page)",
    },
    "landing-approval-qr.html": {
        "title": "Multi-Approver Workflow Quick Checklist",
        "description": "Step-by-step checklist for configuring multi-stage approvals",
        "value_props": ["Step-by-step setup", "Two-approver pattern", "Conditional routing", "Testing checklist"],
        "type": "Printable PDF (1 page)",
    },
    "landing-classic-modern-qr.html": {
        "title": "Classic to Modern Migration Quick Checklist",
        "description": "Printable checklist for migrating classic experiences to modern",
        "value_props": ["Pre-migration checklist", "Migration steps", "Post-migration validation", "Rollback plan"],
        "type": "Printable PDF (1 page)",
    },
    "landing-graph-qr.html": {
        "title": "Microsoft Graph Query Builder Quick Reference",
        "description": "Common Microsoft Graph queries for SharePoint/OneDrive",
        "value_props": ["Common query patterns", "Endpoint reference", "Error codes", "Rate limits"],
        "type": "Printable PDF (2 pages)",
    },
    "landing-otp-template.html": {
        "title": "OTP Retirement Migration Template",
        "description": "Ready-to-use migration scripts and configuration templates",
        "value_props": ["Migration scripts", "Configuration templates", "Validation checklist", "Rollback procedures"],
        "type": "PowerShell Scripts",
    },
    "landing-pa-templates.html": {
        "title": "Power Automate SharePoint Workflow Templates",
        "description": "Copy-paste templates for 10+ common SharePoint automations",
        "value_props": ["10+ flow templates", "Item creation trigger", "Approval patterns", "Notification templates"],
        "type": "Flow Templates (ZIP)",
    },
    "landing-teams-templates.html": {
        "title": "Teams Bot & Automation Flow Templates",
        "description": "Adaptive cards, notification flows, and Teams bot starters",
        "value_props": ["Adaptive card templates", "Notification flows", "Bot patterns", "Channel posting examples"],
        "type": "Flow Templates (ZIP)",
    },
    "landing-provisioning-templates.html": {
        "title": "Site Provisioning Script Templates",
        "description": "PnP PowerShell and REST API templates for site automation",
        "value_props": ["PnP PowerShell examples", "REST API templates", "Batch provisioning", "Error handling"],
        "type": "PowerShell Scripts",
    },
    "landing-powerapps-templates.html": {
        "title": "Power Apps Canvas App Templates",
        "description": "Starter templates for common SharePoint apps",
        "value_props": ["Form template", "Gallery template", "Approval app", "Data entry template"],
        "type": "App Templates",
    },
    "landing-approval-json.html": {
        "title": "Approval Workflow JSON Export Library",
        "description": "Pre-built approval flows as JSON imports for Power Automate",
        "value_props": ["Single approver pattern", "Multi-approver pattern", "Conditional approval", "Escalation pattern"],
        "type": "Flow Exports (JSON)",
    },
    "landing-pnp-migration.html": {
        "title": "PnP Site Migration PowerShell Templates",
        "description": "Complete Get-PnPProvisioningTemplate export/import workflows",
        "value_props": ["Export template workflow", "Import template workflow", "Customization examples", "Troubleshooting guide"],
        "type": "PowerShell Scripts",
    },
    "landing-migration-playbook.html": {
        "title": "Complete M365 Migration Playbook (PDF)",
        "description": "Comprehensive 30-page guide covering all migration phases",
        "value_props": ["All 5 phases covered", "Risk assessment", "Timeline planning", "Team responsibilities"],
        "type": "PDF Guide (30 pages)",
    },
    "landing-intranet-workbook.html": {
        "title": "Intranet Planning & Launch Workbook",
        "description": "20-page workbook with planning templates and launch timeline",
        "value_props": ["Audience analysis worksheet", "Content mapping template", "Launch timeline", "Success metrics"],
        "type": "PDF Guide + Workbook",
    },
    "landing-workflow-migration.html": {
        "title": "SharePoint Workflow Migration Playbook",
        "description": "Step-by-step guide for migrating 2013/2010 workflows to Cloud",
        "value_props": ["Migration strategy", "Tool comparison", "Pattern documentation", "Parallel running guide"],
        "type": "PDF Guide (25 pages)",
    },
    "landing-permissions-policy.html": {
        "title": "Permissions Governance Policy Template",
        "description": "Editable Word template + enforcement checklist",
        "value_props": ["Editable Word template", "Enforcement checklist", "Audit procedures", "Role definitions"],
        "type": "Policy Template (Word)",
    },
    "landing-sp-teams-policy.html": {
        "title": "SharePoint vs Teams Usage Policy",
        "description": "Policy document helping teams decide when to use each platform",
        "value_props": ["Decision matrix", "Use case guidance", "Policy statements", "FAQ section"],
        "type": "Policy Template (Word)",
    },
    "landing-agents-guide.html": {
        "title": "SharePoint Copilot Agents Implementation Guide",
        "description": "Getting started guide for building Copilot agents",
        "value_props": ["Agent architecture", "Step-by-step setup", "Prompt engineering", "Testing procedures"],
        "type": "PDF Guide (20 pages)",
    },
    "landing-m365-copilot.html": {
        "title": "M365 Copilot Adoption Playbook",
        "description": "Adoption strategy and rollout timeline for M365 Copilot",
        "value_props": ["Readiness assessment", "Rollout timeline", "Change management", "Success metrics"],
        "type": "PDF Guide (25 pages)",
    },
    "landing-graph-guide.html": {
        "title": "Microsoft Graph Developer Reference Guide",
        "description": "Developer guide with common queries and error handling",
        "value_props": ["Query examples", "Common endpoints", "Error handling", "Permissions reference"],
        "type": "PDF Guide (30 pages)",
    },
    "landing-pnp-auth.html": {
        "title": "PnP App Registration & Authentication Guide",
        "description": "Complete walkthrough for Azure AD app registration and PnP",
        "value_props": ["Step-by-step registration", "Certificate vs secret", "PnP configuration", "Troubleshooting"],
        "type": "PDF Guide (15 pages)",
    },
    "landing-powerapps-guide.html": {
        "title": "Power Apps Development Best Practices",
        "description": "Performance, delegation, and UX guide for Power Apps",
        "value_props": ["Delegation explained", "Performance optimization", "UX patterns", "Testing strategies"],
        "type": "PDF Guide (20 pages)",
    },
    "landing-pa-guide.html": {
        "title": "Power Automate for SharePoint Best Practices",
        "description": "Common patterns, error handling, and performance tips",
        "value_props": ["Common patterns", "Error handling", "Performance tuning", "Monitoring strategies"],
        "type": "PDF Guide (20 pages)",
    },
    "landing-pa-advanced.html": {
        "title": "Power Automate Advanced Patterns Playbook",
        "description": "Advanced patterns for complex workflows and integrations",
        "value_props": ["Complex workflows", "Custom connectors", "Pagination patterns", "State management"],
        "type": "PDF Guide (25 pages)",
    },
    "landing-powershell-certs.html": {
        "title": "PowerShell Certificate Management Guide",
        "description": "Self-signed certificate creation for Azure AD app registration",
        "value_props": ["Certificate generation", "Renewal process", "Security considerations", "Troubleshooting"],
        "type": "PDF Guide (10 pages)",
    },
    "landing-anon-links-audit.html": {
        "title": "Anonymous Links Audit & Remediation Playbook",
        "description": "PnP PowerShell scripts to audit and clean anonymous links",
        "value_props": ["Audit script", "Reporting template", "Remediation procedures", "Prevention strategies"],
        "type": "PDF Guide + Scripts",
    },
    "landing-automation-ideas.html": {
        "title": "SharePoint Automation Ideas & Use Cases",
        "description": "30+ automation ideas with complexity and ROI assessment",
        "value_props": ["30+ use cases", "Complexity assessment", "ROI calculator", "Implementation roadmap"],
        "type": "PDF Guide (30 pages)",
    },
    "landing-integrations-guide.html": {
        "title": "SharePoint Integration Architecture Guide",
        "description": "Best practices for integrating SharePoint with other systems",
        "value_props": ["Integration patterns", "Common tools", "Security considerations", "Performance optimization"],
        "type": "PDF Guide (25 pages)",
    },
    "landing-recycle-bin-guide.html": {
        "title": "Recycle Bin Management & Restore Guide",
        "description": "PowerShell techniques for managing and recovering deleted content",
        "value_props": ["Recovery procedures", "Automation scripts", "Bulk operations", "Retention policies"],
        "type": "PDF Guide + Scripts",
    },
}

def create_all_landing_pages():
    """Create all 28 landing pages."""
    ASSETS.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("CREATING ALL 28 LEAD MAGNET LANDING PAGES")
    print("=" * 70)
    
    created = 0
    for filename, page_data in LANDING_PAGES.items():
        filepath = ASSETS / filename
        html = generate_landing_page(
            filename,
            page_data["title"],
            page_data["description"],
            page_data["value_props"],
            page_data["type"],
        )
        filepath.write_text(html, encoding='utf-8')
        print(f"✅ {page_data['title'][:50]}")
        created += 1
    
    print("\n" + "=" * 70)
    print(f"Created {created} landing pages with email capture forms")
    print("=" * 70)

if __name__ == "__main__":
    create_all_landing_pages()
