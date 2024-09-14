from langchain_community.utilities import GoogleSerperAPIWrapper
from colorama import Fore, Style, init
from firecrawl import FirecrawlApp
from itertools import product
from dotenv import load_dotenv
import pandas as pd
import argparse
import requests
import time
import json
import sys
import os
import re

# Function to perform the Google search and scrape each page related to the target
def google_search_function(target_verbatim, target_intext, target_intitleurl, output_directory):
    # Check if osint_data directory exists, if not create it for the specified target, plus 'raw' directory
    directory = os.path.join(output_directory, "osint_data_" + ''.join(char for char in str(target_verbatim) if char.isalnum()))
    if not os.path.exists(path=directory):
        os.makedirs(os.path.join(directory, 'raw'))
    else:
        print(Style.BRIGHT + Fore.RED + "\n\n|---> Directory already exists. Delete it or change path.\n" + Style.RESET_ALL)
        sys.exit()

    # Perform a verbatim Google search (tbs value) and return the results
    search_verbatim = GoogleSerperAPIWrapper(tbs="li:1", k=20)
    search_intext = GoogleSerperAPIWrapper(k=20)
    search_inurl = GoogleSerperAPIWrapper(k=20)

    all_search_results = []
    try:
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
        results_inurl = search_inurl.results(target_intitleurl)
        if results_inurl:
            for result in results_inurl['organic']:
                all_search_results.append(result)

        # Removing duplicates
        df = pd.DataFrame(all_search_results).drop_duplicates('title')
        unique_json_data = df.to_dict(orient='records')
        print(Fore.CYAN + "\n  |--- Removing duplicates from search results.\n" + Style.RESET_ALL)
        print(Fore.CYAN + f"  |--- Total duplicates removed: {len(all_search_results)-len(unique_json_data)}, Final items: {len(unique_json_data)}" + Style.RESET_ALL)

        # Create and save the JSON file with unique search results
        raw_data_directory = os.path.join(directory, 'raw')
        with open(os.path.join(raw_data_directory, 'google_search.json'), 'w', encoding='utf-8') as outfile:
            json.dump(unique_json_data, outfile)

    except Exception as e:
        # Handle any errors that occur during the search
        print(Fore.RED + f"  |--- Error during Google search: {str(e)}" + Style.RESET_ALL)
        sys.exit(Fore.RED + "\n  |--- Quitting." + Style.RESET_ALL)
    
    # Introducing sleep for 3 seconds
    time.sleep(3)

    # Checking the number of search results
    if len(all_search_results) == 0:
        print(Fore.RED + "\n  |--- No Google results found for " + Style.BRIGHT + f"{target_verbatim}" + Style.RESET_ALL)
        return raw_data_directory
    else:
        print(Fore.GREEN + "\n  |--- Search DONE. All data goes to " + Style.BRIGHT + f"{directory}" + Style.RESET_ALL)

        # Extracting all the links from search results
        links = []
        noScrape_links = []
        for entry in unique_json_data:
            if 'gov' not in entry['link']:
                links.append(entry['link'])
            else:
                with open(os.path.join(directory, 'raw', 'unscrapeable_urls.txt'), 'a') as f:
                    f.write(entry['link'] + '\n')
        print(Style.BRIGHT + Fore.MAGENTA + "\n\n|---> Starting to scrape." + Style.RESET_ALL)
        print(Fore.MAGENTA + "\n  |--- Unscrapeable URLs (if any) will be added to " + Style.BRIGHT + "unscrapeable_urls.txt\n" + Style.RESET_ALL)
        
        # Initialize the Firecrawl scraper
        for index, url in enumerate(links):
            try:
                scraper = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))
                scrape_result = scraper.scrape_url(url, params={'formats': ['markdown', 'links', 'screenshot@fullPage']})

                # Write the scrape results to separate files
                with open(os.path.join(raw_data_directory, 'page' + str(index + 1) + '.md'), 'w', encoding='utf-8') as outfile:
                    outfile.write(str(scrape_result))
                print('    |- File scrape' + str(index + 1) + '.md DONE.')

                # Introducing sleep for 3 seconds
                time.sleep(3)

            except Exception as e:
                print(Fore.RED + '    |- Error scraping ' + Style.BRIGHT + url + Style.RESET_ALL)
                noScrape_links.append(url)
                with open(os.path.join(directory, 'raw', 'noScrapeLinks.txt'), 'a') as f:
                    f.write(url + '\n')
                continue
        
        # Checking scraped and unscrapeable URLs
        if len(links) > 0 and len(noScrape_links) > 0:
            print(Fore.YELLOW + "\n  |--- Scraping DONE, but not for all links." + Style.RESET_ALL)
            print(Fore.MAGENTA + "\n  |--- Unscrapeable links added to " + Style.BRIGHT + "noScrapeLinks.txt.\n" + Style.RESET_ALL)
            print(Fore.MAGENTA + "  |--- " + Style.BRIGHT + "Suggestion! " + Style.RESET_ALL + Fore.MAGENTA + "Check these URLs manually to collect data." + Style.RESET_ALL)
        elif len(links) > 0 and len(noScrape_links) == 0:
            print(Fore.GREEN + "\n  |--- All links scraped successfully.\n" + Style.RESET_ALL)
        elif len(links) == 0:
            print(Fore.RED + "  |--- No links to scrape." + Style.RESET_ALL)

        return raw_data_directory

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

# Function to extract relevant data from a markdown file
def extract_md_data(md_file_path):
    #print(f"Processing file: {md_file_path}")
    with open(md_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # Load the content in proper format
        res = eval(content)

    # Getting and checking the image URL
    image_url = res.get('screenshot')
    if image_url and str(image_url).startswith('http'):
        #print(f"Extracted URLs from {md_file_path}: {image_url}")
        image_url = image_url

    # Getting the source URL from metadata
    source_url = res['metadata']['sourceURL']

    # Getting all the URLs from the file
    all_urls = res.get('links')

    # Compiling a list of 2 URLs
    urls = [image_url, source_url]

    # Extract email addresses from .md file. Adding {3,} to avoid @2x style notations for image sizes
    emails = re.findall(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]{3,}\.[a-zA-Z0-9-.]+)", content)
    return urls, emails, all_urls

# Download the page screenshot and save it
def download_image(image_url, directory):
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # Check if the request was successful
        with open(directory, 'wb') as file:
            file.write(response.content)
        print("    |- Image saved as: " + Fore.YELLOW + f"{directory}" + Style.RESET_ALL)
    except requests.exceptions.RequestException:
        print(Fore.RED + "    |- Request exception. Failed to retrieve image " + Style.BRIGHT + f"{image_url}" + Style.RESET_ALL + " - skipping")
    except requests.exceptions.MissingSchema:
        print(Fore.RED + "    |- Missing schema. Failed to retrieve image, link invalid: " + Style.BRIGHT + f"{image_url}" + Style.RESET_ALL + " - skipping")
    except requests.exceptions.Timeout:
        print(Fore.RED + "    |- Connection timed out. Failed to retrieve image " + Style.BRIGHT + f"{image_url}" + Style.RESET_ALL + " - skipping")

# Process all .md files in the scraped directory
def process_md_files(target, directory):
    # Iterate over all .md files in the directory and extract image URLs and email addresses
    data_dict = {}
    all_emails = []
    all_image_urls = []
    all_urls = []
    all_aliases = []
    for md_file_name in os.listdir(directory):
        if str(md_file_name).endswith('.md'):
            try:
                # Extract image URLs
                md_file_path = os.path.join(directory, md_file_name)
                extraction_result = extract_md_data(md_file_path)
                image_url = extraction_result[0][0]
                source_url = extraction_result[0][1]
                domain_pattern = r"(https?://)?(www\d?\.)?(?P<domain>[\w\.-]+\.\w+)(/\S*)?"
                match = re.match(domain_pattern, source_url)
                source_url = match.group('domain')
                all_image_urls.append([image_url, str(source_url).replace('.','_')])

                # Extract email addresses
                emails = extraction_result[1]
                for email in emails:
                    all_emails.append(email)

                # Extract all URLs
                urls = extraction_result[2]
                for url in urls:
                    all_urls.append(url)

                # Extract leet aliases
                possible_aliases = detect_aliases(target)
                if len(possible_aliases) > 0:
                    for alias in possible_aliases:
                        if any(alias in sub for sub in email) or any(alias in sub for sub in urls):
                            all_aliases.append(alias)
                else:
                    continue
            except Exception as e:
                print(Fore.RED + f"  |--- Error processing file {md_file_name}: {e}\n" + Style.RESET_ALL)
                continue

    # Iterate over all found image URLs
    print(Style.BRIGHT + Fore.BLUE + "\n\n|---> Saving screenshots.\n" + Style.RESET_ALL)
    if len(all_image_urls) > 0:
        for url_pair in all_image_urls:
            file_no = 1
            ss_path = os.path.join(directory, "ss_" + url_pair[1] + str(file_no) + ".png")
            if not os.path.exists(ss_path):
                download_image(url_pair[0], ss_path)
            else:
                ss_bkp_path = os.path.join(directory, "ss_" + url_pair[1] + str(file_no + 1) + ".png")
                download_image(url_pair[0], ss_bkp_path)
    else:
        print(Fore.RED + "  |--- No screenshots taken.\n" + Style.RESET_ALL)

    # Iterate over all found email addresses
    filtered_email_list = []
    for email in all_emails:
        if type(email) is list:
            for item in email:
                filtered_email_list.append(item)
        else:
            filtered_email_list.append(email)

    # Extract email addresses from .json file
    with open(os.path.join(directory, 'google_search.json'), 'r', encoding='utf-8') as f:
        content = f.read()   
    regex = r"['\"\[\(\{]?\s*(?:mailto:)?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\s*['\"\]\)\}]?"
    emails_from_json = re.findall(regex, content)
    filtered_email_list += emails_from_json

    # Listing all possible aliases
    possible_aliases = detect_aliases(target)

    # Writing all the emails containing the target or target leet to data_dict
    all_main_emails = []
    if len(filtered_email_list) > 0:
        # Check leet target in each link
        if len(possible_aliases) > 0:
            for alias in possible_aliases:
                for email in filtered_email_list:
                    if alias in email:
                        all_main_emails.append(email)
        data_dict['Relevant Email Addresses'] = list(set(all_main_emails))

        # Print out the email addresses
        print(Style.BRIGHT + Fore.YELLOW + "\n\n|---> Email addresses found:\n" + Style.RESET_ALL)
        for email in set(filtered_email_list):
            print(f"    |- {email}")
        print(Fore.GREEN + "\n  |--- Email addresses will be saved to " + Style.BRIGHT + "DATA.json.\n" + Style.RESET_ALL)
        print(Fore.YELLOW + "  |--- " + Style.BRIGHT + "Suggestion! " + Style.RESET_ALL + Fore.YELLOW + "Check the file and re-run 0SINTr for relevant addresses." + Style.RESET_ALL)
    else:
        data_dict['Email Addresses'] = []
        print(Style.BRIGHT + Fore.RED + "\n\n|---> No email addresses found:" + Style.RESET_ALL)

    # Writing all other URLs as secondary links to data_dict
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
    return data_dict

# Search for breaches in HIBP data
def search_breaches(target):
    print(Style.BRIGHT + Fore.YELLOW + "\n\n|---> Checking for breaches: " + Style.RESET_ALL)
    url = "https://haveibeenpwned.com/api/v3/breachedaccount/"
    headers = {"user-agent": "python-requests/2.32.3", "hibp-api-key": os.getenv("HIBP_API_KEY")} 
    response = requests.get(url + target + "?truncateResponse=false" + "?includeUnverified=true", headers=headers)

    # Check HIBP response (pastes)
    if response.status_code == 200:
        print(Fore.GREEN + "\n  |--- Breach data found and saved.\n" + Style.RESET_ALL)
        breach_data = response.json()
        return breach_data
    elif response.status_code == 401:
        print(Fore.RED + "\n  |--- Invalid API key or insufficient credits." + Style.RESET_ALL)
    elif response.status_code == 404:
        print(Fore.RED + "\n  |--- No breached data found for " + Style.BRIGHT + f"{target}" + Style.RESET_ALL)
    elif response.status_code == 429:
        print(Fore.RED + "\n  |--- Too Many Requests. Rate limit exceeded." + Style.RESET_ALL)
    else:
        print('    |- Error code: ' + str(response.status_code))

# Search for pastes in HIBP data
def search_pastes(target):
    print(Style.BRIGHT + Fore.YELLOW + "\n|---> Checking for pastes: " + Style.RESET_ALL)
    time.sleep(10) # Introducing sleep for 10 seconds to avoid statusCode 429
    url = "https://haveibeenpwned.com/api/v3/pasteaccount/"
    headers = {
        "user-agent": "python-requests/2.32.3", 
        "hibp-api-key": os.getenv("HIBP_API_KEY")
    } 
    response = requests.get(url + target, headers=headers)

    # Check HIBP response (pastes)
    if response.status_code == 200:
        print(Fore.GREEN + "\n  |--- Paste data found and saved.\n" + Style.RESET_ALL)
        paste_data = response.json() 
        return paste_data
    elif response.status_code == 401:
        print(Fore.RED + "\n  |--- Invalid API key or insufficient credits." + Style.RESET_ALL)
    elif response.status_code == 404:
        print(Fore.RED + "\n  |--- No paste data found for " + Style.BRIGHT + f"{target}\n" + Style.RESET_ALL)
    elif response.status_code == 429:
        print(Fore.RED + "\n  |--- Too Many Requests. Rate limit exceeded." + Style.RESET_ALL)
    else:
        print('    |- Error code: ' + str(response.status_code))

# Search for data from OSINT.Industries
def osint_industries(target):
    print(Style.BRIGHT + Fore.CYAN + "\n|---> Checking OSINT.Industries for data: " + Style.RESET_ALL)
    time.sleep(1) # Introducing sleep for 1 second
    is_valid_email = check(target)
    if is_valid_email:
        target_type = 'email'
    else:
        target_type = 'username'

    url = "https://api.osint.industries/v2/request"
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
        print(Fore.YELLOW + "\n  |--- Moving on to the Analysis phase without OSINT.Industries data." + Style.RESET_ALL)
    elif response.status_code == 401:
        print(Fore.RED + "\n  |--- Invalid API key or insufficient credits. Check your key and try again." + Style.RESET_ALL)
        print(Fore.YELLOW + "\n  |--- Moving on to the Analysis phase without OSINT.Industries data." + Style.RESET_ALL)    
    elif response.status_code == 404:
        print(Fore.RED + "\n  |--- No data found for " + Style.BRIGHT + f"{target}\n" + Style.RESET_ALL)
    elif response.status_code == 429:
        print(Fore.RED + "\n  |--- Too Many Requests. Rate limit exceeded." + Style.RESET_ALL)
    else:
        print('    |- Error code: ' + str(response.status_code))

# Main research function
def research():
    parser = argparse.ArgumentParser(description='Run 0sintr with the following arguments.')
    parser.add_argument('-t', '--target', help='Target email address or username', required=True)
    parser.add_argument('-o', '--output', help='Directory to save results, full path', required=True)
    args = parser.parse_args()

    # -o argument logic
    if args.output is not None:
        output_directory = str(args.output).rstrip('/')
    else:
        parser.print_help()

    # -t argument logic
    if args.target is not None:
        target = args.target

        # Initializing colorama and env variables
        init()
        load_dotenv()

        # Running the Google search function
        target_verbatim = target
        target_intext = f"intext:\"{target}\""
        target_inurl = f"inurl:\"{target}\""
        target_intitle = f"intitle:\"{target}\""

        # For email addresses, use verbatim, intext and intitle
        is_valid_email = check(target)
        if is_valid_email:
            print(Style.BRIGHT + Fore.CYAN + f"\n\n|---> Running search for email address: {target_verbatim}" + Style.RESET_ALL)
            print(Fore.CYAN + "\n  |--- Search modes: verbatim, intext, intitle" + Style.RESET_ALL)
            directory = google_search_function(target_verbatim, target_intext, target_intitle, output_directory)
        # For usernames, use verbatim, intext and inurl
        else:
            if " " in target:
                print(Fore.RED + "\n|---> Target format incorrect: " + Style.BRIGHT + f"{target_verbatim}\n" + Style.RESET_ALL)
                sys.exit()
            else:
                print(Style.BRIGHT + Fore.CYAN + f"\n\n|---> Running search for username: {target_verbatim}" + Style.RESET_ALL)
                print(Fore.CYAN + "\n  |--- Search modes: verbatim, intext, inurl" + Style.RESET_ALL)
                directory = google_search_function(target_verbatim, target_intext, target_inurl, output_directory)

        if len(os.listdir(directory)) == 0:
            print(Fore.RED + "\n  |--- No .md files to process." + Style.RESET_ALL)
        else:
            # Process all .md files in the specified directory
            data_dict = process_md_files(target, directory)

        # Run the data leak detection functions, first is breach detection
        breach_data = search_breaches(target)
        data_dict['Breaches'] = breach_data

        # Differentiating between email addresses and usernames for paste checking
        if is_valid_email:
            paste_data = search_pastes(target)
        else:
            print(Fore.YELLOW + "\n\n|---> Since you provided a username, I will check pastes for " + Style.BRIGHT + f"{target}@gmail.com" + Style.RESET_ALL)
            paste_data = search_pastes(target + "@gmail.com")
        data_dict['Pastes'] = paste_data

        # Running the OSINT.Industries data collection
        if os.getenv("OSIND_API_KEY") is not None:
            osind_data = osint_industries(target)
            data_dict['OSINDUS'] = osind_data
        else:
            print(Style.BRIGHT + Fore.RED + "\n|---> No OSINT.Industries API key found." + Style.RESET_ALL)
            print(Fore.YELLOW + "\n  |--- Moving on without OSINT.Industries data." + Style.RESET_ALL)

        # Write data_dict to JSON file
        with open(os.path.join(os.path.dirname(directory), 'DATA.json'), 'w', encoding='utf-8') as f:
            json.dump(data_dict, f)
    else:
        parser.print_help()

    # Return the target and main directory (.../osint_<target>/)
    return target, output_directory

if __name__ == "__main__":
    research()