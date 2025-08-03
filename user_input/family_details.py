import difflib # Added for fuzzy matching

import questionary
from .exceptions import BackException
from utils.custom_styles import custom_style

def select_family_details(max_age_for_questions, unconventional_data_selection: dict, debug_print_func):
    """
    Returns a dictionary defining the question for including family details (marital status, children).
    This question is conditional based on the maximum age of the profile or the inclusion of
    unconventional data.
    
    Args:
        max_age_for_questions (int): The maximum age of the generated profile.
        unconventional_data_selection (dict): A dictionary indicating selected unconventional data categories.
        debug_print_func (function): A function for printing debug messages.
        
    Returns:
        dict: A dictionary representing the 'confirm' type question for family details,
              or a 'skipped' type dictionary if the question is not applicable.
    """
    if max_age_for_questions >= 16 or any(unconventional_data_selection.values()):
        return {
            'type': 'confirm',
            'prompt': "Do you want to include family details (marital status, children)?",
            'default': False,
            'name': 'family_details'
        }
    else:
        # If age is too low, automatically skip and return default values
        return {
            'type': 'skipped',
            'value': {
                'family_details': False,
                'marital_status': 'any',
                'num_children': 'any'
            },
            'store_as': ['family_details', 'marital_status', 'num_children']
        }

def select_marital_status(debug_print_func):
    """
    Returns a dictionary defining the question for selecting the desired marital status.
    
    Args:
        debug_print_func (function): A function for printing debug messages.
        
    Returns:
        dict: A dictionary representing the 'select' type question for marital status.
    """
    marital_status_choices = ["single", "married", "divorced", "widowed", "any"]
    choices = [{'name': c.capitalize(), 'value': c} for c in marital_status_choices]
    choices.append({'name': "Back", 'value': "back"})
    return {
        'type': 'select',
        'prompt': "Desired marital status:",
        'choices': choices,
        'default': "any",
        'name': 'marital_status'
    }

def select_num_children(max_age_for_questions, unconventional_data_selection: dict, debug_print_func):
    """
    Returns a dictionary defining the question for specifying the number of children.
    The maximum number of children displayed is conditional based on the profile's age
    and whether unconventional data is included.
    
    Args:
        max_age_for_questions (int): The maximum age of the generated profile.
        unconventional_data_selection (dict): A dictionary indicating selected unconventional data categories.
        debug_print_func (function): A function for printing debug messages.
        
    Returns:
        dict: A dictionary representing the 'text' type question for the number of children.
    """
    max_children_display = 5
    if not any(unconventional_data_selection.values()):
        if max_age_for_questions < 20:
            max_children_display = 0
        elif max_age_for_questions < 25:
            max_children_display = 1
        elif max_age_for_questions < 30:
            max_children_display = 2

    return {
        'type': 'text',
        'prompt': f"Desired number of children (0-{max_children_display}, or 'any'):",
        'default': "any",
        'validate': f"Enter a number between 0 and {max_children_display}, or 'any'.", # Simplified validation for Pygame
        'instruction': "Enter a number, 'any', or 'back' to return to the previous question.",
        'name': 'num_children'
    }