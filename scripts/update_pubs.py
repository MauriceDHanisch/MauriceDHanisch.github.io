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
    
    # Authors (scholarly often gives a string or list, we try to format it)
    # Note: scholarly 'bib' might not have full author list unless filled, 
    # but filling every pub is slow/rate-limited. We'll use what's available.
    # Often 'citation' has more info if we fill, but let's try basic first.
    # For better author list, we might need to fill each pub, but that's risky for rate limits.
    # We will use the 'bib' data which usually contains 'author' string.
    authors = bib.get('author', 'Unknown Authors')
    
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
    if "thesis" in title.lower() or "thesis" in venue.lower():
        badge = "Thesis"
    elif "preprint" in venue.lower() or "arxiv" in venue.lower():
        badge = "Preprint"

    return f"""
  <li class="pub">
    <div class="badge">{badge}</div>
    <div class="title">{title}</div>
    <div class="meta">{authors} · {venue} · {year}</div>
    <div class="links"><a href="{url}" target="_blank">View Paper</a></div>
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
