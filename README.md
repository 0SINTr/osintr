![osintr](osintr/docs/osintr.png)
# OSINTr
**[OFM](https://github.com/0SINTr/ofm) Stage 1 tool for GRASS (Google Recursive Advanced Search & Scrape)**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/0SINTr/osintr/master/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10+-green)](https://www.python.org)
[![Stable Release](https://img.shields.io/badge/version-0.2.0-blue.svg)](https://github.com/0SINTr/osintr/releases/tag/v0.2.0)
[![Last Commit](https://img.shields.io/github/last-commit/0SINTr/osintr)](https://github.com/0SINTr/osintr/commits/main)

**OSINTr** helps you build a strong foundation for any OSINT investigation by quickly creating a **digital footprint** of the target via recursive advanced Google searches via **SerperDev** and **Firecrawl** APIs.

## Why OSINTr?

**OSINTr** directly interacts only with high-quality APIs (SerpDev, Firecrawl) at a low cost, bypassing the need for unreliable third-party apps and implicitly **handling common issues** related to parsing, captchas, proxies or other types of usual setbacks. This ensures full control over the code and exclusive focus on the OSINT tasks rather than troubleshooting scraping and crawling hiccups.

## Workflow

**OSINTr** works best on Linux and tackles **Stage 1 of the [OFM](https://github.com/0SINTr/ofm)** workflow by performing **GRASS** (Google Recursive Advanced Search & Scrape).

### Data Collection

- Requires a **target** for the OSINT investigation (see **Usage** below).   
- Ensure you add your API keys (see **API Keys** below) before running the tool.

**Automated tasks include:**
- Performs **verbatim** (intitle, intext, inanchor included) and **inurl** Google search.
- Scrapes all found URLs and extracts all **email addresses** and **URLs** from each page.
- Saves a **full page screenshot** (if possible) of each page in a separate directory.
- The **initial search** might be performed on an **email**, **username**, **person name** or **company**.
- Goal is to collect at least one **email address** from the initial search and then dig deeper.
- For each email address it finds relevant, it **recursively** performs the **GRASS** job.
- Automatically checks for **matches** between potentially related email addresses, using:
    - Exact matching:
        - `john.doe@tests.com` to `john.doe@test.com`
    - Case-insensitive matching:
        - `JoHn.DoE@test.com` to `john.doe@test.com`
    - Handling plus-addressing:
        - `john.doe+dev@test.com` to `john.doe@test.com`
    - Char to digits mapping & leet:
        - `j0hnd03@example.com` to `john.doe@test.com`
    - Levenshtein fuzzy matching:
        - `johnny.doe@test.com` to `john.doe@test.com`
    - Homoglyph matching:
        - `john.doｅ@test.com` to `john.doe@test.com`
    - Phonetic matching:
        - `john.dough@test.com` to `john.doe@test.com`
    - Substring matching:
        - `john.doe@test.com` to `john.doe99@test.com`
- Automatically checks for **matches** between the target and potentially related URLs, using:
    - Differentiation between **target** being an email or username, vs. person or company name
    - **Name Entity Recognition (NER)** via spaCy tokens for person name or company name matching
    - Stop words and excluded tokens for an improved **scoring system** for URL vs. name matching
    - Exact or **fuzzy token matching**, adjusted penalty logic, sorting URLs by **relevance score**
- If the target is **email** or **username**, recursion is done **automatically** up to a max depth of 2.
- If the target is **person** or **company name**, **you pick** the emails to recurse at each depth level.
- Currently, the **maximum depth for recursion** is set to 2. May increase in the future.
- Creates a directory under **-o OUTPUT** directory named ***osint_TargetName*** for each target.
- Saves all email addresses and URLs from the **GRASS** process to a file **Raw_Data.json**.
- Also creates a Jinja2 template-based **Final_Report.html** with clean structure and formatting.

## Program Workflow

### Initial Target is an Email or Username

```mermaid
flowchart TD
    A[Start: Provide Initial Target] --> B{Determine Target Type}
    B -->|Email| C[Extract Username and Domain]
    B -->|Username| D[Tokenize Username]
    C --> E[Google Search: "username" OR inurl:"username"]
    D --> E[Google Search: "username" OR inurl:"username"]
    E --> F[Remove Duplicate Search Results]
    F --> G[Extract Relevant Links (Exclude 'gov')]
    G --> H[Scrape Extracted Links using Firecrawl]
    H --> I[Extract Emails and URLs from Scraped Data]
    I --> J[Save Screenshots (if available)]
    J --> K[Update Combined Data]
    K --> L[Evaluate URLs for Relevance]
    L --> M{Are there Relevant URLs?}
    M -->|Yes| N[Store Relevant URLs]
    M -->|No| O[Store Other URLs]
    N --> P[Generate HTML Report]
    O --> P[Generate HTML Report]
    P --> Q[Save Raw Data to JSON]
    Q --> R[End]
    
    %% Styling
    classDef startEnd fill:#f9f,stroke:#333,stroke-width:2px;
    class A,R startEnd;
```


## API Keys

Running **OSINTr** requires API keys for the benefits stated previously. The API keys should reside in your environment **prior** to running **OSINTr**.

**To add the API keys to your environment, edit bashrc or zshrc.**
```plaintext
vim ~/.bashrc
export SERPER_API_KEY="<your_key_here>"
export FIRECRAWL_API_KEY="<your_key_here>"
source ~/.bashrc
```

**Getting API Keys:**

- **SerperDev**: [Get your key here](https://serper.dev/)
- **Firecrawl**: [Get your key here](https://www.firecrawl.dev/)

## Costs

**OSINTr** aims to use reliable, but affordable APIs:

- **SerperDev**: 2,500 free queries, then pay-as-you-go (50k queries for $50).
- **Firecrawl**: 500 free credits; $19/mo for 3,000 page scrapes. 

## Installation

**Preparing**
- Ensure **Python >=3.10** is installed.
- Add `/home/<user>/.local/bin` to `PATH`.
- Edit `~/.zshrc` if that's your default.

```bash
sudo apt upgrade python3
sudo apt upgrade python3-pip
vim ~/.bashrc
export PATH="$HOME/.local/bin:$PATH"
source ~/.bashrc
```

**Installing**
```bash
pipx install git+https://github.com/0SINTr/osintr.git
```

## Usage

```console
$ osintr -h
usage: main.py [-h] -t TARGET -o OUTPUT [--max-depth DEPTH]

examples:
osintr -t jdoe95@example.com -o /home/bob/data
osintr -t john.doe95 -o /home/bob/data
osintr -t "John Doe" -o /home/bob/data
osintr -t "Evil Corp Ltd" -o /home/bob/data

options:
  -h, --help         show this help message and exit
  -t TARGET          Target of investigation
  -o OUTPUT          Directory to save results
  --max-depth DEPTH  Maximum recursion depth (default: 2)

NOTE!
For person or company names use double quotes to enclose the whole name.
```

## Screenshot

See an example workflow below. Details related to the target have been **hidden** for obvious reasons.

![osintr_example](osintr/docs/example.png)

## Planned Upgrades

- [ ] Filtering crawled URLs by relevance.
- [ ] Better formating for the JSON data.

## Disclaimer

- **OSINTr** is designed for **passive**, **non-intrusive** OSINT tasks.
- Any illegal or unethical use of the tool is **your** responsibility.
- See **LICENSE** for more details on rights, permissions, and liability.

## Support

**API documentation**:

- [SerperDev API docs](https://serper.dev/)
- [Firecrawl API docs](https://docs.firecrawl.dev/introduction)