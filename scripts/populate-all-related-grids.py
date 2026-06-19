#!/usr/bin/env python3
"""Populate all empty related-grid elements across all guides."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTICLES = ROOT / "articles"

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
    topics = set()
    name_lower = guide_name.lower()
    for topic, keywords in TOPIC_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name_lower:
                topics.add(topic)
    return topics

def find_related_guides(guide_name: str) -> list[str]:
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
    parts = filename.replace("guide-", "").replace(".html", "").split("-")
    return " ".join(word.capitalize() for word in parts)

def populate_related_grid(guide_path: Path) -> tuple[bool, str]:
    """Populate any empty related-grid elements."""
    content = guide_path.read_text(encoding='utf-8')
    
    # Find all empty related-grid elements
    pattern = r'<div class="related-grid">\s*</div>'
    matches = list(re.finditer(pattern, content))
    
    if not matches:
        return False, "No empty related-grid found"
    
    # Get related guides
    related = find_related_guides(guide_path.name)
    if not related:
        return False, "No related guides found"
    
    # Build cards HTML
    cards_html = ""
    for guide_file in related:
        guide_url = guide_file.replace(".html", "")
        display_name = guide_display_name(guide_file)
        cards_html += f'          <a href="/articles/{guide_url}" class="related-card">{display_name}</a>\n'
    
    # Replace each empty grid
    new_content = content
    for match in reversed(matches):  # reverse to maintain position indices
        start, end = match.span()
        replacement = f'<div class="related-grid">\n{cards_html}        </div>'
        new_content = new_content[:start] + replacement + new_content[end:]
    
    guide_path.write_text(new_content, encoding='utf-8')
    return True, f"Populated {len(matches)} grid(s) with {len(related)} guides each"

def main():
    guides = sorted(ARTICLES.glob("guide-*.html"))
    
    print("=" * 70)
    print("POPULATING ALL EMPTY RELATED-GRID ELEMENTS")
    print("=" * 70)
    
    populated = 0
    skipped = 0
    
    for guide in guides:
        success, msg = populate_related_grid(guide)
        status = "✅" if success else "⏭️"
        print(f"{status} {guide.name:60} {msg}")
        if success:
            populated += 1
        else:
            skipped += 1
    
    print("\n" + "=" * 70)
    print(f"Result: {populated} guides populated, {skipped} skipped")
    print("=" * 70)

if __name__ == "__main__":
    main()
