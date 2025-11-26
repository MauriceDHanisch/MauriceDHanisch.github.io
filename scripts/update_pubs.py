import os
import re
from scholarly import scholarly
from datetime import datetime

# Configuration
AUTHOR_ID = 'c4EcLYQAAAAJ'
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'content')
ALL_FILE = os.path.join(OUTPUT_DIR, 'publications.html')
SELECTED_FILE = os.path.join(OUTPUT_DIR, 'selected_publications.html')

# List of publication indices to include in selected publications (1-indexed, based on chronological order)
# Edit this list to select which publications appear on the home page
SELECTED_INDICES = [1, 3, 4]  # e.g., [1, 3, 5] for 1st, 3rd, and 5th publications

def extract_year_from_text(text):
    """Extract a 4-digit year (2000-2099) from text like 'NeurIPS 2025' or 'arXiv:2411.16228'."""
    if not text:
        return None
    # Look for 4-digit years in 2000-2099 range
    match = re.search(r'20[0-9]{2}', text)
    if match:
        return match.group()
    return None

def get_pub_year(pub):
    """Get the publication year, trying multiple sources."""
    bib = pub['bib']
    year = bib.get('pub_year')
    
    # If year is valid, return it
    if year and year != 'N/A' and str(year).isdigit():
        return str(year)
    
    # Try to extract year from venue/journal name
    venue = bib.get('journal') or bib.get('conference') or bib.get('eprint') or ''
    year_from_venue = extract_year_from_text(venue)
    if year_from_venue:
        return year_from_venue
    
    # Try to extract from title
    title = bib.get('title', '')
    year_from_title = extract_year_from_text(title)
    if year_from_title:
        return year_from_title
    
    return 'N/A'

def get_pub_sort_key(pub, original_index=0):
    """Get a sortable date key from publication (year, original_index).
    Uses year only and preserves original retrieval order within each year.
    Google Scholar returns newer publications first, so lower index = newer."""
    year_str = get_pub_year(pub)
    year = int(year_str) if year_str != 'N/A' else 0
    # With reverse=True sorting: higher year first, then lower index first (newer first)
    # Negate index so that with reverse=True, lower original index comes first
    return (year, -original_index)

def fetch_publications(author_id):
    print(f"Fetching publications for author ID: {author_id}...")
    try:
        author = scholarly.search_author_id(author_id)
        author = scholarly.fill(author, sections=['publications'])
        return author['publications']
    except Exception as e:
        print(f"Error fetching publications: {e}")

def format_author_name(name):
    """
    Ensures initials have dots.
    e.g. "M Hanisch" -> "M. Hanisch"
    e.g. "M. D. Hanisch" -> "M. D. Hanisch" (no change)
    """
    parts = name.split()
    new_parts = []
    for part in parts:
        if len(part) == 1 and part.isalpha():
            new_parts.append(f"{part}.")
        else:
            new_parts.append(part)
    return " ".join(new_parts)

def format_publication(pub):
    # Extract details (publications are already filled in main())
    bib = pub['bib']
    title = bib.get('title', 'Untitled')
    year = get_pub_year(pub)  # Use the smart year extraction
    
    # Author
    authors = bib.get('author', 'Unknown Authors')
    if isinstance(authors, list):
        authors = ", ".join(authors)
    elif isinstance(authors, str):
        # sometimes it's already a string, but we want to ensure consistency
        pass
    
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
        # Try to find institution name from bib data
        institution = bib.get('school') or bib.get('institution') or bib.get('publisher') or None
        if institution:
            venue = f"Thesis, {institution}"
        elif venue == 'N/A':
            venue = "Thesis"
    elif "smt" in venue_lower:
        badge = "Talk"
        venue = "Invited Talk at APS March Meeting"  # Override venue for SMT
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
    elif venue == 'N/A':
        # If venue is unknown, check if it might be a thesis based on single author
        num_authors = len(authors.split(", ")) if isinstance(authors, str) else len(authors)
        if num_authors == 1:
            badge = "Thesis"
            # Try to find institution from bib
            institution = bib.get('school') or bib.get('institution') or bib.get('publisher') or None
            if institution:
                venue = f"Thesis, {institution}"
            else:
                venue = "Thesis"

    # Format all author names
    # First replace " and " with ", " to normalize
    if " and " in authors:
        authors = authors.replace(" and ", ", ")
    
    author_list = authors.split(", ")
    formatted_authors = [format_author_name(a) for a in author_list]
    
    # Join with commas, but use "and" before the last author
    if len(formatted_authors) > 1:
        authors = ", ".join(formatted_authors[:-1]) + ", and " + formatted_authors[-1]
    else:
        authors = formatted_authors[0] if formatted_authors else "Unknown Authors"

    # Normalize name variations to "Maurice D. Hanisch"
    name_variations = ["Maurice Hanisch", "M. Hanisch", "M. D. Hanisch"]
    for variant in name_variations:
        if variant in authors:
            authors = authors.replace(variant, "Maurice D. Hanisch")

    # Bold and underline author name
    if "Maurice D. Hanisch" in authors:
        authors = authors.replace("Maurice D. Hanisch", "<u>Maurice D. Hanisch</u>")

    return f"""
  <li class="pub-row">
    <div class="pub-badges">
      <span class="badge-main">{badge}</span>
    </div>
    <div class="pub-content">
      <div class="pub-title">{title}</div>
      <div class="pub-authors">{authors}</div>
      <div class="pub-venue"><em>{venue}</em>, {year}.</div>
      <div class="pub-buttons">
        <a href="{url}" class="btn" target="_blank">PDF</a>
        <a href="https://scholar.google.com/citations?view_op=view_citation&hl=en&user={AUTHOR_ID}&citation_for_view={pub.get('author_pub_id')}" class="btn" target="_blank">Scholar</a>
      </div>
    </div>
  </li>"""

def generate_html(pubs, limit=None, selected_indices=None):
    html_list = ['<ol class="pubs">']
    
    # Sort by year descending, preserving original order within each year
    indexed_pubs = [(i, pub) for i, pub in enumerate(pubs)]
    sorted_indexed = sorted(indexed_pubs, key=lambda x: get_pub_sort_key(x[1], x[0]), reverse=True)
    sorted_pubs = [pub for _, pub in sorted_indexed]
    
    # If selected_indices provided, filter to only those publications
    if selected_indices:
        filtered_pubs = []
        for idx in selected_indices:
            if 1 <= idx <= len(sorted_pubs):
                filtered_pubs.append(sorted_pubs[idx - 1])  # Convert to 0-indexed
        sorted_pubs = filtered_pubs
    
    current_year = None
    count = 0
    for pub in sorted_pubs:
        if limit and count >= limit:
            break
        
        # Add year divider if year changes (use smart year extraction)
        pub_year = get_pub_year(pub)
        if pub_year != current_year:
            current_year = pub_year
            html_list.append(f'\n  <li class="year-divider"><span>{current_year}</span></li>')
        
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
    
    # Fill all publications first to get complete data for sorting
    print("Filling publication details...")
    filled_pubs = []
    for pub in pubs:
        try:
            filled_pub = scholarly.fill(pub)
            filled_pubs.append(filled_pub)
        except Exception as e:
            print(f"Warning: Could not fill publication data: {e}")
            filled_pubs.append(pub)
    
    # Print publication list with indices for reference
    # Sort by year descending, preserving original order within each year
    indexed_pubs = [(i, pub) for i, pub in enumerate(filled_pubs)]
    sorted_indexed = sorted(indexed_pubs, key=lambda x: get_pub_sort_key(x[1], x[0]), reverse=True)
    sorted_pubs = [pub for _, pub in sorted_indexed]
    
    print("\nPublication indices (for SELECTED_INDICES):")
    for i, pub in enumerate(sorted_pubs, 1):
        title = pub['bib'].get('title', 'Untitled')[:60]
        year = get_pub_year(pub)  # Use smart year extraction
        print(f"  {i}. [{year}] {title}...")

    # Generate All Publications
    print(f"\nUpdating {ALL_FILE}...")
    all_html = generate_html(filled_pubs)
    with open(ALL_FILE, 'w', encoding='utf-8') as f:
        f.write(all_html)

    # Generate Selected Publications based on SELECTED_INDICES
    print(f"Updating {SELECTED_FILE}...")
    selected_html = generate_html(filled_pubs, selected_indices=SELECTED_INDICES)
    with open(SELECTED_FILE, 'w', encoding='utf-8') as f:
        f.write(selected_html)

    print("\nDone!")
    print(f"Selected publications: indices {SELECTED_INDICES}")
    print("Edit SELECTED_INDICES in update_pubs.py to change which publications are featured.")

if __name__ == "__main__":
    main()
