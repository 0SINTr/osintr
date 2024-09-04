# 0SINTr Intro

Welcome to the 0SINTr project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

NOTE!
This tool is not meant to perform a full OSINT investigation, but rather to easily build a foundation for the OSINT process.

API KEYS!
You need to get a SerperDev key (https://serper.dev/) and add it to a .env file in the root folder of the project as SERPER_API_KEY=<your_key_here>
You need to get an OpenAI key (https://openai.com/) and add it to the .env file in the root folder of the project as OPENAI_API_KEY=<your_key_here>
Also add OPENAI_MODEL_NAME=<model> (e.g. gpt-4o) to the .env file.

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
