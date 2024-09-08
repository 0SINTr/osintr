from crewai import Agent
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
from prompts import *
import os

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

# Define Analyst Agent
analyst = Agent(
    role="Data Analyst",
    goal=data_analyst_goal_prompt,
    memory=True,
    verbose=True,
    backstory=data_analyst_backstory,
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
