#!/usr/bin/env python3
"""Add final consultation CTA to guides that lack it.

Adds OceanCloud consultation CTA before closing </section> tag
at the end of each guide's main content.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTICLES = ROOT / "articles"

# Template for final CTA section
FINAL_CTA = '''
      <section class="guide-final-cta reveal">
        <div class="cta-box">
          <div class="cta-icon">💬</div>
          <div class="cta-content">
            <h3>Ready to transform your SharePoint and Microsoft 365 environment?</h3>
            <p>OceanCloud specialises in SharePoint consulting, M365 migration, Power Platform solutions, and enterprise governance. Let's discuss how we can help.</p>
            <a href="/contact" class="btn-primary">Book a Free 60-Minute Consultation ➜</a>
          </div>
        </div>
      </section>
'''

def has_final_cta(content: str) -> bool:
    """Check if guide already has a final consultation CTA."""
    return bool(re.search(r'consultation|contact.*free|book.*consultation', content[-1000:], re.IGNORECASE))

def add_final_cta(guide_path: Path) -> tuple[bool, str]:
    """Add final CTA before last closing section tag."""
    content = guide_path.read_text(encoding='utf-8')
    
    if has_final_cta(content):
        return False, "Already has final CTA"
    
    # Find the last </section> tag in the main content area (before footer)
    # Look for it before the footer/related-cards section
    footer_match = re.search(r'<footer>|<aside|<div class="guide-footer"', content)
    footer_pos = footer_match.start() if footer_match else len(content)
    
    # Find the last </section> before footer
    content_before_footer = content[:footer_pos]
    section_matches = list(re.finditer(r'</section>', content_before_footer))
    
    if not section_matches:
        return False, "No closing section tag found"
    
    last_section_pos = section_matches[-1].end()
    
    # Insert CTA after last section
    new_content = content[:last_section_pos] + FINAL_CTA + content[last_section_pos:]
    
    guide_path.write_text(new_content, encoding='utf-8')
    return True, "Final CTA added"

def main():
    guides = sorted(ARTICLES.glob("guide-*.html"))
    
    print("=" * 70)
    print("ADDING FINAL CONSULTATION CTA TO ALL GUIDES")
    print("=" * 70)
    
    added = 0
    skipped = 0
    
    for guide in guides:
        success, msg = add_final_cta(guide)
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
