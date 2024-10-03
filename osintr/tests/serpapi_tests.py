from colorama import Fore, Style
from dotenv import load_dotenv
from tqdm import tqdm
import requests
import json
import os

# Perform Google search API test
target = "black coffee"
def main(target):
    # Load API key
    load_dotenv()

    # Perform test search
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
        results = requests.request("POST", url, headers=headers, data=payload)
        results.raise_for_status()
        if results:
            num_results = len(results.json().get('organic', []))
            # Handle case when no search results are found
            if num_results == 0:
                print(Style.BRIGHT + Fore.CYAN + f"[i] No search results found for " + Fore.YELLOW + f"{target}" + Fore.CYAN + ". Skipping further steps." + Style.RESET_ALL)
                return search_results  # Return empty list

            print("\n" + Style.BRIGHT + Fore.GREEN + "[+] Processing Google search results." + Style.RESET_ALL)
            with tqdm(total=num_results, unit="result", bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt} [{elapsed}]", ncols=80) as search_bar:
                for result in results.json()['organic']:
                    search_results.append(result['link'])
                    search_bar.update(1)
    except requests.exceptions.HTTPError as errh:
        print("Http Error: ", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting: ", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error: ", errt)
    except requests.exceptions.RetryError as errr:
        print("Max Retries Error: ", errr)
    except requests.exceptions.RequestException as err:
        print("Oupsie! Something broke: ", err)

    print(search_results)

if __name__ == '__main__':
    main(target)