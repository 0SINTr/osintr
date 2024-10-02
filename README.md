![osintr](osintr/docs/osintr.png)
# OSINTr
**[OFM](https://github.com/0SINTr/ofm) Stage 1 tool for GRASS (Google Recursive Advanced Search & Scrape)**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/0SINTr/osintr/master/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10+-green)](https://www.python.org)
[![Stable Release](https://img.shields.io/badge/version-0.3.0-blue.svg)](https://github.com/0SINTr/osintr/releases/tag/v0.3.0)
[![Last Commit](https://img.shields.io/github/last-commit/0SINTr/osintr)](https://github.com/0SINTr/osintr/commits/main)

**OSINTr** helps you build a strong foundation for any OSINT investigation by quickly creating a **digital footprint** of the target via recursive advanced Google searches via **SerperDev** and **Firecrawl** APIs.

## Why OSINTr?

**OSINTr** directly interacts only with high-quality APIs (SerpDev, Firecrawl) at a low cost, bypassing the need for unreliable third-party apps and implicitly **handling common issues** related to parsing, captchas, proxies or other types of usual setbacks. This ensures full control over the code and exclusive focus on the OSINT tasks rather than troubleshooting scraping and crawling hiccups.

### Data Collection

**OSINTr** works best on Linux and tackles **Stage 1 of the [OFM](https://github.com/0SINTr/ofm)** workflow by performing **GRASS** (Google Recursive Advanced Search & Scrape).
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
    - **Name Entity Recognition (NER)** via **spaCy** tokens for person name or company name matching
    - Stop words and excluded tokens for an improved **scoring system** for URL vs. name matching
    - Exact or **fuzzy token matching**, adjusted penalty logic, sorting URLs by **relevance score**
- If the target is **email** or **username**: 
    - Recursion is done **automatically** up to a max depth of 1.
- If the target is **person** or **company name**: 
    - **You pick** the emails to recurse at each level of depth.
- Currently, the **maximum depth for recursion** is set to 1. Use **--max-depth** to change it.
- Creates a directory under **-o OUTPUT** directory named ***osint_TargetName*** for each target.
- Saves all email addresses and URLs from the **GRASS** process to a file **Raw_Data.json**.
- Also creates a Jinja2 template-based **Final_Report.html** with clean structure and formatting.

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

After installation, **on the first run**, you will see an output similar to the one below. Don't panic, it's the **spaCy** library downloading its **NER Model**.
```
Downloading 'en_core_web_sm' model...
Collecting en-core-web-sm==3.7.1
  Downloading https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl (12.8 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 12.8/12.8 MB 25.7 MB/s eta 0:00:00
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
  --max-depth DEPTH  Maximum recursion depth (default: 1)

NOTE!
For person or company names use double quotes to enclose the whole name.
```

## Screenshots

See **example workflows** below. 
Details related to the targets have been **hidden** for obvious reasons.
Some output was **omitted** for brevity.

* **OSINT target** is **email address** or **username**.

![osintr_example1](osintr/docs/example-eu.png)

* **OSINT target** is **person name** or **company name**.

![osintr_example2](osintr/docs/example-pc.png)

* Sample **HTML report**.

![osintr_report](osintr/docs/report.png)

## Planned Upgrades

- [x] Filtering crawled URLs by relevance.
- [x] Better formating for the JSON data.
- [x] Adding HTML-based final reporting.
- [x] Improved, better-structured output.
- [ ] Google images, maps, places, reviews.

## Disclaimer

- **OSINTr** is designed for **passive**, **non-intrusive** OSINT tasks.
- Any illegal or unethical use of the tool is **your** responsibility.
- See **LICENSE** for more details on rights, permissions, and liability.

## Support

**API documentation**:

- [SerperDev API docs](https://serper.dev/)
- [Firecrawl API docs](https://docs.firecrawl.dev/introduction)