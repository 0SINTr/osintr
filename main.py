from crewai import Crew, Process
from agents import researcher, report_writer
from tasks import research_task, report_writing_task

# Capture the input from the user
if __name__ == "__main__":
    target_type = input("Target is 1. Email | 2. Username | 3. Phone No.: ")

    if target_type == "1":
        target = input("Enter the Email Address: ")
        query = f'{target}'
    elif target_type == "2":
        target = input("Enter Username: ")
        query = f'{target}'
    elif target_type == "3":
        target = input("Enter Phone No.: ")
        query = f'{target}'
    
    print("Target:", target)  # Verify the target input

    # Create the Crew with the agents and tasks
    crew = Crew(
        agents=[researcher, report_writer],
        tasks=[research_task, report_writing_task],
        process=Process.sequential,  # Ensure tasks are executed in order
        verbose=True,
    )

    # Kick off the crew process, passing the user input as 'target'
    results = crew.kickoff(inputs={'target': target})

    print("~~~ \nCrew work is DONE. Check for report.")