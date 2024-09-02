from crewai import Agent
from textwrap import dedent
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SerpAPIWrapper
from dotenv import load_dotenv

# Import the environment keys
import os
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ['OPENAI_MODEL_NAME'] = os.getenv("OPENAI_MODEL_NAME")
os.environ["SERPAPI_API_KEY"] = os.getenv("SERPAPI_API_KEY")

OpenAIGPT4o = ChatOpenAI(model_name="gpt-4o")

# Define Researcher Agent
researcher = Agent(
    role="OSINT Researcher",
    goal=dedent("Gather comprehensive data on the specified target."),
    tools=[SerpAPIWrapper],
    memory=True,
    verbose=True,
    backstory=dedent("You are an expert in online investigations and OSINT tasks, skilled at using a variety of OSINT tools and techniques to uncover relevant information that others might miss."),
    llm=OpenAIGPT4o
    )

# Define Analyst Agent
analyst = Agent(
    role="Data Analyst",
    goal=dedent("Analyze and synthesize data collected by the researcher to find connections and insights."),
    memory=True,
    verbose=True,
    backstory=dedent("You are a seasoned analyst, capable of turning raw data into actionable intelligence by connecting the dots between different data points and parsing and organizing the information."),
    llm=OpenAIGPT4o
)

# Define Report Writer Agent
report_writer = Agent(
    role="Report Writer",
    goal=dedent("Compile a detailed and well-structured report based on the analyzed data."),
    memory=True,
    verbose=True,
    backstory=dedent("You are a skilled communicator and an excellent report and document creator, with a talent for turning complex information into clear, concise, and visually appealing reports."),
    llm=OpenAIGPT4o
)