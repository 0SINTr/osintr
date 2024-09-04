from langchain_core.tools import Tool
import requests

def validate_url_function(url: str) -> bool:
    """
    Validate whether a given URL is active and reachable.
    Returns True if the URL is valid, False otherwise.
    """
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# Wrap the function into a Tool object
ValidateUrlTool = Tool.from_function(
    func=validate_url_function,
    name="Validate URL Tool",
    description="Validate a URL to check if it is active and reachable. Returns True if the URL is valid, False otherwise.",
)
