# 0SINTr

Welcome to the **0SINTr** project! This tool is designed to help you set up a multi-agent OSINT AI system with ease, leveraging the powerful and flexible framework provided by crewAI. The goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and data analysis capabilities.

**NOTE!** This tool is not meant to perform a full OSINT investigation, but rather to easily build a foundation for the OSINT process. The tool helps you quickly create a digital footprint of the target by leveraging advanced Google searches and breach data, as well as optional data sources such as OSINT.Industries (more to come).

---


### Workflow

0SINTr performs two main tasks:

**1. Data Collection**

You first need to provide a **Username** or **Email Address** at the prompt (see all required options below). This is the **target** of the OSINT investigation. Make sure you create and populate a **.env** file as described below prior to running the tool.

**The app is going to automatically:**
* Search Google for the provided input, using verbatim search, intext search and inurl/intitle search
* The search results are stored as a JSON file and duplicates are removed in the process
* The tool then extracts every source URL from the JSON file and performs a scrape of that page
* Every scrape is saved as a separate Markdown (.md) file in the `scraped` directory of your directory
* The links to pages that the scraper could not scrape (e.g. some social media) are also stored in a .txt file
* For every scraped page the tool also saves a screenshot of the page in the `screenshots` directory
* The app also searches for email addresses in every scraped page and in the JSON file and stores them to a .txt file
* After the currect execution is complete, you can then use the tool again on the scraped email addresses, if relevant
* Regardless of the search term wbeing a username or email address, the app checks breaches and pastes for that account
* Optionally, the app can collect information via the OSINT.Industries API if you own an API key and the key is in .env

**2. Data Analysis**

Most OSINTers are way too focused on the data harvesting phase, neglecting the processing and analysis of the information. Traditionally, this has been done manually for the most part or with the help of isolated automation scripts here and there. With the rapid rise of AI and LLMs, we can now use these new technologies to build teams of AI agents, each with its own goals and tasks, working together to perform various tasks for us.

**The app is going to automatically:**
* As soon as Phase 1 is over and the data is stored locally, the Analysts (crewAI agents) start working at once to analyze the information we collected in the .md, .json (or other) files regardin our target. See the docs at the bottom of this page to learn how everything works behind the scenes.
* Each agent has a clear goal, a specific task, an expected output, a set of tools and specific settings assigned in the main() function.
* After defining the Agents and Tasks inside main(), as well as all the inputs inside prompts.py, 0SINTr then assembles the crew of agents anf kicks off the analysis process. Depending on whether you choose to use a remote model (e.g. gpt-4o) or a local model (e.g. llama-3.1 via Ollama), this task may take more or less time.
* For now, the default remote model is OpenAI's gpt-4o, and the default local model is llama3.1:70b via Ollama. These were just my personal preferences at the time of building this app. They may change over time as the space evolves. You can change these settings from the .env file and inside main(). I will find a better way to handle the available LLMs in upcoming releases.
* The AI crew is going to analyze all the data stored in the osint_ directory and will try to build a profile or digital footprint summary of the target, including any patterns or connection that a human analyst might miss, provided that sufficient or meaningful data has been collected.
* In the end, the Report Writer agent is going to gather the data from the Analyst(s) and assemble everything into a nicely-formatted report.

With time, as I add more data sources and available models, the final report is going to show a more accurate profile of the target.

------------


**API KEYS**
- You need to get an OpenAI key (https://openai.com/) and add it to the .env file in the root folder of 0SINTr.
- You need to get a SerperDev key (https://serper.dev/) and add it to a .env file in the root folder of 0SINTr.
- You need to get a Firecrawl key (https://www.firecrawl.dev/) and add it to the .env file in the root folder of 0SINTr.
- You need to get a HIBP key (https://haveibeenpwned.com/) and add it to the .env file in the root folder of 0SINTr.

------------


**COSTS**

Let's discuss the costs. Most of these services provide free trials or credits, however there are strict limits in this case.

- **OpenAI** charges on a pay-as-you-go model, where you can always recharge your crdit. Every query costs about a couple of cents.
- **SerperDev** provides 2500 free queries, then you can sign up for the Starter plan and pay-as-you-go (e.g. get 50k queries for $50).
- **Firecrawl** provides 500 free credits for as many page scrapes, then the Hobby plan is $19/mo for 3000 page scrapes per month.
- **HaveIBeenPwned** offers the Pwned1 plan for $3.95/mo, allowing you 10 email address searches per minute via their API.

All in all, this entire setup may require about $23 for Firecrawl and HIBP APIs, whilst for OpenAI and SerperDev the costs depend on your usage. For regular OSINT tasks/CTFs, you can probably can get away with roughly $50/month.

------------


**BUT WHY?**
The main benefit of this setup and why I prefer it personally is that the application works directly with high-quality APIs and services at a low cost, without the need to rely on free, 3rd party apps that may break anytime or that have not been actively maintained for years. Of course, this tool has its own dependencies, but having full control over the code itself and only needing to cover the API costs is a huge advantage.

------------


**OPTIONAL**
After the tools above generate their output during execution, I've added the option to choose whether you'd like to collect data from **OSINT.Industries** as well. They also have their own API, with the Intermediate plan providing 100 queries/mo. for £49. Since I know this may be a bit too expensive for some, I've implemented this functionalty as an option which you can choose to pass at runtime. You need to get an OSINT.Industries key (https://www.osint.industries/) and add it to the .env file in the root folder of the project as `OSIND_API_KEY=<your_key_here>`. The Data Analysis stage will be executed whether you have an OSINT. Industries key or not.

------------



### Installation

Ensure you have Python >=3.10 installed on your system. 

`git clone https://github.com/mihpy/0SINTr.git`
`cd 0SINTr`
`python setup.py install`

------------


### How To Use It

`main.py [-h] -t TARGET -a {remote,local} -o OUTPUT`

------------


### Customizing

**Add your `OPENAI_API_KEY` and other relevant API keys in the `.env` file**
Your .env file should be located in the root folder and look likt this:
`OPENAI_API_KEY=<your_key_here>`
`OPENAI_MODEL_NAME=gpt-4o`
`SERPER_API_KEY=<your_key_here>`
`FIRECRAWL_API_KEY=<your_key_here>`
`HIBP_API_KEY=<your_key_here>`

- Modify `ai_logic/prompts.py` to customize the goals, descriptions, tasks and expected outputs. See main() for agents, tasks and crew default setup.

------------


### Running the Tool

To kickstart the data collection process, kick off your crew of AI agents and begin task execution, run this:

```bash
python main.py
```

After collecting the data, the app initializes the OSINT Crew, assembling the agents and assigning them tasks as defined in the main() configuration.

------------


### Understanding Your AI Crew

The OSINT Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `tasks.py`, leveraging their collective skills to achieve complex objectives. The `agents.py` file outlines the capabilities and configurations of each agent in your crew, whilst `prompts.py` contains all the prompts and instructions for your crew members. The prompts provided by default with the app are the ones that woked best for me at the time of the latest test.

------------


### Planned upgrades
- Adding support for more LLMs (Claude, Phi-3, Mistral, Reflection)
- Integrating more data sources from reliable API providers
- Adding support for name and phone number searchs

------------


### Disclaimer

This tool is designed for passive, non-intrusive OSINT tasks, therefore any illegal or unethical usage of the tool is solely your responsibility. Also read the LICENSE for more details on rights, permissions and liability.

------------


### Support

For support, questions, or feedback regarding **crewAI** and all the APIs:
- Visit the [crewAI documentation](https://docs.crewai.com)
- Read more about the [crewAI Tools](https://docs.crewai.com/core-concepts/Tools/)
- Langchain tools [documentation](https://docs.crewai.com/core-concepts/Using-LangChain-Tools/)
- Reach out through the [GitHub repository](https://github.com/joaomdmoura/crewai)
- You can also try [chatting with crewAI](https://chatg.pt/DWjSBZn)
- OpenAI API [documentation](https://platform.openai.com/docs/overview)
- SerperDev API [documentation](https://serper.dev/)
- Firecrawl API [documentation](https://docs.firecrawl.dev/introduction)
- HaveIBeenPwned API [documentation](https://haveibeenpwned.com/API/v3)
- OSINT.Industries API [documentation](https://docs.osint.industries/reference/search)

