from langchain_community.utilities import GoogleSerperAPIWrapper
from firecrawl import FirecrawlApp
from dotenv import load_dotenv
from requests.exceptions import HTTPError
import requests
import time
import json
import sys
import os
import re

# Function to perform the Google search and scrape each page related to the target
def google_search_function(target):
    print(f"\nRunning search for target: {target}")
    
    # Check if osint_data directory exists, if not create it for the specified target
    dir_path = "osint_data_" + ''.join(char for char in str(target) if char.isalnum())
    if not os.path.exists(path=dir_path):
        os.makedirs(dir_path)

    # Perform a verbatim Google search (tbs value) and return 20 results (in line with Firecrawl's Hobby paid plan of 20 scrapes/min)
    search = GoogleSerperAPIWrapper(tbs="li:1", k=20)

    try:
        # Pass the query to the SerpAPIWrapper's search method
        results = search.results(target)

        # Create and save the JSON file with initial search results
        with open(dir_path + '/google_search.json', 'w') as outfile:
            json.dump(results['organic'], outfile)
        
        print(f"\nDONE. Check {dir_path}.\n")

    except Exception as e:
        # Handle any errors that occur during the search
        print(f"Error during Google search: {str(e)}")
        sys.exit("\nQuitting.")
    
    # Introducing sleep for 5 seconds
    time.sleep(5)

    # Creating new directory for scraping results
    scraped_path = dir_path + '/scraped'
    if not os.path.exists(path=scraped_path):
        os.makedirs(scraped_path)

    # Extracting all the links from search results
    links = []
    noScrape_links = []
    for entry in results['organic']:
        links.append(entry['link'])

    print("Starting to scrape.\nForbidden URLs will be added to noScrapeLinks.txt\n")

    # Initialize the Firecrawl scraper
    for index, url in enumerate(links):
        try:
            scraper = FirecrawlApp()
            scrape_result = scraper.scrape_url(url, params={'formats': ['markdown', 'html', 'screenshot'], 'waitFor':3000, 'timeout':10000})

            # Write the scrape results to separate files
            with open(scraped_path + '/scrape' + str(index + 1) + '.md', 'w', encoding='utf-8') as outfile:
                outfile.write(str(scrape_result))

            print('- scrape' + str(index + 1) + '.md DONE.')

        except HTTPError as e:
            # Write un-scrapeable links to a txt file and continue
            noScrape_links.append(url)
            with open(dir_path + '/noScrapeLinks.txt', 'a') as f:
                f.write(url + '\n')
            continue

    return scraped_path

# Function to extract image URLs and email addresses from a markdown file
def extract_image_urls(md_file_path):
    with open(md_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # Load the content in proper format
        res = eval(content)

    # Getting and checking the image URL
    image_url = res['screenshot']
    if str(image_url).startswith('http'):
        #print(f"Extracted URLs from {md_file_path}: {image_url}")
        image_url = image_url
    
    # Getting the source URL from metdata
    source_url = res['metadata']['sourceURL']

    # Compiling a list of 2 URLs
    urls = [image_url, source_url]

    # Extract email addresses. Adding {3,} to avoid @2x style notations for image sizes
    emails = re.findall(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]{3,}\.[a-zA-Z0-9-.]+)", content)

    return urls, emails

# Download the page screenshot and save it
def download_image(image_url, save_path):
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # Check if the request was successful
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"Image saved as {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve image {image_url}. Error: {e}")

# Process all .md files in the scraped directory
def process_md_files(directory, save_directory):
    # Ensure the save directory exists
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # Iterate over all .md files in the directory and extract image URLs and email addresses
    all_emails = []
    all_urls = []
    for md_file_name in os.listdir(directory):
        if str(md_file_name).endswith('.md'):
            # Extract image URLs
            md_file_path = os.path.join(directory, md_file_name)
            extraction_result = extract_image_urls(md_file_path)
            image_url = extraction_result[0][0]
            source_url = extraction_result[0][1]
            domain_pattern = r"(https?://)?(www\d?\.)?(?P<domain>[\w\.-]+\.\w+)(/\S*)?"
            match = re.match(domain_pattern, source_url)
            source_url = match.group('domain')
            all_urls.append([image_url, str(source_url).replace('.','_')])

            # Extract email addresses
            email = extract_image_urls(md_file_path)[1]
            all_emails.append(email)

    # Iterate over all found image URLs
    for url_pair in all_urls:
        save_path = os.path.join(save_directory, "ss_" + url_pair[1] + ".png")
        download_image(url_pair[0], save_path)

    # Iterate over all founf email addresses
    filtered_email_list = []
    for email in all_emails:
        if type(email) is list:
            for item in email:
                filtered_email_list.append(item)
        else:
            filtered_email_list.append(email)

    if len(filtered_email_list) > 0:
        for email in set(filtered_email_list):
            with open(os.path.dirname(save_directory) + '/EmailAddresses.txt', 'a') as f:
                    f.write(email + '\n')
    else:
        with open(os.path.dirname(save_directory) + '/EmailAddresses.txt', 'w') as f:
            f.write('No email addresses found.')

# Load API keys from .env
load_dotenv()

# Run the Google search function
md_directory = google_search_function("Mihai Catalin Teodosiu")

# Defining the firectories to pass to process_md_files()
directory = md_directory
save_directory = md_directory + '/screenshots'

# Process all .md files in the specified directory
process_md_files(directory, save_directory)