from langchain_community.utilities import SerpAPIWrapper
from langchain_core.tools import Tool

def google_search_function(target):
    print(f"\n\nRunning search for target: {target}")
    if not isinstance(target, str):
        print("Error: target is not a string.")
        return None
    
    params = {
    "engine": "google",
    }
    search = SerpAPIWrapper(params=params)

    try:
        result = search.run(target)  # Pass the query to the SerpAPIWrapper's search method
        return result
    except Exception as e:
        # Handle any errors that occur during the search
        print(f"Error during Google search: {str(e)}")
        return None
    
# Wrap the function into a Tool object
GoogleSearchTool = Tool.from_function(
    func=google_search_function,
    name="Google Search Tool",
    description="Search for the target using Google and return the results."
)