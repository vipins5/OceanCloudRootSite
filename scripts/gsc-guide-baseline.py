#!/usr/bin/env python3
"""Capture Google Search Console baseline metrics for all guide pages.

Outputs:
- data/reports/gsc-guide-baseline-YYYYMMDD.csv
- data/reports/gsc-guide-baseline-summary-YYYYMMDD.json
- data/reports/gsc-guide-checkpoints.json
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlparse

from google.oauth2 import service_account
from googleapiclient.discovery import build

DEFAULT_CREDENTIALS = "oceancloud-comments-daead280e122.json"
DEFAULT_SITE_URL = "https://oceancloudconsults.com/"
DEFAULT_DAYS = 28
DEFAULT_OUT_DIR = Path("data/reports")
SCOPES = ["https://www.googleapis.com/auth/webmasters"]


@dataclass
class GuideMetric:
    slug: str
    url: str
    clicks: int
    impressions: int
    ctr: float
    position: float | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture GSC baseline for guide pages.")
    parser.add_argument("--credentials", default=DEFAULT_CREDENTIALS)
    parser.add_argument("--site-url", default=DEFAULT_SITE_URL)
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUT_DIR))
    return parser.parse_args()


def build_service(credentials_path: str):
    creds = service_account.Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
    return build("searchconsole", "v1", credentials=creds, cache_discovery=False)


def preferred_site_url(service, requested_site_url: str) -> str:
    sites = service.sites().list().execute().get("siteEntry", [])
    available = [x.get("siteUrl") for x in sites]
    if requested_site_url in available:
        return requested_site_url

    host = urlparse(requested_site_url).netloc.lower()
    domain_property = f"sc-domain:{host}"
    if domain_property in available:
        return domain_property

    return requested_site_url


def list_guide_urls() -> list[tuple[str, str]]:
    guides_dir = Path("articles")
    pairs: list[tuple[str, str]] = []
    for file in sorted(guides_dir.glob("guide-*.html")):
        slug = file.stem
        url = f"https://oceancloudconsults.com/articles/{slug}"
        pairs.append((slug, url))
    return pairs


def normalize_url(url: str) -> str:
    return url.rstrip("/")


def query_page_rows(service, site_url: str, days: int) -> tuple[dict[str, dict], date, date]:
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=max(days - 1, 0))
    body = {
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "dimensions": ["page"],
        "rowLimit": 25000,
    }
    rows = service.searchanalytics().query(siteUrl=site_url, body=body).execute().get("rows", [])

    by_page: dict[str, dict] = {}
    for row in rows:
        page = normalize_url(row.get("keys", [""])[0])
        by_page[page] = {
            "clicks": int(row.get("clicks", 0)),
            "impressions": int(row.get("impressions", 0)),
            "position": float(row.get("position", 0.0)),
        }
    return by_page, start, end


def build_baseline(guide_pairs: list[tuple[str, str]], by_page: dict[str, dict]) -> list[GuideMetric]:
    metrics: list[GuideMetric] = []
    for slug, url in guide_pairs:
        key = normalize_url(url)
        row = by_page.get(key)
        clicks = int(row["clicks"]) if row else 0
        impressions = int(row["impressions"]) if row else 0
        ctr = (clicks / impressions) if impressions else 0.0
        position = float(row["position"]) if row and impressions else None
        metrics.append(
            GuideMetric(
                slug=slug,
                url=url,
                clicks=clicks,
                impressions=impressions,
                ctr=ctr,
                position=position,
            )
        )
    return metrics


def write_csv(path: Path, metrics: list[GuideMetric]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["slug", "url", "clicks", "impressions", "ctr", "position"])
        for m in metrics:
            writer.writerow(
                [
                    m.slug,
                    m.url,
                    m.clicks,
                    m.impressions,
                    f"{m.ctr:.6f}",
                    "" if m.position is None else f"{m.position:.3f}",
                ]
            )


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> int:
    args = parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    service = build_service(args.credentials)
    effective_site_url = preferred_site_url(service, args.site_url)

    guide_pairs = list_guide_urls()
    by_page, start, end = query_page_rows(service, effective_site_url, args.days)
    metrics = build_baseline(guide_pairs, by_page)

    stamp = date.today().strftime("%Y%m%d")
    csv_path = out_dir / f"gsc-guide-baseline-{stamp}.csv"
    summary_path = out_dir / f"gsc-guide-baseline-summary-{stamp}.json"
    checkpoints_path = out_dir / "gsc-guide-checkpoints.json"

    write_csv(csv_path, metrics)

    total_clicks = sum(m.clicks for m in metrics)
    total_impressions = sum(m.impressions for m in metrics)
    avg_ctr = (total_clicks / total_impressions) if total_impressions else 0.0
    position_weight = sum((m.position or 0.0) * m.impressions for m in metrics)
    avg_position = (position_weight / total_impressions) if total_impressions else None
    active_guides = sum(1 for m in metrics if m.impressions > 0)

    summary = {
        "capturedAt": date.today().isoformat(),
        "effectiveSiteUrl": effective_site_url,
        "window": {
            "days": args.days,
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
        },
        "guideCount": len(metrics),
        "guidesWithImpressions": active_guides,
        "totals": {
            "clicks": total_clicks,
            "impressions": total_impressions,
            "ctr": round(avg_ctr, 6),
            "averagePosition": round(avg_position, 3) if avg_position is not None else None,
        },
        "files": {
            "csv": str(csv_path).replace("\\", "/"),
        },
    }
    write_json(summary_path, summary)

    today = date.today()
    checkpoints = {
        "baselineDate": today.isoformat(),
        "checkpoints": [
            {"name": "Day 7", "targetDate": (today + timedelta(days=7)).isoformat()},
            {"name": "Day 14", "targetDate": (today + timedelta(days=14)).isoformat()},
            {"name": "Day 21", "targetDate": (today + timedelta(days=21)).isoformat()},
        ],
        "baselineFiles": {
            "csv": str(csv_path).replace("\\", "/"),
            "summary": str(summary_path).replace("\\", "/"),
        },
    }
    write_json(checkpoints_path, checkpoints)

    print(f"[ok] Effective site URL: {effective_site_url}")
    print(f"[ok] Guide pages captured: {len(metrics)}")
    print(f"[ok] Guides with impressions: {active_guides}")
    print(f"[ok] Baseline CSV: {csv_path}")
    print(f"[ok] Summary JSON: {summary_path}")
    print(f"[ok] Checkpoints JSON: {checkpoints_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
