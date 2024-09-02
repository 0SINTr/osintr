from crewai import Crew, Process
from agents import researcher, analyst, report_writer
from tasks import research_task, analysis_task, report_writing_task

# Set up the environment keys
import os
os.environ["OPENAI_API_KEY"] = "Your-OSINT-Industries-Key"
os.environ["OPENAI_MODEL_NAME"] = "gpt-4o"
os.environ["SERPAPI_API_KEY"] = "Your-IntelX-Key"

# Creating the Crew
crew = Crew(
    agents=[researcher, analyst, report_writer],
    tasks=[research_task, analysis_task, report_writing_task],
    process=Process.sequential,
    verbose=True,
)

# Execute the Crew
def kickoff(target):
    return crew.kickoff(inputs={"target": target})
