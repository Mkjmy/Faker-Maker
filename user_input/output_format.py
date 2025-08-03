import difflib # Added for fuzzy matching

import questionary
from .exceptions import BackException
from utils.custom_styles import custom_style

def select_output_format(debug_print_func):
    """
    Returns a dictionary defining the question for selecting the desired output format.
    This function is intended for use with the Pygame GUI.
    
    Args:
        debug_print_func (function): A function for printing debug messages.
        
    Returns:
        dict: A dictionary representing the 'select' type question for output format selection.
              It includes choices for 'console', 'csv', and 'json' output.
    """
    output_format_choices = ["console", "csv", "json"]
    choices = [{'name': c.capitalize(), 'value': c} for c in output_format_choices]
    choices.append({'name': "Back", 'value': "back"})
    return {
        'type': 'select',
        'prompt': "Select the desired output format:",
        'choices': choices,
        'default': "console",
        'name': 'output_format'
    }
