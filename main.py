from crew import kickoff
from textwrap import dedent

if __name__ == "__main__":
    print("~~~ Welcome to 0SINTr ~~~")
    target = input(dedent("Enter Email | Username | Phone Number: "))
    result = kickoff(target)
    print("\n\n~~~~~~~~~~~~~~~~~~~~")
    print("~~~ Crew work is DONE. Check for report.")