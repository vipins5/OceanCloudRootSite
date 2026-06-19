#!/usr/bin/env python3
"""Generate Phase 2 Lead Magnet Landing Pages

Creates HTML landing pages for each lead magnet with email capture forms.
Landing pages are positioned between guide article and consultation booking.
"""

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets" / "lead-magnets"
DATA_DIR = ROOT / "data"

def generate_landing_page(magnet_id: str, title: str, description: str, 
                         value_props: list, resource_type: str, resource_url: str) -> str:
    """Generate HTML landing page for a lead magnet."""
    
    value_list = "\n".join([f"            <li>{prop}</li>" for prop in value_props])
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} - OceanCloud</title>
  <meta name="description" content="{description}">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: Segoe UI, sans-serif; background: #f5f5f5; color: #333; line-height: 1.6; }}
    
    .navbar {{ background: white; padding: 16px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
    .navbar-inner {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }}
    .logo {{ font-weight: bold; color: #0077b6; font-size: 18px; }}
    .nav-links {{ display: flex; gap: 20px; font-size: 14px; }}
    .nav-links a {{ color: #333; text-decoration: none; }}
    .nav-links a:hover {{ color: #0077b6; }}
    
    .hero {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 60px 20px; text-align: center; }}
    .hero-content {{ max-width: 700px; margin: 0 auto; }}
    .hero h1 {{ font-size: 42px; margin-bottom: 20px; font-weight: 700; }}
    .hero p {{ font-size: 18px; opacity: 0.95; margin-bottom: 30px; }}
    .hero-badge {{ display: inline-block; background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; font-size: 13px; margin-bottom: 20px; }}
    
    .container {{ max-width: 1200px; margin: 0 auto; padding: 60px 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 60px; }}
    
    .content h2 {{ color: #0077b6; font-size: 28px; margin-bottom: 20px; }}
    .content p {{ color: #666; margin-bottom: 16px; line-height: 1.7; }}
    .value-props {{ list-style: none; margin: 30px 0; }}
    .value-props li {{ padding: 12px 0; padding-left: 32px; position: relative; color: #555; }}
    .value-props li:before {{ content: "✓"; position: absolute; left: 0; color: #4CAF50; font-weight: bold; font-size: 18px; }}
    
    .form-box {{ background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); height: fit-content; }}
    .form-box h3 {{ color: #0077b6; font-size: 24px; margin-bottom: 8px; }}
    .form-box p {{ color: #999; font-size: 13px; margin-bottom: 24px; }}
    
    .form-group {{ margin-bottom: 16px; }}
    .form-group label {{ display: block; margin-bottom: 6px; font-weight: 500; font-size: 14px; color: #333; }}
    .form-group input {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }}
    .form-group input:focus {{ outline: none; border-color: #0077b6; box-shadow: 0 0 0 3px rgba(0,119,182,0.1); }}
    
    .consent {{ font-size: 12px; color: #999; margin-bottom: 20px; line-height: 1.5; }}
    .consent a {{ color: #0077b6; text-decoration: none; }}
    
    .btn-download {{ width: 100%; padding: 14px; background: linear-gradient(135deg, #0077b6 0%, #0096d6 100%); color: white; border: none; border-radius: 6px; font-size: 16px; font-weight: 600; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; }}
    .btn-download:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,119,182,0.3); }}
    
    .trust-signals {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; font-size: 12px; color: #999; }}
    .trust-icons {{ display: flex; justify-content: center; gap: 20px; margin-top: 12px; font-size: 13px; }}
    .trust-icons span {{ display: flex; align-items: center; gap: 4px; }}
    
    @media (max-width: 768px) {{
      .container {{ grid-template-columns: 1fr; gap: 40px; }}
      .hero h1 {{ font-size: 32px; }}
      .form-box {{ margin-top: 30px; }}
    }}
  </style>
</head>
<body>
  <nav class="navbar">
    <div class="navbar-inner">
      <div class="logo">OceanCloud</div>
      <div class="nav-links">
        <a href="/">Home</a>
        <a href="/guides">Guides</a>
        <a href="/services">Services</a>
      </div>
    </div>
  </nav>

  <div class="hero">
    <div class="hero-content">
      <div class="hero-badge">Free Resource • Immediate Access</div>
      <h1>{title}</h1>
      <p>{description}</p>
    </div>
  </div>

  <div class="container">
    <div class="content">
      <h2>What You'll Get</h2>
      <p>This resource includes everything you need to:</p>
      <ul class="value-props">
{value_list}
      </ul>
      
      <p><strong>Resource Type:</strong> {resource_type}</p>
      <p><strong>Time to Read/Complete:</strong> 10-15 minutes</p>
    </div>

    <div class="form-box">
      <h3>Download Now</h3>
      <p>Free instant access • No credit card required</p>
      
      <form onsubmit="handleSubmit(event)">
        <div class="form-group">
          <label for="name">Your Name</label>
          <input type="text" id="name" name="name" required placeholder="John Smith">
        </div>
        
        <div class="form-group">
          <label for="email">Work Email</label>
          <input type="email" id="email" name="email" required placeholder="john@company.com">
        </div>
        
        <div class="form-group">
          <label for="company">Company</label>
          <input type="text" id="company" name="company" placeholder="OceanCloud Inc">
        </div>
        
        <div class="consent">
          By downloading, you agree to receive occasional emails from OceanCloud about resources, best practices, and consulting services. <a href="/privacy">Privacy policy</a>.
        </div>
        
        <button type="submit" class="btn-download">📥 Download Resource</button>
      </form>
      
      <div class="trust-signals">
        <p>✓ No spam • Unsubscribe anytime • Used by 500+ organizations</p>
      </div>
    </div>
  </div>

  <script>
    function handleSubmit(event) {{
      event.preventDefault();
      const name = document.getElementById('name').value;
      const email = document.getElementById('email').value;
      const company = document.getElementById('company').value;
      
      // Send to backend/email service (placeholder)
      console.log('Form submitted:', {{ name, email, company }});
      
      // Trigger download
      window.location.href = '{resource_url}';
      
      // Show thank you message
      alert('Thank you! Your download is starting. Check your email for the resource and next steps.');
    }}
  </script>
</body>
</html>
'''
    return html

def create_landing_pages():
    """Create landing pages for all lead magnets."""
    ASSETS.mkdir(parents=True, exist_ok=True)
    
    # Define first batch of lead magnets
    landing_pages = [
        {
            "id": "copilot-readiness",
            "title": "SharePoint Copilot Readiness Assessment",
            "description": "5-question interactive assessment to gauge your organization's readiness for Copilot adoption",
            "value_props": [
                "Measure your current SharePoint maturity level",
                "Identify governance gaps before Copilot rollout",
                "Get a personalized adoption timeline",
                "See specific recommendations for your org size",
                "Benchmark against similar organizations",
            ],
            "resource_type": "Interactive Assessment (5 min) + PDF Report",
            "resource_url": "/assets/lead-magnets/assessment-copilot-readiness.html",
        },
        {
            "id": "permission-levels-qr",
            "title": "SharePoint Permission Levels Quick Reference",
            "description": "One-page printable guide to all SharePoint permission levels, groups, and inheritance rules",
            "value_props": [
                "Quick reference for all permission levels",
                "Permission inheritance explained",
                "Anonymous & external sharing guide",
                "Common mistakes and how to avoid them",
                "Print and keep on your desk",
            ],
            "resource_type": "Printable PDF (1 page)",
            "resource_url": "/assets/lead-magnets/qr-sharepoint-permission-levels.html",
        },
        {
            "id": "migration-checklist",
            "title": "M365 Migration Checklist (5-Phase Plan)",
            "description": "Complete checklist covering all phases of Microsoft 365 migration from discovery to validation",
            "value_props": [
                "Phase-by-phase migration breakdown",
                "Checkboxes for tracking progress",
                "Typical timeline estimates",
                "Key dependencies and prerequisites",
                "Print and share with your team",
            ],
            "resource_type": "Printable PDF + Tracking Checklist",
            "resource_url": "/assets/lead-magnets/qr-m365-migration.html",
        },
    ]
    
    print("=" * 70)
    print("CREATING LEAD MAGNET LANDING PAGES")
    print("=" * 70)
    
    created = 0
    for page_data in landing_pages:
        filepath = ASSETS / f"landing-{page_data['id']}.html"
        html = generate_landing_page(
            page_data["id"],
            page_data["title"],
            page_data["description"],
            page_data["value_props"],
            page_data["resource_type"],
            page_data["resource_url"],
        )
        filepath.write_text(html, encoding='utf-8')
        print(f"✅ {page_data['title']}")
        print(f"   Landing page: /lead-magnets/landing-{page_data['id']}.html")
        created += 1
    
    print("\n" + "=" * 70)
    print(f"Created {created} landing pages with email capture forms")
    print("=" * 70)

if __name__ == "__main__":
    create_landing_pages()
