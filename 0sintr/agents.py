from crewai import Agent
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
from prompts import *
import os

if os.getenv("OPENAI_MODEL_NAME") == 'gpt-4o':
    load_dotenv()
    OpenAIGPT4o = ChatOpenAI(model_name=os.getenv("OPENAI_MODEL_NAME"))
    llm = OpenAIGPT4o
elif os.getenv("OPENAI_MODEL_NAME") == 'llama3.1':
    os.environ["OPENAI_API_KEY"] = "NA"
    llm = ChatOllama(
        model = "llama3.1",
        base_url = "http://localhost:11434")

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
