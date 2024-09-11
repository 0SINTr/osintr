# Suppress specific UserWarning globally
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
from research import research
from colorama import Fore, Style
from agents import data_organizer, pattern_analyzer, profile_builder
from tasks import data_organizer_task, pattern_analyzer_task, profile_builder_task
from crewai import Crew, Process

# Perform research and assemble the crew for analysis
def main():
    # Run the Reasearch phase and return the target
    research_result = research()
    target = research_result[0]
    directory = research_result[1]

    # Create the Crew with the agents and tasks
    crew = Crew(
        agents=[data_organizer, pattern_analyzer, profile_builder],
        tasks=[data_organizer_task, pattern_analyzer_task, profile_builder_task],
        process=Process.sequential,  # Ensure tasks are executed in order
        verbose=True,
    )

    # Run the Data Analysis phase on the target
    crew.kickoff(inputs={'target': target, 'directory': directory})

    print(Fore.GREEN + "\n\n  |--- DONE. Check " + Style.BRIGHT + "OSINT_REPORT.md\n" + Style.RESET_ALL)

if __name__ == "__main__":
    main()