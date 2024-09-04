from crewai import Task
from prompts import *
from tools.google import GoogleSearchTool
from agents import researcher, report_writer

# Define Research Task
research_task = Task(
    description=google_research_task_description,
    expected_output=google_research_task_output,
    agent=researcher,
    tools=[GoogleSearchTool],
    async_execution=False,
)
'''
# Define Analysis Task
analysis_task = Task(
    description=analysis_task_description,
    expected_output=analysis_task_output,
    agent=analyst,
    async_execution=False,
)
'''
# Define Report Writing Task
report_writing_task = Task(
    description=report_writing_task_description,
    expected_output=report_writing_task_output,
    agent=report_writer,
    output_file='OSINT_REPORT.md',
    async_execution=False
)