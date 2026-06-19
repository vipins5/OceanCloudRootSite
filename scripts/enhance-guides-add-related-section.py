#!/usr/bin/env python3
"""Add related-section to guides that lack it."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTICLES = ROOT / "articles"

# Topic keywords for matching
TOPIC_KEYWORDS = {
    "permissions": ["permission", "access", "auth", "role"],
    "sharepoint": ["sharepoint", "site", "library", "list"],
    "power-automate": ["power automate", "workflow", "flow", "automation"],
    "power-apps": ["power apps", "canvas app", "model app"],
    "teams": ["teams", "channel", "chat"],
    "migration": ["migration", "migrate", "moving"],
    "security": ["security", "compliance", "dlp", "sensitivity", "entra"],
    "copilot": ["copilot", "ai", "copilot studio"],
    "m365": ["m365", "microsoft 365", "office 365"],
    "microsoft-graph": ["graph", "rest api", "http request"],
    "pnp": ["pnp", "powershell", "pnp-powershell"],
}

def extract_topics(guide_name: str) -> set[str]:
    """Extract topics from guide filename."""
    topics = set()
    name_lower = guide_name.lower()
    for topic, keywords in TOPIC_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name_lower:
                topics.add(topic)
    return topics

def find_related_guides(guide_name: str) -> list[str]:
    """Find related guides, return list of filenames."""
    all_guides = sorted(ARTICLES.glob("guide-*.html"))
    current_topics = extract_topics(guide_name)
    
    related = []
    for other_guide in all_guides:
        if other_guide.name == guide_name:
            continue
        other_topics = extract_topics(other_guide.name)
        score = len(current_topics & other_topics)
        if score > 0:
            related.append((other_guide.name, score))
    
    related.sort(key=lambda x: -x[1])
    return [name for name, _ in related[:3]]

def guide_display_name(filename: str) -> str:
    """Convert filename to display name."""
    parts = filename.replace("guide-", "").replace(".html", "").split("-")
    return " ".join(word.capitalize() for word in parts)

def has_related_section(content: str) -> bool:
    """Check if guide has related-section or related-grid."""
    return bool(re.search(r'related-section|related-grid', content))

def add_related_section(guide_path: Path) -> tuple[bool, str]:
    """Add related-section before final CTA or footer."""
    content = guide_path.read_text(encoding='utf-8')
    
    if has_related_section(content):
        return False, "Already has related-section"
    
    related = find_related_guides(guide_path.name)
    if not related:
        return False, "No related guides found"
    
    # Build related-section HTML
    cards = ""
    for guide_file in related:
        guide_url = guide_file.replace(".html", "")
        display_name = guide_display_name(guide_file)
        cards += f'          <a href="/articles/{guide_url}" class="related-card">{display_name}</a>\n'
    
    related_section = f'''      <div class="related-section">
        <p class="related-label">Related Guides</p>
        <div class="related-grid">
{cards}        </div>
      </div>
'''
    
    # Try to insert before final CTA
    final_cta_match = re.search(r'<section class="guide-final-cta', content)
    if final_cta_match:
        insert_pos = final_cta_match.start()
        new_content = content[:insert_pos] + related_section + '\n' + content[insert_pos:]
    else:
        # Fallback: insert before footer
        footer_match = re.search(r'<!-- ===== FOOTER ===== -->', content)
        if footer_match:
            insert_pos = footer_match.start()
            new_content = content[:insert_pos] + related_section + '\n' + content[insert_pos:]
        else:
            return False, "Could not find insertion point"
    
    guide_path.write_text(new_content, encoding='utf-8')
    return True, f"Added related-section with {len(related)} guides"

def main():
    guides = sorted(ARTICLES.glob("guide-*.html"))
    
    print("=" * 70)
    print("ADDING RELATED-SECTION TO GUIDES WITHOUT IT")
    print("=" * 70)
    
    added = 0
    skipped = 0
    
    for guide in guides:
        success, msg = add_related_section(guide)
        status = "✅" if success else "⏭️"
        print(f"{status} {guide.name:60} {msg}")
        if success:
            added += 1
        else:
            skipped += 1
    
    print("\n" + "=" * 70)
    print(f"Result: {added} guides updated, {skipped} skipped")
    print("=" * 70)

if __name__ == "__main__":
    main()
