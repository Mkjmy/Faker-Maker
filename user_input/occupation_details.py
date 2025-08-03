import difflib # Added for fuzzy matching

import questionary
from .exceptions import BackException
from utils.custom_styles import custom_style

def select_desired_education_level(debug_print_func):
    """
    Returns a dictionary defining the question for selecting the desired education level.
    This function is intended for use with the Pygame GUI.
    
    Args:
        debug_print_func (function): A function for printing debug messages.
        
    Returns:
        dict: A dictionary representing the 'select' type question for education level selection.
              It includes choices for various education levels.
    """
    education_level_choices = ["high school", "associates", "bachelors", "masters", "doctorate", "any"]
    choices = [{'name': c.capitalize(), 'value': c} for c in education_level_choices]
    choices.append({'name': "Back", 'value': "back"})
    return {
        'type': 'select',
        'prompt': "Enter desired education level:",
        'choices': choices,
        'default': "any",
        'name': 'desired_education_level'
    }
