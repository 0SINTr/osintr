from crewai import Agent
from langchain_openai import ChatOpenAI
from tools.google import google_search_function
from dotenv import load_dotenv

# Import the environment keys
load_dotenv()

OpenAIGPT4o = ChatOpenAI(model_name="gpt-4o")

# Define Researcher Agent
researcher = Agent(
    role="OSINT Researcher",
    goal="Gather comprehensive data on {target}.",
    tools=[google_search_function],
    memory=True,
    verbose=True,
    backstory="You are an expert in online investigations and OSINT tasks, skilled at using a variety of OSINT tools and techniques to uncover relevant information that others might miss.",
    llm=OpenAIGPT4o
    )

# Define Analyst Agent
analyst = Agent(
    role="Data Analyst",
    goal="Analyze and synthesize data collected by the researcher to find connections and insights about {target}.",
    memory=True,
    verbose=True,
    backstory="You are a seasoned analyst, capable of turning raw data into actionable intelligence by connecting the dots between different data points and parsing and organizing the information.",
    llm=OpenAIGPT4o
)

# Define Report Writer Agent
report_writer = Agent(
    role="Report Writer",
    goal="Compile a detailed and well-structured report based on the analyzed data.",
    memory=True,
    verbose=True,
    backstory="You are a skilled communicator and an excellent report and document creator, with a talent for turning complex information into clear, concise, and visually appealing reports.",
    llm=OpenAIGPT4o
)