from crewai import Crew, Process
from ai_logic.agents import analyst, report_writer
from ai_logic.tasks import analysis_task, report_writing_task

# Capture the input from the user
if __name__ == "__main__":
    print("Target:", target)  # Verify the target input

    # Create the Crew with the agents and tasks
    crew = Crew(
        agents=[analyst, report_writer],
        tasks=[analysis_task, report_writing_task],
        process=Process.sequential,  # Ensure tasks are executed in order
        verbose=True,
    )

    # Kick off the crew process
    results = crew.kickoff()

    print("~~~ \nCrew work is DONE. Check for report.")