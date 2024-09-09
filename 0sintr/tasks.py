from agents import google_analyst, hibp_analyst, osind_analyst, report_writer, curator
from crewai import Task
from prompts import *

# Define the Google Data Analysis Task
google_analysis_task = Task(
    description=google_analyst_task_description,
    expected_output=google_analyst_task_output,
    agent=google_analyst,
    async_execution=True,
)

# Define the HIBP Data Analysis Task
hibp_analysis_task = Task(
    description=hibp_analyst_task_description,
    expected_output=hibp_analyst_task_output,
    agent=hibp_analyst,
    async_execution=True,
)

# Define the OSINT.Industries Data Analysis Task
osind_analysis_task = Task(
    description=osind_analyst_task_description,
    expected_output=osind_analyst_task_output,
    agent=osind_analyst,
    async_execution=True,
)

# Define the Curator Task
curator_task = Task(
    description=curator_task_description,
    expected_output=curator_task_output,
    agent=curator,
    context=[google_analysis_task, hibp_analysis_task, osind_analysis_task],
    async_execution=False,
)

# Define the Report Writing Task
report_writing_task = Task(
    description=report_writing_task_description,
    expected_output=report_writing_task_output,
    agent=report_writer,
    output_file='OSINT_REPORT.md',
    async_execution=False,
)