from agents import data_organizer, pattern_analyzer, profile_builder
from crewai import Task
from prompts import *

# Data Organization Task
data_organizer_task = Task(
    description=data_organizer_task_description,
    expected_output=data_organizer_task_output,
    agent=data_organizer,
    async_execution=False
)

# Pattern Detection Task
pattern_analyzer_task = Task(
    description=pattern_analyzer_task_description,
    expected_output=pattern_analyzer_task_output,
    agent=pattern_analyzer,
    async_execution=False
)

# Digital Footprint Creation Task
profile_builder_task = Task(
    description=profile_builder_task_description,
    expected_output=profile_builder_task_output,
    agent=profile_builder,
    async_execution=False
)