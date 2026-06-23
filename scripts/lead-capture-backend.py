#!/usr/bin/env python3
"""
Lead Capture Backend for OceanCloud
Handles form submissions from contact page and lead magnet landing pages.
Integrates with SendGrid/EmailJS for transactional emails.
"""

from flask import Flask, request, jsonify
from datetime import datetime
import json
import os
from pathlib import Path
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load environment variables from .env when present
load_dotenv()

# ════════════════════════════════════════════════════════════
# CONFIGURATION
# ════════════════════════════════════════════════════════════

# Load environment variables
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
SENDGRID_FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL', 'leads@oceancloudconsults.com')

# Database paths
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'data' / 'leads'
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Lead storage files
LEADS_FILE = DATA_DIR / 'leads.json'
CONTACTS_FILE = DATA_DIR / 'contacts.json'

# ════════════════════════════════════════════════════════════
# UTILITIES
# ════════════════════════════════════════════════════════════

def load_leads():
    """Load leads from JSON file."""
    if LEADS_FILE.exists():
        try:
            return json.loads(LEADS_FILE.read_text(encoding='utf-8'))
        except:
            return []
    return []

def save_leads(leads):
    """Save leads to JSON file."""
    LEADS_FILE.write_text(json.dumps(leads, indent=2, default=str), encoding='utf-8')

def load_contacts():
    """Load contacts (from contact form) from JSON file."""
    if CONTACTS_FILE.exists():
        try:
            return json.loads(CONTACTS_FILE.read_text(encoding='utf-8'))
        except:
            return []
    return []

def save_contacts(contacts):
    """Save contacts to JSON file."""
    CONTACTS_FILE.write_text(json.dumps(contacts, indent=2, default=str), encoding='utf-8')

def send_email_sendgrid(to_email: str, subject: str, html_content: str, 
                        from_email: str = None) -> bool:
    """Send email via SendGrid."""
    if not SENDGRID_API_KEY:
        logger.warning("SendGrid API key not configured")
        return False
    
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        
        message = Mail(
            from_email=from_email or SENDGRID_FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        logger.info(f"Email sent to {to_email}: {response.status_code}")
        return response.status_code in [200, 201, 202]
    except Exception as e:
        logger.error(f"SendGrid error: {str(e)}")
        return False

def generate_lead_welcome_email(name: str, magnet_title: str, 
                                 magnet_link: str) -> str:
    """Generate HTML email for lead magnet signup."""
    return f'''
    <html>
      <body style="font-family: Inter, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
          <h2>Hi {name.split()[0]},</h2>
          
          <p>Thanks for signing up for <strong>{magnet_title}</strong>!</p>
          
          <p>Your resource is ready to download. Click the button below to access it:</p>
          
          <div style="text-align: center; margin: 30px 0;">
            <a href="https://oceancloudconsults.com{magnet_link}" 
               style="background: #0077b6; color: white; padding: 12px 24px; 
                      text-decoration: none; border-radius: 6px; display: inline-block;">
              📥 Download Now
            </a>
          </div>
          
          <p>You'll also receive a 5-email series from us over the next 10 days with:</p>
          <ul>
            <li>Additional tips and best practices</li>
            <li>Case studies from similar companies</li>
            <li>Free consultation offer</li>
          </ul>
          
          <p>Questions? Reply to this email anytime.</p>
          
          <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
          <p style="font-size: 12px; color: #999;">
            OceanCloud Consultants | 
            <a href="https://oceancloudconsults.com/privacy" style="color: #0077b6;">Privacy Policy</a> |
            <a href="#" style="color: #0077b6;">Unsubscribe</a>
          </p>
        </div>
      </body>
    </html>
    '''

def generate_contact_form_email(name: str, email: str, company: str, 
                                services: str, org_size: str, message: str) -> str:
    """Generate HTML email for contact form submission (internal)."""
    return f'''
    <html>
      <body style="font-family: Inter, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
          <h2>New Consultation Request</h2>
          
          <table style="width: 100%; border-collapse: collapse;">
            <tr>
              <td style="padding: 8px; background: #f5f5f5; font-weight: 600; width: 30%;">Name</td>
              <td style="padding: 8px;">{name}</td>
            </tr>
            <tr>
              <td style="padding: 8px; background: #f5f5f5; font-weight: 600;">Email</td>
              <td style="padding: 8px;"><a href="mailto:{email}">{email}</a></td>
            </tr>
            <tr>
              <td style="padding: 8px; background: #f5f5f5; font-weight: 600;">Company</td>
              <td style="padding: 8px;">{company}</td>
            </tr>
            <tr>
              <td style="padding: 8px; background: #f5f5f5; font-weight: 600;">Services</td>
              <td style="padding: 8px;">{services}</td>
            </tr>
            <tr>
              <td style="padding: 8px; background: #f5f5f5; font-weight: 600;">Org Size</td>
              <td style="padding: 8px;">{org_size}</td>
            </tr>
            <tr>
              <td style="padding: 8px; background: #f5f5f5; font-weight: 600; vertical-align: top;">Message</td>
              <td style="padding: 8px;">{message.replace(chr(10), '<br>')}</td>
            </tr>
          </table>
          
          <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
          <p style="font-size: 12px; color: #999;">
            Submitted at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
          </p>
        </div>
      </body>
    </html>
    '''

# ════════════════════════════════════════════════════════════
# ROUTES
# ════════════════════════════════════════════════════════════

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/api/lead-capture', methods=['POST'])
def lead_capture():
    """Capture lead magnet signups."""
    try:
        data = request.json or request.form
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        company = data.get('company', '').strip()
        magnet_id = data.get('magnet_id', '').strip()
        magnet_title = data.get('magnet_title', 'Resource').strip()
        magnet_link = data.get('magnet_link', '/lead-magnets/').strip()
        
        # Validation
        if not name or not email or not magnet_id:
            return jsonify({'error': 'Missing required fields'}), 400
        
        if '@' not in email:
            return jsonify({'error': 'Invalid email'}), 400
        
        # Create lead record
        lead = {
            'id': f"{email}_{magnet_id}_{int(datetime.now().timestamp())}",
            'name': name,
            'email': email,
            'company': company or 'Not provided',
            'magnet_id': magnet_id,
            'magnet_title': magnet_title,
            'magnet_link': magnet_link,
            'captured_at': datetime.now().isoformat(),
            'status': 'new',
            'sequence_stage': 0,
            'source': 'landing_page',
        }
        
        # Save to database
        leads = load_leads()
        leads.append(lead)
        save_leads(leads)
        
        # Send welcome email
        email_html = generate_lead_welcome_email(name, magnet_title, magnet_link)
        email_sent = send_email_sendgrid(
            to_email=email,
            subject=f'Your {magnet_title} is Ready',
            html_content=email_html
        )
        
        logger.info(f"Lead captured: {email} for {magnet_id} (email_sent={email_sent})")
        
        return jsonify({
            'success': True,
            'lead_id': lead['id'],
            'email_sent': email_sent,
            'message': 'Check your email for your resource'
        }), 201
    
    except Exception as e:
        logger.error(f"Lead capture error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/contact-submit', methods=['POST'])
def contact_submit():
    """Handle contact form submissions."""
    try:
        data = request.json or request.form
        
        name = data.get('from_name', '').strip()
        email = data.get('from_email', '').strip()
        company = data.get('from_company', '').strip()
        services = data.get('service', '').strip()
        org_size = data.get('org_size', '').strip()
        message = data.get('message', '').strip()
        
        # Validation
        if not name or not email or not message:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create contact record
        contact = {
            'id': f"{email}_{int(datetime.now().timestamp())}",
            'name': name,
            'email': email,
            'company': company or 'Not provided',
            'services': services,
            'org_size': org_size,
            'message': message,
            'submitted_at': datetime.now().isoformat(),
            'status': 'new',
            'source': 'contact_form',
        }
        
        # Save to database
        contacts = load_contacts()
        contacts.append(contact)
        save_contacts(contacts)
        
        # Send internal notification email
        internal_email_html = generate_contact_form_email(
            name, email, company, services, org_size, message
        )
        
        # Send to support email
        send_email_sendgrid(
            to_email='oceancloudconsults@gmail.com',
            subject=f'New Consultation Request from {name}',
            html_content=internal_email_html
        )
        
        # Send confirmation to user
        confirmation_html = f'''
        <html>
          <body style="font-family: Inter, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <h2>Thanks, {name.split()[0]}!</h2>
              <p>We've received your consultation request and will reach out within one working day.</p>
              <p>In the meantime, check out our <a href="https://oceancloudconsults.com/guides">guides and resources</a>.</p>
              <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
              <p style="font-size: 12px; color: #999;">OceanCloud Consultants</p>
            </div>
          </body>
        </html>
        '''
        
        send_email_sendgrid(
            to_email=email,
            subject='Consultation Request Received - OceanCloud',
            html_content=confirmation_html
        )
        
        logger.info(f"Contact submission received: {email}")
        
        return jsonify({
            'success': True,
            'contact_id': contact['id'],
            'message': 'We\'ve received your message and will be in touch soon'
        }), 201
    
    except Exception as e:
        logger.error(f"Contact submit error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/leads', methods=['GET'])
def get_leads():
    """Get all leads (admin endpoint - should require auth in production)."""
    leads = load_leads()
    return jsonify({
        'total': len(leads),
        'leads': leads
    })

@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    """Get all contacts (admin endpoint - should require auth in production)."""
    contacts = load_contacts()
    return jsonify({
        'total': len(contacts),
        'contacts': contacts
    })

@app.route('/api/leads/stats', methods=['GET'])
def leads_stats():
    """Get leads statistics."""
    leads = load_leads()
    contacts = load_contacts()
    
    # Group by magnet
    magnets = {}
    for lead in leads:
        mid = lead['magnet_id']
        if mid not in magnets:
            magnets[mid] = 0
        magnets[mid] += 1
    
    return jsonify({
        'total_leads': len(leads),
        'total_contacts': len(contacts),
        'by_magnet': magnets,
        'timestamp': datetime.now().isoformat()
    })

# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════

if __name__ == '__main__':
    logger.info("Starting OceanCloud Lead Capture Backend")
    logger.info(f"Data directory: {DATA_DIR}")
    logger.info(f"SendGrid configured: {bool(SENDGRID_API_KEY)}")
    
    # Run in debug mode for development
    # For production, use gunicorn or similar WSGI server
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        threaded=True
    )
