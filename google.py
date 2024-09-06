from langchain_community.utilities import GoogleSerperAPIWrapper
from firecrawl import FirecrawlApp
from dotenv import load_dotenv
from colorama import Fore, Style, init
import pandas as pd
import requests
import time
import json
import sys
import os
import re

# Function to perform the Google search and scrape each page related to the target
def google_search_function(target_verbatim, target_intext, target_inurl):
    print(Fore.CYAN + f"\n  |--- Running search for target: {target}" + Style.RESET_ALL)
    
    # Check if osint_data directory exists, if not create it for the specified target
    dir_path = "osint_data_" + ''.join(char for char in str(target) if char.isalnum())
    if not os.path.exists(path=dir_path):
        os.makedirs(dir_path + '/google/')

    # Perform a verbatim Google search (tbs value) and return the results
    search_verbatim = GoogleSerperAPIWrapper(tbs="li:1", k=20)
    search_intext = GoogleSerperAPIWrapper(k=20)
    search_inurl = GoogleSerperAPIWrapper(k=20)

    try:
        all_search_results = []

        # Pass the query to the SerpAPIWrapper's verbatim search method
        results_verbatim = search_verbatim.results(target_verbatim)
        if results_verbatim:
            for result in results_verbatim['organic']:
                all_search_results.append(result)

        # Pass the query to the SerpAPIWrapper's intext search method
        results_intext = search_intext.results(target_intext)
        if results_intext:
            for result in results_intext['organic']:
                all_search_results.append(result)

        # Pass the query to the SerpAPIWrapper's inurl search method
        results_inurl = search_inurl.results(target_inurl)
        if results_inurl:
            for result in results_inurl['organic']:
                all_search_results.append(result)

        # Removing duplicates
        df = pd.DataFrame(all_search_results)
        df_unique = df.drop_duplicates('title')
        unique_json_data = df_unique.to_dict(orient='records')

        print(Fore.CYAN + "\n  |--- Removing duplicates from search results.\n" + Style.RESET_ALL)
        print(Fore.CYAN + f"  |--- Total duplicates removed: {len(all_search_results)-len(unique_json_data)}, Final items: {len(unique_json_data)}" + Style.RESET_ALL)

        # Create and save the JSON file with unique search results
        with open(dir_path + '/google/google_search.json', 'w') as outfile:
            json.dump(unique_json_data, outfile)
        
        print(Fore.GREEN + "\n  |--- Search DONE. Check folder " + Style.BRIGHT + f"{dir_path}" + Style.RESET_ALL)

    except Exception as e:
        # Handle any errors that occur during the search
        print(Fore.RED + f"  |--- Error during Google search: {str(e)}" + Style.RESET_ALL)
        sys.exit(Fore.RED + "\n  |--- Quitting." + Style.RESET_ALL)
    
    # Introducing sleep for 3 seconds
    time.sleep(3)

    # Creating new directory for scraping results
    scraped_path = dir_path + '/google/scraped'
    if not os.path.exists(path=scraped_path):
        os.makedirs(scraped_path)

    # Extracting all the links from search results
    links = []
    noScrape_links = []
    for entry in unique_json_data:
        if 'gov' not in entry['link']:
            links.append(entry['link'])

    print(Style.BRIGHT + Fore.MAGENTA + "\n\n|---> Starting to scrape." + Style.RESET_ALL)
    print(Fore.MAGENTA + "\n  |--- Forbidden URLs will be added to " + Style.BRIGHT + "/google/noScrapeLinks.txt\n" + Style.RESET_ALL)

    # Initialize the Firecrawl scraper
    for index, url in enumerate(links):
        try:
            scraper = FirecrawlApp()
            scrape_result = scraper.scrape_url(url, params={'formats': ['markdown', 'html', 'screenshot'], 'waitFor':3000, 'timeout':10000})

            # Write the scrape results to separate files
            with open(scraped_path + '/scrape' + str(index + 1) + '.md', 'w', encoding='utf-8') as outfile:
                outfile.write(str(scrape_result))

            print('    |- File scrape' + str(index + 1) + '.md DONE.')

            # Introducing sleep for 3 seconds
            time.sleep(3)

        except requests.exceptions.HTTPError as e:
            # Write un-scrapeable links to a txt file and continue
            noScrape_links.append(url)
            with open(dir_path + '/google/noScrapeLinks.txt', 'a') as f:
                f.write(url + '\n')
            continue

        except Exception as e:
            print(Fore.RED + '    |- Error scraping ' + Style.BRIGHT + url + Style.RESET_ALL)
            continue
    
    return scraped_path

# Function to extract image URLs and email addresses from a markdown file
def extract_image_urls(md_file_path):
    with open(md_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # Load the content in proper format
        res = eval(content)

    # Getting and checking the image URL
    image_url = res.get('screenshot')
    if image_url and str(image_url).startswith('http'):
        #print(f"Extracted URLs from {md_file_path}: {image_url}")
        image_url = image_url
    
    # Getting the source URL from metdata
    source_url = res['metadata']['sourceURL']

    # Compiling a list of 2 URLs
    urls = [image_url, source_url]

    # Extract email addresses from .md files. Adding {3,} to avoid @2x style notations for image sizes
    emails = re.findall(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]{3,}\.[a-zA-Z0-9-.]+)", content)

    return urls, emails

# Download the page screenshot and save it
def download_image(image_url, save_path):
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # Check if the request was successful
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print("    |- Image saved as: " + Fore.YELLOW + f"{save_path}" + Style.RESET_ALL)
    except requests.exceptions.RequestException as e:
        #print(f"Failed to retrieve image {image_url}. Error: {e}")
        pass

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
    print(Style.BRIGHT + Fore.CYAN + "\n\n|---> Saving screenshots.\n" + Style.RESET_ALL)
    for url_pair in all_urls:
        file_no = 1
        save_path = os.path.join(save_directory, "ss_" + url_pair[1] + str(file_no) + ".png")
        if not os.path.exists(save_path):
            download_image(url_pair[0], save_path)
        else:
            save_bkp_path = os.path.join(save_directory, "ss_" + url_pair[1] + str(file_no + 1) + ".png")
            download_image(url_pair[0], save_bkp_path)

    # Iterate over all found email addresses
    filtered_email_list = []
    for email in all_emails:
        if type(email) is list:
            for item in email:
                filtered_email_list.append(item)
        else:
            filtered_email_list.append(email)

    # Extract email addresses from .json file
    with open(os.path.dirname(save_directory) + '/google_search.json', 'r') as f:
        content = f.read()
    
    emails_from_json = re.findall(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]{3,}\.[a-zA-Z0-9-.]+)", content)
    filtered_email_list += emails_from_json

    # Writing the email addresses to a .txt file
    if len(filtered_email_list) > 0:
        for email in set(filtered_email_list):
            with open(os.path.dirname(save_directory) + '/emailAddresses.txt', 'a') as f:
                    f.write(email + '\n')
        
        # Print out the email addresses
        print(Style.BRIGHT + Fore.YELLOW + "\n\n|---> Email addresses found:\n" + Style.RESET_ALL)
        for email in set(filtered_email_list):
            print(f"    |- {email}")

    else:
        print(Style.BRIGHT + Fore.YELLOW + "\n\n|---> No email addresses found:" + Style.RESET_ALL)
        with open(os.path.dirname(save_directory) + '/emailAddresses.txt', 'w') as f:
            f.write('No email addresses found.')

def search_breaches(target):
    print(Style.BRIGHT + Fore.RED + "\n\n|---> Checking for breaches: " + Style.RESET_ALL)
    url = "https://haveibeenpwned.com/api/v3/breachedaccount/"
    headers = {"user-agent": "python-requests/2.32.3", "hibp-api-key": os.getenv("HIBP_API_KEY")} 
    response = requests.get(url + target + "?truncateResponse=false" + "?includeUnverified=true", headers=headers)

    if response.status_code == 200:
        breach_data = response.json()

        # Create new directory 
        dir_path = "osint_data_" + ''.join(char for char in str(target) if char.isalnum())
        if os.path.exists(path=dir_path):
            os.makedirs(dir_path + '/leaks/')

        # Write JSON data to directory
        with open(dir_path + '/leaks/breaches.json', 'w') as outfile:
            json.dump(breach_data, outfile)

        print(Fore.RED + "\n  |--- Breached data added to " + Style.BRIGHT + "/leaks/breaches.json" + Style.RESET_ALL)

    elif response.status_code == 404:
        print(Fore.GREEN + "\n  |--- No breached data found for " + Style.BRIGHT + f"{target}" + Style.RESET_ALL)

    else:
        print('    |- Error code: ' + str(response.status_code))

def search_pastes(target):
    print(Style.BRIGHT + Fore.RED + "\n\n|---> Checking for pastes: " + Style.RESET_ALL)
    time.sleep(10) # Introducing sleep for 10 seconds to avoid statusCode 429
    url = "https://haveibeenpwned.com/api/v3/pasteaccount/"
    headers = {"user-agent": "python-requests/2.32.3", "hibp-api-key": os.getenv("HIBP_API_KEY")} 
    response = requests.get(url + target, headers=headers)

    if response.status_code == 200:
        paste_data = response.json()

        # Check leaks directory 
        dir_path = "osint_data_" + ''.join(char for char in str(target) if char.isalnum())
        if os.path.exists(path=dir_path) and not os.path.exists(path=dir_path + '/leaks/'):
            os.makedirs(dir_path + '/leaks/')

        # Write JSON data to directory
        with open(dir_path + '/leaks/pastes.json', 'w') as outfile:
            json.dump(paste_data, outfile)

        print(Fore.RED + "\n  |--- Paste data added to " + Style.BRIGHT + "/leaks/pastes.json\n" + Style.RESET_ALL)

    elif response.status_code == 404:
        print(Fore.GREEN + "\n  |--- No paste data found for " + Style.BRIGHT + f"{target}\n" + Style.RESET_ALL)

    else:
        print('    |- Error code: ' + str(response.status_code))

# Load API keys from .env
load_dotenv()

# Run the Google search function
init() # For colorama
target = input(Style.BRIGHT + Fore.CYAN + "\n|---> Enter target [Username | Email Address]: " + Style.RESET_ALL)
target_verbatim = target
target_intext = 'intext:' + '"' + target + '"'
target_inurl = 'inurl:' + '"' + target + '"'
md_directory = google_search_function(target_verbatim, target_intext, target_inurl)

# Defining the firectories to pass to process_md_files()
directory = md_directory
save_directory = os.path.dirname(md_directory) + '/screenshots'

# Process all .md files in the specified directory
process_md_files(directory, save_directory)

# Run the data leak detection functions
search_breaches(target)
search_pastes(target)