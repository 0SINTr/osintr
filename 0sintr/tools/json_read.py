import json
import os
from crewai_tools import tool

@tool
def JSONFileReaderTool(file_path: str, encoding: str = 'utf-8') -> str:
    """
    Custom tool to read and return the contents of a JSON file with specified encoding.
    
    Parameters:
    file_path (str): Path of the JSON file to read
    encoding (str): Encoding of the file (default is 'utf-8')
    
    Returns:
    str: A string containing the contents of the JSON file or an error message.
    """
    try:
        # Check if the file exists
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' does not exist."
        
        # Check if the file is a JSON file
        if not file_path.endswith('.json'):
            return "Error: The file provided is not a JSON file."

        # Read the JSON file with the specified encoding
        with open(file_path, 'r', encoding=encoding) as json_file:
            data = json.load(json_file)
        
        # Return the formatted contents of the JSON file
        return json.dumps(data, indent=4)
    
    except UnicodeDecodeError:
        return f"Error: Unable to decode the file using '{encoding}' encoding."
    
    except json.JSONDecodeError:
        return "Error: The file contains invalid JSON."
    
    except Exception as e:
        return f"Error reading the file: {str(e)}"