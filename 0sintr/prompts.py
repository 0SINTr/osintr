# Data organizing
data_organizer_goal = '''
Organize data collected in JSON files into categories based on relevance and relationship with the target and build a report.
'''

data_organizer_backstory = '''
This agent is specialized in sorting through vast amounts of data to bring order and structure, ensuring that no detail is missed.
'''

data_organizer_task_description = '''
Search {directory} for the GOOGLE.json, BREACHES.json, PASTES.json, OSINDUS.json files using the DirectoryReadTool.
Use the JSONFileReaderTool to read each file and start building the report with the following sections:
- Introduction: overview of the target, files and tools used to build the report, programming language etc.

Read the GOOGLE.json file and:
- Add the values corresponding to "Relevant Email Addresses" to Section 1 of the report.
- Add the values corresponding to "Relevant Links" and organize to Section 2 of the report.
- Add the values corresponding to "Possibly Related Emails" to Section 6 of the report.
- Add the values corresponding to "Possibly Related Links" to Section 7 of the report.

Read the BREACHES.json file and:
- Add the values of Name, BreachDate and Description, organize them in Section 3 of the report.

Read the PASTES.json file and:
- Add the values of Source, Id, Title and Date, and organize them in Section 4 of the report.

Read the OSINDUS.json file and:
- Extract all values corresponding to the "module" keys and mark them as "Registered" in Section 5 of the report.

Keep track of the files you already read and make sure to not re-read them.
If you don't find one or more of the JSON files above, move on to the next one until all JSON files have been read.
Make sure to add the sections in ascending order. If some JSON files are missing, re-number the sections accordingly. 
Once you build the report with all the sections above, check it to be well-structured and visually appealing, then stop.
'''

data_organizer_task_output = '''
Professional report in Markdown format.
'''


# Pattern analysis
pattern_analyzer_goal = '''
Analyze organized data for patterns, recurring emails, linked usernames, or connections across platforms.
'''

pattern_analyzer_backstory = '''
A skilled observer, adept at finding connections and patterns within the data, this agent excels at identifying hidden relationships between disparate data points.
'''

pattern_analyzer_task_description = '''
Analyze the Markdown report provided by Information Aggregator for recurring emails, usernames, and connections across platforms for the target {target}. Detect patterns and associations between different datasets.
'''

pattern_analyzer_task_output = '''
Summary with identified patterns and connections related to {target}.
'''