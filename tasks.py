from crewai import Task
from agents import researcher, analyst, report_writer
from textwrap import dedent

# Define Research Task
research_task = Task(
    description=dedent("Conduct an in-depth OSINT investigation on the specified target which is {target}. If you do your BEST WORK, I'll give you a $10,000 commission!"),
    expected_output=dedent("A comprehensive dataset including all relevant details about the target."),
    agent=researcher,
    async_execution=True
)

# Define Analysis Task
analysis_task = Task(
    description=dedent("Analyze the data provided by the researcher to identify connections, patterns, and insights. If you do your BEST WORK, I'll give you a $10,000 commission!"),
    expected_output=dedent("A well-thought-out analysis of the data provided by the researcher that highlights key connections, insights and findings about the target of the investigation."),
    agent=analyst,
    async_execution=False
)

# Define Report Writing Task
report_writing_task = Task(
    description=dedent("Create a detailed and visually appealing report based on the analysis. If you do your BEST WORK, I'll give you a $10,000 commission!"),
    expected_output=dedent("A professional, well-structured report in markdown format summarizing the OSINT findings, complete with sections and highlights. Do not add the triple tick marks at the beginning or end of the file. Also do not say what type it is in the first line."),
    agent=report_writer,
    output_file='osint_report.md',
    async_execution=False
)