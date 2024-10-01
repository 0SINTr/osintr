import os
import sys
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from colorama import Fore, Style
from datetime import datetime

def generate_html_report(data, template_path, output_html_path):
    """
    Generates an HTML report from the provided data using a Jinja2 template.

    Parameters:
    - data (dict): The combined OSINT data containing email addresses and relevant URLs.
    - template_path (str): Path to the Jinja2 HTML template.
    - output_html_path (str): Path where the generated HTML report will be saved.
    """
    # Extract data
    initial_target = data.get('OSINT Target', 'N/A')
    email_addresses = data.get('Email Addresses', [])
    relevant_urls = data.get('Relevant URLs', [])
    other_urls = data.get('Other URLs', [])

    # Ensure the template_path exists
    if not os.path.isfile(template_path):
        print(Fore.RED + f"Error: Template file '{template_path}' does not exist." + Style.RESET_ALL)
        sys.exit(1)

    # Extract the directory and filename from the template_path
    template_dir = os.path.dirname(template_path)
    template_file_name = os.path.basename(template_path)

    # Initialize Jinja2 environment with the template directory
    env = Environment(loader=FileSystemLoader(searchpath=template_dir))

    try:
        # Load the specified template
        template = env.get_template(template_file_name)
    except TemplateNotFound:
        print(Fore.RED + f"Error: Template '{template_file_name}' not found in directory '{template_dir}'." + Style.RESET_ALL)
        sys.exit(1)

    # Render the template with data
    rendered_html = template.render(
        initial_target=initial_target,
        email_addresses=email_addresses,
        relevant_urls=relevant_urls,
        other_urls=other_urls,
        generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    # Ensure the output directory exists
    output_dir = os.path.dirname(output_html_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Write the rendered HTML to the output file
    try:
        with open(output_html_path, 'w', encoding='utf-8') as f:
            f.write(rendered_html)
        print(Fore.GREEN + " [+] Relevant data saved to " + Style.BRIGHT + f"{output_html_path}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Error writing report to '{output_html_path}': {e}" + Style.RESET_ALL)
        sys.exit(1)
