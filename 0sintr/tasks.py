from crewai import Task
from agents import google_analyst, hibp_analyst, osind_analyst, report_writer
from prompts import *
from crewai_tools import (
    DirectorySearchTool,
    JSONSearchTool,
    MDXSearchTool
)

# Define Google Data Analysis Task
google_analysis_task = Task(
    description=google_analyst_task_description,
    expected_output=google_analyst_task_output,
    tools=[DirectorySearchTool,MDXSearchTool],
    agent=google_analyst,
    async_execution=True,
)

# Define HIBP Data Analysis Task
hibp_analysis_task = Task(
    description=hibp_analyst_task_description,
    expected_output=hibp_analyst_task_output,
    tools=[DirectorySearchTool,JSONSearchTool],
    agent=hibp_analyst,
    async_execution=True,
)

# Define OSINT.Industries Data Analysis Task
osind_analysis_task = Task(
    description=osind_analyst_task_description,
    expected_output=osind_analyst_task_output,
    tools=[DirectorySearchTool,JSONSearchTool],
    agent=osind_analyst,
    async_execution=True,
)

# Define Report Writing Task
report_writing_task = Task(
    description=report_writing_task_description,
    expected_output=report_writing_task_output,
    agent=report_writer,
    context=[google_analysis_task, hibp_analysis_task, osind_analysis_task]
    output_file='OSINT_REPORT.md',
    async_execution=False,
)