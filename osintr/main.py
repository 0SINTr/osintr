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
        print("\n" + Style.BRIGHT + Fore.CYAN + "[i] Putting OSINTr to work." + Style.RESET_ALL)
        os.makedirs(directory)
    else:
        print("\n" + Style.BRIGHT + Fore.CYAN + f"[i] Writing " + Fore.YELLOW + f"{target}" + Fore.CYAN + " data to target directory." + Style.RESET_ALL)
    return directory

# Perform verbatim and inurl Google search on target
def google_search(target):
    url = "https://google.serper.dev/search"
    query = f"\"{target}\" OR inurl:\"{target}\""
    payload = json.dumps({
        "q": query,
        "num": 20,
        "autocorrect": False
    })
    headers = {
        'X-API-KEY': os.getenv('SERPER_API_KEY'),
        'Content-Type': 'application/json'
    }

    try:
        search_results = []
        results = requests.request("POST", url, headers=headers, data=payload)
        if results:
            num_results = len(results.json().get('organic', []))
            # Handle case when no search results are found
            if num_results == 0:
                print(Style.BRIGHT + Fore.CYAN + f"[i] No search results found for " + Fore.YELLOW + f"{target}" + Fore.CYAN + ". Skipping further steps." + Style.RESET_ALL)
                return search_results  # Return empty list

            print("\n" + Style.BRIGHT + Fore.GREEN + "[+] Processing Google search results." + Style.RESET_ALL)
            with tqdm(total=num_results, unit="result", bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt} [{elapsed}]", ncols=80) as search_bar:
                for result in results.json()['organic']:
                    search_results.append(result)
                    search_bar.update(1)
    except Exception as e:
        sys.exit(Style.BRIGHT + Fore.RED + f"[-] Quitting. Error during Google search: {str(e)}\n" + Style.RESET_ALL)

    return search_results

# Remove duplicate search results
def remove_duplicates(results):
    df = pd.DataFrame(results).drop_duplicates('title')
    unique_data = df.to_dict(orient='records')
    print(Style.BRIGHT + Fore.CYAN + "[i] Duplicates removed from search results." + Style.RESET_ALL)
    return unique_data

# Extracting links from search results
def extract_links(unique_data):
    scrape_links = []
    for entry in unique_data:
        if 'gov' not in entry['link']:
            scrape_links.append(entry['link'])
    print(Style.BRIGHT + Fore.CYAN + "[i] Links extracted and ready for scraping.\n" + Style.RESET_ALL)
    return scrape_links

# Scraping links with Firecrawl
def scraped_links(scrape_links, progress_bar=None):
    """
    Scrapes the provided list of URLs and optionally updates a given progress bar.
    If the number of links changes dynamically, adjusts the total count of the progress bar.
    """
    scrape_results = []

    # Only show progress bar if there are links to scrape
    if len(scrape_links) == 0:
        tqdm.write(Style.BRIGHT + Fore.CYAN + "[i] No links to scrape." + Style.RESET_ALL)
        return scrape_results

    # Adjust the progress bar total dynamically if needed
    if progress_bar is not None:
        initial_total = len(scrape_links)
        progress_bar.total = initial_total
        progress_bar.refresh()

    for link in scrape_links:
        try:
            scraper = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))
            scrape_result = scraper.scrape_url(link, params={'formats': ['markdown', 'links', 'screenshot@fullPage']})
            scrape_results.append(scrape_result)
            time.sleep(1)
        except Exception:
            pass  # Skip failed links

        # Update the progress bar even when a link fails
        if progress_bar is not None:
            progress_bar.update(1)
            progress_bar.refresh()  # Force refresh in case of visual lag

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
    except Exception as e:
        pass

# Process the data and save to dictionary
def process_data(scrape_results, target, directory):
    data_dict = {}
    all_emails = []
    all_urls = []
    all_image_urls = []

    for scrape_result in scrape_results:
        extracted_data = extract_data(scrape_result)
        image_url = extracted_data[0]
        if image_url:
            all_image_urls.append(image_url)
        emails = extracted_data[1]
        all_emails.extend(emails)
        urls = extracted_data[2]
        all_urls.extend(urls)

    data_dict['Email Addresses'] = list(set(all_emails)) if all_emails else []
    data_dict['URLs'] = list(set(all_urls)) if all_urls else []

    if all_image_urls:
        #print("\n" + Style.BRIGHT + Fore.GREEN + "[" + Fore.WHITE + "*" + Fore.GREEN + "]" + " Taking screenshots where possible." + Style.RESET_ALL)
        ss_path = os.path.join(directory, 'screenshots')
        if not os.path.exists(ss_path):
            os.makedirs(ss_path)

        # Progress bar for saving screenshots
        print("\n" + Style.BRIGHT + Fore.GREEN + "[+] Saving screenshots." + Style.RESET_ALL)
        with tqdm(total=len(all_image_urls), unit="screenshot", bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt} [{elapsed}]", ncols=80) as screenshot_bar:
            for url in all_image_urls:
                image_path = os.path.join(ss_path, 'ss_' + ''.join(random.choices(string.ascii_lowercase, k=5)) + '.png')
                save_screenshot(url, image_path)
                screenshot_bar.update(1)
    else:
        tqdm.write(Style.BRIGHT + Fore.CYAN + "[i] No screenshots to save." + Style.RESET_ALL)
    
    time.sleep(1)
    tqdm.write("\n" + Style.BRIGHT + Fore.CYAN + f"[i] All Google search data for " + Fore.YELLOW + f"{target}" + Fore.CYAN + " was saved." + Style.RESET_ALL)
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
    parser.add_argument('--max-depth', dest='DEPTH', type=int, default=1, help='Maximum recursion depth (default: 1)')
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
        print(Style.BRIGHT + Fore.CYAN + f" [i] Maximum recursion depth reached for target " + Fore.YELLOW + f"{target}" + Fore.CYAN + " - Skipping further recursion." + Style.RESET_ALL)
        return combined_data

    if processed_targets is None:
        processed_targets = set()
    if combined_data is None:
        combined_data = {'Email Addresses': set(), 'URLs': set()}

    # Check if the target has already been processed
    if target in processed_targets:
        print(Style.BRIGHT + Fore.CYAN + f" [i] Target '{target}' has already been processed. Skipping." + Style.RESET_ALL)
        return combined_data

    processed_targets.add(target)

    # Indicate which target is being processed
    print(Style.BRIGHT + Fore.GREEN + f"\n[+] Starting search and scrape for target: " + Fore.YELLOW + f"{target}" + Fore.GREEN + f" (Depth: {depth})" + Style.RESET_ALL)

    # Checking if directory exists and get the path
    directory = check_directory(target, output)

    # Loading environment variables
    load_dotenv()
    if not all([os.getenv('SERPER_API_KEY'), os.getenv('FIRECRAWL_API_KEY')]):
        print("\n" + Style.BRIGHT + Fore.RED + "[-] API key(s) not found.\n" + Style.RESET_ALL)
        sys.exit()

    # Perform the search and scrape process
    results = google_search(target)
    if not results:  # No search results found
        #print(Style.BRIGHT + Fore.CYAN + f"[i] No search results found for target '{target}'. Skipping further steps." + Style.RESET_ALL)
        return combined_data  # Stop processing this target
    
    uniques = remove_duplicates(results)
    if not uniques:  # Edge case: all results are duplicates and no unique results remain
        print(Style.BRIGHT + Fore.CYAN + f"[i] No unique results after removing duplicates for target '{target}'." + Style.RESET_ALL)
        return combined_data
    
    # Extract links and continue
    scrape_links = extract_links(uniques)

    # Skip progress bar creation if there are no links to scrape
    if len(scrape_links) == 0:
        print(Style.BRIGHT + Fore.CYAN + f"[i] No links to scrape for target " + Fore.YELLOW + f"{target}" + Fore.CYAN + "." + Style.RESET_ALL)
        return combined_data
    
    # Create a new progress bar for each unique scraping task
    print(Style.BRIGHT + Fore.GREEN + "[+] Scraping URLs and extracting data." + Style.RESET_ALL)
    with tqdm(total=len(scrape_links), unit="url", bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt} [{elapsed}]", ncols=80) as progress_bar:
        # Perform scraping and update the progress bar
        scraped_data = scraped_links(scrape_links, progress_bar=progress_bar)

    # Process the scraped data and update combined data
    data_dict = process_data(scraped_data, target, directory)

    # Update combined data with the newly collected emails and URLs
    combined_data['Email Addresses'].update(data_dict.get('Email Addresses', []))
    combined_data['URLs'].update(data_dict.get('URLs', []))

    # Display the emails found in this iteration
    found_emails = data_dict.get('Email Addresses', [])
    if found_emails:
        print(Style.BRIGHT + Fore.GREEN + f"\n[+] Emails found for target " + Fore.YELLOW + f"{target}" + Fore.GREEN + f":" + Style.RESET_ALL)
        for idx, email in enumerate(found_emails, 1):
            print(f"    {idx}. {email}")
    else:
        print(Style.BRIGHT + Fore.CYAN + f"\n[i] No emails found for target " + Fore.YELLOW + f"{target}" + Fore.CYAN + "." + Style.RESET_ALL)
        if depth == 0:
            print(Style.BRIGHT + Fore.CYAN + " [i] No emails identified during the initial search." + Style.RESET_ALL)
        return combined_data  # No emails to process further

    # Determine the type of the initial target
    if depth == 0:
        initial_target_type = get_target_type(target)
    else:
        initial_target_type = "email"  # Subsequent targets are emails

    # Automatic recursion for emails or usernames
    if initial_target_type in ["email", "username"]:
        matched_emails = set()
        
        # Create a progress bar for matching emails
        if found_emails:
            tqdm.write(Style.BRIGHT + Fore.GREEN + f"\n[+] Matching relevant emails to " + Fore.YELLOW + f"{target}" + Fore.GREEN + " and performing recursive search." + Style.RESET_ALL)
            with tqdm(total=len(found_emails), unit="email", ncols=80, bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt} [{elapsed}]") as email_match_bar:
                for email in found_emails:
                    if email == target or match_emails(target, [email]):
                        matched_emails.add(email)
                    email_match_bar.update(1)
        else:
            tqdm.write(Style.BRIGHT + Fore.CYAN + "[i] No emails found for matching." + Style.RESET_ALL)

        # Remove already processed emails
        matched_emails -= processed_targets

        # Display only matched emails that will be processed recursively
        if matched_emails:
            print(Style.BRIGHT + Fore.CYAN + f"\n[i] Matched emails to be processed further:" + Style.RESET_ALL)
            for email in matched_emails:
                print(f"    - {email}")
        else:
            print(Fore.CYAN + f"\n[i] No matched emails for further processing." + Style.RESET_ALL)
            return combined_data  # No matched emails, so stop recursion

        # Recursively process each matched email
        for email in matched_emails:
            if email not in processed_targets and is_valid_email(email):
                recursive_search_and_scrape(email, output, processed_targets, combined_data, depth=depth+1, max_depth=max_depth, initial_target_type=initial_target_type, unified_progress_bar=None)

    elif initial_target_type == "name_company":
        # User-guided recursion for company or name targets
        print(Style.BRIGHT + Fore.BLUE + "\n[i] Since the initial target is a name or company, please select which emails to recurse into:" + Style.RESET_ALL)
        selected_indices = input(Style.BRIGHT + Fore.YELLOW + "Your selection: " + Style.RESET_ALL)
        selected_indices = [int(idx.strip()) for idx in selected_indices.split(',') if idx.strip().isdigit()]
        selected_emails = [found_emails[idx - 1] for idx in selected_indices if 1 <= idx <= len(found_emails)]

        if selected_emails:
            for email in selected_emails:
                if email not in processed_targets and is_valid_email(email):
                    recursive_search_and_scrape(email, output, processed_targets, combined_data, depth=depth+1, max_depth=max_depth, initial_target_type=initial_target_type, unified_progress_bar=None)

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
        print("\n" + Style.BRIGHT + Fore.GREEN + "[+] Starting URL relevance matching in collected data." + Style.RESET_ALL)

        # Initialize progress bar for URL relevance matching
        with tqdm(total=len(combined_data['URLs']), unit="url", ncols=80, bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt} [{elapsed}]") as relevance_bar:
            relevant_urls_with_scores = []
            for url, score in evaluate_urls(initial_target, combined_data['URLs']):
                relevant_urls_with_scores.append((url, score))
                relevance_bar.update(1)

        # Adjust the threshold as needed. For example, 50
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
            print(Style.BRIGHT + Fore.GREEN + "\n[+] Relevant URLs found and saved." + Style.RESET_ALL)
            #for url in relevant_urls:
                #print(f"    - {url}")
        else:
            print(Style.BRIGHT + Fore.CYAN + "\n[i] No relevant URLs identified." + Style.RESET_ALL)
    else:
        print(Style.BRIGHT + Fore.CYAN + "\n[i] No URLs found to match." + Style.RESET_ALL)
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

    print(Style.BRIGHT + Fore.BLUE + "[v] Raw data saved to " + Fore.YELLOW + f"{output_file}\n" + Style.RESET_ALL)

if __name__ == '__main__':
    main()