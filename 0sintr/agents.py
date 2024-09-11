import os
import sys
from colorama import Fore, Style
from crewai import Agent
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
from prompts import *
from tools.jsonread import JSONFileReaderTool
from tools.dirread import DirectoryReadTool
from crewai_tools import FileReadTool

# Load env variables
load_dotenv()

# Instantiate FileReadTool
FileTool = FileReadTool()

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
        print(Style.BRIGHT + Fore.RED + "\n|---> No LLM API key found. Cannot run Data Analysis phase. See README.\n" + Style.RESET_ALL)
        sys.exit()
except NameError as e:
    print(e)

# Data Organizer Agent
data_organizer = Agent(
    role='Information Aggregator',
    goal=data_organizer_goal,
    verbose=True,
    memory=True,
    tools=[DirectoryReadTool,JSONFileReaderTool],
    backstory=data_organizer_backstory,
    allow_delegation=False,
    llm=llm
)

# Pattern Analyzer Agent
pattern_analyzer = Agent(
    role='Data Correlation Specialist',
    goal=pattern_analyzer_goal,
    verbose=True,
    memory=True,
    backstory=pattern_analyzer_backstory,
    allow_delegation=False,
    llm=llm
)