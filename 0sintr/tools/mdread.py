from crewai_tools import tool

@tool
def MarkdownFileReaderTool(file_path: str) -> str:
    """
    Reads the content of a Markdown file and handles encoding issues.

    Args:
        file_path (str): The path to the Markdown file.

    Returns:
        str: The content of the file or an error message.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except UnicodeDecodeError:
        # Fallback to latin-1 encoding
        try:
            with open(file_path, "r", encoding="latin-1") as file:
                return file.read()
        except Exception as e:
            return f"Error reading the file: {str(e)}"
