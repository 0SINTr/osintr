from match import match_emails, is_valid_email
from firecrawl import FirecrawlApp
from colorama import Fore, Style
from dotenv import load_dotenv
import pandas as pd
import textwrap
import argparse
import requests
import random
import string
import json
import time
import sys
import os
import re

# Check if osint_ directory exists, if not create it
def check_directory(target, directory):
    directory = os.path.join(directory, "osint_data_" + ''.join(char for char in str(target) if char.isalnum()))
    if not os.path.exists(path=directory):
        print("\n" + Style.BRIGHT + Fore.GREEN + "[" + Fore.WHITE + "*" + Fore.GREEN + "]" + f" Initializing OSINTr for target '{target}' and searching Google." + Style.RESET_ALL)
        os.makedirs(directory)
    else:
        print("\n" + Style.BRIGHT + Fore.YELLOW + "[" + Fore.WHITE + "!" + Fore.YELLOW + "]" + f" Directory for target '{target}' already exists. Continuing..." + Style.RESET_ALL)
    return directory

# Perform verbatim and inurl Google search on target
def google_search(target):
    url = "https://google.serper.dev/search"
    query = f"\"{target}\" OR inurl:\"{target}\""
    payload = json.dumps({
    "q": query,
    "num": 10,
    "autocorrect": False
    })
    headers = {
    'X-API-KEY': os.getenv('SERPER_API_KEY'),
    'Content-Type': 'application/json'
    }

    try:
        search_results = []
        # Submit the query
        results = requests.request("POST", url, headers=headers, data=payload)
        if results:
            for result in results.json()['organic']:
                search_results.append(result)
    except Exception as e:
        sys.exit(Style.BRIGHT + Fore.WHITE + "[" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + f" Quitting. Error during Google search: {str(e)}\n" + Style.RESET_ALL)
    return search_results

# Remove duplicate search results
def remove_duplicates(results):
    df = pd.DataFrame(results).drop_duplicates('title')
    unique_data = df.to_dict(orient='records')
    print(Fore.GREEN + " [" + Fore.WHITE + "+" + Fore.GREEN + "]" + Fore.WHITE + " Duplicates removed from search results." + Style.RESET_ALL)
    return unique_data

# Extracting links from search results
def extract_links(unique_data):
    scrape_links = []
    for entry in unique_data:
        if 'gov' not in entry['link']:
            scrape_links.append(entry['link'])
    print(Fore.GREEN + " [" + Fore.WHITE + "+" + Fore.GREEN + "]" + Fore.WHITE + " Links extracted and ready for scraping." + Style.RESET_ALL)
    return scrape_links

# Scarping links with Firecrawl
def scraped_links(scrape_links):
    print("\n" + Style.BRIGHT + Fore.GREEN + "[" + Fore.WHITE + "*" + Fore.GREEN + "]" + " Starting to scrape links. Moving on if nothing to scrape." + Style.RESET_ALL)
    print(Fore.GREEN + " [" + Fore.WHITE + "!" + Fore.GREEN + "]" + Fore.WHITE + " Some pages or screenshots may fail, don't panic." + Style.RESET_ALL)
    scrape_results = []
    for link in scrape_links:
        try:
            print(Fore.WHITE + " [" + Fore.GREEN + "+" + Fore.WHITE + "]" + Fore.GREEN + " Scraping " + Style.RESET_ALL + link)
            scraper = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))
            scrape_result = scraper.scrape_url(link, params={'formats': ['markdown', 'links', 'screenshot@fullPage']})
            scrape_results.append(scrape_result)
            time.sleep(1)
        except Exception as e:
            print(Fore.WHITE + " [" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + ' Scraping not allowed for ' + Style.RESET_ALL + link + Style.BRIGHT + Fore.RED + " - skipping" + Style.RESET_ALL)
            continue
    return scrape_results

# Extract emails and links from results
def extract_data(scrape_result):
    # Image URL
    if 'screenshot' in scrape_result:
        if str(scrape_result['screenshot']).startswith('http'):
            image_url = scrape_result['screenshot']
        else:
            image_url = ''
    else:
        image_url = ''

    # Email addresses
    emails = re.findall(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]{3,}\.[a-zA-Z0-9-.]+)", str(scrape_result))

    # All URLs
    all_urls = scrape_result['links']

    return image_url, emails, all_urls

# Check if the target is a valid email address, otherwise it's a username
def check(target):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if(re.fullmatch(regex, target)):
        return target
    else:
        return None
    
# Saving screenshots via image URLs
def save_screenshot(image_url, directory):
    try:
        response = requests.get(image_url)
        # Check if the request was successful
        response.raise_for_status() 
        with open(directory, 'wb') as file:
            file.write(response.content)
        print(Fore.WHITE + " [" + Fore.GREEN + "+" + Fore.WHITE + "]" + Fore.GREEN + " Screenshot saved as: " + Style.RESET_ALL + directory)
    except Exception as e:
        print(Fore.WHITE + " [" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + " Failed to retrieve image from" + Style.RESET_ALL + f" {image_url}" + Style.BRIGHT + Fore.RED + " - skipping" + Style.RESET_ALL)

# Process the data and save to dictionary
def process_data(scrape_results, target, directory):
    data_dict = {}
    all_emails = []
    all_urls = []
    all_image_urls = []
    # Iterating over search results and extracting data
    for scrape_result in scrape_results:
        extracted_data = extract_data(scrape_result)
        # Image URL
        image_url = extracted_data[0]
        all_image_urls.append(image_url)

        # Extract email addresses
        emails = extracted_data[1]
        for email in emails:
            all_emails.append(email)

        # Extract all URLs
        urls = extracted_data[2]
        for url in urls:
            all_urls.append(url)
    
    # Writing emails and URLs to dictionary
    if len(all_emails) > 0:
        data_dict['Email Addresses'] = list(set(all_emails))
    else:
        data_dict['Email Addresses'] = []

    if len(all_urls) > 0:
        data_dict['URLs'] = list(set(all_urls))
    else:
        data_dict['URLs'] = []

    # Iterating over all image URLs and taking screenshots
    if len(all_image_urls):
        print("\n" + Style.BRIGHT + Fore.GREEN + "[" + Fore.WHITE + "*" + Fore.GREEN + "]" + " Taking screenshots where possible." + Style.RESET_ALL)
        ss_path = os.path.join(directory, "osint_data_" + ''.join(char for char in str(target) if char.isalnum()), 'screenshots')
        if not os.path.exists(ss_path):
            os.makedirs(ss_path)
        for url in all_image_urls:
            image_path = os.path.join(ss_path, 'ss_' + ''.join(random.choices(string.ascii_lowercase, k=5)) + '.png')
            save_screenshot(url, image_path)
    else:
        print(Fore.WHITE + "[" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + " No screenshots taken." + Style.RESET_ALL)

    print(Style.BRIGHT + Fore.WHITE + "[" + Fore.GREEN + "-" + Fore.WHITE + "]" + Fore.GREEN + " All Google search data was saved." + Style.RESET_ALL)
    return data_dict

# Parsing CLI arguments
def arg_parsing():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
            examples:                 
            osintr -t jdoe95@example.com -o /home/bob/data
            osintr -t john.doe95 -o /home/bob/data
            osintr -t +123456789 -o /home/bob/data
            osintr -t "John Doe" -o /home/bob/data
            osintr -t "Evil Corp Ltd" -o /home/bob/data                                                                  
            '''),
        epilog=textwrap.dedent('''\
            NOTE!
            For person or company names use double quotes to enclose the whole name.             
            '''))
    parser.add_argument('-t', dest='TARGET', help='Target of investigation', required=True)
    parser.add_argument('-o', dest='OUTPUT', help='Directory to save results', required=True)
    args = parser.parse_args()

    # TARGET argument
    if args.TARGET is not None:
        target = args.TARGET
        pass
    else:
        parser.print_help()

    # OUTPUT argument
    if args.OUTPUT is not None:
        output_directory = str(args.OUTPUT).rstrip('/')
    else:
        parser.print_help()

    return target, output_directory

# Data dictionary return function
def data_dictfunc():
    args = arg_parsing()
    target = args[0]
    output = args[1]

    # Checking if directory exists
    check_directory(target, output)

    # Loading env variables
    load_dotenv()
    if all([os.getenv('SERPER_API_KEY'), os.getenv('FIRECRAWL_API_KEY')]):
        results = google_search(target)
        uniques = remove_duplicates(results)              
        scrape_links = extract_links(uniques)
        scraped_data = scraped_links(scrape_links)
        data_dict = process_data(scraped_data, target, output)
        return target, data_dict
    else:
        print("\n" + Style.BRIGHT + Fore.RED + "[" + Fore.WHITE + "-" + Fore.RED + "]" + " API key(s) not found.\n" + Style.RESET_ALL)
        sys.exit()

def recursive_search_and_scrape(target, output, processed_targets=None, combined_data=None, depth=0, max_depth=2):
    if depth > max_depth:
        print(Fore.YELLOW + f" [!] Maximum recursion depth reached for target '{target}'. Skipping further recursion." + Style.RESET_ALL)
        return combined_data

    if processed_targets is None:
        processed_targets = set()
    if combined_data is None:
        combined_data = {'Email Addresses': set(), 'URLs': set()}

    # Check if the target has already been processed
    if target in processed_targets:
        print(Fore.CYAN + f" [i] Target '{target}' has already been processed. Skipping." + Style.RESET_ALL)
        return combined_data

    processed_targets.add(target)

    # Indicate which target is being processed
    print(Style.BRIGHT + Fore.GREEN + f"\n[+] Starting search and scrape for target: '{target}' (Depth: {depth})" + Style.RESET_ALL)

    # Checking if directory exists
    directory = check_directory(target, output)

    # Loading env variables
    load_dotenv()
    if not all([os.getenv('SERPER_API_KEY'), os.getenv('FIRECRAWL_API_KEY')]):
        print("\n" + Style.BRIGHT + Fore.RED + "[" + Fore.WHITE + "-" + Fore.RED + "]" + " API key(s) not found.\n" + Style.RESET_ALL)
        sys.exit()

    # Perform the search and scrape process
    results = google_search(target)
    uniques = remove_duplicates(results)
    scrape_links = extract_links(uniques)
    scraped_data = scraped_links(scrape_links)
    data_dict = process_data(scraped_data, target, output)

    # Update combined data
    combined_data['Email Addresses'].update(data_dict.get('Email Addresses', []))
    combined_data['URLs'].update(data_dict.get('URLs', []))

    # Display the emails found in this iteration
    found_emails = data_dict.get('Email Addresses', [])
    if found_emails:
        print(Fore.GREEN + f"\n[+] Emails found for target '{target}':" + Style.RESET_ALL)
        for email in found_emails:
            print(f"    - {email}")
    else:
        print(Style.BRIGHT + Fore.YELLOW + f"\n[!] No emails found for target '{target}'." + Style.RESET_ALL)
        if depth == 0:
            print(Fore.YELLOW + f" [!] No emails identified during the initial search." + Style.RESET_ALL)
        return combined_data  # No emails to process further

    # Now, apply match_emails() to the found emails
    # Since the initial target is not an email, we compare the found emails among themselves
    # This step helps to find related emails among the found ones
    matched_emails = set()
    for email in found_emails:
        matches = match_emails(email, found_emails)
        matched_emails.update(matches)

    # Remove emails that have already been processed
    matched_emails = matched_emails - processed_targets

    # Display matched emails that will be processed recursively
    if matched_emails:
        print(Style.BRIGHT + Fore.CYAN + f"\n[i] Matched emails to be processed further:" + Style.RESET_ALL)
        for email in matched_emails:
            print(f"    - {email}")
    else:
        print(Fore.CYAN + f"\n[i] No matched emails for further processing." + Style.RESET_ALL)

    # Recursively process each matched email
    for email in matched_emails:
        # Ensure that the email hasn't been processed and is valid
        if email not in processed_targets and is_valid_email(email):
            recursive_search_and_scrape(email, output, processed_targets, combined_data, depth=depth+1, max_depth=max_depth)

    return combined_data

def main():
    # Parsing CLI arguments
    args = arg_parsing()
    initial_target = args[0]
    output_directory = args[1]

    # Start recursive search and scrape
    combined_data = recursive_search_and_scrape(initial_target, output_directory)

    # Convert sets to lists for final output
    combined_data['Email Addresses'] = list(combined_data['Email Addresses'])
    combined_data['URLs'] = sorted(list(combined_data['URLs']))

    # Save combined data to a JSON file or output as needed
    # For example, print the results
    #print("\n" + Style.BRIGHT + Fore.GREEN + "[" + Fore.WHITE + "*" + Fore.GREEN + "]" + " Final Data:" + Style.RESET_ALL)
    #print(json.dumps(combined_data, indent=2))

    # Save combined data to a JSON file
    output_file = os.path.join(output_directory, "osint_data_" + ''.join(char for char in str(initial_target) if char.isalnum()), 'final_data.json')
    with open(output_file, 'w') as f:
        json.dump(combined_data, f, indent=2)

    print(Fore.GREEN + f" [+] Final data saved to {output_file}\n" + Style.RESET_ALL)

if __name__ == '__main__':
    main()