#!/usr/bin/env python3
"""Add procedural steps to guides missing them - Phase 1 completion."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTICLES = ROOT / "articles"

# Define steps for each guide
GUIDE_STEPS = {
    "guide-pnp-entra-app-registration.html": [
        ("Register an Azure AD application", "Go to portal.azure.com > Azure Active Directory > App registrations. Click 'New registration', give it a name (e.g., 'PnP-Script-Admin'), select 'Accounts in this organizational directory only', and click Register. Note the Application ID (client ID) — you'll need this for authentication."),
        ("Configure API permissions", "In your app registration, go to 'API permissions' > 'Add a permission'. Select 'Microsoft Graph' > 'Application permissions'. Search for and add: 'Sites.FullControl.All', 'Files.ReadWrite.All', 'User.Read.All'. Click 'Grant admin consent' so users don't see consent prompts."),
        ("Create a client secret", "Go to 'Certificates & secrets' > 'Client secrets' > 'New client secret'. Set expiry (90 days or 12 months) and click Add. Copy the Value immediately — you won't see it again. Store it securely (never commit to git)."),
        ("Create an Azure Key Vault (optional but recommended)", "In Azure Portal, create an Azure Key Vault to store secrets. Add your client secret as a key vault secret. Update your PnP scripts to retrieve secrets from Key Vault instead of hardcoding them."),
        ("Test authentication in your PnP PowerShell script", "Use Connect-PnPOnline -Url [site-url] -ClientId [app-id] -ClientSecret [secret]. Verify connection succeeds. Once working, wrap it in try-catch to handle token expiry and re-authentication gracefully."),
    ],
    "guide-power-apps-sharepoint.html": [
        ("Start with your SharePoint list", "Go to your SharePoint site and create or identify the list you want to use as your app's data source. Make sure column names are clear and column types are set correctly (text, choice, person, date, lookup, etc.). Poor column setup here leads to bad app performance later."),
        ("Open Power Apps and create a new canvas app", "Go to powerapps.microsoft.com > Create > Canvas app from blank. Give it a name and choose phone or tablet layout based on your primary users. Power Apps launches in edit mode."),
        ("Connect to your SharePoint list", "Click 'Data' (left sidebar) > 'Add data' > search for SharePoint > select your site > select your list. Power Apps now has read/write access to your list columns."),
        ("Build your form using controls", "Drag text input, choice dropdown, date picker, and other controls onto your screen. For each control, set its 'Default' property to point to list columns (e.g., TextInput1.Default = ThisItem.Title). Build the form layout that suits your task."),
        ("Add buttons for Save, New, and Delete", "Insert buttons with OnSelect formulas: Save = Patch(ListName, ThisItem, {updated fields}); New = NewForm(FormName); Delete = Remove(ListName, ThisItem). Test each action thoroughly before sharing."),
        ("Share your app with users", "Publish the app. Go to Share > enter user names or groups. Each user needs a Power Apps licence (included in Microsoft 365). Test the app as an end user before full rollout."),
    ],
    "guide-power-automate-sharepoint.html": [
        ("Create a new cloud flow", "Go to powerautomate.microsoft.com > Create > Automated cloud flow > select a trigger (SharePoint trigger like 'When an item is created' or 'When an item is modified'). Name your flow."),
        ("Configure your SharePoint trigger", "Select your SharePoint site and list. Set any filtering conditions (e.g., 'Only trigger for items where Status = Pending'). Configure trigger frequency if needed. Click Create."),
        ("Add actions to process the item", "Add actions like 'Get file properties', 'Update item', 'Send email', 'Create event in calendar', or 'Post to Teams'. Each action pulls data from the trigger using dynamic content tokens like @{triggerOutputs()['body/ID']}."),
        ("Configure conditional logic (if needed)", "Add 'Condition' actions to branch logic: if Status = Approved, send approval email; if Status = Rejected, move item to archive. Use comparison operators (is equal to, contains, greater than)."),
        ("Add error handling", "Add 'Configure run after' to the final action to catch failures. Set it to run if the previous action 'has failed' or 'has timed out'. Log errors to a Teams channel or email for visibility."),
        ("Test and monitor", "Save and test the flow by manually creating a SharePoint item. Monitor the flow run history in Power Automate to confirm all steps executed. Adjust actions and conditions based on real results."),
    ],
    "guide-power-automate-triggers-actions.html": [
        ("Navigate to Power Automate and create a new flow", "Go to powerautomate.microsoft.com > Create > select flow type (Cloud flow or Desktop flow). For this guide, we focus on Cloud flows with SharePoint triggers."),
        ("Choose and configure your trigger", "Select a trigger from 'SharePoint' or 'Microsoft 365' category (e.g., 'When an item is created', 'When an approval is completed', 'When a new email arrives'). Set any required parameters like site and list."),
        ("Add your first action", "In the flow designer, click '+ New step'. Search for and select an action (e.g., 'Send email', 'Create reminder', 'Post message'). Map trigger outputs to action inputs using dynamic content buttons."),
        ("Add parallel actions (optional)", "Click '+ Add a parallel branch' to run multiple actions simultaneously. Useful for sending emails AND creating calendar events when a trigger fires."),
        ("Set up conditions to control flow", "Add 'Condition' blocks to check if values meet criteria. For example: if email subject contains 'URGENT', escalate to manager; otherwise, route to standard process. Use all available operators and functions."),
        ("Configure error handling and notifications", "Add 'On failure' handlers to catch errors. Log to SharePoint list or send alert to admin Teams channel. Test the flow with various inputs to ensure robustness."),
    ],
    "guide-sharepoint-approval-multiple-approvers.html": [
        ("Set up your SharePoint list with approval columns", "Create a list with: Title, Requestor (person), Amount (number), Approval Status (choice: Pending/Approved/Rejected), Primary Approver (person), Secondary Approver (person). Test the column setup before building the flow."),
        ("Create a Power Automate flow triggered by new items", "Go to powerautomate.microsoft.com > Automate > Cloud flow > Automated. Trigger: 'When an item is created' in your list. Name: 'Multi-Approver Workflow'."),
        ("Send to primary approver for initial review", "Add action 'Send an approval request'. Set 'Assigned to' to the Primary Approver person field, include the request details, and wait for response. Capture approval response."),
        ("Route to secondary approver if amount exceeds threshold", "Add Condition: if Amount > [threshold], send approval request to Secondary Approver; otherwise, skip. Both approvers must approve before marking complete."),
        ("Update list status based on approvals", "Add 'Update item' action to set Approval Status = 'Approved' if both approved, or 'Rejected' if either declines. Include rejection reason if provided."),
        ("Notify requestor of outcome", "Add 'Send an email' action to the requestor with outcome. Include approval chain summary, final status, and next steps (e.g., 'Your request has been approved and will be processed')."),
    ],
    "guide-sharepoint-external-sharing-complete-admin-guide.html": [
        ("Review your current external sharing settings", "Go to SharePoint admin center > Sharing settings. Review current policy: unrestricted, specific domains only, or existing external users. Document baseline for compliance/audit."),
        ("Enable anonymous links for specific scenarios", "If business need exists, enable 'Anyone' links for low-risk content only. Set expiry (7-30 days typical). Always require password if business data is involved. Monitor usage via audit logs."),
        ("Configure permitted domains for guests", "If restricting to specific partners, go to Sharing > Limit external sharing by domain > add trusted partner domains to allowlist. External users outside allowlist cannot access."),
        ("Set up a guest review process", "For highly regulated content: use Power Automate to notify admins when guests are added. Create a checklist for security review: confirm identity, verify business need, set access expiry dates."),
        ("Apply sensitivity labels to external-shared content", "Go to Sensitivity labels in SharePoint > assign 'Confidential' label to content shared externally. Labels restrict downstream sharing, enforce watermarks, and trigger notifications."),
        ("Monitor external sharing activity", "Set up audit logging for external user access. Review monthly: which guests accessed what content, duration, and whether access should be revoked. Remove guests who no longer need access."),
    ],
    "guide-sharepoint-intranet.html": [
        ("Define your intranet audience and content zones", "Identify primary users (all employees, department-specific, managers). Plan content zones: News & Updates, HR/Benefits, IT Help, Project Hub, Culture. Map each zone to a SharePoint site or hub."),
        ("Create hub sites for main sections", "Set up hub sites in SharePoint admin center for major departments/functions. Link regular team sites to hub sites so content flows up and users see navigation across related sites."),
        ("Design a homepage for discoverability", "Build a modern SharePoint homepage with featured news, important announcements, quick-link cards, and search-friendly content. Keep above-the-fold content to high-priority business items."),
        ("Implement a news aggregation strategy", "Enable News web parts on hub sites to surface announcements from connected team sites. Set up content moderation: draft → review → publish. Assign editorial team ownership."),
        ("Set up search and navigation", "Configure the global search box to search across all intranet sites. Create navigation breadcrumbs linking related content. Test search results are relevant and performant."),
        ("Roll out in phases with user training", "Launch to a pilot group (managers/champions), gather feedback, refine content structure. Provide training on how to post news, request content promotion, and find resources. Monitor adoption metrics."),
    ],
    "guide-sharepoint-pnp-site-migration.html": [
        ("Export source site with PnP PowerShell", "Use PnP command: Get-PnPProvisioningTemplate -Out 'template.xml' to export site structure, lists, and content. Add flags like -IncludeContentTypes, -IncludeTermGroups as needed. Export takes time for large sites."),
        ("Review and customize the template", "Open template.xml in editor. Remove unwanted list items (often data bloat). Customize column mappings, security groups, branding. Remove hardcoded GUIDs if template will be reused across tenants."),
        ("Prepare target environment", "Create target site collection in destination tenant. Pre-create required Azure AD groups. Assign permissions to ensure PnP has rights to apply template (admin or site owner)."),
        ("Apply template to target site with PnP", "Run: Apply-PnPProvisioningTemplate -Path 'template.xml' against target site. Verify all lists, content types, columns created successfully. Check permissions applied correctly."),
        ("Migrate content and permissions", "Use PnP Copy-PnPFile or Invoke-PnPSiteTransfer to move files and list items. Map source users to target tenant identities. Verify nobody has lost access post-migration."),
        ("Validate and test", "Smoke test: access lists, download files, run workflows, check formulas. Compare source vs target side-by-side for missing content. Get sign-off from business owner."),
    ],
    "guide-sharepoint-workflow-migration.html": [
        ("Audit existing SharePoint 2013 workflows", "List all active workflows in your farms. Document: trigger conditions, actions, approval paths, external connections. Identify which workflows are still business-critical vs deprecated."),
        ("Categorize workflows by complexity", "Simple (linear, 1-2 steps): migrate first. Medium (branching, 5-10 steps): requires testing. Complex (nested loops, external API calls, state machines): evaluate retiring or rewriting."),
        ("Rebuild simple workflows in Power Automate", "Create new cloud flows matching old logic. Use 'When an item is created/modified' trigger + conditions + actions. Test thoroughly: edge cases, error paths, notifications."),
        ("Handle external connections and approvals", "For workflows connecting to external APIs: use HTTP connector or custom connectors in Power Automate. For approvals: use Approval actions with person fields and multi-stage routing."),
        ("Run workflows in parallel during transition", "For 2-4 weeks, run both old (2013 workflows) and new (Power Automate) versions for same trigger. Compare results. Once confident new works, disable old."),
        ("Decommission old workflows and clean up", "Once migration complete and tested, disable SharePoint 2013 workflows. Document new flow ownership and maintenance contact. Archive old workflow definitions for audit."),
    ],
    "guide-teams-automation.html": [
        ("Identify automation opportunities in Teams", "Audit: channel message workflows, meeting scheduling, bot integrations, file management. Prioritise high-frequency, repetitive tasks (notifications, approvals, data entry)."),
        ("Create a Teams bot or use connectors", "Option 1: Use Power Virtual Agent for chatbot flows. Option 2: Use connectors (Slack-like automation). Build flow triggered by Teams message or mention. Route messages to appropriate handlers."),
        ("Set up adaptive cards for interactive experiences", "Design adaptive card templates in Power Automate: approval cards, form cards, data display cards. Send cards to Teams channels when events trigger (e.g., 'New help desk ticket approved')."),
        ("Implement notification routing", "Create flows that route notifications to Teams channels based on priority/category: 'Urgent' → @channel mention; 'Info' → no mention. Aggregate notifications to reduce noise."),
        ("Build Teams-to-backend connectors", "Connect Teams messages/approvals to backend systems: approve in Teams → update SharePoint list → trigger invoice process. Use HTTP connectors or Dataverse for data sync."),
        ("Test bot and connector with pilot users", "Launch bot/automation to test team. Gather feedback on card design, messaging clarity, workflow logic. Iterate before org-wide rollout to prevent user frustration."),
    ],
}

def create_steps_html(steps: list) -> str:
    """Create HTML for procedural steps."""
    html = '      <ol class="art-steps">\n'
    for i, (title, body) in enumerate(steps, 1):
        html += f'''        <li>
          <div class="art-step-num">{i}</div>
          <div class="art-step-body">
            <strong>{title}</strong>
            <p>{body}</p>
          </div>
        </li>
'''
    html += '      </ol>\n'
    return html

def add_steps_to_guide(guide_name: str) -> tuple[bool, str]:
    """Add steps to a guide."""
    if guide_name not in GUIDE_STEPS:
        return False, "Not in steps dict"
    
    guide_path = ARTICLES / guide_name
    if not guide_path.exists():
        return False, "Guide not found"
    
    content = guide_path.read_text(encoding='utf-8')
    
    # Check if already has ordered list
    if '<ol class="art-steps">' in content:
        return False, "Already has steps"
    
    # Find insertion point: after first h2
    h2_match = re.search(r'</h2>', content)
    if not h2_match:
        return False, "No h2 found"
    
    insertion_point = h2_match.end()
    
    # Get steps and create HTML
    steps = GUIDE_STEPS[guide_name]
    steps_html = create_steps_html(steps)
    
    # Insert with proper spacing
    new_content = content[:insertion_point] + '\n\n' + steps_html + '\n' + content[insertion_point:]
    
    guide_path.write_text(new_content, encoding='utf-8')
    return True, f"Added {len(steps)} steps"

def main():
    print("=" * 70)
    print("ADDING PROCEDURAL STEPS TO 10 GUIDES - PHASE 1 COMPLETION")
    print("=" * 70)
    
    added = 0
    skipped = 0
    
    for guide_name in sorted(GUIDE_STEPS.keys()):
        success, msg = add_steps_to_guide(guide_name)
        status = "✅" if success else "⏭️"
        print(f"{status} {guide_name:60} {msg}")
        if success:
            added += 1
        else:
            skipped += 1
    
    print("\n" + "=" * 70)
    print(f"Result: {added} guides updated, {skipped} skipped")
    print("=" * 70)

if __name__ == "__main__":
    main()
