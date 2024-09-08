import os
from crewai import Agent
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
from prompts import *
from crewai_tools import (
    DirectorySearchTool,
    JSONSearchTool,
    MDXSearchTool
)

load_dotenv()
# Discover the LLM to use based on .env data
try:
    if os.getenv("OPENAI_MODEL_NAME") == 'gpt-4o':
        llm = ChatOpenAI(
            model_name=os.getenv("OPENAI_MODEL_NAME")
            )
    elif os.getenv("OPENAI_MODEL_NAME") == 'llama3.1':
        os.getenv["OPENAI_API_KEY"]
        llm = ChatOllama(
            model = "llama3.1",
            base_url = "http://localhost:11434"
            )
except NameError as e:
    print(e)

# Define Google Data Analyst Agent
google_analyst = Agent(
    role="Google Data Analyst",
    goal=google_data_analyst_goal,
    tools=[DirectorySearchTool,MDXSearchTool]
    memory=True,
    verbose=True,
    backstory=google_data_analyst_backstory,
    allow_delegation=False,
    llm=llm
)

# Define HIBP Data Analyst Agent
hibp_analyst = Agent(
    role="HIBP Data Analyst",
    goal=hibp_data_analyst_goal,
    tools=[DirectorySearchTool,JSONSearchTool],
    memory=True,
    verbose=True,
    backstory=hibp_data_analyst_backstory,
    allow_delegation=False,
    llm=llm
)

# Define OSINT.Industries Data Analyst Agent
osind_analyst = Agent(
    role="OSINT.Industries Data Analyst",
    goal=osind_data_analyst_goal,
    tools=[DirectorySearchTool,JSONSearchTool],
    memory=True,
    verbose=True,
    backstory=osind_data_analyst_backstory,
    allow_delegation=False,
    llm=llm
)

# Define Report Writer Agent
report_writer = Agent(
    role="Report Writer",
    goal=report_writer_goal_prompt,
    memory=True,
    verbose=True,
    backstory=report_writer_backstory,
    allow_delegation=False,
    llm=llm
)
