#!/usr/bin/env python3
"""Add internal guide links to all guides lacking them.

Analyzes guide titles and content to find related guides,
then inserts a related guides section.
"""

import re
from pathlib import Path
from collections import defaultdict

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

def find_related_guides(guide_name: str) -> list[tuple[str, int]]:
    """Find related guides, return [(guide_file, score), ...]."""
    all_guides = sorted(ARTICLES.glob("guide-*.html"))
    current_topics = extract_topics(guide_name)
    
    related = []
    for other_guide in all_guides:
        if other_guide.name == guide_name:
            continue
        other_topics = extract_topics(other_guide.name)
        # Score = number of matching topics
        score = len(current_topics & other_topics)
        if score > 0:
            related.append((other_guide.name, score))
    
    # Sort by score descending, take top 3
    related.sort(key=lambda x: -x[1])
    return related[:3]

def guide_display_name(filename: str) -> str:
    """Convert guide filename to display name."""
    # guide-sharepoint-permissions.html -> SharePoint Permissions
    parts = filename.replace("guide-", "").replace(".html", "").split("-")
    return " ".join(word.capitalize() for word in parts)

def has_related_links_populated(content: str) -> bool:
    """Check if guide already has populated related-grid."""
    return bool(re.search(r'<div class="related-grid">.*?<a.*?href.*?articles.*?guide', content, re.DOTALL))

def add_related_guides_section(guide_path: Path) -> tuple[bool, str]:
    """Populate related guides in existing related-grid."""
    content = guide_path.read_text(encoding='utf-8')
    
    if has_related_links_populated(content):
        return False, "Related grid already populated"
    
    related = find_related_guides(guide_path.name)
    if not related:
        return False, "No related guides found"
    
    # Build related guide cards for the grid
    cards_html = ""
    for guide_file, _ in related:
        guide_url = guide_file.replace(".html", "")
        display_name = guide_display_name(guide_file)
        cards_html += f'          <a href="/articles/{guide_url}" class="related-card">{display_name}</a>\n'
    
    # Replace empty related-grid with populated one
    pattern = r'(<div class="related-grid">)\s*(</div>)'
    replacement = f'\\1\n{cards_html}          \\2'
    new_content = re.sub(pattern, replacement, content)
    
    if new_content == content:
        return False, "Could not find related-grid element"
    
    guide_path.write_text(new_content, encoding='utf-8')
    return True, f"Populated {len(related)} related guides"

def main():
    guides = sorted(ARTICLES.glob("guide-*.html"))
    
    print("=" * 70)
    print("ADDING INTERNAL GUIDE LINKS TO ALL GUIDES")
    print("=" * 70)
    
    added = 0
    skipped = 0
    
    for guide in guides:
        success, msg = add_related_guides_section(guide)
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
