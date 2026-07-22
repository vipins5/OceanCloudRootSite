#!/usr/bin/env python3
"""Add Organization schema to pages that reference it."""

import re
from pathlib import Path

# Organization schema to insert (from about.html)
org_schema = '''{
        "@type": "Organization",
        "@id": "https://oceancloudconsults.com/#organization",
        "name": "OceanCloud Consultants",
        "alternateName": "OceanCloud",
        "legalName": "OceanCloud Consultants",
        "url": "https://oceancloudconsults.com/",
        "logo": "https://oceancloudconsults.com/assets/logo.png",
        "description": "Microsoft 365 consultancy focused on SharePoint, migration, Power Platform, Copilot readiness, and workplace transformation.",
        "telephone": "+1-469-809-4053",
        "email": "oceancloudconsults@gmail.com",
        "address": {
          "@type": "PostalAddress",
          "addressLocality": "Dallas",
          "addressRegion": "TX",
          "addressCountry": "US"
        },
        "areaServed": { "@type": "Country", "name": "United States" },
        "contactPoint": [
          {
            "@type": "ContactPoint",
            "name": "Main phone",
            "telephone": "+1-469-809-4053",
            "contactType": "sales and customer service",
            "description": "Available Monday-Friday, 9:00 AM-6:00 PM Eastern Time."
          },
          {
            "@type": "ContactPoint",
            "name": "WhatsApp",
            "telephone": "+1-917-675-3126",
            "contactType": "customer support",
            "contactOption": "WhatsApp",
            "description": "Available Monday-Friday, 9:00 AM-6:00 PM Eastern Time."
          }
        ]
      },'''

pages = ['services.html', 'guides.html', 'contact.html', 'faq.html']

for page in pages:
    file_path = Path(page)
    if not file_path.exists():
        print(f'⚠️  {page}: File not found')
        continue
    
    content = file_path.read_text(encoding='utf-8')
    
    # Find where WebSite starts and insert Organization before it
    match = re.search(r'(\n      \{\n        "@type": "WebSite",)', content)
    if match:
        insert_pos = match.start(1)
        # Insert Organization before WebSite
        new_content = content[:insert_pos] + ',\n      ' + org_schema + '\n' + content[insert_pos:]
        
        file_path.write_text(new_content, encoding='utf-8')
        print(f'✅ {page}: Organization schema inserted')
    else:
        print(f'⚠️  {page}: WebSite pattern not found')
