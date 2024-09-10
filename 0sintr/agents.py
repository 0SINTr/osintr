import os
import sys
from colorama import Fore, Style
from crewai import Agent
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
from prompts import *
from mdread import MarkdownFileReaderTool
from dirread import DirectoryReadTool
from crewai_tools import FileReadTool

# Load env variables
load_dotenv()

# Instantiate FileReadTool
fileTool = FileReadTool()

# Discover the LLM to use based on .env data
try:
    if os.getenv("OPENAI_API_KEY") is not None:
        llm = ChatOpenAI(
            model_name="gpt-4o"
            )
    elif os.getenv("ANTHROPIC_API_KEY") is not None:
        llm = ChatAnthropic(
            model = "claude-3-5-sonnet-20240620"
            )
    else:
        print(Style.BRIGHT + Fore.RED + "\n|---> No LLM API key found. Quitting the Data Analysis phase.\n" + Style.RESET_ALL)
        sys.exit()
except NameError as e:
    print(e)

# Define Google Data Analyst Agent
google_analyst = Agent(
    role="Google Data Analyst",
    goal=google_data_analyst_goal,
    tools=[DirectoryReadTool,MarkdownFileReaderTool],
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
    tools=[DirectoryReadTool,fileTool],
    memory=True,
    verbose=True,
    backstory=hibp_data_analyst_backstory,
    allow_delegation=False,
    llm=llm
)

# Define OSINT.Industries Data Analyst Agent
osind_analyst = Agent(
    role="OSINT Industries Data Analyst",
    goal=osind_data_analyst_goal,
    tools=[DirectoryReadTool,fileTool],
    memory=True,
    verbose=False,
    backstory=osind_data_analyst_backstory,
    allow_delegation=False,
    llm=llm
)

# Define Curator Agent
curator = Agent(
    role="Curator",
    goal=curator_goal,
    memory=True,
    verbose=True,
    backstory=curator_backstory,
    allow_delegation=False,
    llm=llm
)
