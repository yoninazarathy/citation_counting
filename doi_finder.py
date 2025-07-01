import requests
import time

# --- CONFIGURATION ---

API_KEY = "QQQQ-REPLACE" 

PAPER_TITLES = [
    "Spectrally negative Levy processes with Parisian reflection below and classical reflection above",
    "Affine processes on R_+^m x R^n and multiparameter time changes",
    "BRAVO for many-server QED systems",
    "Towards q-learning the Whittle index for restless bandits",
    "A series expansion formula of the scale matrix with applications in CUSUM",
    "Fixed confidence best arm identification in the Bayesian setting",
    "Wireless channel selection with restless bandits",
    "Mathematical engineering of deep learning",
    "Perfect sampling for Gibbs point processes using partial rejection sampling",
    "COMBSS: best subset selection via continuous optimization",
    "Nonzero-sum optimal stopping game with continuous vs. periodic exercise opportunities",
    "Levy bandits under Poissonian decision times",
    "Optimal periodic replenishment policies for spectrally positive Levy demand processes",
    "The value of information and efficient switching in channel selection",
    "Inventory control for spectrally positive Levy demand processes"
]

# --- END OF CONFIGURATION ---

S2_API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
OUTPUT_FILE = "dois.txt"

def find_and_save_dois():
    """Finds DOIs using the correct GET method and correct fields."""
    if not API_KEY or "YOUR_API_KEY" in API_KEY:
        print("ERROR: API key is missing.")
        return

    print("--- Starting DOI Finder (Final Corrected GET Version) ---")
    print(f"Processing {len(PAPER_TITLES)} clean paper titles...")
    
    headers = {'x-api-key': API_KEY}
    found_dois = set()
    
    for i, title in enumerate(PAPER_TITLES):
        print(f"\n({i+1}/{len(PAPER_TITLES)}) Searching for: '{title[:70]}...'")
        
        time.sleep(1.5)
        
        # We MUST use a GET request for this endpoint.
        # The query parameters are passed in the 'params' argument.
        params = {
            'query': title,
            'fields': 'externalIds,title' # This is the correct field name
        }
        
        try:
            response = requests.get(S2_API_URL, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('data'):
                first_result = data['data'][0]
                external_ids = first_result.get('externalIds', {})
                doi = external_ids.get('DOI') # Extract DOI from the nested dictionary
                
                if doi:
                    match_title = first_result.get('title', 'N/A')
                    print(f"  -> Found DOI: {doi} (Matched Title: {match_title})")
                    found_dois.add(doi)
                else:
                    print(f"  -> WARN: Found a matching paper but it has no DOI listed.")
            else:
                print(f"  -> WARN: No search results found for this title.")
                
        except requests.exceptions.HTTPError as e:
            print(f"  -> HTTP ERROR: An API error occurred: {e}")
        except Exception as e:
            print(f"  -> UNEXPECTED ERROR: {e}")
            
    if not found_dois:
        print("\nProcess complete. No DOIs were found.")
        return

    with open(OUTPUT_FILE, 'w') as f:
        for doi in sorted(list(found_dois)):
            f.write(f"{doi}\n")
            
    print("\n" + "="*50)
    print(f"SUCCESS: Saved {len(found_dois)} DOIs to '{OUTPUT_FILE}'")
    print("="*50)
    print("You can now run 'citation_analyzer.py'.")

if __name__ == "__main__":
    find_and_save_dois()