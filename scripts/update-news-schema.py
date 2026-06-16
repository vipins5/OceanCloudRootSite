#!/usr/bin/env python3
"""
Batch update all news articles to include mainEntityOfPage in Article JSON-LD.
This fixes older news articles that were generated before mainEntityOfPage was added.
"""

import re
from pathlib import Path

ARTICLES_DIR = Path(__file__).parent.parent / "articles"

def update_article_schema(html_content):
    """
    Add mainEntityOfPage to Article JSON-LD if missing.
    """
    # Find all Article blocks in the JSON-LD
    article_pattern = r'(\{\s*"@type":\s*"Article"[^}]*?"url":\s*"([^"]+)"[^}]*?"datePublished")'
    
    def replace_article(match):
        block = match.group(0)
        url = match.group(2)
        
        # Check if mainEntityOfPage already exists
        if '"mainEntityOfPage"' in block:
            return block  # Already has mainEntityOfPage
        
        # Insert mainEntityOfPage after "url": "{canonical}"
        new_block = block.replace(
            f'"url": "{url}",',
            f'"url": "{url}",\n        "mainEntityOfPage": "{url}",'
        )
        return new_block
    
    updated_content = re.sub(article_pattern, replace_article, html_content)
    return updated_content

# Process all news articles
news_files = list(ARTICLES_DIR.glob("news-*.html"))
print(f"Found {len(news_files)} news articles to process…")

updated_count = 0
for article_file in sorted(news_files):
    content = article_file.read_text(encoding="utf-8")
    updated_content = update_article_schema(content)
    
    if content != updated_content:
        article_file.write_text(updated_content, encoding="utf-8")
        updated_count += 1
        print(f"  ✓ {article_file.name}")
    else:
        print(f"  - {article_file.name} (already updated)")

print(f"\n[ok] Updated {updated_count} article(s) with mainEntityOfPage.")
