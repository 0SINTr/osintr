from langchain_community.utilities import GoogleSerperAPIWrapper
from firecrawl import FirecrawlApp
from dotenv import load_dotenv
from requests.exceptions import HTTPError
import json

def google_search_function(target):
    print(f"\nRunning search for target: {target}")
    
    # Perform a verbatim Google search (tbs value) and return 20 results (in line with Firecrawl's Hobby paid plan of 20 scrapes/min)
    search = GoogleSerperAPIWrapper(tbs="li:1", k=20)

    try:
        results = search.results(target)  # Pass the query to the SerpAPIWrapper's search method

        # Create and save the JSON file with initial search results
        path = r"osint_data/google_search.json"
        with open(path, "w") as outfile:
            json.dump(results['organic'], outfile)
        
        print(f"\nDONE. Check {path}.\n")

    except Exception as e:
        # Handle any errors that occur during the search
        print(f"Error during Google search: {str(e)}")
        return None
    
    # Extracting all the links from search results
    links = []
    for entry in results['organic']:
        links.append(entry['link'])

    try:
        # Initialize the Firecrawl scraper
        for index, url in enumerate(links):
            scraper = FirecrawlApp()
            scrape_result = scraper.scrape_url(url, params={'formats': ['markdown', 'html']})

            path = r"osint_data/"
            with open(path + "scrape" + str(index) + ".md", "w") as outfile:
                outfile.write(scrape_result)
    
    except HTTPError as e:
        pass


# Load API keys from .env
load_dotenv()

# Run the Google search function
google_search_function("Mihai Catalin Teodosiu")