from crewai import Agent
from ai_logic.prompts import *
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Import the environment keys
os.environ["CREWAI_TELEMETRY_DISABLED"] = "true"
load_dotenv()

OpenAIGPT4o = ChatOpenAI(model_name="gpt-4o")

# Define Analyst Agent
analyst = Agent(
    role="Data Analyst",
    goal=data_analyst_goal_prompt,
    memory=True,
    verbose=True,
    backstory=data_analyst_backstory,
    allow_delegation=False,
    llm=OpenAIGPT4o
)

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