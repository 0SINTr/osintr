from crewai import Crew, Process
from agents import researcher, analyst, report_writer
from tasks import research_task, analysis_task, report_writing_task

# Capture the input from the user
if __name__ == "__main__":
    target = input("Enter Email | Username | Phone Number: ")
    print("Target:", target)  # Verify the target input

    # Create the Crew with the agents and tasks
    crew = Crew(
        agents=[researcher, analyst, report_writer],
        tasks=[research_task, analysis_task, report_writing_task],
        process=Process.sequential,  # Ensure tasks are executed in order
        verbose=True,
    )

    # Kick off the crew process, passing the user input as 'target'
    results = crew.kickoff(inputs={'target': target})

    print("~~~ \nCrew work is DONE. Check for report.")