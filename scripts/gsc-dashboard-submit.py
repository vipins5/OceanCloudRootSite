#!/usr/bin/env python3
"""Google Search Console dashboard + sitemap submission helper.

This script uses a service account to:
1. Validate property access.
2. List currently submitted sitemaps and their status.
3. Pull a recent Search Analytics summary.
4. Optionally submit/update sitemaps.

Usage examples:
  python scripts/gsc-dashboard-submit.py
  python scripts/gsc-dashboard-submit.py --submit
  python scripts/gsc-dashboard-submit.py --days 30 --site-url https://oceancloudconsults.com/
"""

from __future__ import annotations

import argparse
import json
from datetime import date, timedelta
from urllib.parse import urlparse
from pathlib import Path
from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

DEFAULT_CREDENTIALS = "oceancloud-comments-daead280e122.json"
DEFAULT_SITE_URL = "https://oceancloudconsults.com/"
DEFAULT_OUTPUT = "data/reports/gsc-dashboard-report.json"
DEFAULT_SITEMAPS = [
    "https://oceancloudconsults.com/sitemap.xml",
    "https://oceancloudconsults.com/sitemap-guides.xml",
    "https://oceancloudconsults.com/sitemap-mc.xml",
]
SCOPES = ["https://www.googleapis.com/auth/webmasters"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check GSC dashboard data and optionally submit sitemaps."
    )
    parser.add_argument("--credentials", default=DEFAULT_CREDENTIALS)
    parser.add_argument("--site-url", default=DEFAULT_SITE_URL)
    parser.add_argument("--days", type=int, default=28)
    parser.add_argument("--submit", action="store_true")
    parser.add_argument(
        "--cleanup-legacy",
        action="store_true",
        help="Delete non-canonical sitemap entries after listing/submission.",
    )
    parser.add_argument(
        "--sitemap",
        action="append",
        dest="sitemaps",
        help="Repeat to provide custom sitemap URLs.",
    )
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    return parser.parse_args()


def build_gsc_service(credentials_path: str):
    creds = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=SCOPES,
    )
    return build("searchconsole", "v1", credentials=creds, cache_discovery=False)


def property_access(service: Any, site_url: str) -> dict[str, Any]:
    sites = service.sites().list().execute().get("siteEntry", [])
    found = None
    for entry in sites:
        if entry.get("siteUrl") == site_url:
            found = entry
            break
    return {
        "siteUrl": site_url,
        "hasAccess": bool(found),
        "permissionLevel": (found or {}).get("permissionLevel"),
        "availableProperties": [x.get("siteUrl") for x in sites],
    }


def preferred_site_url(requested_site_url: str, available_properties: list[str]) -> str:
    """Pick the best property URL for API calls.

    Priority:
    1. Requested URL-prefix property (exact match)
    2. Matching sc-domain property for the same host
    3. Requested URL as fallback
    """
    if requested_site_url in available_properties:
        return requested_site_url

    host = urlparse(requested_site_url).netloc.lower()
    domain_property = f"sc-domain:{host}"
    if domain_property in available_properties:
        return domain_property

    return requested_site_url


def list_sitemaps(service: Any, site_url: str) -> list[dict[str, Any]]:
    result = service.sitemaps().list(siteUrl=site_url).execute()
    return result.get("sitemap", [])


def submit_sitemaps(
    service: Any, site_url: str, sitemap_urls: list[str]
) -> list[dict[str, Any]]:
    outcomes: list[dict[str, Any]] = []
    for sm in sitemap_urls:
        try:
            service.sitemaps().submit(siteUrl=site_url, feedpath=sm).execute()
            outcomes.append({"sitemap": sm, "ok": True, "error": None})
        except HttpError as exc:
            outcomes.append({"sitemap": sm, "ok": False, "error": str(exc)})
    return outcomes


def cleanup_legacy_sitemaps(
    service: Any,
    site_url: str,
    existing_entries: list[dict[str, Any]],
    canonical_sitemaps: list[str],
) -> list[dict[str, Any]]:
    """Delete sitemap entries not in the canonical list."""
    canonical = set(canonical_sitemaps)
    existing_paths = [entry.get("path") for entry in existing_entries if entry.get("path")]
    legacy_paths = sorted(path for path in existing_paths if path not in canonical)

    outcomes: list[dict[str, Any]] = []
    for path in legacy_paths:
        try:
            service.sitemaps().delete(siteUrl=site_url, feedpath=path).execute()
            outcomes.append({"sitemap": path, "deleted": True, "error": None})
        except HttpError as exc:
            outcomes.append({"sitemap": path, "deleted": False, "error": str(exc)})
    return outcomes


def analytics_summary(service: Any, site_url: str, days: int) -> dict[str, Any]:
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=max(days - 1, 0))
    body = {
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "dimensions": ["date"],
        "rowLimit": 25000,
    }

    response = service.searchanalytics().query(siteUrl=site_url, body=body).execute()
    rows = response.get("rows", [])

    clicks = 0
    impressions = 0
    weighted_position = 0.0
    for row in rows:
        row_clicks = int(row.get("clicks", 0))
        row_impressions = int(row.get("impressions", 0))
        row_position = float(row.get("position", 0.0))
        clicks += row_clicks
        impressions += row_impressions
        weighted_position += row_position * row_impressions

    ctr = (clicks / impressions) if impressions else 0.0
    avg_position = (weighted_position / impressions) if impressions else None

    return {
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "days": days,
        "clicks": clicks,
        "impressions": impressions,
        "ctr": round(ctr, 6),
        "averagePosition": round(avg_position, 3) if avg_position is not None else None,
        "rowCount": len(rows),
    }


def main() -> int:
    args = parse_args()
    sitemaps = args.sitemaps if args.sitemaps else list(DEFAULT_SITEMAPS)

    report: dict[str, Any] = {
        "requestedSiteUrl": args.site_url,
        "effectiveSiteUrl": args.site_url,
        "credentialsFile": args.credentials,
        "checkedAt": date.today().isoformat(),
        "submitRequested": bool(args.submit),
        "property": None,
        "sitemaps": None,
        "analytics": None,
        "submitResults": None,
        "legacyCleanupResults": None,
        "errors": [],
    }

    try:
        service = build_gsc_service(args.credentials)
    except Exception as exc:
        report["errors"].append(f"Failed to build Search Console client: {exc}")
        save_report(args.output, report)
        print("[error] Failed to authenticate/build Search Console client.")
        return 1

    try:
        prop = property_access(service, args.site_url)
        report["property"] = prop
        effective_site_url = preferred_site_url(
            args.site_url,
            prop.get("availableProperties", []),
        )
        report["effectiveSiteUrl"] = effective_site_url
        print(f"[ok] Property check complete. Access={prop['hasAccess']}")
        if effective_site_url != args.site_url:
            print(f"[ok] Using fallback property for API calls: {effective_site_url}")
    except HttpError as exc:
        report["errors"].append(f"Property access check failed: {exc}")
        effective_site_url = args.site_url

    sitemap_entries: list[dict[str, Any]] = []
    try:
        sitemap_entries = list_sitemaps(service, effective_site_url)
        report["sitemaps"] = sitemap_entries
        print(f"[ok] Retrieved {len(sitemap_entries)} sitemap entries.")
    except HttpError as exc:
        report["errors"].append(f"Sitemap listing failed: {exc}")
        print("[warn] Could not list sitemaps.")

    try:
        analytics = analytics_summary(service, effective_site_url, args.days)
        report["analytics"] = analytics
        print(
            "[ok] Analytics summary "
            f"clicks={analytics['clicks']} impressions={analytics['impressions']} ctr={analytics['ctr']}"
        )
    except HttpError as exc:
        report["errors"].append(f"Analytics query failed: {exc}")
        print("[warn] Could not read analytics summary.")

    if args.submit:
        try:
            submit_results = submit_sitemaps(service, effective_site_url, sitemaps)
            report["submitResults"] = submit_results
            ok_count = sum(1 for x in submit_results if x["ok"])
            print(f"[ok] Sitemap submit attempts complete: {ok_count}/{len(submit_results)} successful.")
        except HttpError as exc:
            report["errors"].append(f"Sitemap submission failed: {exc}")
            print("[warn] Sitemap submission failed.")

    if args.cleanup_legacy:
        try:
            cleanup_results = cleanup_legacy_sitemaps(
                service,
                effective_site_url,
                sitemap_entries,
                sitemaps,
            )
            report["legacyCleanupResults"] = cleanup_results
            deleted_count = sum(1 for x in cleanup_results if x["deleted"])
            print(f"[ok] Legacy sitemap cleanup complete: {deleted_count}/{len(cleanup_results)} deleted.")
        except HttpError as exc:
            report["errors"].append(f"Legacy sitemap cleanup failed: {exc}")
            print("[warn] Legacy sitemap cleanup failed.")

    save_report(args.output, report)
    print(f"[ok] Report written: {args.output}")

    return 0 if not report["errors"] else 2


def save_report(path: str, report: dict[str, Any]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
