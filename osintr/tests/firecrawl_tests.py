from firecrawl import FirecrawlApp
from dotenv import load_dotenv
from pprint import pprint
import os

# Perform Firecrawl API test
url = "https://example.com/"
def main(url):
    # Load API key
    load_dotenv()

    # Perform test scrape
    scrape_results = []
    try:
        scraper = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))
        scrape_result = scraper.scrape_url(url, params={'formats': ['markdown', 'links']})
        scrape_results.append(scrape_result)
    except Exception as err:
        print("Oupsie! Something broke: ", err)

    pprint(scrape_results)

if __name__ == '__main__':
    main(url)