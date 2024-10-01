import os
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from colorama import Fore, Style

def generate_html_report(data, template_path='report_template.html', output_html_path='Final_Report.html'):
    """
    Generates an HTML report from the provided data using a Jinja2 template.

    Parameters:
    - data (dict): The combined OSINT data containing email addresses and relevant URLs.
    - template_path (str): Path to the Jinja2 HTML template.
    - output_html_path (str): Path where the generated HTML report will be saved.
    """
    # Extract data
    initial_target = data.get('initial_target', 'N/A')
    email_addresses = data.get('Email Addresses', [])
    relevant_urls = data.get('Relevant URLs', [])
    other_urls = data.get('Other URLs', [])
    
    # Set up Jinja2 environment
    template_dir = os.path.dirname(template_path)
    if template_dir == '':
        template_dir = '.'  # Current directory
    env = Environment(loader=FileSystemLoader(searchpath=os.path.dirname(template_path) or './'))
    template = env.get_template(os.path.basename(template_path))
    
    # Render the template with data
    rendered_html = template.render(
        initial_target=initial_target,
        email_addresses=email_addresses,
        relevant_urls=relevant_urls,
        other_urls=other_urls,
        generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_html_path), exist_ok=True)

    # Write the rendered HTML to the output file
    with open(output_html_path, 'w') as f:
        f.write(rendered_html)
    
    print(Fore.GREEN + "\n [+] Relevant data saved to " + Style.BRIGHT + f"{output_html_path}" + Style.RESET_ALL)
