from crewai import Agent
from prompts import *
from langchain_openai import ChatOpenAI
from tools.google import GoogleSearchTool
from dotenv import load_dotenv
import os

# Import the environment keys
os.environ["CREWAI_TELEMETRY_DISABLED"] = "true"
load_dotenv()

OpenAIGPT4o = ChatOpenAI(model_name="gpt-4o")

# Define Researcher Agent
researcher = Agent(
    role="Researcher",
    goal=google_researcher_goal_prompt,
    tools=[GoogleSearchTool],
    memory=True,
    verbose=True,
    backstory=google_researcher_backstory,
    max_rpm=None,
    max_iter=2,
    llm=OpenAIGPT4o
    )
'''
# Define Analyst Agent
analyst = Agent(
    role="Data Analyst",
    goal=analyst_goal_prompt,
    memory=True,
    verbose=True,
    backstory=analyst_backstory,
    allow_delegation=False,
    llm=OpenAIGPT4o
)
'''
# Define Report Writer Agent
report_writer = Agent(
    role="Report Writer",
    goal=report_writer_goal_prompt,
    memory=True,
    verbose=True,
    backstory=report_writer_backstory,
    allow_delegation=False,
    llm=OpenAIGPT4o
)