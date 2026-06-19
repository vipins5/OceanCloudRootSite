#!/usr/bin/env python3
"""
Enhance search index with FAQ entries for better discoverability.
"""
import json
from pathlib import Path

# Load original search index
index_file = Path(__file__).parent.parent / "data" / "search-index.json"
with open(index_file, "r", encoding="utf-8") as f:
    index = json.load(f)

print(f"📊 Current search index: {len(index)} entries")

# Find FAQ page entry
faq_page_index = None
for i, entry in enumerate(index):
    if entry.get("id") == "faq":
        faq_page_index = i
        break

if faq_page_index is None:
    print("❌ FAQ page not found!")
    exit(1)

print(f"✓ Found FAQ page at index {faq_page_index}")

# Define 20 FAQ Q&A entries
faq_entries = [
    {
        "id": "faq-sharepoint-online",
        "type": "faq",
        "tag": "FAQ",
        "title": "What is SharePoint Online?",
        "heading": "What is SharePoint Online?",
        "excerpt": "Cloud-based collaboration and document management platform included in Microsoft 365.",
        "body": "SharePoint Online is Microsoft's cloud-based collaboration and document management platform for storing, sharing, and managing documents with teams.",
        "url": "/faq",
        "dateDisplay": "",
        "dateSort": ""
    },
    {
        "id": "faq-sharepoint-onedrive",
        "type": "faq",
        "tag": "FAQ",
        "title": "What's the difference between SharePoint and OneDrive?",
        "heading": "What's the difference between SharePoint and OneDrive?",
        "excerpt": "OneDrive is personal cloud storage. SharePoint is a team collaboration platform.",
        "body": "OneDrive is personal cloud storage for individual files. SharePoint is a team collaboration platform for shared documents, team sites, and intranet content.",
        "url": "/faq",
        "dateDisplay": "",
        "dateSort": ""
    },
    {
        "id": "faq-m365-included",
        "type": "faq",
        "tag": "FAQ",
        "title": "What is Microsoft 365 and what's included?",
        "heading": "What is Microsoft 365 and what's included?",
        "excerpt": "Subscription suite including productivity apps, cloud services, and security features.",
        "body": "Microsoft 365 is a subscription suite that bundles productivity apps, cloud services like SharePoint and Teams, and security features.",
        "url": "/faq",
        "dateDisplay": "",
        "dateSort": ""
    },
    {
        "id": "faq-teams-sharepoint",
        "type": "faq",
        "tag": "FAQ",
        "title": "How do Teams and SharePoint work together?",
        "heading": "How do Teams and SharePoint work together?",
        "excerpt": "Every Teams team creates a SharePoint site. Files in Teams are stored in SharePoint.",
        "body": "Every Microsoft Teams team automatically creates a SharePoint site. Files shared in Teams are stored in SharePoint.",
        "url": "/faq",
        "dateDisplay": "",
        "dateSort": ""
    },
    {
        "id": "faq-remote-access",
        "type": "faq",
        "tag": "FAQ",
        "title": "Can I access SharePoint from outside the office?",
        "heading": "Can I access SharePoint from outside the office?",
        "excerpt": "Yes, cloud-based and accessible anywhere with secure MFA authentication.",
        "body": "Yes. SharePoint Online is cloud-based and accessible from any device with an internet connection using secure MFA.",
        "url": "/faq",
        "dateDisplay": "",
        "dateSort": ""
    },
    {
        "id": "faq-permissions",
        "type": "faq",
        "tag": "FAQ",
        "title": "How do SharePoint permissions work?",
        "heading": "How do SharePoint permissions work?",
        "excerpt": "Uses permission levels assigned to groups with inheritance that can be broken.",
        "body": "SharePoint uses permission levels assigned to groups. Permissions inherit downward but can be broken for unique permissions.",
        "url": "/faq",
        "dateDisplay": "",
        "dateSort": ""
    },
    {
        "id": "faq-security",
        "type": "faq",
        "tag": "FAQ",
        "title": "How secure is Microsoft 365?",
        "heading": "How secure is Microsoft 365?",
        "excerpt": "90+ compliance certifications, AES-256 encryption, shared responsibility model.",
        "body": "Microsoft 365 has 90+ compliance certifications with AES-256 encryption. Security is a shared responsibility.",
        "url": "/faq",
        "dateDisplay": "",
        "dateSort": ""
    },
    {
        "id": "faq-governance",
        "type": "faq",
        "tag": "FAQ",
        "title": "What is SharePoint governance?",
        "heading": "What is SharePoint governance?",
        "excerpt": "Policies and processes that keep environments organized, secure, and useful.",
        "body": "SharePoint governance is the set of policies and processes covering site creation, naming, ownership, retention, and access reviews.",
        "url": "/faq",
        "dateDisplay": "",
        "dateSort": ""
    },
    {
        "id": "faq-migration-timeline",
        "type": "faq",
        "tag": "FAQ",
        "title": "How long does a Microsoft 365 migration take?",
        "heading": "How long does a Microsoft 365 migration take?",
        "excerpt": "4-8 weeks for small orgs, 8-16 weeks for mid-size, 3-12 months for enterprise.",
        "body": "Small organizations: 4-8 weeks. Mid-size: 8-16 weeks. Enterprise: 3-12 months.",
        "url": "/faq",
        "dateDisplay": "",
        "dateSort": ""
    },
    {
        "id": "faq-google-migration",
        "type": "faq",
        "tag": "FAQ",
        "title": "How do I migrate from Google Workspace to Microsoft 365?",
        "heading": "How do I migrate from Google Workspace to Microsoft 365?",
        "excerpt": "Move email, files, and calendars using Microsoft 365 admin centre tools.",
        "body": "Migration involves moving email to Exchange Online, files to SharePoint/OneDrive, and calendars using M365 tools.",
        "url": "/faq",
        "dateDisplay": "",
        "dateSort": ""
    },
    {
        "id": "faq-spmt",
        "type": "faq",
        "tag": "FAQ",
        "title": "What is the SharePoint Migration Tool?",
        "heading": "What is the SharePoint Migration Tool?",
        "excerpt": "Free tool for migrating files to SharePoint Online and OneDrive.",
        "body": "The SharePoint Migration Tool is a free application for migrating files from file servers and on-premises SharePoint to SharePoint Online.",
        "url": "/faq",
        "dateDisplay": "",
        "dateSort": ""
    },
    {
        "id": "faq-copilot",
        "type": "faq",
        "tag": "FAQ",
        "title": "What is Microsoft Copilot for M365?",
        "heading": "What is Microsoft Copilot for M365?",
        "excerpt": "AI assistant integrated into M365 apps for summarizing, drafting, and analyzing.",
        "body": "Microsoft 365 Copilot is an AI assistant integrated into M365 apps that summarizes emails, drafts documents, and answers questions.",
        "url": "/faq",
        "dateDisplay": "",
        "dateSort": ""
    },
    {
        "id": "faq-power-platform",
        "type": "faq",
        "tag": "FAQ",
        "title": "What is Power Platform and how does it connect to SharePoint?",
        "heading": "What is Power Platform and how does it connect to SharePoint?",
        "excerpt": "Includes automation, apps, dashboards, and websites. SharePoint is a common data source.",
        "body": "Power Platform includes Power Automate, Power Apps, Power BI, and Power Pages. SharePoint is a common data source.",
        "url": "/faq",
        "dateDisplay": "",
        "dateSort": ""
    },
    {
        "id": "faq-viva",
        "type": "faq",
        "tag": "FAQ",
        "title": "What is Microsoft Viva?",
        "heading": "What is Microsoft Viva?",
        "excerpt": "Employee experience platform with Connections, Engage, Learning, Insights, and Goals.",
        "body": "Viva is an employee experience platform with modules for intranet, communities, learning, analytics, and OKR tracking.",
        "url": "/faq",
        "dateDisplay": "",
        "dateSort": ""
    },
    {
        "id": "faq-search",
        "type": "faq",
        "tag": "FAQ",
        "title": "How does SharePoint search work?",
        "heading": "How does SharePoint search work?",
        "excerpt": "Security-trimmed search showing only results users have permission to see.",
        "body": "SharePoint search is security-trimmed and shows only results users have permission to view.",
        "url": "/faq",
        "dateDisplay": "",
        "dateSort": ""
    },
    {
        "id": "faq-business-enterprise",
        "type": "faq",
        "tag": "FAQ",
        "title": "What's the difference between Business and Enterprise plans?",
        "heading": "What's the difference between Business and Enterprise plans?",
        "excerpt": "Business: up to 300 users. Enterprise: unlimited with advanced features.",
        "body": "Business plans are for up to 300 users. Enterprise plans have no limit and add advanced compliance and analytics.",
        "url": "/faq",
        "dateDisplay": "",
        "dateSort": ""
    },
    {
        "id": "faq-intranet",
        "type": "faq",
        "tag": "FAQ",
        "title": "What is an intranet and does my business need one?",
        "heading": "What is an intranet and does my business need one?",
        "excerpt": "Internal website for news and policies. Works well for 50+ employees.",
        "body": "An intranet is an internal website serving as your digital headquarters. Works well for organizations with 50+ employees.",
        "url": "/faq",
        "dateDisplay": "",
        "dateSort": ""
    },
    {
        "id": "faq-customization",
        "type": "faq",
        "tag": "FAQ",
        "title": "Can SharePoint be customized to match our brand?",
        "heading": "Can SharePoint be customized to match our brand?",
        "excerpt": "Yes with custom themes, logos, and SPFx web parts.",
        "body": "Yes. SharePoint supports custom themes, logos, and SPFx web parts for branding.",
        "url": "/faq",
        "dateDisplay": "",
        "dateSort": ""
    },
    {
        "id": "faq-consultant",
        "type": "faq",
        "tag": "FAQ",
        "title": "Do I need a consultant for SharePoint?",
        "heading": "Do I need a consultant for SharePoint?",
        "excerpt": "Basic use: no. Intranets, migrations, governance, or Copilot: yes.",
        "body": "For intranets, migrations, governance at scale, or Copilot rollouts, a consultant prevents expensive mistakes.",
        "url": "/faq",
        "dateDisplay": "",
        "dateSort": ""
    },
    {
        "id": "faq-oceancloud-engagement",
        "type": "faq",
        "tag": "FAQ",
        "title": "How does an OceanCloud engagement work?",
        "heading": "How does an OceanCloud engagement work?",
        "excerpt": "Free 60-min discovery call, then scoped work with no long-term contracts.",
        "body": "Every engagement starts with a free discovery call. We then propose scoped work with no long-term contracts required.",
        "url": "/faq",
        "dateDisplay": "",
        "dateSort": ""
    }
]

# Insert FAQ entries after the FAQ page
for i, entry in enumerate(faq_entries):
    index.insert(faq_page_index + 1 + i, entry)

# Write enhanced index
with open(index_file, "w", encoding="utf-8") as f:
    json.dump(index, f, indent=2, ensure_ascii=False)

print(f"✅ Enhanced search index with {len(faq_entries)} FAQ entries")
print(f"📊 Total entries now: {len(index)}")
