from research import research
from crewai import Crew, Process
from agents import analyst, report_writer
from tasks import analysis_task, report_writing_task

# Perform research and assemble the crew for analysis
def main():
    # Run the Reasearch phase
    research()

    # Create the Crew with the agents and tasks
    crew = Crew(
        agents=[analyst, report_writer],
        tasks=[analysis_task, report_writing_task],
        process=Process.sequential,  # Ensure tasks are executed in order
        verbose=True,
    )

    # Run the Data Analysis phase
    crew.kickoff()

    print("~~~ \nCrew work is DONE. Check for report.")

if __name__ == "__main__":
    main()