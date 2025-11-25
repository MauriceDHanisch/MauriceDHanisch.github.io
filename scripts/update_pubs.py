import os
from scholarly import scholarly
from datetime import datetime

# Configuration
AUTHOR_ID = 'c4EcLYQAAAAJ'
SELECTED_COUNT = 5
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'content')
SELECTED_FILE = os.path.join(OUTPUT_DIR, 'selected_publications.html')
ALL_FILE = os.path.join(OUTPUT_DIR, 'publications.html')

def fetch_publications(author_id):
    print(f"Fetching publications for author ID: {author_id}...")
    try:
        author = scholarly.search_author_id(author_id)
        author = scholarly.fill(author, sections=['publications'])
        return author['publications']
    except Exception as e:
        print(f"Error fetching publications: {e}")
        return []

def format_publication(pub):
    # Extract details
    bib = pub.get('bib', {})
    title = bib.get('title', 'Untitled')
    year = bib.get('pub_year', 'N/A')
    
    # Author
    # scholarly 'bib' usually contains 'author' string like "M Hanisch, ..."
    # or sometimes it's a list in 'author' field of the pub object itself
    authors = bib.get('author', 'Unknown Authors')
    if isinstance(authors, list):
        authors = ", ".join(authors)
    
    # Clean up authors string if needed (sometimes has 'and' or different separators)
    authors = authors.replace(" and ", ", ")
    
    # Venue/Journal
    venue = bib.get('journal') or bib.get('conference') or bib.get('eprint') or 'N/A'
    
    # Link
    # scholarly provides 'pub_url' sometimes, or we can link to scholar citation
    url = pub.get('pub_url')
    if not url:
        # Try to find eprint url if available in bib
        url = bib.get('eprint_url') or bib.get('url')
    
    if not url:
        # Fallback to Google Scholar citation link
        url = f"https://scholar.google.com/citations?view_op=view_citation&hl=en&user={AUTHOR_ID}&citation_for_view={pub.get('author_pub_id')}"

    # Badge logic (simple heuristic)
    badge = "Paper"
    venue_lower = venue.lower()
    if "thesis" in title.lower() or "thesis" in venue_lower:
        badge = "Thesis"
    elif "neurips" in venue_lower:
        badge = "NeurIPS"
    elif "iclr" in venue_lower:
        badge = "ICLR"
    elif "icml" in venue_lower:
        badge = "ICML"
    elif "cvpr" in venue_lower:
        badge = "CVPR"
    elif "arxiv" in venue_lower:
        badge = "Preprint"

    # Bold author name
    # Try different variations of the name
    my_names = ["Maurice Hanisch", "M. Hanisch", "M Hanisch"]
    for name in my_names:
        if name in authors:
            authors = authors.replace(name, f"<b>{name}</b>")
            break # Only replace one instance/variation

    return f"""
  <li class="pub-row">
    <div class="pub-badges">
      <span class="badge-main">{badge}</span>
    </div>
    <div class="pub-content">
      <div class="pub-title">{title}</div>
      <div class="pub-authors">{authors}</div>
      <div class="pub-venue">In <em>{venue}</em>, {year}.</div>
      <div class="pub-buttons">
        <a href="{url}" class="btn" target="_blank">PDF</a>
        <a href="https://scholar.google.com/citations?view_op=view_citation&hl=en&user={AUTHOR_ID}&citation_for_view={pub.get('author_pub_id')}" class="btn" target="_blank">Scholar</a>
      </div>
    </div>
  </li>"""

def generate_html(pubs, limit=None):
    html_list = ['<ol class="pubs">']
    
    # Sort by year descending, then title
    sorted_pubs = sorted(pubs, key=lambda x: (int(x['bib'].get('pub_year', 0)), x['bib'].get('title', '')), reverse=True)
    
    count = 0
    for pub in sorted_pubs:
        if limit and count >= limit:
            break
        html_list.append(format_publication(pub))
        count += 1
        
    html_list.append('</ol>')
    return '\n'.join(html_list)

def main():
    pubs = fetch_publications(AUTHOR_ID)
    if not pubs:
        print("No publications found or error occurred.")
        return

    print(f"Found {len(pubs)} publications.")

    # Generate Selected Publications
    print(f"Updating {SELECTED_FILE}...")
    selected_html = generate_html(pubs, limit=SELECTED_COUNT)
    with open(SELECTED_FILE, 'w', encoding='utf-8') as f:
        f.write(selected_html)

    # Generate All Publications
    print(f"Updating {ALL_FILE}...")
    all_html = generate_html(pubs)
    with open(ALL_FILE, 'w', encoding='utf-8') as f:
        f.write(all_html)

    print("Done!")

if __name__ == "__main__":
    main()
