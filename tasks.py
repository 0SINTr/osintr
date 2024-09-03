from crewai import Task
from agents import researcher, analyst, report_writer

# Define Research Task
research_task = Task(
    description="Conduct an in-depth OSINT investigation on {target} using the provided tools. Perform the search on the exact string matching the {target} and do not add other search terms.",
    expected_output="A comprehensive dataset including all relevant details about {target} gathered from Google search results.",
    agent=researcher,
    async_execution=False,
)

# Define Analysis Task
analysis_task = Task(
    description="Analyze the data provided by the researcher to identify connections, patterns, and insights for {target}.",
    expected_output="A well-thought-out analysis of the data provided by the researcher that highlights key connections, insights and findings about {target}.",
    agent=analyst,
    async_execution=False,
)

# Define Report Writing Task
report_writing_task = Task(
    description="Create a detailed and visually appealing report based on the analysis.",
    expected_output="A professional, well-structured report in markdown format summarizing the OSINT findings, complete with sections and highlights. Do not add the triple tick marks at the beginning or end of the file. Also do not say what type it is in the first line.",
    agent=report_writer,
    output_file='osint_report.md',
    async_execution=False
)