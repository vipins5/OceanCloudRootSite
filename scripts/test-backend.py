#!/usr/bin/env python3
"""
Test suite for Lead Capture Backend
Verifies API endpoints and email delivery
"""

import requests
import json
from datetime import datetime
import time

BASE_URL = "http://localhost:5000"

# ANSI colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

def test_health():
    """Test health endpoint"""
    print(f"\n{BOLD}Testing Health Endpoint{RESET}")
    try:
        r = requests.get(f"{BASE_URL}/health")
        if r.status_code == 200:
            print(f"{GREEN}✓ Health check passed{RESET}")
            print(f"  Response: {r.json()}")
            return True
        else:
            print(f"{RED}✗ Health check failed: {r.status_code}{RESET}")
            return False
    except Exception as e:
        print(f"{RED}✗ Connection error: {str(e)}{RESET}")
        print(f"  Make sure backend is running: python scripts/lead-capture-backend.py")
        return False

def test_lead_capture():
    """Test lead capture endpoint"""
    print(f"\n{BOLD}Testing Lead Capture{RESET}")
    
    payload = {
        "name": f"Test Lead {datetime.now().strftime('%H%M%S')}",
        "email": f"test+{int(time.time())}@oceancloudconsults.com",
        "company": "Test Company",
        "magnet_id": "landing-copilot-readiness",
        "magnet_title": "Copilot Readiness Assessment",
        "magnet_link": "/lead-magnets/landing-copilot-readiness.html"
    }
    
    try:
        r = requests.post(f"{BASE_URL}/api/lead-capture", json=payload)
        data = r.json()
        
        if r.status_code == 201 and data.get('success'):
            print(f"{GREEN}✓ Lead captured successfully{RESET}")
            print(f"  Lead ID: {data.get('lead_id')}")
            print(f"  Email sent: {data.get('email_sent')}")
            print(f"  Message: {data.get('message')}")
            return True
        else:
            print(f"{RED}✗ Lead capture failed: {r.status_code}{RESET}")
            print(f"  Response: {data}")
            return False
    except Exception as e:
        print(f"{RED}✗ Error: {str(e)}{RESET}")
        return False

def test_contact_submit():
    """Test contact form submission"""
    print(f"\n{BOLD}Testing Contact Form Submission{RESET}")
    
    payload = {
        "from_name": f"Contact Test {datetime.now().strftime('%H%M%S')}",
        "from_email": f"contact+{int(time.time())}@oceancloudconsults.com",
        "from_company": "Test Contact Company",
        "service": "SharePoint Consulting, M365 Migration",
        "org_size": "500-2k",
        "message": "This is a test message from the backend test suite."
    }
    
    try:
        r = requests.post(f"{BASE_URL}/api/contact-submit", json=payload)
        data = r.json()
        
        if r.status_code == 201 and data.get('success'):
            print(f"{GREEN}✓ Contact submitted successfully{RESET}")
            print(f"  Contact ID: {data.get('contact_id')}")
            print(f"  Message: {data.get('message')}")
            return True
        else:
            print(f"{RED}✗ Contact submission failed: {r.status_code}{RESET}")
            print(f"  Response: {data}")
            return False
    except Exception as e:
        print(f"{RED}✗ Error: {str(e)}{RESET}")
        return False

def test_get_leads():
    """Test getting all leads"""
    print(f"\n{BOLD}Testing Get Leads Endpoint{RESET}")
    
    try:
        r = requests.get(f"{BASE_URL}/api/leads")
        data = r.json()
        
        if r.status_code == 200:
            total = data.get('total', 0)
            print(f"{GREEN}✓ Retrieved leads successfully{RESET}")
            print(f"  Total leads: {total}")
            if total > 0:
                print(f"  Latest lead: {data['leads'][-1]['name']} ({data['leads'][-1]['email']})")
            return True
        else:
            print(f"{RED}✗ Failed to retrieve leads: {r.status_code}{RESET}")
            return False
    except Exception as e:
        print(f"{RED}✗ Error: {str(e)}{RESET}")
        return False

def test_get_contacts():
    """Test getting all contacts"""
    print(f"\n{BOLD}Testing Get Contacts Endpoint{RESET}")
    
    try:
        r = requests.get(f"{BASE_URL}/api/contacts")
        data = r.json()
        
        if r.status_code == 200:
            total = data.get('total', 0)
            print(f"{GREEN}✓ Retrieved contacts successfully{RESET}")
            print(f"  Total contacts: {total}")
            if total > 0:
                print(f"  Latest contact: {data['contacts'][-1]['name']} ({data['contacts'][-1]['email']})")
            return True
        else:
            print(f"{RED}✗ Failed to retrieve contacts: {r.status_code}{RESET}")
            return False
    except Exception as e:
        print(f"{RED}✗ Error: {str(e)}{RESET}")
        return False

def test_leads_stats():
    """Test leads statistics endpoint"""
    print(f"\n{BOLD}Testing Leads Statistics{RESET}")
    
    try:
        r = requests.get(f"{BASE_URL}/api/leads/stats")
        data = r.json()
        
        if r.status_code == 200:
            print(f"{GREEN}✓ Retrieved statistics successfully{RESET}")
            print(f"  Total leads: {data.get('total_leads', 0)}")
            print(f"  Total contacts: {data.get('total_contacts', 0)}")
            if data.get('by_magnet'):
                print(f"  Leads by magnet:")
                for magnet, count in sorted(data['by_magnet'].items(), key=lambda x: x[1], reverse=True):
                    print(f"    - {magnet}: {count}")
            return True
        else:
            print(f"{RED}✗ Failed to retrieve statistics: {r.status_code}{RESET}")
            return False
    except Exception as e:
        print(f"{RED}✗ Error: {str(e)}{RESET}")
        return False

def test_validation():
    """Test form validation"""
    print(f"\n{BOLD}Testing Form Validation{RESET}")
    
    # Missing required fields
    tests = [
        {
            "name": "Missing name",
            "data": {"email": "test@test.com", "company": "Test"},
            "expect_fail": True
        },
        {
            "name": "Invalid email",
            "data": {"name": "Test", "email": "not-an-email", "company": "Test"},
            "expect_fail": True
        },
        {
            "name": "Valid data",
            "data": {
                "name": "Valid Test",
                "email": f"valid+{int(time.time())}@test.com",
                "company": "Test"
            },
            "expect_fail": False
        }
    ]
    
    results = []
    for test in tests:
        test_data = test['data'].copy()
        test_data.update({
            "magnet_id": "test-magnet",
            "magnet_title": "Test",
            "magnet_link": "/test"
        })
        
        try:
            r = requests.post(f"{BASE_URL}/api/lead-capture", json=test_data)
            
            if test['expect_fail']:
                if r.status_code >= 400:
                    print(f"{GREEN}✓ {test['name']}: correctly rejected{RESET}")
                    results.append(True)
                else:
                    print(f"{RED}✗ {test['name']}: should have failed but didn't{RESET}")
                    results.append(False)
            else:
                if r.status_code == 201:
                    print(f"{GREEN}✓ {test['name']}: correctly accepted{RESET}")
                    results.append(True)
                else:
                    print(f"{RED}✗ {test['name']}: should have passed but failed{RESET}")
                    results.append(False)
        except Exception as e:
            print(f"{RED}✗ {test['name']}: error - {str(e)}{RESET}")
            results.append(False)
    
    return all(results)

def main():
    print(f"\n{BOLD}{'='*70}")
    print("OceanCloud Lead Capture Backend Test Suite")
    print(f"{'='*70}{RESET}")
    print(f"Target: {BASE_URL}")
    
    tests = [
        test_health,
        test_lead_capture,
        test_contact_submit,
        test_get_leads,
        test_get_contacts,
        test_leads_stats,
        test_validation,
    ]
    
    results = []
    for test_func in tests:
        try:
            results.append(test_func())
        except Exception as e:
            print(f"{RED}✗ Unexpected error in {test_func.__name__}: {str(e)}{RESET}")
            results.append(False)
    
    # Summary
    print(f"\n{BOLD}{'='*70}")
    print("Test Summary")
    print(f"{'='*70}{RESET}")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"{GREEN}✓ All {total} tests passed!{RESET}")
    else:
        print(f"{YELLOW}⚠ {passed}/{total} tests passed{RESET}")
        if passed == 0:
            print(f"{RED}✗ Backend is not responding. Make sure it's running.{RESET}")
    
    return passed == total

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
