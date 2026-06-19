# OceanCloud Lead Capture Backend Setup Guide

## Overview

The lead capture backend is a Flask API that:
- Accepts form submissions from contact page and landing pages
- Integrates with SendGrid for email delivery
- Stores lead data in JSON files for tracking
- Provides admin endpoints for viewing leads and statistics

## Architecture

```
Frontend (HTML Form)
        ↓
Lead Capture Backend (Flask API)
        ↓
    ├─ Data Storage (JSON files)
    ├─ SendGrid Email API
    └─ Admin Dashboard (future)
```

## Installation

### 1. Install Backend Dependencies

```bash
pip install -r requirements-backend.txt
```

This installs:
- `flask` - Web framework
- `sendgrid` - Email service
- `python-dotenv` - Environment configuration
- `gunicorn` - Production WSGI server

### 2. Configure SendGrid

1. **Create SendGrid Account**
   - Sign up at https://app.sendgrid.com
   - Free tier includes 100 emails/day

2. **Generate API Key**
   - Go to Settings → API Keys
   - Create new key with mail/send permissions
   - Copy the key

3. **Set Environment Variables**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and fill in:
   SENDGRID_API_KEY=your_key_here
   SENDGRID_FROM_EMAIL=leads@oceancloudconsults.com
   ```

### 3. Verify Installation

```bash
python scripts/lead-capture-backend.py
```

Expected output:
```
Starting OceanCloud Lead Capture Backend
Data directory: .../data/leads
SendGrid configured: True
Running on http://127.0.0.1:5000
```

## Development Usage

### Local Testing

1. **Start the backend**
```bash
python scripts/lead-capture-backend.py
```

2. **Test lead capture endpoint**
```bash
curl -X POST http://localhost:5000/api/lead-capture \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "company": "Acme Corp",
    "magnet_id": "landing-copilot-readiness",
    "magnet_title": "Copilot Readiness Assessment",
    "magnet_link": "/lead-magnets/landing-copilot-readiness.html"
  }'
```

Expected response:
```json
{
  "success": true,
  "lead_id": "john@example.com_landing-copilot-readiness_1718900000",
  "email_sent": true,
  "message": "Check your email for your resource"
}
```

3. **Test contact form endpoint**
```bash
curl -X POST http://localhost:5000/api/contact-submit \
  -H "Content-Type: application/json" \
  -d '{
    "from_name": "Jane Smith",
    "from_email": "jane@example.com",
    "from_company": "TechCorp",
    "service": "SharePoint Consulting, M365 Migration",
    "org_size": "500-2k",
    "message": "We need help with our SharePoint migration"
  }'
```

### View Leads

```bash
# Get all leads
curl http://localhost:5000/api/leads

# Get all contacts
curl http://localhost:5000/api/contacts

# Get statistics
curl http://localhost:5000/api/leads/stats
```

## Production Deployment

### Option 1: Using Gunicorn (Recommended)

1. **Start with Gunicorn**
```bash
gunicorn -w 4 -b 127.0.0.1:5000 scripts.lead_capture_backend:app
```

Parameters:
- `-w 4` = 4 worker processes
- `-b 127.0.0.1:5000` = bind to localhost:5000

2. **Use systemd service** (Linux)

Create `/etc/systemd/system/oceancloud-backend.service`:
```ini
[Unit]
Description=OceanCloud Lead Capture Backend
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/oceancloud
Environment="PATH=/var/www/oceancloud/.venv/bin"
Environment="SENDGRID_API_KEY=your_key"
Environment="SENDGRID_FROM_EMAIL=leads@oceancloudconsults.com"
ExecStart=/var/www/oceancloud/.venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 scripts.lead_capture_backend:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Start the service:
```bash
sudo systemctl start oceancloud-backend
sudo systemctl enable oceancloud-backend
sudo systemctl status oceancloud-backend
```

### Option 2: Using Nginx Reverse Proxy

1. **Configure Nginx**

```nginx
# /etc/nginx/sites-available/oceancloud

upstream backend {
    server 127.0.0.1:5000;
}

server {
    listen 443 ssl http2;
    server_name oceancloudconsults.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Backend API proxy
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Frontend static files
    location / {
        root /var/www/oceancloud;
        try_files $uri $uri/ =404;
    }
}
```

2. **Enable the configuration**
```bash
sudo ln -s /etc/nginx/sites-available/oceancloud /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Data Management

### Lead Storage Location

Leads are stored in JSON files:
- **Leads**: `data/leads/leads.json` (from landing pages)
- **Contacts**: `data/leads/contacts.json` (from contact form)

### Backup Strategy

1. **Daily backups**
```bash
# Create backup directory
mkdir -p backups

# Backup leads
cp data/leads/leads.json backups/leads_$(date +%Y%m%d).json
cp data/leads/contacts.json backups/contacts_$(date +%Y%m%d).json
```

2. **Automated backup (cron)**
```bash
# Add to crontab
0 2 * * * cp /var/www/oceancloud/data/leads/*.json /var/www/oceancloud/backups/$(date +\%Y\%m\%d)/
```

### Exporting Leads to CSV

```python
import json
import csv

with open('data/leads/leads.json') as f:
    leads = json.load(f)

with open('leads_export.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=leads[0].keys())
    writer.writeheader()
    writer.writerows(leads)
```

## Frontend Integration

### Landing Pages

Landing pages automatically use the backend when they include:

1. **Script tag**
```html
<script src="/js/lead-capture.js"></script>
```

2. **Form element**
```html
<form id="leadForm">
  <input name="name" required>
  <input name="email" required>
  <input name="company">
  <button type="submit">Download</button>
</form>

<script>
document.getElementById('leadForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const result = await LeadCapture.submitLeadForm({
    name: document.querySelector('input[name="name"]').value,
    email: document.querySelector('input[name="email"]').value,
    company: document.querySelector('input[name="company"]').value,
    magnet_id: 'landing-example',
    magnet_title: 'Example Resource',
    magnet_link: '/lead-magnets/landing-example.html'
  });
  
  if (result.success) {
    alert('Check your email!');
  }
});
</script>
```

### Contact Form

The contact form automatically submits to the backend. No changes needed if you've already updated contact.html.

## Monitoring & Maintenance

### Check Backend Status

```bash
curl http://localhost:5000/health
```

### View Recent Leads

```bash
# View last 10 leads (JSON)
tail -50 data/leads/leads.json | head -20
```

### Monitor Logs

```bash
# If running with systemd
sudo journalctl -u oceancloud-backend -f

# Or check Flask logs
tail -f logs/backend.log
```

## Troubleshooting

### Issue: "SendGrid API key not configured"

**Solution**: Make sure `.env` file is created and contains `SENDGRID_API_KEY`

```bash
echo "SENDGRID_API_KEY=your_key_here" >> .env
```

### Issue: CORS errors in browser

**Solution**: Frontend must be on same domain or you need to enable CORS

For local dev, the frontend uses `/api` which proxies to backend via Nginx.

### Issue: Emails not sending

**Solution**: Check SendGrid account status

1. Verify API key is valid
2. Check SendGrid dashboard for delivery status
3. Verify "from" email is authorized in SendGrid

## Next Steps

1. ✅ Backend API running
2. ✅ Frontend form submission working
3. ⏭️ Set up email automation sequences (nurture campaigns)
4. ⏭️ Create analytics dashboard
5. ⏭️ Set up PDF delivery system
6. ⏭️ Configure webhook integrations

## API Endpoints

### Lead Capture
- **POST** `/api/lead-capture` - Capture landing page signups
- **GET** `/api/leads` - Get all leads
- **GET** `/api/leads/stats` - Get lead statistics

### Contact Form
- **POST** `/api/contact-submit` - Submit contact form
- **GET** `/api/contacts` - Get all contact submissions

### Health
- **GET** `/health` - Health check

## Support

For issues or questions, check:
- Backend logs: `scripts/lead-capture-backend.py` output
- SendGrid dashboard: https://app.sendgrid.com
- Flask documentation: https://flask.palletsprojects.com/
