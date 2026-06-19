#!/usr/bin/env python3
"""Create Quick Reference Checklists (PDF-ready HTML)

These are 1-2 page checklists that users can download and print.
Each is designed to be reference-friendly and print-optimized.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets" / "lead-magnets"

QUICK_REFERENCES = {
    "sharepoint-permission-levels": {
        "title": "SharePoint Permission Levels Quick Reference",
        "filename": "qr-sharepoint-permission-levels.html",
        "html": '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SharePoint Permission Levels Quick Reference</title>
  <style>
    body { font-family: Segoe UI, sans-serif; max-width: 8.5in; margin: 0; padding: 0.5in; color: #333; line-height: 1.4; }
    h1 { color: #0077b6; font-size: 18pt; margin: 0 0 8pt 0; }
    h2 { color: #0077b6; font-size: 12pt; margin: 12pt 0 6pt 0; border-bottom: 2px solid #0077b6; padding-bottom: 4pt; }
    table { width: 100%; border-collapse: collapse; margin: 8pt 0; font-size: 9pt; }
    th, td { padding: 6pt; text-align: left; border: 1px solid #ddd; }
    th { background: #e0f2f1; font-weight: bold; }
    .level-group { margin: 12pt 0; }
    .tip { background: #fff3cd; padding: 8pt; border-left: 4pt solid #ff9800; margin: 10pt 0; font-size: 9pt; }
    .footer { margin-top: 12pt; font-size: 8pt; color: #666; border-top: 1px solid #ddd; padding-top: 6pt; }
    @media print { body { padding: 0.25in; } }
  </style>
</head>
<body>
  <h1>📋 SharePoint Permission Levels Quick Reference</h1>
  <p><strong>OceanCloud Consulting</strong> | SharePoint Permission Guide | 2026</p>

  <h2>Permission Levels at a Glance</h2>
  <table>
    <thead><tr><th>Permission Level</th><th>Typical Role</th><th>Can Do</th><th>Cannot Do</th></tr></thead>
    <tbody>
      <tr><td><strong>Owner</strong></td><td>Site Admin</td><td>Everything (full control)</td><td>Nothing - full control</td></tr>
      <tr><td><strong>Member</strong></td><td>Content Editor</td><td>Add, edit, delete items/docs</td><td>Manage permissions, site structure</td></tr>
      <tr><td><strong>Contributor</strong></td><td>Regular User</td><td>Add, edit own items</td><td>Delete items, manage library</td></tr>
      <tr><td><strong>Reader</strong></td><td>Viewer</td><td>View items/docs only</td><td>Edit, add, delete anything</td></tr>
      <tr><td><strong>Limited Access</strong></td><td>Minimal Guest</td><td>Access assigned item only</td><td>View other items or structure</td></tr>
    </tbody>
  </table>

  <h2>SharePoint Groups (Pre-built)</h2>
  <div class="level-group">
    <strong>Site Owners</strong> = Full Control<br>
    <strong>Site Members</strong> = Edit (Contribute)<br>
    <strong>Site Visitors</strong> = Read (View Only)
  </div>

  <h2>Permission Inheritance Rules</h2>
  <table>
    <tr><td><strong>Default Behavior:</strong></td><td>All items inherit permissions from parent library/list</td></tr>
    <tr><td><strong>Break Inheritance:</strong></td><td>Item/folder gets unique permissions (not linked to parent)</td></tr>
    <tr><td><strong>Restore Inheritance:</strong></td><td>Item returns to parent's permissions (old unique perms deleted)</td></tr>
  </table>

  <h2>Anonymous & External Sharing</h2>
  <table>
    <tr><td><strong>Anonymous Link (Anyone)</strong></td><td>No sign-in needed; anyone with link can access</td></tr>
    <tr><td><strong>People Link (Specific People)</strong></td><td>Requires Microsoft account or org account</td></tr>
    <tr><td><strong>Guest Link (External)</strong></td><td>External users sign in with Microsoft account or identity provider</td></tr>
  </table>

  <div class="tip">
    <strong>💡 Tip:</strong> Review permissions quarterly. Many organizations have excessive sharing due to cascading inheritance. Use "Manage Direct Permissions" in SharePoint admin to audit and clean up.
  </div>

  <div class="tip">
    <strong>⚠️ Common Mistake:</strong> Breaking inheritance on individual items (vs library-wide). Instead, use library settings or create sub-folders with different permissions to reduce complexity.
  </div>

  <div class="footer">
    This quick reference is part of "SharePoint Permissions Guide for IT Admins" | oceancloudconsults.com/guides<br>
    Need help implementing these? <a href="https://oceancloudconsults.com/contact">Book a consultation</a>
  </div>
</body>
</html>
''',
    },
    "power-automate-triggers-actions": {
        "title": "Power Automate Triggers & Actions Reference",
        "filename": "qr-power-automate-triggers-actions.html",
        "html": '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Power Automate Triggers & Actions Reference</title>
  <style>
    body { font-family: Segoe UI, sans-serif; max-width: 8.5in; margin: 0; padding: 0.5in; color: #333; line-height: 1.4; }
    h1 { color: #0077b6; font-size: 18pt; margin: 0 0 8pt 0; }
    h2 { color: #0077b6; font-size: 11pt; margin: 10pt 0 6pt 0; border-bottom: 2px solid #0077b6; }
    .col-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12pt; }
    .trigger, .action { background: #f5f5f5; padding: 8pt; margin: 6pt 0; border-left: 4pt solid #0077b6; }
    .trigger strong { color: #0077b6; }
    .action strong { color: #d32f2f; }
    table { width: 100%; border-collapse: collapse; margin: 8pt 0; font-size: 9pt; }
    td { padding: 4pt; border: 1px solid #ddd; }
    .tip { background: #fff3cd; padding: 6pt; border-left: 4pt solid #ff9800; margin: 8pt 0; font-size: 9pt; }
    @media print { body { padding: 0.25in; } }
  </style>
</head>
<body>
  <h1>⚡ Power Automate Triggers & Actions Reference</h1>
  <p><strong>OceanCloud Consulting</strong> | Power Platform Guide | 2026</p>

  <h2>Common Triggers (What Starts the Flow)</h2>
  <div class="col-2">
    <div>
      <div class="trigger"><strong>When an item is created</strong> - SharePoint list item added</div>
      <div class="trigger"><strong>When an item is modified</strong> - Item updated</div>
      <div class="trigger"><strong>When a file is created</strong> - File uploaded to drive</div>
      <div class="trigger"><strong>When an approval is completed</strong> - Approver responds</div>
    </div>
    <div>
      <div class="trigger"><strong>When a new email arrives</strong> - Email received</div>
      <div class="trigger"><strong>On new Teams message</strong> - Message posted to channel</div>
      <div class="trigger"><strong>Schedule</strong> - Time-based (daily, weekly)</div>
      <div class="trigger"><strong>Button</strong> - Manual trigger</div>
    </div>
  </div>

  <h2>Common Actions (What the Flow Does)</h2>
  <table>
    <tr><td><strong>Send an email</strong></td><td>To, Subject, Body, Attachments</td></tr>
    <tr><td><strong>Send approval request</strong></td><td>Assigned to, Title, Details, Options</td></tr>
    <tr><td><strong>Create item/Update item</strong></td><td>Set list column values</td></tr>
    <tr><td><strong>Post message to Teams</strong></td><td>Channel, Message, Adaptive Card</td></tr>
    <tr><td><strong>Create event in calendar</strong></td><td>Date, Time, Attendees, Description</td></tr>
    <tr><td><strong>Call HTTP webhook</strong></td><td>External API integration</td></tr>
  </table>

  <h2>Control Flow Actions</h2>
  <table>
    <tr><td><strong>Condition</strong></td><td>If/Then branching logic</td></tr>
    <tr><td><strong>Switch</strong></td><td>Multi-branch routing</td></tr>
    <tr><td><strong>For each</strong></td><td>Loop over array items</td></tr>
    <tr><td><strong>Delay</strong></td><td>Pause before next action</td></tr>
    <tr><td><strong>Terminate</strong></td><td>Stop flow execution</td></tr>
  </table>

  <div class="tip">
    <strong>💡 Tips:</strong> Use Condition blocks to route logic. Always add "Configure run after" to handle failures. Test with real data before deploying to production.
  </div>

  <div class="tip">
    <strong>📌 Reference:</strong> Learn.microsoft.com/en-us/connectors/connector-reference/
  </div>

  <p style="font-size: 8pt; color: #666; margin-top: 12pt; border-top: 1px solid #ddd; padding-top: 6pt;">
    Part of "Power Automate & SharePoint Guide" | oceancloudconsults.com/guides | Need help? <a href="https://oceancloudconsults.com/contact">Book a consultation</a>
  </p>
</body>
</html>
''',
    },
    "migration-checklist": {
        "title": "M365 Migration Quick Checklist",
        "filename": "qr-m365-migration.html",
        "html": '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>M365 Migration Quick Checklist</title>
  <style>
    body { font-family: Segoe UI, sans-serif; max-width: 8.5in; margin: 0; padding: 0.5in; color: #333; }
    h1 { color: #0077b6; font-size: 16pt; margin: 0 0 8pt 0; }
    h2 { color: #0077b6; font-size: 11pt; margin: 10pt 0 6pt 0; border-bottom: 2px solid #0077b6; }
    .checkbox { display: flex; align-items: center; margin: 4pt 0; }
    .checkbox input { margin-right: 8pt; width: 16pt; height: 16pt; }
    .phase { background: #e3f2fd; padding: 8pt; margin: 8pt 0; border-left: 4pt solid #0077b6; }
    .phase-title { font-weight: bold; color: #0077b6; font-size: 10pt; }
    @media print { body { padding: 0.25in; } .checkbox input { accent-color: #0077b6; } }
  </style>
</head>
<body>
  <h1>✅ M365 Migration Quick Checklist</h1>
  <p><strong>OceanCloud Consulting</strong> | Complete Phase-by-Phase Plan | 2026</p>

  <div class="phase">
    <div class="phase-title">📋 PHASE 1: PLAN & ASSESS (Weeks 1-2)</div>
    <div class="checkbox"><input type="checkbox"> Inventory current environment (data, users, licenses)</div>
    <div class="checkbox"><input type="checkbox"> Identify business requirements and success metrics</div>
    <div class="checkbox"><input type="checkbox"> Audit SharePoint content for cleanup opportunities</div>
    <div class="checkbox"><input type="checkbox"> Identify dependencies and custom solutions</div>
    <div class="checkbox"><input type="checkbox"> Plan tenant structure and site architecture</div>
  </div>

  <div class="phase">
    <div class="phase-title">🏗️ PHASE 2: BUILD (Weeks 3-6)</div>
    <div class="checkbox"><input type="checkbox"> Set up Microsoft 365 tenant structure</div>
    <div class="checkbox"><input type="checkbox"> Configure Azure AD sync and authentication</div>
    <div class="checkbox"><input type="checkbox"> Create user accounts and licenses</div>
    <div class="checkbox"><input type="checkbox"> Configure SharePoint hub sites and team sites</div>
    <div class="checkbox"><input type="checkbox"> Set up Teams and OneDrive for Business</div>
  </div>

  <div class="phase">
    <div class="phase-title">🧪 PHASE 3: PILOT (Weeks 7-8)</div>
    <div class="checkbox"><input type="checkbox"> Select pilot user group (50-100 users)</div>
    <div class="checkbox"><input type="checkbox"> Migrate pilot data</div>
    <div class="checkbox"><input type="checkbox"> Run parallel old/new systems (1-2 weeks)</div>
    <div class="checkbox"><input type="checkbox"> Gather feedback and make adjustments</div>
    <div class="checkbox"><input type="checkbox"> Sign-off from pilot group before full cutover</div>
  </div>

  <div class="phase">
    <div class="phase-title">🚀 PHASE 4: CUTOVER (Weeks 9-10)</div>
    <div class="checkbox"><input type="checkbox"> Final data migration and sync</div>
    <div class="checkbox"><input type="checkbox"> Disable old system access</div>
    <div class="checkbox"><input type="checkbox"> Enable production Microsoft 365 access</div>
    <div class="checkbox"><input type="checkbox"> Monitor for issues</div>
    <div class="checkbox"><input type="checkbox"> User support and training</div>
  </div>

  <div class="phase">
    <div class="phase-title">✔️ PHASE 5: VALIDATE & CLOSE (Weeks 11+)</div>
    <div class="checkbox"><input type="checkbox"> Verify all data migrated correctly</div>
    <div class="checkbox"><input type="checkbox"> Archive old systems (retention policy)</div>
    <div class="checkbox"><input type="checkbox"> Decommission legacy infrastructure</div>
    <div class="checkbox"><input type="checkbox"> Complete post-migration optimization</div>
  </div>

  <p style="font-size: 8pt; color: #666; margin-top: 10pt; border-top: 1px solid #ddd; padding-top: 6pt;">
    Get the complete playbook: oceancloudconsults.com/guides/m365-migration | Need guidance? <a href="https://oceancloudconsults.com/contact">Book a consultation</a>
  </p>
</body>
</html>
''',
    },
}

def create_quick_references():
    """Create all quick reference HTML files."""
    ASSETS.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("CREATING QUICK REFERENCE CHECKLISTS")
    print("=" * 70)
    
    created = 0
    for ref_id, ref_data in QUICK_REFERENCES.items():
        filepath = ASSETS / ref_data["filename"]
        filepath.write_text(ref_data["html"], encoding='utf-8')
        print(f"✅ {ref_data['title']}")
        print(f"   Saved to: {filepath}")
        created += 1
    
    print("\n" + "=" * 70)
    print(f"Created {created} quick reference files (print-to-PDF ready)")
    print("=" * 70)

if __name__ == "__main__":
    create_quick_references()
