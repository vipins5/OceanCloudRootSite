#!/usr/bin/env python3
"""Add Organization schema to pages that reference it."""

import re
from pathlib import Path

# Organization schema to insert (from about.html)
org_schema = '''{
        "@type": "Organization",
        "@id": "https://oceancloudconsults.com/#organization",
        "name": "OceanCloud",
        "url": "https://oceancloudconsults.com/",
        "logo": "https://oceancloudconsults.com/assets/logo.png",
        "foundingDate": "2013",
        "description": "Microsoft Solutions Partner specialising in SharePoint consulting, Microsoft 365 migration, Power Platform development, and workplace transformation.",
        "areaServed": "US",
        "numberOfEmployees": {
          "@type": "QuantitativeValue",
          "value": 15
        },
        "employee": [
          {
            "@type": "Person",
            "name": "James Whitfield",
            "jobTitle": "Chief Executive Officer",
            "description": "SharePoint MVP with 18 years of enterprise Microsoft deployments. Personally oversees every client engagement.",
            "worksFor": {
              "@id": "https://oceancloudconsults.com/#organization"
            }
          },
          {
            "@type": "Person",
            "name": "Sara Okafor",
            "jobTitle": "Head of Architecture",
            "description": "Microsoft Certified Solutions Architect specialising in M365 governance and Zero Trust security frameworks.",
            "worksFor": {
              "@id": "https://oceancloudconsults.com/#organization"
            }
          },
          {
            "@type": "Person",
            "name": "Ben Marchetti",
            "jobTitle": "Lead Power Platform Engineer",
            "description": "Power Platform champion who has automated over 200 business processes across finance, legal, and retail sectors.",
            "worksFor": {
              "@id": "https://oceancloudconsults.com/#organization"
            }
          }
        ],
        "award": [
          "Microsoft Solutions Partner — Modern Work",
          "Microsoft Solutions Partner — Security",
          "ISO 27001 Certified"
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
