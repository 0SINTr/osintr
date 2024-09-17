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
import time
import sys
import os
import re

# Check if osint_ directory exists, if not create it
def check_directory(target, directory):
    directory = os.path.join(directory, "osint_data_" + ''.join(char for char in str(target) if char.isalnum()))
    if not os.path.exists(path=directory):
        os.makedirs(directory)
        return directory
    else:
        print(Style.BRIGHT + Fore.RED + "\n|---> Directory already exists. Delete it or change path.\n" + Style.RESET_ALL)
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
        sys.exit(Fore.RED + f"\n  |--- Quitting. Error during Google search: {str(e)}" + Style.RESET_ALL)
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
        sys.exit(Fore.RED + f"\n  |--- Quitting. Error during Google search: {str(e)}" + Style.RESET_ALL)
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
        sys.exit(Fore.RED + f"\n  |--- Quitting. Error during Google search: {str(e)}" + Style.RESET_ALL)
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
        sys.exit(Fore.RED + f"\n  |--- Quitting. Error during Google search: {str(e)}" + Style.RESET_ALL)
    return search_results

# Join all search results into a list
def join_results(res_one, res_two, res_thr, *res):
    results = list(chain(res_one, res_two, res_thr))
    return results

# Remove duplicate search results
def remove_duplicates(results):
    df = pd.DataFrame(results).drop_duplicates('title')
    unique_data = df.to_dict(orient='records')
    return unique_data

# Extracting links from search results
def extract_links(unique_data):
    scrape_links = []
    for entry in unique_data:
        if 'gov' not in entry['link']:
            scrape_links.append(entry['link'])
    return scrape_links

# Scarping links with Firecrawl
def scrape_links(scrape_links):
    scrape_results = []
    for link in scrape_links:
        try:
            scraper = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))
            scrape_result = scraper.scrape_url(link, params={'formats': ['markdown', 'links', 'screenshot@fullPage']})
            scrape_results.append(scrape_result)
            time.sleep(1)
        except Exception as e:
            print(Fore.RED + '    |- Error scraping ' + Style.BRIGHT + link + Style.RESET_ALL)
            continue
    return scrape_results

# Extract emails and links from results
def extract_data(scrape_result):
    # Image URL
    image_url = scrape_result['screenshot']
    if image_url and str(image_url).startswith('http'):
        image_url = image_url

    # Source URL
    source_url = scrape_result['metadata']['sourceURL']

    # All URLs
    all_urls = scrape_result['links']

    # Email addresses
    emails = re.findall(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]{3,}\.[a-zA-Z0-9-.]+)", str(scrape_result))

    return image_url, emails, all_urls

# Saving screenshots via image URLs
def save_screenshot(image_url, directory):
    try:
        response = requests.get(image_url)
        # Check if the request was successful
        response.raise_for_status() 
        with open(directory, 'wb') as file:
            file.write(response.content)
        print("    |- Image saved as: " + Fore.YELLOW + f"{directory}" + Style.RESET_ALL)
    except requests.exceptions.RequestException:
        print(Fore.RED + "    |- Request exception. Failed to retrieve image " + Style.BRIGHT + f"{image_url}" + Style.RESET_ALL + " - skipping")
    except requests.exceptions.MissingSchema:
        print(Fore.RED + "    |- Missing schema. Failed to retrieve image, link invalid: " + Style.BRIGHT + f"{image_url}" + Style.RESET_ALL + " - skipping")
    except requests.exceptions.Timeout:
        print(Fore.RED + "    |- Connection timed out. Failed to retrieve image " + Style.BRIGHT + f"{image_url}" + Style.RESET_ALL + " - skipping")

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
    print(Style.BRIGHT + Fore.YELLOW + "\n|---> Extracting data from Google advanced search ..." + Style.RESET_ALL)
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
        emails = extract_data[1]
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
        ss_path = os.path.join(directory, 'screenshots')
        if not os.path.exists(ss_path):
            os.makedirs(ss_path)
        for url in all_image_urls:
            image_path = os.path.join(ss_path, 'ss_' + ''.join(random.choices(string.ascii_lowercase, k=5)) + '.png')
            save_screenshot(url, image_path)
    else:
        print(Fore.RED + "  |--- No screenshots taken.\n" + Style.RESET_ALL)

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
        print(Style.BRIGHT + Fore.YELLOW + "\n\n|---> Email addresses found:\n" + Style.RESET_ALL)
        for email in set(unzipped_email_list):
            print(f"    |- {email}")
    else:
        data_dict['Email Addresses'] = []
        print(Style.BRIGHT + Fore.RED + "\n\n|---> No email addresses found:" + Style.RESET_ALL)

    # Writing all other emails as secondary emails to data_dict
    all_unique_emails = set(all_emails)
    all_unique_main_emails = set(all_main_emails)
    diff = all_unique_emails.difference(all_unique_main_emails)
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
        data_dict['Relevant Links'] = list(set(all_main_urls))
    else:
        data_dict['Relevant Links'] = []

    # Writing all other URLs as secondary links to data_dict
    all_unique_urls = set(all_urls)
    all_unique_main_urls = set(all_main_urls)
    diff = all_unique_urls.difference(all_unique_main_urls)
    data_dict['Possibly Related Links'] = list(diff)

    print(Fore.GREEN + "\n  |--- Google search data found and saved.\n" + Style.RESET_ALL)
    return data_dict

# Search for breaches in HIBP data
def search_breaches(target):
    print(Style.BRIGHT + Fore.YELLOW + "\n\n|---> Checking HIBP for breaches ..." + Style.RESET_ALL)
    url = "https://haveibeenpwned.com/api/v3/breachedaccount/"
    headers = {"user-agent": "python-requests/2.32.3", "hibp-api-key": os.getenv("HIBP_API_KEY")} 
    response = requests.get(url + target + "?truncateResponse=false" + "?includeUnverified=true", headers=headers)

    # Check HIBP response (pastes)
    if response.status_code == 200:
        print(Fore.GREEN + "\n  |--- HIBP breach data found and saved.\n" + Style.RESET_ALL)
        breach_data = response.json()
        return breach_data
    elif response.status_code == 401:
        print(Fore.RED + "\n  |--- Invalid API key or insufficient credits." + Style.RESET_ALL)
    elif response.status_code == 404:
        print(Fore.RED + "\n  |--- No HIBP breached data found for " + Style.BRIGHT + f"{target}" + Style.RESET_ALL)
    elif response.status_code == 429:
        print(Fore.RED + "\n  |--- Too Many Requests. Rate limit exceeded." + Style.RESET_ALL)
    else:
        print('    |- Error code: ' + str(response.status_code))

# Search for pastes in HIBP data
def search_pastes(target):
    print(Style.BRIGHT + Fore.YELLOW + "\n|---> Checking HIBP for pastes ..." + Style.RESET_ALL)
    time.sleep(10) # Introducing sleep for 10 seconds to avoid statusCode 429
    url = 'https://haveibeenpwned.com/api/v3/pasteaccount/'
    headers = {
        'user-agent': 'python-requests/2.32.3', 
        'hibp-api-key': os.getenv('HIBP_API_KEY')
    } 
    response = requests.get(url + target, headers=headers)

    # Check HIBP response (pastes)
    if response.status_code == 200:
        print(Fore.GREEN + "\n  |--- HIBP paste data found and saved.\n" + Style.RESET_ALL)
        paste_data = response.json() 
        return paste_data
    elif response.status_code == 401:
        print(Fore.RED + "\n  |--- Invalid API key or insufficient credits." + Style.RESET_ALL)
    elif response.status_code == 404:
        print(Fore.RED + "\n  |--- No HIBP paste data found for " + Style.BRIGHT + f"{target}\n" + Style.RESET_ALL)
    elif response.status_code == 429:
        print(Fore.RED + "\n  |--- Too Many Requests. Rate limit exceeded." + Style.RESET_ALL)
    else:
        print('    |- Error code: ' + str(response.status_code))

# Search for data from OSINT.Industries
def osint_industries(target):
    print(Style.BRIGHT + Fore.YELLOW + "\n|---> Checking OSINT.Industries for data ..." + Style.RESET_ALL)
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
        print(Fore.GREEN + "\n  |--- OSINT.Industries data found and saved.\n" + Style.RESET_ALL)
        osind_data = response.json()
        return osind_data
    elif response.status_code == 400:
        print(Fore.RED + "\n  |--- Bad Request. Invalid query value." + Style.RESET_ALL)
    elif response.status_code == 401:
        print(Fore.RED + "\n  |--- Invalid API key or insufficient credits. Check your key and try again." + Style.RESET_ALL)
    elif response.status_code == 404:
        print(Fore.RED + "\n  |--- No data found for " + Style.BRIGHT + f"{target}\n" + Style.RESET_ALL)
    elif response.status_code == 429:
        print(Fore.RED + "\n  |--- Too Many Requests. Rate limit exceeded." + Style.RESET_ALL)
    else:
        print('    |- Error code: ' + str(response.status_code))

def search_whoxy(target, target_type):
    print(Style.BRIGHT + Fore.CYAN + "\n|---> Checking Whoxy for reverse whois data ..." + Style.RESET_ALL)
    # API key
    whoxy_key = os.getenv('WHOXY_API_KEY')
    url = 'https://api.whoxy.com/?key=xxxxx&reverse=whois&'

# Main function
def main():
    parser = argparse.ArgumentParser(
        description='Run osintr with the following arguments.',
        epilog=textwrap.dedent('''\
            additional information:
                For person and company name use double quotes to enclose the whole name.
            '''
        ))
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-e', '--email', help='Target email address')
    group.add_argument('-u', '--user', help='Target username')
    group.add_argument('-p', '--phone', help='Target phone number')
    group.add_argument('-n', '--name', help='Target person name')
    group.add_argument('-c', '--company', help='Target company name')
    parser.add_argument('-o', '--output', help='Directory to save results', required=True)
    args = parser.parse_args()

    # -o argument logic
    if args.output is not None:
        output_directory = str(args.output).rstrip('/')
    else:
        parser.print_help()

    # Loading env variables
    load_dotenv()

    # Initalizing colorama
    init()

    # -e argument logic
    if args.email is not None:
        target = args.email
        is_valid_email = check(target)
        if is_valid_email:
            check_directory()
            res_one = verbatim_search()
            res_two = intext_search()
            res_thr = intitle_search()
            results = join_results(res_one, res_two, res_thr)
            uniques = remove_duplicates(results)
            scrape_links = extract_links(uniques)
            scraped_data = scrape_links(scrape_links)
            data_dict = process_data(scraped_data, target, output_directory)
            breach_data = search_breaches(target)
            data_dict['Breaches'] = breach_data
            paste_data = search_pastes(target)
            data_dict['Pastes'] = paste_data
            if os.getenv("OSIND_API_KEY") is not None:
                osind_data = osint_industries(target)
                data_dict['OSINDUS'] = osind_data
        else:
            print(Fore.RED + "\n  |--- Invalid email address." + Style.RESET_ALL)
            sys.exit()

    # -u argument logic
    if args.user is not None:
        target = args.user
        check_directory()
        res_one = verbatim_search()
        res_two = intext_search()
        res_thr = inurl_search()
        results = join_results(res_one, res_two, res_thr)
        uniques = remove_duplicates(results)
        scrape_links = extract_links(uniques)
        scraped_data = scrape_links(scrape_links)
        data_dict = process_data(scraped_data, target, output_directory)
        breach_data = search_breaches(target)
        data_dict['Breaches'] = breach_data
        paste_data = search_pastes(target + "@gmail.com")
        data_dict['Pastes'] = paste_data
        if os.getenv("OSIND_API_KEY") is not None:
            osind_data = osint_industries(target)
            data_dict['OSINDUS'] = osind_data

    # -p argument logic
    if args.phone is not None:
        target = args.phone
        check_directory()
        res_one = verbatim_search()
        res_two = intext_search()
        res_thr = inurl_search()
        res_fou = intitle_search()
        results = join_results(res_one, res_two, res_thr, res_fou)
        uniques = remove_duplicates(results)
        scrape_links = extract_links(uniques)
        scraped_data = scrape_links(scrape_links)
        data_dict = process_data(scraped_data, target, output_directory)
        if os.getenv("OSIND_API_KEY") is not None:
            osind_data = osint_industries(target)
            data_dict['OSINDUS'] = osind_data

    # -n argument logic
    if args.name is not None:
        target = args.name
        check_directory()
        res_one = verbatim_search()
        res_two = intext_search()
        res_thr = inurl_search()
        res_fou = intitle_search()
        results = join_results(res_one, res_two, res_thr, res_fou)
        uniques = remove_duplicates(results)
        scrape_links = extract_links(uniques)
        scraped_data = scrape_links(scrape_links)
        data_dict = process_data(scraped_data, target, output_directory)

    # -c argument logic
    if args.company is not None:
        target = args.company
        check_directory()
        res_one = verbatim_search()
        res_two = intext_search()
        res_thr = inurl_search()
        res_fou = intitle_search()
        results = join_results(res_one, res_two, res_thr, res_fou)
        uniques = remove_duplicates(results)
        scrape_links = extract_links(uniques)
        scraped_data = scrape_links(scrape_links)
        data_dict = process_data(scraped_data, target, output_directory)

if __name__ == "__main__":
    main()