import os
import sys
import importlib.resources
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from colorama import Fore, Style
from datetime import datetime

def generate_html_report(data, output_html_path):
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
    try:
        # Use importlib.resources to locate the report_template.html file in the templates directory
        with importlib.resources.path('osintr.templates', 'report_template.html') as template_file:
            # Extract the directory and filename from the template_path
            template_dir = os.path.dirname(template_file)
            template_file_name = os.path.basename(template_file)

            # Initialize Jinja2 environment with the template directory
            env = Environment(loader=FileSystemLoader(searchpath=template_dir))
            template = env.get_template(template_file_name)
            
            # Render the template with data
            rendered_html = template.render(
                initial_target=initial_target,
                email_addresses=email_addresses,
                relevant_urls=relevant_urls,
                other_urls=other_urls,
                generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
    except TemplateNotFound:
        print(Style.BRIGHT + Fore.RED + "[-] Error: report_template.html not found." + Style.RESET_ALL)
        sys.exit(1)
    except Exception as e:
        print(Style.BRIGHT + Fore.RED + f"[-] An error occurred while generating the report: {e}" + Style.RESET_ALL)
        sys.exit(1)

    # Ensure the output directory exists
    output_dir = os.path.dirname(output_html_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Write the rendered HTML to the output file
    try:
        with open(output_html_path, 'w', encoding='utf-8') as f:
            f.write(rendered_html)
        print(Style.BRIGHT + Fore.BLUE + "\n[v] Relevant data saved to " + Fore.YELLOW + f"{output_html_path}" + Style.RESET_ALL)
    except Exception as e:
        print(Style.BRIGHT + Fore.RED + f"[-] Error writing report to '{output_html_path}': {e}" + Style.RESET_ALL)
        sys.exit(1)
