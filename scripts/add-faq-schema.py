#!/usr/bin/env python3
"""
Add FAQPage JSON-LD schema + HTML accordion to guide articles that are missing it.
Run from repo root: python scripts/add-faq-schema.py
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
ARTICLES = ROOT / "articles"

# ---------------------------------------------------------------------------
# FAQ definitions per article slug
# ---------------------------------------------------------------------------
FAQS = {
    "guide-sharepoint-copilot-agents": {
        "questions": [
            {
                "q": "What is a SharePoint Copilot agent?",
                "a": "A SharePoint Copilot agent is an AI assistant scoped to your SharePoint content. It uses Microsoft 365 Copilot or Copilot Studio to answer questions, summarise documents, and automate tasks based on files, lists, and pages in your SharePoint environment — without exposing content outside your tenant.",
            },
            {
                "q": "Do I need a Microsoft 365 Copilot licence to use SharePoint agents?",
                "a": "For out-of-the-box declarative agents inside Microsoft 365 Copilot, yes — each user needs an M365 Copilot licence. For custom agents built in Copilot Studio and published to a Teams channel or SharePoint site, you can use Copilot Studio capacity-based licensing (Copilot Credits) instead.",
            },
            {
                "q": "What is the difference between a declarative agent and a Copilot Studio agent?",
                "a": "A declarative agent is a no-code configuration that focuses an M365 Copilot user on specific SharePoint sites, files, or lists. A Copilot Studio agent is a fully built chatbot with conversation flows, custom connectors, and multi-channel publishing. Use declarative agents for quick, content-scoped Q&A and Copilot Studio agents when you need business logic, integrations, or multi-step workflows.",
            },
            {
                "q": "What are Copilot Credits and how are they consumed?",
                "a": "Copilot Credits are the billing unit for Copilot Studio. Each agent message that invokes a generative AI action or connector call consumes credits. Simple conversational turns without generative AI do not consume credits. Credits are purchased as capacity packs and shared across all agents in your tenant.",
            },
            {
                "q": "Can SharePoint Copilot agents access content from other Microsoft 365 apps?",
                "a": "Yes. A SharePoint-grounded agent can reference Teams chats, Outlook emails, OneDrive files, and other Microsoft Graph data if the underlying Copilot licence includes those connectors and the user has permission to access that content. Access is always governed by Microsoft 365 permissions — the agent never bypasses security.",
            },
        ]
    },
    "guide-m365-copilot": {
        "questions": [
            {
                "q": "What is Microsoft 365 Copilot?",
                "a": "Microsoft 365 Copilot is an AI assistant embedded across Word, Excel, PowerPoint, Outlook, Teams, and other M365 apps. It uses large language models grounded in your Microsoft Graph data — emails, documents, meetings, and chats — to draft content, summarise information, and automate tasks inside the apps you already use.",
            },
            {
                "q": "How much does a Microsoft 365 Copilot licence cost?",
                "a": "Microsoft 365 Copilot is an add-on licence priced at $30 per user per month (as of 2026). It requires an eligible base plan such as Microsoft 365 Business Standard, Business Premium, E3, or E5.",
            },
            {
                "q": "What SharePoint governance is needed before deploying Copilot?",
                "a": "Copilot surfaces content that users can access, so overly permissive SharePoint sites will expose sensitive data through Copilot responses. Before rollout you should audit site permissions, remove excessive Everyone/Everyone Except External Users sharing, label sensitive files with Microsoft Purview sensitivity labels, and clean up stale content.",
            },
            {
                "q": "How do I measure Microsoft 365 Copilot adoption?",
                "a": "Use the Microsoft Viva Insights Copilot Dashboard in the Microsoft 365 admin center. It shows active users per app, Copilot-assisted actions (summaries, drafts, chat), and week-over-week trends. You can also track adoption through the Microsoft 365 usage reports under Reports > Usage.",
            },
            {
                "q": "What are the most common Microsoft 365 Copilot rollout mistakes?",
                "a": "The most common mistakes are: deploying before fixing SharePoint permissions (Copilot will surface over-shared content), skipping end-user training (adoption stays low), expecting Copilot to work on unlicensed users, and not setting a success metric before launch. A phased rollout starting with a pilot group of 25–50 users is the recommended approach.",
            },
        ]
    },
    "guide-sharepoint-automation-ideas": {
        "questions": [
            {
                "q": "What are the best SharePoint automation ideas for small teams?",
                "a": "The highest-value starting points for small teams are: document approval workflows with Power Automate, automatic metadata tagging when files are uploaded, new employee onboarding checklists triggered by HR system events, and weekly digest emails that summarise new content added to key libraries.",
            },
            {
                "q": "Do I need a developer to automate SharePoint processes?",
                "a": "No. Most SharePoint automations can be built with Power Automate using its visual flow builder — no code required. For advanced scenarios like tenant-wide provisioning or bulk operations, PnP PowerShell adds significant capability with minimal scripting knowledge.",
            },
            {
                "q": "What is the difference between Power Automate and SharePoint Designer workflows?",
                "a": "SharePoint Designer workflows (2010 and 2013 versions) are deprecated and will be removed. Power Automate is the modern replacement. Power Automate connects to hundreds of services beyond SharePoint, supports mobile approvals, runs on Microsoft's cloud infrastructure, and receives ongoing investment from Microsoft.",
            },
            {
                "q": "How do I prioritise which SharePoint processes to automate first?",
                "a": "Focus on processes that are high-frequency (done daily or weekly), involve multiple people (approvals, handoffs), or are currently tracked in email. Document the current manual steps, estimate time per run, then multiply by weekly frequency. Start with the highest time-savings-per-build-effort ratio.",
            },
            {
                "q": "Can SharePoint automations trigger from outside Microsoft 365?",
                "a": "Yes. Power Automate supports triggers from hundreds of external services including Salesforce, ServiceNow, Jira, GitHub, and Dynamics 365. You can also use SharePoint webhooks with Azure Logic Apps or Azure Functions to respond to SharePoint events from any platform.",
            },
        ]
    },
    "guide-teams-automation": {
        "questions": [
            {
                "q": "What can Power Automate automate in Microsoft Teams?",
                "a": "Power Automate can post adaptive card messages to channels, create Planner tasks from meeting action items, send approval requests inside Teams, trigger welcome messages for new members, monitor keywords in conversations, and send weekly digest cards — all without any custom development.",
            },
            {
                "q": "Do Teams automations require a premium Power Automate licence?",
                "a": "Most Teams automations use standard connectors (Teams, Planner, SharePoint, Outlook) which are included in Microsoft 365 business licences. Premium connectors like HTTP requests or third-party SaaS integrations require a Power Automate Premium (formerly Per-User) plan.",
            },
            {
                "q": "How do I send an adaptive card to a Teams channel from Power Automate?",
                "a": "Use the 'Post adaptive card in a chat or channel' action in the Teams connector. You provide the team and channel, then paste in your adaptive card JSON. Use the Adaptive Cards designer at adaptivecards.io to build the card visually, then copy the JSON into Power Automate.",
            },
            {
                "q": "Can Teams automations respond to specific keywords in messages?",
                "a": "Yes. Use the 'When a new channel message is added' trigger, then add a Condition action that checks if the message body contains your keyword. Because Teams stores message content as HTML, use a 'contains' check on the body/content field, not an exact match.",
            },
            {
                "q": "What is the most reliable way to create Planner tasks from Teams meetings?",
                "a": "Use the 'When a Teams meeting ends' trigger (requires Teams Premium or Meeting Recording connector), then parse the meeting transcript or action items with an AI action, and create Planner tasks via the Planner connector. For simpler setups without Teams Premium, use a post-meeting form or an approval step that extracts actions manually.",
            },
        ]
    },
    "guide-power-automate-sharepoint": {
        "questions": [
            {
                "q": "What are the most useful Power Automate flows for SharePoint?",
                "a": "The five highest-value flows are: document approval with email and Teams notifications, contract expiry reminders triggered by a date column, new employee onboarding triggered from an HR list, stale content alerts for libraries not updated in 90+ days, and multi-level escalation approvals for sensitive documents.",
            },
            {
                "q": "Can Power Automate read and update SharePoint list items?",
                "a": "Yes. The SharePoint connector includes 'Get items', 'Get item', 'Create item', 'Update item', and 'Delete item' actions. You can filter items using OData queries, update specific fields, and work with attachments — all without writing any code.",
            },
            {
                "q": "How do I trigger a Power Automate flow when a SharePoint file is uploaded?",
                "a": "Use the 'When a file is created (properties only)' trigger on your document library. This fires for new uploads and provides the file metadata. For files created in subfolders, enable the 'Include subfolders' option in the trigger settings.",
            },
            {
                "q": "Why does my SharePoint approval flow sometimes not trigger?",
                "a": "Common causes: the flow is turned off, the trigger is on the wrong site or library, the triggering user is the flow owner (owner-triggered flows can sometimes self-suppress), or throttling from high list activity. Check the flow's run history in Power Automate for the exact error. Also verify the flow has permission to access the SharePoint site.",
            },
            {
                "q": "What happens to pending approvals if the Power Automate flow is edited?",
                "a": "Editing and saving a flow creates a new version. Approvals that started on the old version continue running on that version until they complete or time out. New triggers use the new version. Avoid editing flows with many in-flight approvals — instead, build a v2 flow and turn off the old one after in-flight runs complete.",
            },
        ]
    },
    "guide-power-automate-triggers-actions": {
        "questions": [
            {
                "q": "What is the difference between SharePoint triggers in Power Automate?",
                "a": "'When a file is created' fires only on new file creation. 'When a file is created or modified' fires on both create and update. 'When an item is created' and 'When an item is created or modified' work the same way but for list items. Use the narrowest trigger to avoid unnecessary flow runs and reduce throttling risk.",
            },
            {
                "q": "How do I filter SharePoint list items in Power Automate?",
                "a": "Use an OData filter query in the 'Get items' action. For example: Status eq 'Approved' filters to approved items only. You can combine filters with 'and' / 'or', filter by date with ge (greater than or equal), and reference column internal names. Always set a Top Count limit to avoid retrieving thousands of items unnecessarily.",
            },
            {
                "q": "What is the 'Send an HTTP request to SharePoint' action used for?",
                "a": "This action calls the SharePoint REST API directly, giving you access to operations not exposed by the standard connector — such as managing permissions, working with site collections, updating content types, or reading term store data. It requires knowing the REST endpoint and passing correct Accept and Content-Type headers.",
            },
            {
                "q": "Why does my 'Get items' action only return 100 results?",
                "a": "The default Top Count is 100. Increase it up to 5000 in the action settings. For lists larger than 5000 items, use pagination: enable 'Pagination' in Settings and set the threshold. For very large lists, consider filtering server-side with OData queries first to reduce the result set before pagination.",
            },
            {
                "q": "How do I avoid throttling in SharePoint Power Automate flows?",
                "a": "Throttling occurs when too many API calls hit SharePoint in a short window. Mitigation strategies: avoid loops that call SharePoint on every item (batch with Select columns instead), add a Delay action between iterations, use 'Get items' with OData filters rather than filtering client-side after retrieving all items, and schedule high-volume flows outside business hours.",
            },
        ]
    },
    "guide-power-apps-sharepoint": {
        "questions": [
            {
                "q": "Can I use SharePoint as a database for Power Apps?",
                "a": "Yes, SharePoint is the most common data source for Power Apps in Microsoft 365 environments. You connect via the SharePoint connector and work with list items directly. For simple data entry and viewing scenarios it works well, but it has delegation limits — queries that can't be processed server-side are limited to 500–2000 records client-side.",
            },
            {
                "q": "What is delegation in Power Apps and why does it matter?",
                "a": "Delegation means the data source (SharePoint) processes a filter or sort query on the server, returning only matching records. Non-delegable functions (like Search() or most text functions) run client-side on a capped record set. If your list has more than 2000 items and you use non-delegable filters, users will see incomplete results without any warning.",
            },
            {
                "q": "What is the difference between canvas apps and model-driven apps?",
                "a": "Canvas apps give you pixel-precise control over layout and connect to any data source. Model-driven apps are data-first: you define the data model and the app generates its UI automatically. Canvas apps suit custom interfaces; model-driven apps suit complex business data with relationships, business rules, and standard CRM-style views.",
            },
            {
                "q": "How do I share a Power App with users in my organisation?",
                "a": "From the Power Apps portal, open the app and select Share. Enter names or groups. Users need at least a Microsoft 365 licence to run Power Apps that connect to standard connectors. For premium connectors, each user needs a Power Apps Premium (Per User) licence. Also share the underlying SharePoint list with appropriate permissions.",
            },
            {
                "q": "Can Power Apps connect to data sources outside Microsoft 365?",
                "a": "Yes. Power Apps supports hundreds of connectors including SQL Server, Dataverse, Salesforce, ServiceNow, REST APIs via custom connectors, and on-premises data sources via the on-premises data gateway. Connectors marked 'Premium' require a Power Apps Premium licence.",
            },
        ]
    },
    "guide-sharepoint-approval-workflow": {
        "questions": [
            {
                "q": "How do I build a SharePoint document approval workflow in Power Automate?",
                "a": "Create a flow triggered by 'When a file is created or modified' on your SharePoint library. Add a 'Start and wait for an approval' action, configure the approver, subject, and item link. Then use a Condition to check if the outcome is 'Approve' or 'Reject', and update a Status column in SharePoint with the result.",
            },
            {
                "q": "Can I send approval requests in Microsoft Teams instead of email?",
                "a": "Yes. In the 'Start and wait for an approval' action, set the approval type to 'Approve/Reject - First to respond' or 'Custom responses'. Use the Teams connector to post the approval card. Approvers receive an actionable card directly in Teams and can approve without leaving the app.",
            },
            {
                "q": "What happens if an approver does not respond to a SharePoint approval request?",
                "a": "Without a timeout, the approval waits indefinitely. Add a 'Start and wait for an approval' action inside a 'Do until' loop with a timeout expression, or use the built-in 'Request options' to set an expiry duration. When the timeout fires, update the document status to 'Escalated' or 'Timed Out' and notify the approver's manager.",
            },
            {
                "q": "How do I update a SharePoint column after a document is approved or rejected?",
                "a": "After the approval action returns, use a Condition to check the outcome value. In each branch, add an 'Update file properties' action targeting the same library item. Use the 'ID' from the trigger output to identify the correct item, and set your Status, Approval Date, or Approver Name columns accordingly.",
            },
            {
                "q": "Can I track SharePoint approval history for compliance?",
                "a": "Yes. Power Automate provides the full approval history (approver, response, date, comments) in the approval action outputs. Log this to a separate SharePoint list using a 'Create item' action, or use the built-in Microsoft 365 Compliance features to retain approval records in the audit log.",
            },
        ]
    },
    "guide-sharepoint-approval-multiple-approvers": {
        "questions": [
            {
                "q": "How do I require multiple people to approve a document in SharePoint?",
                "a": "Use the 'Start and wait for an approval' action in Power Automate with type 'Approve/Reject - Everyone must approve'. Add all required approvers to the Assigned To field. The flow waits until every approver responds. If any approver rejects, the flow takes the rejection path immediately without waiting for remaining approvers.",
            },
            {
                "q": "What is the difference between sequential and parallel approvals in Power Automate?",
                "a": "Sequential approval sends requests one at a time — Approver 2 is notified only after Approver 1 approves. Parallel approval (Everyone must approve) notifies all approvers simultaneously and waits for all responses. Sequential is better for hierarchical sign-off chains; parallel is better when approvers are independent and you want faster completion.",
            },
            {
                "q": "How do I route an approval to different people based on the document category?",
                "a": "Use a Switch or nested Condition action after the trigger to read the Category column value, then set an approver variable for each case. Pass that variable into the 'Assigned To' field of the approval action. This way a single flow handles all categories without duplicating the approval logic.",
            },
            {
                "q": "How do I handle out-of-office approvers in a multi-step approval flow?",
                "a": "The cleanest approach is to use delegation: in Outlook, approvers set an auto-delegate when out of office. Power Automate approval requests sent to them are auto-forwarded. Alternatively, build a fallback into the flow: if no response after N days, reassign to the approver's manager using a 'Get manager' action from Microsoft 365 Users connector.",
            },
            {
                "q": "Can I build a compliance audit trail for multi-level approvals in SharePoint?",
                "a": "Yes. After each approval stage resolves, log the approver name, decision, timestamp, and comments to a dedicated SharePoint list. Combine this with SharePoint list versioning on the document library to create a full audit trail. For regulated industries, you can also route approval records to Microsoft Purview via a retention label.",
            },
        ]
    },
    "guide-sharepoint-workflow-migration": {
        "questions": [
            {
                "q": "When does Microsoft retire SharePoint Designer workflows?",
                "a": "SharePoint 2010 workflow platform was retired in November 2020 for new tenants and is in maintenance mode for existing ones. SharePoint 2013 workflows are still running but Microsoft has signalled end of investment — they are not available in new SharePoint sites. Power Automate is the supported replacement for both.",
            },
            {
                "q": "Can I automatically migrate SharePoint Designer workflows to Power Automate?",
                "a": "There is no fully automated one-click migration tool. Microsoft's Power Automate migration tool (in preview) can detect and propose migration paths for some 2013 workflows, but complex custom actions, InfoPath forms, and custom code behind workflows require manual reconstruction in Power Automate.",
            },
            {
                "q": "What features in SharePoint Designer workflows have no direct Power Automate equivalent?",
                "a": "InfoPath form integration, impersonation steps that run as a different user, workflow status column with custom states, and complex looping with indexed variables have no direct equivalent. Impersonation is replaced by service accounts or managed identities. InfoPath forms are replaced by Power Apps.",
            },
            {
                "q": "How long does a SharePoint workflow migration project typically take?",
                "a": "A simple approval or notification workflow can be rebuilt in Power Automate in a few hours. A complex multi-stage workflow with custom actions, lookups, and form integration may take several days including testing. Full tenant migrations with hundreds of workflows are typically scoped as 4–12 week projects depending on volume and complexity.",
            },
            {
                "q": "Should I migrate all SharePoint Designer workflows at once?",
                "a": "No — a phased approach works best. Inventory all workflows, classify them by complexity and business impact, and start with simple high-use workflows to build team familiarity with Power Automate. Decommission old workflows immediately after the new flow is validated in production.",
            },
        ]
    },
    "guide-sharepoint-permissions-best-practices": {
        "questions": [
            {
                "q": "What is the least privilege principle in SharePoint permissions?",
                "a": "Least privilege means users receive only the minimum permission level needed to do their job. In SharePoint this means most users get Contribute or Read on their team sites, never Full Control. Site Owners should be kept to a small group, and permission changes should require documented justification.",
            },
            {
                "q": "Should I use SharePoint groups or Microsoft 365 groups to manage permissions?",
                "a": "For team sites connected to Microsoft Teams or Outlook, use Microsoft 365 group membership — changes in Teams membership automatically flow to SharePoint. For communication sites or standalone sites, use SharePoint groups (Owners, Members, Visitors). Avoid assigning permissions directly to individual accounts.",
            },
            {
                "q": "How do I conduct a SharePoint permissions audit?",
                "a": "Use the SharePoint admin center's Active sites report to identify sites with external sharing enabled. Run the 'Check permissions' tool on individual sites for user-level inspection. For tenant-wide auditing, use PnP PowerShell's Get-PnPSiteCollectionAdmin and Get-PnPGroupMember cmdlets, or the Microsoft 365 Purview audit log for permission change history.",
            },
            {
                "q": "How often should I review SharePoint permissions?",
                "a": "Microsoft recommends quarterly access reviews for sensitive sites and annually for standard sites. Use Microsoft Entra ID Access Reviews (included in Entra ID P2) to automate the review process — site owners are prompted to confirm or remove each member without IT intervention.",
            },
            {
                "q": "What is the risk of unique permissions on SharePoint folders and items?",
                "a": "Unique permissions on folders or items break inheritance and create a shadow permission model that is difficult to audit. They are invisible in the standard site permissions view. Over time, users leave the organisation but retain access to individual items. Best practice is to separate sensitive content into its own library or site rather than using item-level unique permissions.",
            },
        ]
    },
    "guide-sharepoint-integrations": {
        "questions": [
            {
                "q": "What are the main ways to integrate SharePoint with other business systems?",
                "a": "The four main integration approaches are: Power Automate for no-code event-driven flows, Microsoft Graph API for programmatic read/write access, SharePoint webhooks for real-time change notifications to external systems, and embedded web parts or iFrames for surfacing external app content inside SharePoint pages.",
            },
            {
                "q": "Can SharePoint integrate with Salesforce or Dynamics 365?",
                "a": "Yes. Power Automate has certified connectors for both Salesforce and Dynamics 365. You can sync records between SharePoint lists and CRM, trigger document creation in SharePoint from CRM events, or attach SharePoint documents to CRM records. Microsoft Dynamics 365 also has native SharePoint document management integration built in.",
            },
            {
                "q": "What is Microsoft Graph and why does it matter for SharePoint integrations?",
                "a": "Microsoft Graph is the unified API endpoint for all Microsoft 365 services. For SharePoint, it exposes sites, lists, drives (document libraries), pages, permissions, and search. Any integration that needs to read or write SharePoint data programmatically — from a web app, Azure Function, or external system — goes through Graph.",
            },
            {
                "q": "Do SharePoint integrations require an Azure subscription?",
                "a": "Not always. Power Automate integrations run entirely within Microsoft 365 with no Azure dependency. Microsoft Graph API calls can be made from any platform using app registrations in Microsoft Entra ID. Azure is only required for hosting custom code such as Azure Functions, Logic Apps, or Azure API Management.",
            },
            {
                "q": "How do I keep SharePoint data in sync with an external database?",
                "a": "Use Power Automate with the 'When an item is created or modified' SharePoint trigger to push changes to an external system via an HTTP action or connector. For two-way sync, pair this with a scheduled flow (Recurrence trigger) that polls the external system and updates SharePoint. For high-volume scenarios, use Azure Logic Apps with retry policies and dead-letter queuing.",
            },
        ]
    },
    "guide-m365-migration-checklist": {
        "questions": [
            {
                "q": "How long does a Microsoft 365 migration take?",
                "a": "A basic mailbox-only migration for a 50-user organisation can take 2–4 weeks. A full migration including SharePoint, OneDrive, Teams, and hybrid Exchange typically takes 8–16 weeks. Enterprise migrations above 1,000 users are usually 6–12 month programmes with phased cutover.",
            },
            {
                "q": "What data cannot be migrated to Microsoft 365 automatically?",
                "a": "SharePoint Designer workflow history, InfoPath forms, custom list views with complex XSL, SharePoint 2010/2013 custom solution packages (.wsp), and third-party app data stored in SharePoint's app catalog all require manual reconstruction rather than migration. Legacy calendar overlays and publishing page layouts also require rebuild.",
            },
            {
                "q": "Do I need to run a parallel environment during Microsoft 365 migration?",
                "a": "For email migrations, yes — a hybrid Exchange configuration lets you run on-premises and Exchange Online simultaneously with full mailflow. For SharePoint, parallel environments are optional but recommended for a validation window. For Teams, most organisations cut over by tenant with no parallel running period.",
            },
            {
                "q": "What is the most common Microsoft 365 migration mistake?",
                "a": "Migrating without first cleaning up the source environment. Migrating stale content, obsolete sites, outdated distribution lists, and expired licences increases project cost and creates a cluttered destination. A pre-migration clean-up of unused mailboxes, sites older than 2 years, and large personal drives typically saves 20–40% of migration effort.",
            },
            {
                "q": "Which migration tool should I use for SharePoint Online?",
                "a": "Microsoft's SharePoint Migration Tool (SPMT) is free and handles on-premises SharePoint and file share migrations. Mover (also free, bundled in M365 admin center) handles Google Workspace, Box, and Dropbox. For complex enterprise migrations, third-party tools like ShareGate, Sharegate, or AvePoint offer reporting, scheduling, and incremental sync features.",
            },
        ]
    },
    "guide-sharepoint-pnp-site-migration": {
        "questions": [
            {
                "q": "What can PnP PowerShell migrate between SharePoint sites?",
                "a": "PnP PowerShell can migrate site structure (content types, columns, views), document libraries with files and metadata, list items with column values, modern site pages, navigation, and site theme. It cannot migrate workflows, permissions inheritance, custom code, or large files over the tenant upload limit.",
            },
            {
                "q": "Do I need admin rights to run a PnP PowerShell migration?",
                "a": "You need at minimum Site Collection Admin rights on both the source and destination sites. For cross-tenant migrations or bulk operations across many sites, a Global Admin or SharePoint Admin role with an app registration (client credentials) is more practical than interactive sign-in.",
            },
            {
                "q": "Can PnP PowerShell migrate SharePoint files and their version history?",
                "a": "The Invoke-PnPSiteTemplate approach migrates the latest version of files only. To preserve version history, use the built-in SharePoint Migration Manager or SPMT, which supports version history migration. PnP PowerShell's Copy-PnPFile cmdlet copies files but does not preserve version history.",
            },
            {
                "q": "How do I handle large file migrations with PnP PowerShell?",
                "a": "For files over 250 MB, use the chunked upload method with Set-PnPFileToLocal and Add-PnPFile with the -Chunked parameter. For bulk library migrations, batch files into groups and add error handling with try/catch blocks to log failures without stopping the entire run.",
            },
            {
                "q": "How long does a PnP PowerShell SharePoint site migration take?",
                "a": "A small site with under 1,000 files typically completes in under 30 minutes. A large site with 50,000+ files can take several hours depending on average file size and SharePoint throttling. Run migrations outside business hours and add retry logic to handle 429 throttling responses.",
            },
        ]
    },
    "guide-microsoft-graph-sharepoint": {
        "questions": [
            {
                "q": "What is the Microsoft Graph API and how does it relate to SharePoint?",
                "a": "Microsoft Graph is the single unified REST API for all Microsoft 365 services. For SharePoint, it exposes the /sites, /drives, /lists, and /pages endpoints, giving you programmatic access to site collections, document libraries, list data, and permissions from any platform or language.",
            },
            {
                "q": "How do I authenticate to Microsoft Graph for SharePoint access?",
                "a": "Register an application in Microsoft Entra ID and grant it the necessary Graph permissions (Sites.Read.All, Sites.ReadWrite.All, etc). Use the client credentials flow for background automation or the auth code flow for user-delegated access. Get an access token from the OAuth 2.0 token endpoint and pass it as a Bearer token in the Authorization header.",
            },
            {
                "q": "What is the difference between delegated and application permissions in Microsoft Graph?",
                "a": "Delegated permissions act as the signed-in user — the API call can only access what the user can access. Application permissions act as the app itself with tenant-wide access, requiring admin consent. For automation scripts that run without a user, use application permissions. For apps that access data on behalf of users, use delegated permissions.",
            },
            {
                "q": "Can I use Microsoft Graph to read SharePoint list items?",
                "a": "Yes. Use GET /sites/{site-id}/lists/{list-id}/items with optional $select, $filter, and $expand parameters. To include column values, expand the fields property: /items?$expand=fields. For large lists, use $top and $skiptoken for server-side pagination.",
            },
            {
                "q": "What is Graph Explorer and how do I use it for SharePoint testing?",
                "a": "Graph Explorer (developer.microsoft.com/en-us/graph/graph-explorer) is a browser-based tool for testing Microsoft Graph API calls without writing code. Sign in with your Microsoft 365 account, enter a Graph endpoint URL, and see the live JSON response. It also shows required permissions and includes sample queries for common SharePoint operations.",
            },
        ]
    },
    "guide-pnp-entra-app-registration": {
        "questions": [
            {
                "q": "What is PnP PowerShell and why does it need an Entra app registration?",
                "a": "PnP PowerShell is the community-maintained PowerShell module for SharePoint and Microsoft 365 administration. App registration (client credentials with a certificate) allows PnP to authenticate as an application rather than as an interactive user — essential for scheduled scripts, automation pipelines, and CI/CD workflows that cannot prompt for a password.",
            },
            {
                "q": "What permissions does a PnP PowerShell app registration need?",
                "a": "For SharePoint-only operations: Sites.FullControl.All (application permission). For tenant-level operations (creating site collections, managing users): SharePoint > Have full control of all site collections. For Exchange Online operations: Exchange.ManageAsApp plus appropriate Exchange role assignment. Always follow least privilege — grant only what the script actually uses.",
            },
            {
                "q": "Why use a certificate instead of a client secret for PnP authentication?",
                "a": "Client secrets expire (maximum 2 years) and must be manually rotated. Certificates can have longer validity periods and are bound to the device or key vault where they're stored, making them harder to exfiltrate. For production automation, certificates stored in Azure Key Vault or the Windows Certificate Store are significantly more secure than secrets stored in environment variables.",
            },
            {
                "q": "How do I connect PnP PowerShell using a certificate?",
                "a": "Use Connect-PnPOnline -Url https://tenant.sharepoint.com -ClientId 'your-app-id' -Tenant 'tenant.onmicrosoft.com' -CertificateBase64Encoded 'base64string' -CertificatePassword (ConvertTo-SecureString 'pwd' -AsPlainText -Force). In CI/CD pipelines, store the certificate and password as secrets and load them at runtime.",
            },
            {
                "q": "Which admin role do I need to register an app in Microsoft Entra ID?",
                "a": "The Application Administrator role is sufficient for registering apps and granting non-admin API permissions. To grant application permissions that require admin consent (such as Sites.FullControl.All), you need the Global Administrator or Cloud Application Administrator role to click 'Grant admin consent' in the Entra portal.",
            },
        ]
    },
    "guide-sharepoint-otp-retirement-entra-b2b": {
        "questions": [
            {
                "q": "What is SharePoint OTP retirement and what does it mean for external sharing?",
                "a": "Microsoft retired the legacy SharePoint one-time passcode (OTP) experience in favour of Microsoft Entra B2B Direct Connect. External users who previously received a one-time email code to access SharePoint content must now authenticate through Entra B2B — typically using a Microsoft account, Google account, or their own Entra ID tenant.",
            },
            {
                "q": "Do existing external users lose access after the OTP retirement?",
                "a": "Users who were accessing SharePoint via OTP are prompted to complete Entra B2B redemption on their next login attempt. If they have a compatible identity (Microsoft account or their organisation's Entra tenant), they redeem seamlessly. Users with only personal email addresses may need Google federation or email one-time passcode configured in your tenant's Entra External Identities settings.",
            },
            {
                "q": "What is the EnableAzureB2BIntegration setting in SharePoint?",
                "a": "EnableAzureB2BIntegration is a SharePoint admin setting that controls whether SharePoint external sharing goes through Entra B2B invitation flows. When set to True, external invitations create Entra B2B guest accounts in your directory. Microsoft has been enabling this by default across tenants as part of the OTP retirement rollout.",
            },
            {
                "q": "How do I configure Google federation for Entra External ID?",
                "a": "In the Entra admin center, go to External Identities > All identity providers > Google. Create a Google OAuth app at console.developers.google.com, configure the authorised redirect URI to your Entra tenant's callback URL, then enter the Google Client ID and Client Secret in Entra. External users with Gmail addresses can then redeem invitations using their Google credentials.",
            },
            {
                "q": "Does the OTP retirement affect SharePoint Anonymous (Anyone) links?",
                "a": "No. Anonymous (Anyone) links are unaffected — they never required authentication to begin with. OTP retirement only affects authenticated external guest access where external users sign in to view content. Anonymous links bypass identity entirely and should be governed separately through your tenant sharing settings.",
            },
        ]
    },
    "guide-sharepoint-site-provisioning-automation": {
        "questions": [
            {
                "q": "What is SharePoint site provisioning automation?",
                "a": "SharePoint site provisioning automation is a pipeline that creates new SharePoint sites on demand without requiring IT to manually build each one. Requestors fill out a form or submit a list item; an approval flow validates the request; then an automated process (Azure Logic App, PnP PowerShell runbook, or Power Automate) creates the site with the correct template, permissions, and metadata.",
            },
            {
                "q": "What components do I need to build automated SharePoint site provisioning?",
                "a": "The core components are: a SharePoint request list (intake form), a Power Automate approval flow (manager sign-off), an Azure Automation runbook with PnP PowerShell (site creation and configuration), and a status column in the request list (tracks pending/approved/created states). Optional additions include Azure Logic Apps as an orchestrator and a SharePoint site template (.pnp file) for consistent structure.",
            },
            {
                "q": "Can Power Automate create SharePoint site collections on its own?",
                "a": "Power Automate can trigger the site creation process and handle approvals, but creating a full site collection with custom templates, hub site association, and metadata configuration typically requires the PnP.PowerShell module or the SharePoint REST API via the 'Send an HTTP request to SharePoint' action. Simple modern team sites or communication sites can be created via the Graph API from Power Automate.",
            },
            {
                "q": "How do I ensure newly provisioned SharePoint sites follow a consistent structure?",
                "a": "Create a reference site with the desired structure (columns, content types, libraries, pages), export it as a PnP template with Export-PnPSiteTemplate, then apply that template to every new site with Invoke-PnPSiteTemplate during provisioning. Hub site association, navigation links, and sensitivity labels can also be set programmatically in the same runbook.",
            },
            {
                "q": "What Azure permissions does the site provisioning runbook need?",
                "a": "The Azure Automation account needs a Managed Identity or service principal with SharePoint admin permissions granted in Microsoft Entra. In the SharePoint admin center, add the managed identity as a SharePoint admin or grant it Sites.FullControl.All application permission via Microsoft Graph. No user credentials should be stored in the runbook — use the managed identity exclusively.",
            },
        ]
    },
    "guide-sharepoint-classic-calendar-to-modern-view": {
        "questions": [
            {
                "q": "Why is Microsoft retiring the SharePoint classic calendar view?",
                "a": "The classic SharePoint calendar view relied on Silverlight and legacy JavaScript rendering that is no longer supported in modern browsers. Microsoft has been deprecating classic SharePoint experiences in favour of the modern, responsive interface. Classic calendar views do not display on mobile devices and are not compatible with Microsoft Teams-embedded SharePoint pages.",
            },
            {
                "q": "What replaces the classic SharePoint calendar view?",
                "a": "The modern Calendar view is the direct replacement — it provides the same monthly/weekly/daily views on any modern SharePoint list or library with a Date column. For advanced calendaring (overlaying multiple lists, multi-tenant views), Microsoft recommends integrating with Outlook Calendar or Microsoft Bookings via Power Automate.",
            },
            {
                "q": "Will migrating to the modern calendar view lose existing calendar data?",
                "a": "No. The migration only changes the view — the underlying list items (events) remain intact. The migration script creates a new Modern Calendar view on the same list without deleting the Classic view, so you can validate the modern view before decommissioning the old one.",
            },
            {
                "q": "Can I migrate all classic calendar views in my tenant at once?",
                "a": "Yes, with PnP PowerShell you can enumerate all site collections, find lists using the Events base template (106), and apply the migration script to each one in a loop. Build in tenant throttling protection (pause between sites) and log successes and failures to a CSV for post-run review.",
            },
            {
                "q": "How do I roll back if the classic calendar migration causes issues?",
                "a": "Because the migration only adds a new view and does not modify list data, rollback is straightforward — delete the new modern view and restore the original Classic view as the default. Run Remove-PnPView targeting the newly created view name. Existing items are completely unaffected.",
            },
        ]
    },
    "guide-sharepoint-anonymous-links-report-remove-pnp-powershell": {
        "questions": [
            {
                "q": "What are anonymous (Anyone) links in SharePoint and why are they risky?",
                "a": "Anonymous links (also called Anyone links) give access to a SharePoint file or folder to anyone with the link — no sign-in required. Once shared, the link can be forwarded to anyone outside your organisation without any audit trail. If the link is posted publicly or forwarded to the wrong person, the content is exposed with no access controls.",
            },
            {
                "q": "How do I find all anonymous links across a SharePoint tenant?",
                "a": "Use the SharePoint admin center's Active sites > Sharing report for a high-level view, or use PnP PowerShell with Get-PnPListItem and Get-PnPFileSharingLink to enumerate sharing links across all site collections. The OceanCloud anonymous links script automates tenant-wide enumeration and exports results to CSV.",
            },
            {
                "q": "Can I remove anonymous links without affecting other share permissions?",
                "a": "Yes. Removing an anonymous sharing link only revokes the Anyone link access — it does not remove permissions for users who were added directly (Specific People links) or Microsoft 365 group members. Use Revoke-PnPFileSharingLink with the specific link ID to target only anonymous links.",
            },
            {
                "q": "How do I prevent anonymous links from being created in SharePoint?",
                "a": "In the SharePoint admin center, go to Policies > Sharing and set the external sharing level to 'New and existing guests' or lower. Set the default sharing link type to 'Specific people' rather than 'Anyone'. You can also set expiry dates on Anyone links at the tenant level under the 'Advanced settings for external sharing' section.",
            },
            {
                "q": "Will disabling anonymous links break existing shared documents?",
                "a": "Yes — anyone who has an existing Anyone link will lose access when you disable or remove it. Before bulk removal, identify links that are actively used (check the SharePoint admin sharing activity report) and notify document owners. Give users 2–4 weeks notice and a process to reshare via Specific People links before revoking existing anonymous links.",
            },
        ]
    },
    "guide-sharepoint-recycle-bin-restore-pnp-powershell": {
        "questions": [
            {
                "q": "How long does SharePoint keep deleted items in the Recycle Bin?",
                "a": "SharePoint retains deleted items in the first-stage (site) Recycle Bin for 93 days. When the 93-day period expires or the Recycle Bin exceeds its storage quota, items move to the second-stage (site collection) Recycle Bin, where they remain for another 93 days before permanent deletion. Site collection admins can restore items from either stage.",
            },
            {
                "q": "Can I restore SharePoint files deleted more than 93 days ago?",
                "a": "After 93 days in the second-stage Recycle Bin, items are permanently deleted from SharePoint. Recovery at that point depends on whether your tenant has Microsoft 365 Backup enabled (a paid add-on) or whether files were archived to another storage destination. Standard SharePoint recycle bin recovery only covers the 93-day window.",
            },
            {
                "q": "What does the PnP PowerShell SharePoint restore script do?",
                "a": "The script queries the site collection Recycle Bin for items matching your specified criteria (file name pattern, deleted date range, deleted-by user), outputs a preview list for review, and then restores matching items back to their original library location. It handles both first-stage and second-stage bin items.",
            },
            {
                "q": "Does restoring from the SharePoint Recycle Bin restore version history?",
                "a": "Yes. When you restore an item from the SharePoint Recycle Bin, it returns with its full version history intact, as long as the item's version history was not explicitly purged before deletion. The restored item reappears at its original path with the same permissions it had before deletion.",
            },
            {
                "q": "What happens if the original folder no longer exists when restoring from the Recycle Bin?",
                "a": "SharePoint will attempt to restore the item but fails if the parent folder was also deleted. First restore the parent folder from the Recycle Bin (it has its own entry), then restore the files within it. If the parent folder's Recycle Bin entry has also expired, restore files to the library root manually.",
            },
        ]
    },
    "guide-powershell-self-signed-certificate-entra-app-registration": {
        "questions": [
            {
                "q": "Why use a certificate instead of a client secret for Entra app authentication?",
                "a": "Client secrets expire (maximum 24 months) and must be manually rotated — a missed rotation breaks all connected automations. Certificates can have longer validity, are bound to a specific device or key vault, and their private key never leaves the secure store. For production automation, certificates are the Microsoft-recommended approach.",
            },
            {
                "q": "Can I use a self-signed certificate for production PowerShell automations?",
                "a": "Yes. Self-signed certificates are acceptable for server-to-server authentication with Microsoft Entra ID because the trust relationship is established by uploading the certificate's public key to the app registration — not by a third-party CA chain. The certificate just needs to be valid (not expired) and its private key must be available to the script at runtime.",
            },
            {
                "q": "Where should I store the certificate private key for automated scripts?",
                "a": "The most secure options are: Azure Key Vault (access via managed identity, no credential in code), the Windows Certificate Store on the automation server (LocalMachine\\My), or a CI/CD secrets manager (GitHub Actions secrets, Azure DevOps secure files). Never store certificate PFX files or passwords in source code repositories.",
            },
            {
                "q": "How long should a self-signed certificate be valid for Entra authentication?",
                "a": "Microsoft Entra ID accepts certificates valid for up to 3 years (some tenants allow longer). A 2-year validity is a common balance between rotation frequency and operational overhead. Set a calendar reminder 60 days before expiry to generate a new certificate, upload its public key to the app registration, and update the private key on all automation hosts before the old one expires.",
            },
            {
                "q": "What PowerShell permissions do I need to create a self-signed certificate?",
                "a": "On Windows, New-SelfSignedCertificate requires running PowerShell as Administrator when writing to the LocalMachine certificate store. Writing to the CurrentUser store does not require elevation. On Linux/macOS with PowerShell 7, use the openssl command-line tool instead, as New-SelfSignedCertificate is a Windows-only cmdlet.",
            },
        ]
    },
    "guide-get-started-sharepoint-agents": {
        "questions": [
            {
                "q": "What is a SharePoint agent?",
                "a": "A SharePoint agent is an AI assistant scoped to content in a specific SharePoint site or set of files. It uses Microsoft 365 Copilot to answer questions, summarise documents, and help users find information — all grounded in your tenant's SharePoint content and governed by your existing Microsoft 365 permissions.",
            },
            {
                "q": "Do I need Microsoft 365 Copilot to use SharePoint agents?",
                "a": "Yes. SharePoint agents require a Microsoft 365 Copilot licence (currently $30/user/month as an add-on to eligible M365 plans). Without a Copilot licence, the agent creation interface is visible but the agents cannot run for unlicensed users.",
            },
            {
                "q": "What is the difference between a SharePoint agent and a Copilot Studio agent?",
                "a": "A SharePoint agent is a no-code declarative agent you create directly in SharePoint — it is scoped to specific sites, files, or lists and uses natural language to query that content. A Copilot Studio agent is a fully built chatbot with custom conversation flows, connectors, and multi-channel publishing. Start with a SharePoint agent for content Q&A; use Copilot Studio when you need business logic or external integrations.",
            },
            {
                "q": "Can a SharePoint agent access content from multiple sites?",
                "a": "Yes. When creating a SharePoint agent, you can add multiple SharePoint sites as knowledge sources. The agent queries across all configured sites when answering questions. Access is always governed by the signed-in user's permissions — the agent cannot surface content a user does not already have access to.",
            },
            {
                "q": "How do I share a SharePoint agent with my team?",
                "a": "From the SharePoint site where the agent was created, open the agent and use the Share option to share it to a Teams channel or copy a direct link. Team members with a Copilot licence can interact with the agent in Teams, in SharePoint, or in Microsoft 365 Copilot Chat. The agent inherits SharePoint site permissions for data access.",
            },
        ]
    },
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def faq_schema_block(slug: str) -> str:
    """Return JSON object string for FAQPage to insert in @graph."""
    questions = FAQS[slug]["questions"]
    items = []
    for qa in questions:
        items.append(
            "          {\n"
            '            "@type": "Question",\n'
            f'            "name": {json.dumps(qa["q"])},\n'
            '            "acceptedAnswer": {\n'
            '              "@type": "Answer",\n'
            f'              "text": {json.dumps(qa["a"])}\n'
            "            }\n"
            "          }"
        )
    entities = ",\n".join(items)
    return (
        "      {\n"
        '        "@type": "FAQPage",\n'
        f'        "@id": "https://oceancloudconsults.com/articles/{slug}#faq",\n'
        '        "mainEntity": [\n'
        + entities + "\n"
        "        ]\n"
        "      },"
    )


def faq_html_block(slug: str) -> str:
    """Return HTML accordion block for the article body."""
    questions = FAQS[slug]["questions"]
    items_html = []
    for qa in questions:
        q_escaped = qa["q"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        # Split answer into paragraphs
        sentences = qa["a"].split(". ")
        # Keep first ~2 sentences as paragraph 1, rest as paragraph 2
        mid = max(1, len(sentences) // 2)
        p1 = ". ".join(sentences[:mid]).strip()
        p2 = ". ".join(sentences[mid:]).strip()
        if not p1.endswith("."):
            p1 += "."
        p2_html = f"\n              <p>{p2}</p>" if p2 and p2 != "." else ""
        items_html.append(
            '        <div class="faq-item">\n'
            '          <button class="faq-q" aria-expanded="false">\n'
            f"            {q_escaped}\n"
            '            <span class="faq-icon" aria-hidden="true">+</span>\n'
            "          </button>\n"
            '          <div class="faq-a" role="region">\n'
            '            <div class="faq-a-inner">\n'
            f"              <p>{p1}</p>{p2_html}\n"
            "            </div>\n"
            "          </div>\n"
            "        </div>"
        )
    return (
        '\n      <div class="article-faq">\n'
        '        <h2 class="faq-heading">Frequently Asked Questions</h2>\n\n'
        + "\n\n".join(items_html) + "\n"
        "      </div>\n\n      "
    )


# ---------------------------------------------------------------------------
# Main injection logic
# ---------------------------------------------------------------------------

def inject_article(filename: str, slug: str) -> bool:
    path = ARTICLES / filename
    if not path.exists():
        print(f"  SKIP (not found): {filename}")
        return False

    content = path.read_text(encoding="utf-8")

    if "FAQPage" in content:
        print(f"  SKIP (already has FAQ): {filename}")
        return False

    # ── 1. Inject FAQPage into JSON-LD @graph ──────────────────────────────
    # Insert before the first BreadcrumbList entry
    bc_marker = '"@type": "BreadcrumbList"'
    idx = content.find(bc_marker)
    if idx == -1:
        print(f"  WARN (no BreadcrumbList): {filename}")
        return False

    # Walk back to the opening { of the BreadcrumbList object
    # Find the last \n      { before bc_marker
    pre = content[:idx]
    obj_start = pre.rfind("\n      {")
    if obj_start == -1:
        print(f"  WARN (cannot find object start): {filename}")
        return False

    schema_block = faq_schema_block(slug)
    content = content[:obj_start] + "\n" + schema_block + "\n" + content[obj_start:]

    # ── 2. Inject HTML accordion before related-section ────────────────────
    related_marker = '<div class="related-section">'
    ridx = content.find(related_marker)
    if ridx == -1:
        print(f"  WARN (no related-section): {filename}")
        return False

    html_block = faq_html_block(slug)
    content = content[:ridx] + html_block + content[ridx:]

    path.write_text(content, encoding="utf-8")
    print(f"  OK: {filename}")
    return True


def main():
    articles = [
        ("guide-sharepoint-copilot-agents.html",    "guide-sharepoint-copilot-agents"),
        ("guide-m365-copilot.html",                  "guide-m365-copilot"),
        ("guide-sharepoint-automation-ideas.html",  "guide-sharepoint-automation-ideas"),
        ("guide-teams-automation.html",              "guide-teams-automation"),
        ("guide-power-automate-sharepoint.html",    "guide-power-automate-sharepoint"),
        ("guide-power-automate-triggers-actions.html", "guide-power-automate-triggers-actions"),
        ("guide-power-apps-sharepoint.html",        "guide-power-apps-sharepoint"),
        ("guide-sharepoint-approval-workflow.html", "guide-sharepoint-approval-workflow"),
        ("guide-sharepoint-approval-multiple-approvers.html", "guide-sharepoint-approval-multiple-approvers"),
        ("guide-sharepoint-workflow-migration.html", "guide-sharepoint-workflow-migration"),
        ("guide-sharepoint-permissions-best-practices.html", "guide-sharepoint-permissions-best-practices"),
        ("guide-sharepoint-integrations.html",      "guide-sharepoint-integrations"),
        ("guide-m365-migration-checklist.html",     "guide-m365-migration-checklist"),
        ("guide-sharepoint-pnp-site-migration.html", "guide-sharepoint-pnp-site-migration"),
        ("guide-microsoft-graph-sharepoint.html",   "guide-microsoft-graph-sharepoint"),
        ("guide-pnp-entra-app-registration.html",   "guide-pnp-entra-app-registration"),
        ("guide-sharepoint-otp-retirement-entra-b2b.html", "guide-sharepoint-otp-retirement-entra-b2b"),
        ("guide-sharepoint-site-provisioning-automation.html", "guide-sharepoint-site-provisioning-automation"),
        ("guide-sharepoint-classic-calendar-to-modern-view.html", "guide-sharepoint-classic-calendar-to-modern-view"),
        ("guide-sharepoint-anonymous-links-report-remove-pnp-powershell.html", "guide-sharepoint-anonymous-links-report-remove-pnp-powershell"),
        ("guide-sharepoint-recycle-bin-restore-pnp-powershell.html", "guide-sharepoint-recycle-bin-restore-pnp-powershell"),
        ("guide-powershell-self-signed-certificate-entra-app-registration.html", "guide-powershell-self-signed-certificate-entra-app-registration"),
        ("guide-get-started-sharepoint-agents.html", "guide-get-started-sharepoint-agents"),
    ]

    updated = 0
    for filename, slug in articles:
        updated += inject_article(filename, slug)

    print(f"\nDone: {updated}/{len(articles)} articles updated.")


if __name__ == "__main__":
    main()
