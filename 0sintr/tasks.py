from crewai import Task
from agents import analyst, report_writer
from prompts import *

# Define Analysis Task
analysis_task = Task(
    description=data_analyst_task_description,
    expected_output=data_analyst_task_output,
    agent=analyst,
    async_execution=False,
)

# Define Report Writing Task
report_writing_task = Task(
    description=report_writing_task_description,
    expected_output=report_writing_task_output,
    agent=report_writer,
    output_file='OSINT_REPORT.md',
async_execution=False
)