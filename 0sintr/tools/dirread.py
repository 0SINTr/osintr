import os
from crewai_tools import tool

@tool
def DirectoryReadTool(directory_path: str) -> str:
    """
    Custom tool to read and list contents of a directory.
    
    Parameters:
    directory_path (str): Path of the directory to read
    
    Returns:
    str: A string containing the list of files and subdirectories.
    """
    try:
        if not os.path.exists(directory_path):
            return f"Error: Directory '{directory_path}' does not exist."

        files_and_dirs = os.listdir(directory_path)
        if not files_and_dirs:
            return f"Directory '{directory_path}' is empty."

        return files_and_dirs
    
    except Exception as e:
        return f"Error reading directory: {str(e)}"
