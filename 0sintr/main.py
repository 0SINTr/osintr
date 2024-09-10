# Suppress specific UserWarning globally
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
from research import research
from colorama import Fore, Style
from agents import google_analyst, hibp_analyst, osind_analyst, curator
from tasks import google_analysis_task, hibp_analysis_task, osind_analysis_task, curator_task
from crewai import Crew, Process

# Perform research and assemble the crew for analysis
def main():
    # Run the Reasearch phase and return the target
    research_result = research()
    target = research_result[0]
    directory = research_result[1]
    top_directory = research_result[2]

    # Create the Crew with the agents and tasks
    crew = Crew(
        agents=[google_analyst, hibp_analyst, osind_analyst, curator],
        tasks=[google_analysis_task, hibp_analysis_task, osind_analysis_task, curator_task],
        process=Process.sequential,  # Ensure tasks are executed in order
        verbose=True,
    )

    # Run the Data Analysis phase on the target
    crew.kickoff(inputs={'target': target, 'directory': directory, 'top_directory': top_directory})

    print(Fore.GREEN + "\n\n  |--- DONE. Check " + Style.BRIGHT + "OSINT_REPORT.md\n" + Style.RESET_ALL)

if __name__ == "__main__":
    main()