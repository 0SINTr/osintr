from crewai import Task
from tools.google import GoogleSearchTool
from agents import researcher, analyst, report_writer

# Define Research Task
research_task = Task(
    description="Conduct an in-depth OSINT investigation on {target} using the provided tool. Perform the search on the exact string matching {target} and DO NOT ADD OTHER SEARCH TERMS OR VARIATIONS.",
    expected_output="A comprehensive dataset including all relevant details about {target} gathered from Google search results.",
    agent=researcher,
    tools=[GoogleSearchTool],
    async_execution=False,
)

# Define Analysis Task
analysis_task = Task(
    description="Analyze the data provided by the researcher to identify connections, patterns, and insights for {target}. Do your best to scrape the search results from the Researcher and list ALL the websites, pages or forums where {target} has a profile page or account, as well as any other open-source personal information about {target} that might be relevant to the OSINT investigation. Add these lists to your analysis.",
    expected_output="A very detailed and well-thought-out analysis of the data provided by the researcher that highlights key connections, insights and findings about {target}.",
    agent=analyst,
    async_execution=False,
)

# Define Report Writing Task
report_writing_task = Task(
    description="Create a detailed and visually appealing report based on the analysis. Don't miss anything that might be relevant to the investigation.",
    expected_output="A professional, well-structured report in markdown format summarizing the OSINT findings, complete with sections and highlights. Do not add the triple tick marks at the beginning or end of the file. Also do not say what type it is in the first line.",
    agent=report_writer,
    output_file='osint_report.md',
    async_execution=False
)