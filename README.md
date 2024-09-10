
# 0SINTr

Welcome to the **0SINTr** project!  This tool helps you set up a multi-agent OSINT AI system with ease, leveraging the flexible framework provided by crewAI. The goal is to enable agents to collaborate effectively on complex tasks, maximizing their collective intelligence and data analysis capabilities.

> **Note:** This tool is not designed for a full OSINT investigation but rather to build a foundation for the OSINT process by quickly creating a digital footprint of the target via advanced Google searches, breach and paste data, and optional data sources.

---

## Why 0SINTr?

The app directly interacts with high-quality APIs and LLMs at a low cost, bypassing the need for unreliable third-party apps. This ensures you have full control over the code and only need to cover the API costs.

---

## Workflow

0SINTr performs two primary tasks:

### 1. Data Collection

You provide a **Username** or **Email Address** for the **-t** argument (see below). This is the **target** of the OSINT investigation. Ensure you create and populate a `.env` file as described below before running the tool.

**Automated tasks include:**
- Perform verbatim search, intext, inurl, and intitle search on Google.
- Store search results as JSON and remove duplicates.
- Scrape URLs from JSON and save each page as Markdown files in the `scraped` directory.
- Save unscreened pages (e.g., social media) in a `.txt` file.
- Save screenshots in the `screenshots` directory.
- Extract email addresses from scraped pages and store them in a `.txt` file.
- Check breaches and pastes for the account (username/email).
- Optionally use the OSINT.Industries API if an API key is provided.

### 2. Data Analysis

Once data is collected, the AI crew automatically analyzes the information. The crew is composed of multiple AI agents, each with unique roles and tasks. Tasks are defined in `tasks.py`, and agent configurations are outlined in `agents.py`. Prompts for the crew are found in `prompts.py`.

**Automated tasks include:**
- Analyze `.md`, `.json`, and other files in the target directory.
- AI agents work together, each with a specific goal, toolset, and output task.
- Default AI model is [GPT-4o](https://platform.openai.com/docs/models/gpt-4o). Other models supported: [Claude Sonnet](https://docs.anthropic.com/en/docs/about-claude/models#model-comparison-table).
- 0SINTr builds a profile or digital footprint of the target based on collected data.
- The gathered data is curated and the final report is provided in .md format.

---

## API Keys

Running the **Data Analysis** phase via **GPT-4o** or **Claude Sonnet** depends on the items you enter into the `.env` file.
0SINTr automatically detects your `.env` settings and runs the AI crew with the correct LLM accordingly.

**To use 0SINTr with GPT-4o, you need the following items in your `.env` file in the root folder of 0SINTr.**
```plaintext
OPENAI_API_KEY=<your_key_here>
SERPER_API_KEY=<your_key_here>
FIRECRAWL_API_KEY=<your_key_here>
HIBP_API_KEY=<your_key_here>
``` 

**To use 0SINTr with Claude, you need the following items in your `.env` file in the root folder of 0SINTr.** 
```plaintext
ANTHROPIC_API_KEY=<your_key_here>
SERPER_API_KEY=<your_key_here>
FIRECRAWL_API_KEY=<your_key_here>
HIBP_API_KEY=<your_key_here>
```


**API Keys:**
- **OpenAI**: [Get your key here](https://openai.com/)
- **Anthropic**: [Get your key here](https://www.anthropic.com/)
- **SerperDev**: [Get your key here](https://serper.dev/)
- **Firecrawl**: [Get your key here](https://www.firecrawl.dev/)
- **HaveIBeenPwned**: [Get your key here](https://haveibeenpwned.com/)

---

## Optional Feature

Optionally, you can collect data from **OSINT.Industries** via their API. Add the key in `.env` as `OSIND_API_KEY=<your_key_here>`. This functionality is triggered if you have a valid key saved in `.env`.

---

## Costs

- **OpenAI**: Pay-as-you-go.
- **Anthropic**: Pay-as-you-go.
- **SerperDev**: 2,500 free queries, then pay-as-you-go (50k queries for $50).
- **Firecrawl**: 500 free credits; $19/mo for 3,000 page scrapes. 
- **HIBP**: Pwned1 plan for $3.95/mo, 10 email searches/minute.
- **OSINT.Industries** (optional): Starting at £19/mo.

---

## Installation

Ensure Python >=3.10 is installed.

```bash
git clone https://github.com/0SINTr/0SINTr.git
cd 0SINTr
python setup.py install
```

---

## Usage

```bash
0sintr [-h] -t TARGET -o OUTPUT
```

---

## Upgrading

To update this tool to the latest version, follow these steps:

```bash
cd 0SINTr
git pull origin main
python setup.py install
```

---

## Planned Upgrades

- Support for additional LLMs (Phi-3, Mistral, Reflection)
- More data sources from quality API providers
- Phone number and company search capabilities

---

## Disclaimer

This tool is designed for passive, non-intrusive OSINT tasks. Any illegal or unethical use of the tool is your responsibility. See LICENSE for more details on rights, permissions, and liability.

---

## Support

For support, questions, or feedback:

- [crewAI documentation](https://docs.crewai.com)
- [crewAI Tools](https://docs.crewai.com/core-concepts/Tools/)
- [crewAI & LLMs](https://docs.crewai.com/how-to/LLM-Connections/#ollama-local-integration)
- [Langchain tools](https://docs.crewai.com/core-concepts/Using-LangChain-Tools/)
- [GitHub repository](https://github.com/joaomdmoura/crewai)
- [OpenAI API docs](https://platform.openai.com/docs/overview)
- [Anthropic API docs](https://console.anthropic.com/docs/)
- [SerperDev API docs](https://serper.dev/)
- [Firecrawl API docs](https://docs.firecrawl.dev/introduction)
- [HaveIBeenPwned API docs](https://haveibeenpwned.com/API/v3)
- [OSINT.Industries API docs](https://docs.osint.industries/reference/search)
