"""
Google Indexing API - Batch URL submission
Requests Google to crawl/index a list of URLs.

Requirements:
    pip install google-auth requests

Setup:
    1. Google Cloud Console -> Enable "Indexing API"
    2. Create a Service Account -> download JSON key file
    3. Google Search Console -> Settings -> Users & Permissions
       -> Add the service account email as an Owner
"""

import json
from pathlib import Path
import requests
import google.auth
import google.auth.transport.requests
from google.oauth2 import service_account

# ─── Configuration ────────────────────────────────────────────────────────────

SERVICE_ACCOUNT_KEY_FILE = "oceancloud-comments-daead280e122.json"   # Path to your downloaded JSON key

INDEXING_ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
SCOPES = ["https://www.googleapis.com/auth/indexing"]
BASE_SITE_URL = "https://oceancloudconsults.com"
GUIDES_GLOB = "articles/guide-*.html"

# URL_UPDATED  = tell Google the page is new or has changed (request crawl)
# URL_DELETED  = tell Google the page has been removed
NOTIFICATION_TYPE = "URL_UPDATED"

def build_guide_urls() -> list[str]:
    root = Path(__file__).resolve().parents[1]
    guide_files = sorted(root.glob(GUIDES_GLOB))
    return [
        f"{BASE_SITE_URL}/articles/{guide_path.stem}"
        for guide_path in guide_files
    ]

# ─── Auth ─────────────────────────────────────────────────────────────────────

def get_access_token():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_KEY_FILE, scopes=SCOPES
    )
    auth_request = google.auth.transport.requests.Request()
    credentials.refresh(auth_request)
    return credentials.token


# ─── Submit ───────────────────────────────────────────────────────────────────

def submit_url(url: str, token: str) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {"url": url, "type": NOTIFICATION_TYPE}
    response = requests.post(INDEXING_ENDPOINT, headers=headers, json=payload, timeout=15)
    return {"url": url, "status": response.status_code, "response": response.json()}


def main():
    urls = build_guide_urls()
    if not urls:
        raise RuntimeError(f"No guides found with pattern: {GUIDES_GLOB}")

    print(f"Authenticating with service account from: {SERVICE_ACCOUNT_KEY_FILE}")
    token = get_access_token()
    print(f"Submitting {len(urls)} URL(s) as {NOTIFICATION_TYPE}...\n")

    results = []
    for url in urls:
        result = submit_url(url, token)
        results.append(result)
        status = result["status"]
        symbol = "✓" if status == 200 else "✗"
        print(f"  [{symbol}] {status}  {url}")
        if status != 200:
            print(f"       Response: {result['response']}")

    success = sum(1 for r in results if r["status"] == 200)
    print(f"\nDone. {success}/{len(urls)} submitted successfully.")

    # Optionally save results to a JSON file
    output_file = "indexing-results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    main()
