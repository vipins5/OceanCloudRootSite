#!/usr/bin/env python3
"""Audit guides against dual monetization plan Phase 1 requirements.

Phase 1 checklist per article:
1. One clear search intent (in title/description/meta)
2. One H1
3. Practical steps/checklist
4. Internal links to related guides
5. One contextual service CTA
6. Final consultation CTA
7. Comments enabled
8. Sitemap entry

Generates a compliance report and improvement recommendations.
"""

import re
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
ARTICLES = ROOT / "articles"
SITEMAP_XML = ROOT / "sitemap.xml"

def check_h1(content: str) -> bool:
    """Check for exactly one H1 tag."""
    h1_count = len(re.findall(r"<h1[^>]*>.*?</h1>", content, re.DOTALL))
    return h1_count == 1

def check_steps_checklist(content: str) -> bool:
    """Check for procedural steps or checklist (h2/h3 with ol/ul or checklist markers)."""
    has_ordered_list = bool(re.search(r"<ol[^>]*>.*?</ol>", content, re.DOTALL))
    has_h2_h3 = bool(re.search(r"<h[23][^>]*>.*?</h[23]>", content, re.DOTALL))
    return has_ordered_list and has_h2_h3

def check_internal_links(content: str) -> bool:
    """Check for at least 2 internal guide links (various formats)."""
    # Look for links with different href patterns
    patterns = [
        r'href=["\'](?:/articles/)?guide-[a-z-]+(?:\.html)?["\']',  # /articles/guide-* or guide-*
        r'href=["\']#guide-',  # anchor links
    ]
    matches = set()
    for pattern in patterns:
        found = re.findall(pattern, content)
        matches.update(found)
    return len(matches) >= 2

def check_contextual_cta(content: str) -> bool:
    """Check for contextual service CTA (in-article call-to-action)."""
    cta_patterns = [
        r'OceanCloud can help',
        r'Book a .+? call',
        r'Get a .+? assessment',
        r'Contact OceanCloud',
        r'consultation',
    ]
    for pattern in cta_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    return False

def check_final_consultation_cta(content: str) -> bool:
    """Check for final consultation CTA anywhere in content."""
    # Check for the CTA section that was added
    return bool(re.search(
        r'guide-final-cta|Ready to transform.*consultation',
        content,
        re.IGNORECASE | re.DOTALL
    ))

def check_comments_enabled(content: str) -> bool:
    """Check for comments section markup."""
    return bool(re.search(r'comments|giscus|utterances', content, re.IGNORECASE))

def check_sitemap_entry(guide_path: str) -> bool:
    """Check if guide URL is in sitemap.xml."""
    if not SITEMAP_XML.exists():
        return False
    guide_name = guide_path.stem
    guide_url = f"/articles/{guide_name}"
    sitemap = SITEMAP_XML.read_text(encoding='utf-8')
    return guide_url in sitemap

def audit_guides():
    """Audit all guides in articles/ directory."""
    guides = sorted(ARTICLES.glob("guide-*.html"))
    
    results = {
        "total": len(guides),
        "passed": 0,
        "guides": [],
    }
    
    criteria_scores = defaultdict(lambda: {"pass": 0, "fail": 0})
    
    print("=" * 80)
    print("MONETIZATION PLAN PHASE 1 AUDIT: GUIDE COMPLIANCE")
    print("=" * 80)
    print(f"\nTotal guides found: {results['total']}\n")
    
    for guide in guides:
        content = guide.read_text(encoding='utf-8')
        
        checks = {
            "h1": check_h1(content),
            "steps_checklist": check_steps_checklist(content),
            "internal_links": check_internal_links(content),
            "contextual_cta": check_contextual_cta(content),
            "final_consultation_cta": check_final_consultation_cta(content),
            "comments_enabled": check_comments_enabled(content),
            "sitemap_entry": check_sitemap_entry(guide),
        }
        
        passed = sum(checks.values())
        total = len(checks)
        
        for criterion, result in checks.items():
            if result:
                criteria_scores[criterion]["pass"] += 1
            else:
                criteria_scores[criterion]["fail"] += 1
        
        compliant = all(checks.values())
        if compliant:
            results["passed"] += 1
        
        results["guides"].append({
            "file": guide.name,
            "passed": passed,
            "total": total,
            "compliant": compliant,
            "checks": checks,
        })
        
        status = "✅ PASS" if compliant else f"⚠️  FAIL ({passed}/{total})"
        print(f"{status} — {guide.name}")
        if not compliant:
            missing = [k for k, v in checks.items() if not v]
            print(f"      Missing: {', '.join(missing)}")
    
    print("\n" + "=" * 80)
    print("CRITERIA SUMMARY")
    print("=" * 80)
    for criterion, scores in sorted(criteria_scores.items()):
        pct = 100 * scores["pass"] / (scores["pass"] + scores["fail"]) if (scores["pass"] + scores["fail"]) > 0 else 0
        print(f"{criterion:30} {scores['pass']:3}/{results['total']:3} ({pct:5.1f}%)")
    
    print("\n" + "=" * 80)
    print(f"OVERALL: {results['passed']}/{results['total']} guides fully compliant ({100*results['passed']/results['total']:.1f}%)")
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    audit_guides()
