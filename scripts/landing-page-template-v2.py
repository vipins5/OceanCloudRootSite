#!/usr/bin/env python3
"""
Generate updated landing pages with backend integration
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets" / "lead-magnets"

def generate_landing_page_v2(magnet_id: str, title: str, description: str, 
                            value_props: list, resource_type: str) -> str:
    """Generate HTML landing page with backend form integration."""
    
    value_list = "\n".join([f"            <li>{prop}</li>" for prop in value_props])
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="magnet-id" content="{magnet_id}">
  <meta name="magnet-title" content="{title}">
  <title>{title} - OceanCloud</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: 'Segoe UI', sans-serif; background: #f5f5f5; color: #333; line-height: 1.6; }}
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
    .form-group input {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; font-family: inherit; }}
    .form-group input:focus {{ outline: none; border-color: #0077b6; box-shadow: 0 0 0 3px rgba(0,119,182,0.1); }}
    .btn {{ width: 100%; padding: 14px; background: linear-gradient(135deg, #0077b6 0%, #0096d6 100%); color: white; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; }}
    .btn:hover {{ transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,119,182,0.3); }}
    .btn:disabled {{ opacity: 0.6; cursor: not-allowed; }}
    .form-message {{ margin-top: 12px; padding: 10px; border-radius: 6px; font-size: 14px; display: none; }}
    .form-message.success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; display: block; }}
    .form-message.error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; display: block; }}
    .privacy-text {{ font-size: 12px; color: #999; margin-top: 12px; text-align: center; }}
    .privacy-text a {{ color: #0077b6; text-decoration: none; }}
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
      <form id="leadForm">
        <div class="form-group">
          <label for="name">Name *</label>
          <input type="text" id="name" name="name" required placeholder="Your Name" autocomplete="name">
        </div>
        <div class="form-group">
          <label for="email">Email *</label>
          <input type="email" id="email" name="email" required placeholder="you@company.com" autocomplete="email">
        </div>
        <div class="form-group">
          <label for="company">Company</label>
          <input type="text" id="company" name="company" placeholder="Optional" autocomplete="organization">
        </div>
        <button type="submit" class="btn" id="submitBtn">📥 Download Resource</button>
        <div class="form-message" id="formMessage"></div>
      </form>
      <p class="privacy-text">
        We respect your privacy. <a href="/privacy" target="_blank">Privacy Policy</a> | 
        <a href="#" onclick="unsubscribe(); return false;">Unsubscribe</a>
      </p>
    </div>
  </div>

  <script src="/js/lead-capture.js"></script>
  <script>
    document.getElementById('leadForm').addEventListener('submit', async (e) => {{
      e.preventDefault();
      
      const name = document.getElementById('name').value.trim();
      const email = document.getElementById('email').value.trim();
      const company = document.getElementById('company').value.trim();
      const submitBtn = document.getElementById('submitBtn');
      const formMessage = document.getElementById('formMessage');
      
      // Disable button
      submitBtn.disabled = true;
      submitBtn.textContent = 'Processing...';
      
      try {{
        const metadata = LeadCapture.getMagnetMetadata();
        const result = await LeadCapture.submitLeadForm({{
          name,
          email,
          company,
          ...metadata
        }});
        
        if (result.success) {{
          formMessage.className = 'form-message success';
          formMessage.textContent = '✓ Check your email for your resource!';
          document.getElementById('leadForm').reset();
          
          // Optionally redirect after success
          setTimeout(() => {{
            window.location.href = '/';
          }}, 2500);
        }} else {{
          formMessage.className = 'form-message error';
          formMessage.textContent = '✗ ' + (result.error || 'Failed to capture email. Please try again.');
          submitBtn.disabled = false;
          submitBtn.textContent = '📥 Download Resource';
        }}
      }} catch (error) {{
        formMessage.className = 'form-message error';
        formMessage.textContent = '✗ An error occurred. Please try again.';
        console.error('Submission error:', error);
        submitBtn.disabled = false;
        submitBtn.textContent = '📥 Download Resource';
      }}
    }});
    
    function unsubscribe() {{
      alert('Unsubscribe functionality coming soon. Reply to any email with "unsubscribe".');
    }}
  </script>
</body>
</html>
'''
    return html

if __name__ == "__main__":
    print("Landing page template v2 ready for use in create-all-landing-pages.py")
