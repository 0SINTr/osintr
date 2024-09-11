# Data organizing
data_organizer_goal = '''
Organize collected OSINT data into categories based on relevance and relationship with the target.
'''

data_organizer_backstory = '''
This agent is specialized in sorting through vast amounts of data to bring order and structure, ensuring that no detail is missed.
'''

data_organizer_task_description = '''
Organize the data from the OSINT tool outputs located in {directory} (GOOGLE.json, BREACHES.json, PASTES.json, OSINDUS.json) related to the target {target} into categorized outputs for further analysis.
If a file is missing, continue processing the JSON files that are present and skip the missing ones.
'''

data_organizer_task_output = '''
A structured analysis of the data from the JSON files in {directory} related to {target}.
'''


# Pattern analysis
pattern_analyzer_goal = '''
Analyze organized data for patterns, recurring emails, linked usernames, or connections across platforms.
'''

pattern_analyzer_backstory = '''
A skilled observer, adept at finding connections and patterns within the data, this agent excels at identifying hidden relationships between disparate data points.
'''

pattern_analyzer_task_description = '''
Analyze the organized data for recurring emails, usernames, and connections across platforms for the target {target}. Detect patterns and associations between different datasets.
'''

pattern_analyzer_task_output = '''
A JSON file with identified patterns and connections related to {target}.
'''


# Profile building
profile_builder_goal = '''
Create a cohesive online profile, identifying digital associations and recurring data points.
'''

profile_builder_backstory = '''
An expert at piecing together digital footprints, this agent pulls together a comprehensive picture of a target’s online presence.
'''

profile_builder_task_description = '''
Create a comprehensive profile from the analyzed data, highlighting important associations, recurring emails, and accounts across different platforms for the target {target}.
'''

profile_builder_task_output = '''
A structured final report in Markdown format, saved to {directory}, summarizing the digital footprint of {target}, including key findings and patterns, as well as a list with relevant emails, links or usernames directly related to {target}.
'''