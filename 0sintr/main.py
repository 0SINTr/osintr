from research import main
from crewai import Crew, Process
from agents import analyst, report_writer
from tasks import analysis_task, report_writing_task

# Perform research and assemble the crew for analysis
if __name__ == "__main__":
    # Create the Crew with the agents and tasks
    crew = Crew(
        agents=[analyst, report_writer],
        tasks=[analysis_task, report_writing_task],
        process=Process.sequential,  # Ensure tasks are executed in order
        verbose=True,
    )

    # Kick off the crew process, passing the user input as 'target'
    results = crew.kickoff()

    print("~~~ \nCrew work is DONE. Check for report.")