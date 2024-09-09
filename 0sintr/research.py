from langchain_community.utilities import GoogleSerperAPIWrapper
from email_validator import validate_email
from colorama import Fore, Style, init
from firecrawl import FirecrawlApp
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
def google_search_function(target_verbatim, target_intext, target_intitleurl, outputDir):
    # Check if osint_data directory exists, if not create it for the specified target
    dir_path = outputDir + "/osint_data_" + ''.join(char for char in str(target_verbatim) if char.isalnum())
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
        results_inurl = search_inurl.results(target_intitleurl)
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
    print(Fore.MAGENTA + "\n  |--- Unscrapeable URLs will be added to " + Style.BRIGHT + "/google/noScrapeLinks.txt\n" + Style.RESET_ALL)

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
    
    # Checking unscrapeable URLs
    with open(dir_path + '/google/noScrapeLinks.txt', 'r') as f:
        un_links = f.readlines()
    
    if len(un_links) == 0:
        print(Fore.MAGENTA + "\n  |--- All links scraped successfully.\n" + Style.RESET_ALL)
    else:
        print(Fore.MAGENTA + "\n  |--- Unscrapeable links added to " + Style.BRIGHT + "noScrapeLinks.txt.\n" + Style.RESET_ALL)
        print(Fore.MAGENTA + "  |--- " + Style.BRIGHT + "Suggestion! " + Style.RESET_ALL + Fore.MAGENTA + "Check the URLs manually to collect relevant data.\n" + Style.RESET_ALL)

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
    print(Style.BRIGHT + Fore.BLUE + "\n\n|---> Saving screenshots.\n" + Style.RESET_ALL)
    if len(all_urls) > 0:
        for url_pair in all_urls:
            file_no = 1
            save_path = os.path.join(save_directory, "ss_" + url_pair[1] + str(file_no) + ".png")
            if not os.path.exists(save_path):
                download_image(url_pair[0], save_path)
            else:
                save_bkp_path = os.path.join(save_directory, "ss_" + url_pair[1] + str(file_no + 1) + ".png")
                download_image(url_pair[0], save_bkp_path)
    else:
        print(Fore.BLUE + "  |--- No screenshots taken.\n" + Style.RESET_ALL)

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

        print(Fore.YELLOW + "\n  |--- Email addresses added to " + Style.BRIGHT + "emailAddresses.txt.\n" + Style.RESET_ALL)
        print(Fore.YELLOW + "  |--- " + Style.BRIGHT + "Suggestion! " + Style.RESET_ALL + Fore.YELLOW + "Check the file and re-run 0SINTr for relevant addresses.\n" + Style.RESET_ALL)

    else:
        print(Style.BRIGHT + Fore.YELLOW + "\n\n|---> No email addresses found:" + Style.RESET_ALL)
        with open(os.path.dirname(save_directory) + '/emailAddresses.txt', 'w') as f:
            f.write('No email addresses found.')


def search_breaches(target, directory):
    print(Style.BRIGHT + Fore.RED + "\n\n|---> Checking for breaches: " + Style.RESET_ALL)
    url = "https://haveibeenpwned.com/api/v3/breachedaccount/"
    headers = {"user-agent": "python-requests/2.32.3", "hibp-api-key": os.getenv("HIBP_API_KEY")} 
    response = requests.get(url + target + "?truncateResponse=false" + "?includeUnverified=true", headers=headers)

    if response.status_code == 200:
        breach_data = response.json()

        # Create new directory 
        dir_path = directory + "/osint_data_" + ''.join(char for char in str(target) if char.isalnum())
        if os.path.exists(path=dir_path):
            os.makedirs(dir_path + '/leaks/')

        # Write JSON data to directory
        with open(dir_path + '/leaks/breaches.json', 'w') as outfile:
            json.dump(breach_data, outfile)

        print(Fore.RED + "\n  |--- Breached data added to " + Style.BRIGHT + "/leaks/breaches.json" + Style.RESET_ALL)

    elif response.status_code == 401:
        print(Fore.RED + "\n  |--- Invalid API key or insufficient credits." + Style.RESET_ALL)

    elif response.status_code == 404:
        print(Fore.GREEN + "\n  |--- No breached data found for " + Style.BRIGHT + f"{target}" + Style.RESET_ALL)

    elif response.status_code == 429:
        print(Fore.RED + "\n  |--- Too Many Requests. Rate limit exceeded." + Style.RESET_ALL)

    else:
        print('    |- Error code: ' + str(response.status_code))


def search_pastes(target, directory):
    print(Style.BRIGHT + Fore.RED + "\n|---> Checking for pastes: " + Style.RESET_ALL)
    time.sleep(10) # Introducing sleep for 10 seconds to avoid statusCode 429
    url = "https://haveibeenpwned.com/api/v3/pasteaccount/"
    headers = {
        "user-agent": "python-requests/2.32.3", 
        "hibp-api-key": os.getenv("HIBP_API_KEY")
    } 
    response = requests.get(url + target, headers=headers)

    if response.status_code == 200:
        paste_data = response.json() 

        # Check leaks directory 
        dir_path = directory + "/osint_data_" + ''.join(char for char in str(target) if char.isalnum())
        if os.path.exists(path=dir_path) and not os.path.exists(path=dir_path + '/leaks/'):
            os.makedirs(dir_path + '/leaks/')

        # Write JSON data to directory
        with open(dir_path + '/leaks/pastes.json', 'w') as outfile:
            json.dump(paste_data, outfile)

        print(Fore.RED + "\n  |--- Paste data added to " + Style.BRIGHT + "/leaks/pastes.json\n" + Style.RESET_ALL)

    elif response.status_code == 401:
        print(Fore.RED + "\n  |--- Invalid API key or insufficient credits." + Style.RESET_ALL)

    elif response.status_code == 404:
        print(Fore.GREEN + "\n  |--- No paste data found for " + Style.BRIGHT + f"{target}\n" + Style.RESET_ALL)

    elif response.status_code == 429:
        print(Fore.RED + "\n  |--- Too Many Requests. Rate limit exceeded." + Style.RESET_ALL)

    else:
        print('    |- Error code: ' + str(response.status_code))


def osint_industries(target, directory):
    print(Style.BRIGHT + Fore.CYAN + "\n|---> Checking OSINT.Industries for data: " + Style.RESET_ALL)
    time.sleep(1) # Introducing sleep for 1 second
    if validate_email(target):
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

    if response.status_code == 200:
        osind_data = response.json() 

        # Check leaks directory 
        dir_path = directory + "/osint_data_" + ''.join(char for char in str(target) if char.isalnum())
        if os.path.exists(path=dir_path) and not os.path.exists(path=dir_path + '/osint_ind/'):
            os.makedirs(dir_path + '/osint_ind/')

        # Write JSON data to directory
        with open(dir_path + '/osint_ind/osind.json', 'w') as outfile:
            json.dump(osind_data, outfile)

        print(Fore.RED + "\n  |--- Data added to " + Style.BRIGHT + "/osint_ind/osind.json\n" + Style.RESET_ALL)

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

def research():
    parser = argparse.ArgumentParser(description='Run 0sintr with the following arguments.')
    parser.add_argument('-t', '--target', help='Target email address or username', required=True)
    parser.add_argument('-o', '--output', help='Directory to save results, full path', required=True)
    args = parser.parse_args()

    # -o argument logic
    if args.output is not None:
        outputDir = args.output
    else:
        parser.print_usage()

    # -t argument logic
    if args.target is not None:
        target = args.target

        # # Initializing colorama
        init()

        # Running the Google search function
        target_verbatim = target
        target_intext = f"intext:\"{target}\""
        target_inurl = f"inurl:\"{target}\""
        target_intitle = f"intitle:\"{target}\""

        # For email addresses, use verbatim, intext and intitle
        if validate_email(target):
            print(Style.BRIGHT + Fore.CYAN + f"\n\n|---> Running search for email address: {target_verbatim}" + Style.RESET_ALL)
            print(Fore.CYAN + "\n  |--- Search modes: verbatim, intext, intitle" + Style.RESET_ALL)
            md_directory = google_search_function(target_verbatim, target_intext, target_intitle, outputDir)
        else:
            print(Style.BRIGHT + Fore.CYAN + f"\n\n|---> Running search for username: {target_verbatim}" + Style.RESET_ALL)
            print(Fore.CYAN + "\n  |--- Search modes: verbatim, intext, inurl" + Style.RESET_ALL)
            md_directory = google_search_function(target_verbatim, target_intext, target_inurl, outputDir)

        # Defining the directories to pass to process_md_files()
        directory = md_directory
        save_directory = os.path.dirname(md_directory) + '/screenshots'

        # Process all .md files in the specified directory
        process_md_files(directory, save_directory)

        # Run the data leak detection functions, first is breach detection
        search_breaches(target, outputDir)

        # Differentiating between email addresses and usernames for paste checking
        if validate_email(target):
            search_pastes(target, outputDir)
        else:
            print(Fore.YELLOW + "\n\n|---> Since you provided a username, I will check pastes for " + Style.BRIGHT + f"{target}@gmail.com" + Style.RESET_ALL)
            search_pastes(target + "@gmail.com", outputDir)

        # Running the OSINT.Industries data collection, as an option
        load_dotenv()
        if os.getenv["OSIND_API_KEY"] is not None:
            osint_industries(target, outputDir)
        else:
            print(Style.BRIGHT + Fore.RED + "\n|---> No OSINT.Industries API key found." + Style.RESET_ALL)
            print(Fore.YELLOW + "\n  |--- Moving on to the Analysis phase without OSINT.Industries data." + Style.RESET_ALL)

    else:
        parser.print_usage()

    # Kick off the crew process
    print(Style.BRIGHT + Fore.GREEN + "\n\n|---> Starting the AI analysis, please wait. This may take a while." + Style.RESET_ALL)

    # Return the target string, md_directory (.../osint_<target>/google/scarpes) and main directory (.../osint_<target>/)
    return target, md_directory, os.path.dirname(os.path.dirname(save_directory))

if __name__ == "__main__":
    research()