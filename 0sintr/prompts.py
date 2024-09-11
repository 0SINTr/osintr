# Data organizing
data_organizer_goal = '''
Organize data collected in JSON files into categories based on relevance and relationship with the target and build a report.
'''

data_organizer_backstory = '''
This agent is specialized in sorting through vast amounts of data to bring order and structure, ensuring that no detail is missed.
'''

data_organizer_task_description = '''
Organize the data from the GOOGLE.json, BREACHES.json, PASTES.json, OSINDUS.json files located in {directory}.
If a json file is missing, continue processing the JSON files that are present and skip the missing ones.
From GOOGLE.json, take the values corresponding to "Relevant Email Addresses" and organize them in a section of the report.
From GOOGLE.json, take the values corresponding to "Relevant Links" and organize them in a section of the report.
From BREACHES.json, take the Name, BreachDate and Description, and organize them in a section of the report.
From PASTES.json, take the Source, Id, Title and Date, and organize them in a section of the report.
From OSINDUS.json, extract all values corresponding to "module" and mark them as "Registered" in a section of the report.
From GOOGLE.json, take the values corresponding to "Relevant Email Addresses" and organize them in a section of the report.
From GOOGLE.json, take the values corresponding to "Possibly Related Emails" and organize them in a section of the report.
From GOOGLE.json, take the values corresponding to "Possibly Related Links" and organize them in a section of the report.
Format the report to be well structured and visually appealing.
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