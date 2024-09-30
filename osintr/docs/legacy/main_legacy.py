from langchain_community.utilities import GoogleSerperAPIWrapper
from colorama import Fore, Style, init
from firecrawl import FirecrawlApp
from itertools import product, chain
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
        print("\n" + Style.BRIGHT + Fore.GREEN + "[" + Fore.WHITE + "*" + Fore.GREEN + "]" + " Initializing OSINTr and searching Google." + Style.RESET_ALL)
        os.makedirs(directory)
        return directory
    else:
        print("\n" + Style.BRIGHT + Fore.RED + "[" + Fore.WHITE + "-" + Fore.RED + "]" + " Directory already exists. Delete it or change path.\n" + Style.RESET_ALL)
        sys.exit()

# Perform verbatim Google search on target
def verbatim_search(target):
    search = GoogleSerperAPIWrapper(tbs="li:1", k=20)
    try:
        search_results = []
        # Pass the query to the SerpAPIWrapper's verbatim search method
        results = search.results(target)
        if results:
            for result in results['organic']:
                search_results.append(result)
    except Exception as e:
        sys.exit(Style.BRIGHT + Fore.WHITE + "[" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + f" Quitting. Error during Google search: {str(e)}" + Style.RESET_ALL)
    return search_results

# Perform intext Google search on target
def intext_search(target):
    search = GoogleSerperAPIWrapper(k=20)
    target = f"intext:\"{target}\""   
    try:
        search_results = []
        # Pass the query to the SerpAPIWrapper's intext search method
        results = search.results(target)
        if results:
            for result in results['organic']:
                search_results.append(result)
    except Exception as e:
        sys.exit(Style.BRIGHT + Fore.WHITE + "[" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + f" Quitting. Error during Google search: {str(e)}" + Style.RESET_ALL)
    return search_results

# Perform inurl Google search on target
def inurl_search(target):
    search = GoogleSerperAPIWrapper(k=20)
    target = f"inurl:\"{target}\""
    try:
        search_results = []
        # Pass the query to the SerpAPIWrapper's inurl search method
        results = search.results(target)
        if results:
            for result in results['organic']:
                search_results.append(result)
    except Exception as e:
        sys.exit(Style.BRIGHT + Fore.WHITE + "[" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + f" Quitting. Error during Google search: {str(e)}" + Style.RESET_ALL)
    return search_results

# Perform intitle Google search on target
def intitle_search(target):
    search = GoogleSerperAPIWrapper(k=20)
    target = f"intitle:\"{target}\""  
    try:
        search_results = []
        # Pass the query to the SerpAPIWrapper's intitle search method
        results = search.results(target)
        if results:
            for result in results['organic']:
                search_results.append(result)
    except Exception as e:
        sys.exit(Style.BRIGHT + Fore.WHITE + "[" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + f" Quitting. Error during Google search: {str(e)}" + Style.RESET_ALL)
    return search_results

# Join all search results into a list
def join_results(res_one, res_two, res_thr, *res):
    results = list(chain(res_one, res_two, res_thr))
    return results

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

# Check if the target is a valid email address, otherwise it's a username
def check(user_input):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if(re.fullmatch(regex, user_input)):
        return user_input
    else:
        return None
    
# Function for detecting aliases from target (leet)
def detect_aliases(target):
    if check(target):
        user = str(target).split('@')[0]
    else:
        user = target
    
    # Mapping for letters to digit aliases
    mapping = {letter: str(index) for index, letter in enumerate('oizeasgtb')}
    mapping.update({letter.upper(): str(index) for index, letter in enumerate('oizeasgtb')})

    possible_aliases = []
    for l in user:
        ll = mapping.get(l, l)  # Get the alias if it exists, otherwise the original character     
        if ll == l:  # If the character is not mapped to a number
            # Add both lowercase and uppercase versions as possible alternatives
            possible_aliases.append((l.lower(), l.upper()))
        else:
            # If mapped to a number, include both lowercase and uppercase versions of the original letter, and the digit alias
            possible_aliases.append((l.lower(), l.upper(), ll))    
    return [''.join(t) for t in product(*possible_aliases)]

# Process the data and save to JSON
def process_data(scrape_results, target, directory):
    data_dict = {}
    all_image_urls = []
    all_emails = []
    all_urls = []
    all_aliases = []
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

        # Extract leet aliases
        possible_aliases = detect_aliases(target)
        if len(possible_aliases) > 0:
            for alias in possible_aliases:
                if any(alias in sub for sub in email) or any(alias in sub for sub in urls):
                    all_aliases.append(alias)

    # Iterate over all image URLs
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

    # Iterate over all email addresses
    unzipped_email_list = []
    for email in all_emails:
        if type(email) is list:
            for item in email:
                unzipped_email_list.append(item)
        else:
            unzipped_email_list.append(email)

    # Listing all possible aliases
    possible_aliases = detect_aliases(target)

    # Writing all the emails containing the target or target leet to data_dict
    all_main_emails = []
    if len(unzipped_email_list) > 0:
        # Check leet target in each link
        if len(possible_aliases) > 0:
            for alias in possible_aliases:
                for email in unzipped_email_list:
                    if alias in email:
                        all_main_emails.append(email)
        data_dict['Relevant Email Addresses'] = list(set(all_main_emails))

        # Print out the email addresses
        print('\n' + Style.BRIGHT + Fore.GREEN + "[" + Fore.WHITE + "*" + Fore.GREEN + "]" + " Relevant email addresses found:" + Style.RESET_ALL)
        for email in set(unzipped_email_list):
            print(Fore.WHITE + " [" + Fore.GREEN + "+" + Fore.WHITE + "]" + Style.RESET_ALL + f" {email}")
    else:
        data_dict['Email Addresses'] = []
        print('\n' + Fore.WHITE + "[" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + " No relevant or alternate email addresses found for " + Style.BRIGHT + target + Style.RESET_ALL)

    # Writing all other emails as secondary emails to data_dict
    all_unique_emails = set(all_emails)
    all_unique_main_emails = set(all_main_emails)
    diff = all_unique_emails.difference(all_unique_main_emails)
    if len(diff):
        print(Fore.WHITE + "[" + Fore.GREEN + "+" + Fore.WHITE + "]" + Fore.GREEN + " Possibly related email addresses found and saved." + Style.RESET_ALL)
    data_dict['Possibly Related Emails'] = list(diff)

    # Writing all the URLs containing the target or target leet to data_dict
    all_main_urls = []
    if len(all_urls) > 0:
        # Check target in each link
        if check(target):
            target = str(target).split('@')[0]
            for link in all_urls:
                if target in link:
                    all_main_urls.append(link)
        else:
            for link in all_urls:
                if target in link:
                    all_main_urls.append(link)

        # Check leet target in each link
        if len(possible_aliases) > 0:
            for alias in possible_aliases:
                for link in all_urls:
                    if alias in link:
                        all_main_urls.append(link)
        print(Fore.WHITE + "[" + Fore.GREEN + "+" + Fore.WHITE + "]" + Fore.GREEN + " Relevant links found and saved." + Style.RESET_ALL)
        data_dict['Relevant Links'] = list(set(all_main_urls))
    else:
        data_dict['Relevant Links'] = []

    # Writing all other URLs as secondary links to data_dict
    all_unique_urls = set(all_urls)
    all_unique_main_urls = set(all_main_urls)
    diff = all_unique_urls.difference(all_unique_main_urls)
    if len(diff):
        print(Fore.WHITE + "[" + Fore.GREEN + "+" + Fore.WHITE + "]" + Fore.GREEN + " Possibly related links found and saved." + Style.RESET_ALL)
    data_dict['Possibly Related Links'] = list(diff)

    print(Style.BRIGHT + Fore.WHITE + "[" + Fore.GREEN + "-" + Fore.WHITE + "]" + Fore.GREEN + " All Google search data was saved." + Style.RESET_ALL)
    return data_dict

# Search for breaches in HIBP data
def search_breaches(target):
    print("\n" + Style.BRIGHT + Fore.GREEN + "[" + Fore.WHITE + "*" + Fore.GREEN + "]" + " Checking HIBP for breach data." + Style.RESET_ALL)
    url = "https://haveibeenpwned.com/api/v3/breachedaccount/"
    headers = {"user-agent": "python-requests/2.32.3", "hibp-api-key": os.getenv("HIBP_API_KEY")} 
    response = requests.get(url + target + "?truncateResponse=false" + "?includeUnverified=true", headers=headers)

    # Check HIBP response (pastes)
    if response.status_code == 200:
        print(Fore.GREEN + " [" + Fore.WHITE + "+" + Fore.GREEN + "]" + " HIBP breach data found and saved." + Style.RESET_ALL)
        breach_data = response.json()
        return breach_data
    elif response.status_code == 401:
        print(Fore.WHITE + " [" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + " Invalid API key or insufficient credits." + Style.RESET_ALL)
    elif response.status_code == 404:
        print(Fore.WHITE + " [" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + " No HIBP breach data found for " + Style.BRIGHT + f"{target}" + Style.RESET_ALL)
    elif response.status_code == 429:
        print(Fore.WHITE + " [" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + " Too Many Requests. Rate limit exceeded." + Style.RESET_ALL)
    else:
        print(Fore.WHITE + " [" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + " Error code: " + Style.RESET_ALL + str(response.status_code))

# Search for pastes in HIBP data
def search_pastes(target):
    print("\n" + Style.BRIGHT + Fore.GREEN + "[" + Fore.WHITE + "*" + Fore.GREEN + "]" + " Checking HIBP for paste data." + Style.RESET_ALL)
    time.sleep(10) # Introducing sleep for 10 seconds to avoid statusCode 429
    url = 'https://haveibeenpwned.com/api/v3/pasteaccount/'
    headers = {
        'user-agent': 'python-requests/2.32.3', 
        'hibp-api-key': os.getenv('HIBP_API_KEY')
    } 
    response = requests.get(url + target, headers=headers)

    # Check HIBP response (pastes)
    if response.status_code == 200:
        print(Fore.GREEN + " [" + Fore.WHITE + "+" + Fore.GREEN + "]" + " HIBP paste data found and saved." + Style.RESET_ALL)
        paste_data = response.json() 
        return paste_data
    elif response.status_code == 401:
        print(Fore.WHITE + " [" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + " Invalid API key or insufficient credits." + Style.RESET_ALL)
    elif response.status_code == 404:
        print(Fore.WHITE + " [" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + " No HIBP paste data found for " + Style.BRIGHT + f"{target}" + Style.RESET_ALL)
    elif response.status_code == 429:
        print(Fore.WHITE + " [" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + " Too Many Requests. Rate limit exceeded." + Style.RESET_ALL)
    else:
        print(Fore.WHITE + " [" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + " Error code: " + Style.RESET_ALL + str(response.status_code))

# Search for data from Whoxy
def search_whoxy(target_type, target):
    print("\n" + Style.BRIGHT + Fore.GREEN + "[" + Fore.WHITE + "*" + Fore.GREEN + "]" + " Checking Whoxy for reverse whois data." + Style.RESET_ALL)
    # API key and URL
    whoxy_key = os.getenv('WHOXY_API_KEY')
    url = f'https://api.whoxy.com/?key={whoxy_key}&reverse=whois&'
    response = requests.get(url + target_type + '=' + target)

    # Check Whoxy response
    if response.status_code == 200:
        print(Fore.GREEN + " [" + Fore.WHITE + "+" + Fore.GREEN + "]" + " Whoxy data found and saved." + Style.RESET_ALL)
        whoxy_data = response.json()
        return whoxy_data
    elif response.status_code == 401:
        print(Fore.WHITE + " [" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + " Invalid API key or insufficient credits." + Style.RESET_ALL)
    elif response.status_code == 404:
        print(Fore.WHITE + " [" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + " No Whoxy reverse whois data found for " + Style.BRIGHT + f"{target}" + Style.RESET_ALL)
    elif response.status_code == 429:
        print(Fore.WHITE + " [" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + " Too Many Requests. Rate limit exceeded." + Style.RESET_ALL)
    else:
        print(Fore.WHITE + " [" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + " Error code: " + Style.RESET_ALL + str(response.status_code))

# Search for data from OSINT.Industries
def osint_industries(target):
    print("\n" + Style.BRIGHT + Fore.GREEN + "[" + Fore.WHITE + "*" + Fore.GREEN + "]" + " Checking OSINT.Industries for data." + Style.RESET_ALL)
    # Check if target is email or username
    is_valid_email = check(target)
    if is_valid_email:
        target_type = 'email'
    else:
        target_type = 'username'

    url = 'https://api.osint.industries/v2/request'
    headers = {
        'accept': 'application/json',
        'api-key': os.getenv("OSIND_API_KEY"),
    }
    params = {
        'type': target_type,
        'query': target,
    }
    response = requests.get(url, params=params, headers=headers)

    # Check OSINT.Industries response 
    if response.status_code == 200:
        print(Fore.GREEN + " [" + Fore.WHITE + "+" + Fore.GREEN + "]" + " OSINT.Industries data found and saved." + Style.RESET_ALL)
        osind_data = response.json()
        return osind_data
    elif response.status_code == 400:
        print(Fore.WHITE + " [" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + " Bad Request. Invalid query value." + Style.RESET_ALL)
    elif response.status_code == 401:
        print(Fore.WHITE + " [" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + " Invalid API key or insufficient credits." + Style.RESET_ALL)
    elif response.status_code == 404:
        print(Fore.WHITE + " [" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + " No OSINT Industries data found for " + Style.BRIGHT + f"{target}" + Style.RESET_ALL)
    elif response.status_code == 429:
        print(Fore.WHITE + " [" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + " Too Many Requests. Rate limit exceeded." + Style.RESET_ALL)
    else:
        print(Fore.WHITE + " [" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + " Error code: " + Style.RESET_ALL + str(response.status_code))

# Main function
def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
            See below all available arguments for osintr.
            Use only one -e|-u|-p|-n|-c argument at a time.
            
            example:
            osintr -e example@example.com -o /home/bob/data
            '''),
        epilog=textwrap.dedent('''\
            NOTE!
            For person or company name use double quotes to enclose the whole name.             
            '''))
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-e', dest='EMAIL', help='Target email address')
    group.add_argument('-u', dest='USER', help='Target username')
    group.add_argument('-p', dest='PHONE', help='Target phone number')
    group.add_argument('-n', dest='NAME', help='Target person name')
    group.add_argument('-c', dest='COMPANY', help='Target company name')
    parser.add_argument('-o', dest='OUTPUT', help='Directory to save results', required=True)
    args = parser.parse_args()

    # -o argument logic
    if args.OUTPUT is not None:
        output_directory = str(args.OUTPUT).rstrip('/')
    else:
        parser.print_help()

    # Loading env variables
    load_dotenv()

    # Initalizing colorama
    init()

    # -e argument logic
    if args.EMAIL is not None:
        target = args.EMAIL
        is_valid_email = check(target)
        if is_valid_email:
            data_dir = check_directory(target, output_directory)
            if all([os.getenv('SERPER_API_KEY'), os.getenv('FIRECRAWL_API_KEY')]):
                res_one = verbatim_search(target)
                res_two = intext_search(target)
                res_thr = intitle_search(target)
                results = join_results(res_one, res_two, res_thr)
                uniques = remove_duplicates(results)              
                scrape_links = extract_links(uniques)
                scraped_data = scraped_links(scrape_links)
                data_dict = process_data(scraped_data, target, output_directory)
            if os.getenv('HIBP_API_KEY'):
                breach_data = search_breaches(target)
                data_dict['Breaches'] = breach_data
                paste_data = search_pastes(target)
                data_dict['Pastes'] = paste_data
            if os.getenv('WHOXY_API_KEY'):
                whoxy_data = search_whoxy('email', target)
                data_dict['Whoxy'] = whoxy_data
            if os.getenv("OSIND_API_KEY"):
                osind_data = osint_industries(target)
                data_dict['OSINDUS'] = osind_data
        else:
            print("\n" + Style.BRIGHT + Fore.RED + "[" + Fore.WHITE + "-" + Fore.RED + "]" + " Invalid email address.\n" + Style.RESET_ALL)
            sys.exit()

    # -u argument logic
    if args.USER is not None:
        target = args.USER
        data_dir = check_directory(target, output_directory)
        if all([os.getenv('SERPER_API_KEY'), os.getenv('FIRECRAWL_API_KEY')]):
            res_one = verbatim_search(target)
            res_two = intext_search(target)
            res_thr = inurl_search(target)
            results = join_results(res_one, res_two, res_thr)
            uniques = remove_duplicates(results)
            scrape_links = extract_links(uniques)
            scraped_data = scraped_links(scrape_links)
            data_dict = process_data(scraped_data, target, output_directory)
        if os.getenv('HIBP_API_KEY'):
            breach_data = search_breaches(target)
            data_dict['Breaches'] = breach_data
            paste_data = search_pastes(target + "@gmail.com")
            data_dict['Pastes'] = paste_data
        if os.getenv('WHOXY_API_KEY'):
            whoxy_data = search_whoxy('email', target + "@gmail.com")
            data_dict['Whoxy'] = whoxy_data
        if os.getenv("OSIND_API_KEY") is not None:
            osind_data = osint_industries(target)
            data_dict['OSINDUS'] = osind_data

    # -p argument logic
    if args.PHONE is not None:
        target = args.PHONE
        data_dir = check_directory(target, output_directory)
        if all([os.getenv('SERPER_API_KEY'), os.getenv('FIRECRAWL_API_KEY')]):
            res_one = verbatim_search(target)
            res_two = intext_search(target)
            res_thr = inurl_search(target)
            res_fou = intitle_search(target)
            results = join_results(res_one, res_two, res_thr, res_fou)
            uniques = remove_duplicates(results)
            scrape_links = extract_links(uniques)
            scraped_data = scraped_links(scrape_links)
            data_dict = process_data(scraped_data, target, output_directory)
        if os.getenv("OSIND_API_KEY") is not None:
            osind_data = osint_industries(target)
            data_dict['OSINDUS'] = osind_data

    # -n argument logic
    if args.NAME is not None:
        target = args.NAME
        data_dir = check_directory(target, output_directory)
        if all([os.getenv('SERPER_API_KEY'), os.getenv('FIRECRAWL_API_KEY')]):
            res_one = verbatim_search(target)
            res_two = intext_search(target)
            res_thr = inurl_search(target)
            res_fou = intitle_search(target)
            results = join_results(res_one, res_two, res_thr, res_fou)
            uniques = remove_duplicates(results)
            scrape_links = extract_links(uniques)
            scraped_data = scraped_links(scrape_links)
            data_dict = process_data(scraped_data, target, output_directory)
        if os.getenv('WHOXY_API_KEY'):
            whoxy_data = search_whoxy('name', '+'.join(str(target).split()))
            data_dict['Whoxy'] = whoxy_data

    # -c argument logic
    if args.COMPANY is not None:
        target = args.COMPANY
        data_dir = check_directory(target, output_directory)
        if all([os.getenv('SERPER_API_KEY'), os.getenv('FIRECRAWL_API_KEY')]):
            res_one = verbatim_search(target)
            res_two = intext_search(target)
            res_thr = inurl_search(target)
            res_fou = intitle_search(target)
            results = join_results(res_one, res_two, res_thr, res_fou)
            uniques = remove_duplicates(results)
            scrape_links = extract_links(uniques)
            scraped_data = scraped_links(scrape_links)
            data_dict = process_data(scraped_data, target, output_directory)
        if os.getenv('WHOXY_API_KEY'):
            whoxy_data = search_whoxy('company', '+'.join(str(target).split()))
            data_dict['Whoxy'] = whoxy_data

    # Write data_dict to JSON file
    with open(os.path.join(data_dir, 'DATA.json'), 'w', encoding='utf-8') as f:
        json.dump(data_dict, f)
        print("\n" + Style.BRIGHT + Fore.GREEN + "[" + Fore.WHITE + "v" + Fore.GREEN + "]" + " DONE. " + Style.RESET_ALL + Fore.GREEN + f"Check" + Style.BRIGHT + f" {data_dir} " + Style.RESET_ALL + Fore.GREEN + "for " + Style.BRIGHT + f"DATA.json\n" + Style.RESET_ALL)

if __name__ == "__main__":
    main()