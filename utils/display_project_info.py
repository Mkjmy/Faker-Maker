import os
import re
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

def display_project_information(console=None, wait_for_input=True):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    usage_path = os.path.join(script_dir, 'usage.txt')
    
    try:
        with open(usage_path, 'r') as f:
            usage_content = f.read()

        # Remove Rich markup for Pygame display
        # This regex removes patterns like [bold green], [/bold green], [bold], [/bold], etc.
        cleaned_content = re.sub(r'\[/?(?:bold|italic|underline|strike|dim|red|green|blue|cyan|magenta|yellow|white|black|#\w+)(?:\s+\w+)?\]', '', usage_content)
        
        # For CLI mode, still return Rich objects
        if console and not wait_for_input: # This condition implies CLI usage
            project_info_text = Text.from_markup(usage_content)
            return Align.center(project_info_text)
        else:
            # For Pygame or other non-Rich contexts, return plain text
            return cleaned_content

    except FileNotFoundError:
        # For CLI mode, return Rich Panel
        if console:
            return Panel(Text("[red]Error: usage.txt not found.[/red]", style="red"), title="Error", border_style="red")
        else:
            # For Pygame, return a simple error string
            return "Error: usage.txt not found."