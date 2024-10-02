from osintr.modules.match_emails import match_emails, is_valid_email
from osintr.modules.report_generator import generate_html_report
from osintr.modules.match_urls import evaluate_urls
from firecrawl import FirecrawlApp
from colorama import Fore, Style
from dotenv import load_dotenv
from tqdm import tqdm
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
        print("\n" + Style.BRIGHT + Fore.YELLOW + "[" + Fore.WHITE + "!" + Fore.YELLOW + "]" + f" Writing '{target}' data to target directory ..." + Style.RESET_ALL)
    return directory

# Perform verbatim and inurl Google search on target
def google_search(target):
    url = "https://google.serper.dev/search"
    query = f"\"{target}\" OR inurl:\"{target}\""
    payload = json.dumps({
    "q": query,
    "num": 5,
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

# Scraping links with Firecrawl
def scraped_links(scrape_links, progress_bar=None):
    """
    Scrapes the provided list of URLs and optionally updates a given progress bar.
    """
    scrape_results = []
    for link in scrape_links:
        try:
            # Use tqdm.write to prevent interference with the progress bar
            tqdm.write(Fore.WHITE + " [" + Fore.GREEN + "+" + Fore.WHITE + "]" + Fore.GREEN + " Scraping " + Style.RESET_ALL + link)
            scraper = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))
            scrape_result = scraper.scrape_url(link, params={'formats': ['markdown', 'links', 'screenshot@fullPage']})
            scrape_results.append(scrape_result)
            time.sleep(1)
        except Exception as e:
            tqdm.write(Fore.WHITE + " [" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + ' Scraping not allowed for ' + Style.RESET_ALL + link + Style.BRIGHT + Fore.RED + " - skipping" + Style.RESET_ALL)
            continue
        
        # Ensure progress bar is updated even when a link fails
        if progress_bar is not None:
            progress_bar.update(1)

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
        ss_path = os.path.join(directory, 'screenshots')
        if not os.path.exists(ss_path):
            os.makedirs(ss_path)
        for url in all_image_urls:
            image_path = os.path.join(ss_path, 'ss_' + ''.join(random.choices(string.ascii_lowercase, k=5)) + '.png')
            save_screenshot(url, image_path)
    else:
        print(Fore.WHITE + "[" + Fore.RED + "-" + Fore.WHITE + "]" + Fore.RED + " No screenshots taken." + Style.RESET_ALL)

    print(Style.BRIGHT + Fore.WHITE + "[" + Fore.GREEN + "-" + Fore.WHITE + "]" + Fore.GREEN + " All Google search data was saved." + Style.RESET_ALL)
    return data_dict

# Determine the type of the target
def get_target_type(target):
    """Determine if the target is an email, username, or name/company."""
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    username_regex = r"^[a-zA-Z0-9_.-]+$"

    if re.fullmatch(email_regex, target):
        return "email"
    elif re.fullmatch(username_regex, target):
        return "username"
    else:
        return "name_company"
    
# Parsing CLI arguments
def arg_parsing():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
            examples:                 
            osintr -t jdoe95@example.com -o /home/bob/data
            osintr -t john.doe95 -o /home/bob/data
            osintr -t "John Doe" -o /home/bob/data
            osintr -t "Evil Corp Ltd" -o /home/bob/data                                                                  
            '''),
        epilog=textwrap.dedent('''\
            NOTE!
            For person or company names use double quotes to enclose the whole name.             
            '''))
    parser.add_argument('-t', dest='TARGET', help='Target of investigation', required=True)
    parser.add_argument('-o', dest='OUTPUT', help='Directory to save results', required=True)
    parser.add_argument('--max-depth', dest='DEPTH', type=int, default=2, help='Maximum recursion depth (default: 2)')
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

    # MAX_DEPTH argument
    max_depth = args.DEPTH

    return target, output_directory, max_depth

# Function for performing GRASS
def recursive_search_and_scrape(target, output, processed_targets=None, combined_data=None, depth=0, max_depth=2, initial_target_type=None, unified_progress_bar=None):
    """
    Main function that performs recursive searching and scraping based on the initial target type.
    """
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

    # Checking if directory exists and get the path
    directory = check_directory(target, output)

    # Loading environment variables
    load_dotenv()
    if not all([os.getenv('SERPER_API_KEY'), os.getenv('FIRECRAWL_API_KEY')]):
        print("\n" + Style.BRIGHT + Fore.RED + "[" + Fore.WHITE + "-" + Fore.RED + "]" + " API key(s) not found.\n" + Style.RESET_ALL)
        sys.exit()

    # Perform the search and scrape process
    results = google_search(target)
    uniques = remove_duplicates(results)
    scrape_links = extract_links(uniques)

    # If unified_progress_bar is None, create a new one for the first time
    if unified_progress_bar is None:
        unified_progress_bar = tqdm(total=len(scrape_links), desc="Scraping URLs and extracting data", unit="url")

    # Update the total count of the progress bar based on new links
    unified_progress_bar.total += len(scrape_links) - unified_progress_bar.n
    unified_progress_bar.refresh()

    # Perform scraping and update the unified progress bar
    scraped_data = scraped_links(scrape_links, progress_bar=unified_progress_bar)

    # Process the scraped data and update combined data
    data_dict = process_data(scraped_data, target, directory)

    # Update combined data with the newly collected emails and URLs
    combined_data['Email Addresses'].update(data_dict.get('Email Addresses', []))
    combined_data['URLs'].update(data_dict.get('URLs', []))

    # Display the emails found in this iteration
    found_emails = data_dict.get('Email Addresses', [])
    if found_emails:
        print(Style.BRIGHT + Fore.GREEN + f"\n[+] Emails found for target '{target}':" + Style.RESET_ALL)
        for idx, email in enumerate(found_emails, 1):
            print(f"    {idx}. {email}")
    else:
        print(Style.BRIGHT + Fore.YELLOW + f"\n[!] No emails found for target '{target}'." + Style.RESET_ALL)
        if depth == 0:
            print(Fore.YELLOW + f" [!] No emails identified during the initial search." + Style.RESET_ALL)
        return combined_data  # No emails to process further

    # Determine the type of the initial target
    if depth == 0:
        initial_target_type = get_target_type(target)
    else:
        initial_target_type = "email"  # Subsequent targets are emails

    # Automatic recursion for emails or usernames
    if initial_target_type in ["email", "username"]:
        matched_emails = set()
        print(Style.BRIGHT + Fore.GREEN + f"\n[+] Matching relevant emails to '{target}' and performing recursive search." + Style.RESET_ALL)

        # Create a progress bar for matching emails
        with tqdm(total=len(found_emails), desc="Matching Emails", unit="email") as email_match_bar:
            for email in found_emails:
                matches = match_emails(email, found_emails)
                matched_emails.update(matches)
                email_match_bar.update(1)

        # Remove already processed emails
        matched_emails = matched_emails - processed_targets

        # Recursively process each matched email
        for email in matched_emails:
            if email not in processed_targets and is_valid_email(email):
                recursive_search_and_scrape(email, output, processed_targets, combined_data, depth=depth+1, max_depth=max_depth, initial_target_type=initial_target_type, unified_progress_bar=unified_progress_bar)

    elif initial_target_type == "name_company":
        # User-guided recursion for company or name targets
        print(Style.BRIGHT + Fore.CYAN + "\n[i] Since the initial target is a name or company, please select which emails to recurse into:" + Style.RESET_ALL)
        selected_indices = input(Style.BRIGHT + Fore.YELLOW + "Your selection: " + Style.RESET_ALL)
        selected_indices = [int(idx.strip()) for idx in selected_indices.split(',') if idx.strip().isdigit()]
        selected_emails = [found_emails[idx - 1] for idx in selected_indices if 1 <= idx <= len(found_emails)]

        if selected_emails:
            for email in selected_emails:
                if email not in processed_targets and is_valid_email(email):
                    recursive_search_and_scrape(email, output, processed_targets, combined_data, depth=depth+1, max_depth=max_depth, initial_target_type=initial_target_type, unified_progress_bar=unified_progress_bar)

    # Close the unified progress bar once all tasks are completed
    unified_progress_bar.close()

    return combined_data

def main():
    # Parsing CLI arguments
    args = arg_parsing()
    initial_target = args[0]
    output_directory = args[1]
    max_depth = args[2]

    # Start recursive search and scrape
    combined_data = recursive_search_and_scrape(initial_target, output_directory, max_depth=max_depth)

    # Add 'OSINT Target' to combined_data
    combined_data['OSINT Target'] = initial_target
    
    # Convert sets to lists for final output
    combined_data['Email Addresses'] = list(combined_data['Email Addresses'])
    combined_data['URLs'] = sorted(list(combined_data['URLs']))

    # Now, perform URL relevance matching
    if combined_data['URLs']:
        print(Style.BRIGHT + Fore.GREEN + f"\n[+] Starting URL relevance matching in collected data." + Style.RESET_ALL)
        relevant_urls_with_scores = evaluate_urls(initial_target, combined_data['URLs'])
        # Adjust the threshold as needed. For example, 50:
        relevant_urls = [url for url, score in relevant_urls_with_scores if score >= 50]
        irrelevant_urls = list(set(combined_data['URLs']) - set(relevant_urls))

        # Update combined_data dictionary
        combined_data['Relevant URLs'] = relevant_urls
        combined_data['Other URLs'] = irrelevant_urls

        # Remove the 'URLs' key
        if 'URLs' in combined_data:
            del combined_data['URLs']

        # Display relevant URLs
        if relevant_urls:
            print(Style.BRIGHT + Fore.GREEN + f"\n[+] Relevant URLs found and saved." + Style.RESET_ALL)
            #for url in relevant_urls:
                #print(f"    - {url}")
        else:
            print(Fore.YELLOW + f"\n[!] No relevant URLs identified." + Style.RESET_ALL)
    else:
        print(Fore.YELLOW + f"\n[!] No URLs found to match." + Style.RESET_ALL)
        combined_data['Relevant URLs'] = []
        # 'URLs' key is already empty or as it was

    # Obtain the report directory once
    report_directory = check_directory(initial_target, output_directory)

    # Generate the HTML report
    report_output_path = os.path.join(report_directory, 'Final_Report.html')

    generate_html_report(combined_data, output_html_path=report_output_path)
    
    # Save (raw) combined data to a JSON file
    output_file = os.path.join(report_directory, 'Raw_Data.json')
    with open(output_file, 'w') as f:
        json.dump(combined_data, f, indent=2)

    print(Fore.GREEN + " [+] Raw data saved to " + Style.BRIGHT + f"{output_file}\n" + Style.RESET_ALL)

if __name__ == '__main__':
    main()