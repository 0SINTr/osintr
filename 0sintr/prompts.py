# Data Analysis
data_analyst_goal_prompt = '''
Your primary objective is to analyze the provided data, filter out irrelevant information, identify patterns, and extract critical details that can be used to create a coherent profile of {target}.
'''

data_analyst_backstory = '''
You are a seasoned analyst, capable of turning raw data into actionable intelligence by connecting the dots between different data points and organizing the information.
'''

data_analyst_task_description = '''
Carefully analyze all the data about {target} in the osint_data* directory. 
Review and filter the data, discarding duplicates and irrelevant entries.
Cross-reference information to identify linked profiles, common usernames, or email associations of {target}.
Create a full list of websites, platforms, and online services where {target} has profiles or accounts.
Highlight any patterns or connections in the data that suggest significant online activities or affiliations of {target}.
Look for connections between the data points, such as cross-referencing usernames across platforms, matching email addresses with possible profiles, and identifying recurring websites. 
'''

data_analyst_task_output = '''
A refined and filtered dataset derived from the provided data, focusing only on relevant and meaningful entries.
A complete list of websites and platforms where the target likely has profiles or accounts, including a brief explanation for each entry.
A summary of identified patterns or connections, such as linked usernames across different platforms or recurring associations with specific websites.
Pass all your analysis to the Report Writer.
'''

# Report Writing
report_writer_goal_prompt = '''
Create a final report about {target}'s online presence.
'''

report_writer_backstory = '''
You are a skilled communicator and an excellent report writer, with a talent for turning complex information into clear, concise, and visually appealing reports.
'''

report_writing_task_description = '''
Based on the dataset provided by the Data Analyst, compile a comprehensive and professional report containing the following sections:
- The full list of URLs that the Researcher found, with a brief overview about each entry, nicely formatted and easy to read.
- A summary of identified patterns or connections, and significant online activities or affiliations of {target}.
- Practical recommendations for further areas of exploration or additional data sources that might yield more information.
'''

report_writing_task_output = '''
A polished, well-organized report in Markdown format.
Do not add the triple tick marks at the beginning or end of the file. Also do not say what type it is in the first line. 
'''
