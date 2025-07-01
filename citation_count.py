import requests
import time

# --- CONFIGURATION ---
API_KEY = "QQQQ-REPLACE" 

# The list of your team members to exclude from citation counts.
TEAM_MEMBERS = [
    "Yamazaki Kazutoshi",
    "Sarat Moka",
    "Yoni Nazarathy",
    "José Luis Pérez Garmendia"
]

# The input file containing one DOI per line.
DOI_FILE = "dois.txt"

# --- END OF CONFIGURATION ---

S2_API_URL = "https://api.semanticscholar.org/graph/v1"
# Create a normalized set of team member names for fast, case-insensitive checking.
TEAM_MEMBER_NAMES_NORMALIZED = {name.lower() for name in TEAM_MEMBERS}

def read_dois_from_file(filename):
    """Reads a list of DOIs from a text file."""
    try:
        with open(filename, 'r') as f:
            # Read all non-empty lines and strip any extra whitespace
            dois = [line.strip() for line in f if line.strip()]
        return dois
    except FileNotFoundError:
        print(f"ERROR: The file '{filename}' was not found in this folder.")
        print("Please make sure 'dois.txt' exists.")
        return []

def get_paper_details(doi, headers):
    """Fetches paper details from Semantic Scholar API using its DOI."""
    paper_id_query = "DOI:" + doi
    # Request the title and the authors of every paper in the citation list
    params = {'fields': 'title,citations.authors'}
    try:
        response = requests.get(
            f"{S2_API_URL}/paper/{paper_id_query}",
            params=params,
            headers=headers
        )
        response.raise_for_status() # Raises an exception for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"  -> ERROR: Could not fetch data for {doi}: {e}")
        return None

def is_team_citation(citing_paper_authors):
    """Checks if any author of a citing paper is in the team."""
    for author in citing_paper_authors:
        # Check if the author's name exists in our normalized set of team members
        if author.get('name', '').lower() in TEAM_MEMBER_NAMES_NORMALIZED:
            return True # It's a team citation
    return False # It's an external citation

def analyze_citations():
    """Main function to read DOIs and analyze their citations."""
    if not API_KEY or "YOUR_API_KEY" in API_KEY:
        print("ERROR: Please add your Semantic Scholar API key to the script.")
        return
        
    print(f"--- Starting Citation Analyzer (with API key) ---")
    team_paper_dois = read_dois_from_file(DOI_FILE)
    
    if not team_paper_dois:
        return

    print(f"Analyzing {len(team_paper_dois)} papers from '{DOI_FILE}'...")
    print("-" * 50)
    
    headers = {'x-api-key': API_KEY}
    grand_total_citations = 0
    grand_total_external_citations = 0
    results = {}

    for i, doi in enumerate(team_paper_dois):
        print(f"\n({i+1}/{len(team_paper_dois)}) Processing DOI: {doi}")
        
        time.sleep(1.5) # Be a polite user of the API
        
        paper_data = get_paper_details(doi, headers)
        
        if not paper_data:
            print("  -> Skipping this paper due to error.")
            continue
            
        paper_title = paper_data.get('title', 'N/A')
        citations = paper_data.get('citations', [])
        paper_total_citations = len(citations)
        paper_external_citations = 0

        # Loop through every paper that cites our paper
        for citing_paper in citations:
            citing_authors = citing_paper.get('authors', [])
            if not is_team_citation(citing_authors):
                paper_external_citations += 1
        
        print(f"  -> Title: {paper_title}")
        print(f"  -> Total citations found: {paper_total_citations}")
        print(f"  -> External (non-team) citations: {paper_external_citations}")

        # Store results for the final summary table
        results[doi] = {
            'title': paper_title, 
            'total': paper_total_citations, 
            'external': paper_external_citations
        }
        
        # Add this paper's counts to the grand totals
        grand_total_citations += paper_total_citations
        grand_total_external_citations += paper_external_citations

    # --- Print the Final Report ---
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE: SUMMARY REPORT")
    print("=" * 80)
    
    # Print a summary table with aligned columns
    print(f"{'DOI':<30} | {'Total Cites':<12} | {'External Cites':<15} | {'Title'}")
    print(f"{'-'*30} | {'-'*12} | {'-'*15} | {'-'*40}")
    for doi, data in sorted(results.items()):
        # Truncate long titles for neatness
        title_short = (data['title'][:37] + '...') if len(data['title']) > 40 else data['title']
        print(f"{doi:<30} | {data['total']:<12} | {data['external']:<15} | {title_short}")
        
    print("-" * 80)
    print(f"GRAND TOTAL (across {len(team_paper_dois)} papers):")
    print(f"  Total Citations in Semantic Scholar: {grand_total_citations}")
    print(f"  Total External (Non-Team) Citations: {grand_total_external_citations}")
    print("-" * 80)

if __name__ == "__main__":
    analyze_citations()