from crewai_tools import SerperDevTool

def google_search_function(target):
    print(f"Running search for target: {target}")
    
    # Initialize the tool for Internet searching capabilities
    tool = SerperDevTool(
        search_url='https://google.serper.dev/search',
        n_results=50,
    )

    try:
        result = tool.run(search_query=target)  # Pass the query to the SerpAPIWrapper's search method
        return result
    except Exception as e:
        # Handle any errors that occur during the search
        print(f"Error during Google search: {str(e)}")
        return None