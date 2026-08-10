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

import argparse
import json
import re
from pathlib import Path
import requests
import google.auth
import google.auth.transport.requests
from google.oauth2 import service_account

# ─── Configuration ────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parents[1]
SERVICE_ACCOUNT_KEY_FILE = ROOT / "oceancloud-comments-daead280e122.json"

INDEXING_ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
SCOPES = ["https://www.googleapis.com/auth/indexing"]
BASE_SITE_URL = "https://oceancloudconsults.com"
SITEMAPS = [ROOT / "sitemap.xml", ROOT / "sitemap-guides.xml"]

# Results are written outside the site root -- these used to be committed at
# the repo root and, since this is a static site, got publicly served with
# no SEO benefit (cleaned up once already; see commit 498a73b).
OUTPUT_FILE = ROOT / "data" / "reports" / "indexing-results.json"

# URL_UPDATED  = tell Google the page is new or has changed (request crawl)
# URL_DELETED  = tell Google the page has been removed
NOTIFICATION_TYPE = "URL_UPDATED"

def build_sitemap_urls() -> list[str]:
    urls: list[str] = []
    for sitemap in SITEMAPS:
        if not sitemap.exists():
            continue
        urls.extend(re.findall(r"<loc>([^<]+)</loc>", sitemap.read_text(encoding="utf-8")))
    return sorted(set(urls))

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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="List URLs without calling the API")
    args = parser.parse_args()

    urls = build_sitemap_urls()
    if not urls:
        raise RuntimeError(f"No URLs found in sitemaps: {SITEMAPS}")

    if args.dry_run:
        print(f"Would submit {len(urls)} URL(s):")
        for url in urls:
            print(f"  {url}")
        return

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

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
