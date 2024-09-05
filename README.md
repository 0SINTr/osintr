# 0SINTr Intro

Welcome to the 0SINTr project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent OSINT AI system with ease, leveraging the powerful and flexible framework provided by crewAI. The goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

**NOTE**
This tool is not meant to perform a full OSINT investigation, but rather to easily build a foundation for the OSINT process. The tool helps you quickly create a digital footprint of the target by leveraging advanced Google searches and breach data, as well as optional information sources such as OSINT.Industries.

**FUNCTIONALITY**
You need to provide a Username, Email Address or Phone Number at the prompt. This is the target of the OSINT investigation.

The app is going to automatically:
* Search Google for the provided input, using verbatim search, intext search and inurl search
* The search results are stored as a JSON file and duplicates are removed in the process
* The app extracts every source URL from the JSON file and performs a scrape of that page
* Every scrape is saved as a separate Markdown (.md) file in the `scraped` directory
* The links to pages that the scraper could not scrape (e.g. some social media) are also stores in a .txt file
* For every scraped page the app also saves a screenshot of the page in the `screenshot` directory
* The app also searches for email addresses in every scraped page and in the JSON file and stores them to a .txt file
* If the search term was a username or email address, the app checks breaches and pastes for that account
* Optionally, the app can collect information via the OSINT.Industries API if you own an API key

How is this information analyzed?

**API KEYS**
You need to get an OpenAI key (https://openai.com/) and add it to the .env file in the root folder of the project as OPENAI_API_KEY=<your_key_here>
You need to get a SerperDev key (https://serper.dev/) and add it to a .env file in the root folder of the project as SERPER_API_KEY=<your_key_here>
You need to get a Firecrawl key (https://www.firecrawl.dev/) and add it to the .env file in the root folder of the project as FIRECRAWL_API_KEY=<your_key_here>
You need to get a HIBP key (https://haveibeenpwned.com/) and add it to the .env file in the root folder of the project as HIBP_API_KEY=<your_key_here>
Also add OPENAI_MODEL_NAME=<model> (e.g. gpt-4o) to the .env file.

**COSTS**
Let's discuss the costs. Most of these services provide free trials or credits, however there are strict limits in this case.
OpenAI charges on a pay-as-you-go model, where you can always recharge your crdit. Every query costs about a couple of cents.
SerperDev provides 2500 free queries, then you can sign up for the Starter plan and pay-as-you-go (e.g. get 50k queries for $50).
Firecrawl provides 500 free credits for as many page scrapes, then the Hobby plan is $19/mo for 3000 page scrapes per month.
HaveIBeenPwned offers the Pwned1 plan for $3.95/mo, allowing you 10 email address searches per minute via their API.
All in all, this entire setup may requires about $23 for Firecrawl and HIBP APIs, whilst for OpenAI and SerperDev the costs depend on your usage. For regular OSINT tasks, you can probably can get away with roughly $50/month.

**BUT WHY?**
The main benefit of this setup and why I prefer it personally is that the application works directly with high-quality APIs and services at a low cost, without the need to rely on free, 3rd party apps that may break anytime with a library update or have not been actively maintained for years. Of course, this tool has its own dependencies, but having full control over the code itself and only needing to cover the API costs is a huge advantage.

**OPTIONAL**
After the tools above generate their output dutin execution, I've added the user option to choose whether you'd like to collect data from OSINT.Industries as well. They also have their own API, with the Intermediate plan providing 100 queries/mo. for £49. Since I know this may be a bit too expensive for some, I've implemented this functionalty as an option which you can choose to pass at runtime. You need to get an OSINT.Industries key (https://www.osint.industries/) and add it to the .env file in the root folder of the project as OSINTI_API_KEY=<your_key_here>.


## Installation

Ensure you have Python >=3.10 installed on your system. 

First, if you haven't already, install CrewAI:

```bash | cmd
pip install crewai crewai-tools
pip install python-dotenv
pip install google-search-results
pip install langchain-ollama
```

### Customizing

**Add your `OPENAI_API_KEY` and other relevant API keys into the `.env` file**

- Modify `agents.py` to define your agents
- Modify `tasks.py` to define your tasks
- Modify `main.py` to define the process

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```
or, from VSCode:

```bash
$ python main.py
```

This is how you initialize the OSINT Crew, assembling the agents and assigning them tasks as defined in your configuration.

## Understanding Your Crew

The OSINT Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the Osint Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
