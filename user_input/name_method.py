import questionary
from .exceptions import BackException
from utils.custom_styles import custom_style

def select_name_generation_method(debug_print_func):
    """
    Returns a dictionary defining the question for selecting the name generation method.
    This function is intended for use with the Pygame GUI.
    
    Args:
        debug_print_func (function): A function for printing debug messages.
        
    Returns:
        dict: A dictionary representing the 'select' type question for name generation method.
              It includes choices for 'existing' names or 'custom' names.
    """
    return {
        'type': 'select',
        'prompt': "Please select a name generation method:",
        'choices': [
            {"name": "Use existing names (from data files)", "value": "existing"},
            {"name": "Enter custom first and last names", "value": "custom"},
            {"name": "Go back to previous question", "value": "back"}
        ],
        'default': "existing",
        'name': 'name_generation_method'
    }

def get_custom_name_questions(debug_print_func):
    """
    A generator function that yields dictionaries defining questions for entering
    custom first and last names. Intended for use with the Pygame GUI.
    
    Args:
        debug_print_func (function): A function for printing debug messages.
        
    Yields:
        dict: A dictionary representing a 'text' type question for either the
              custom first name or the custom last name.
    """
    yield {
        'name': 'custom_first_name',
        'prompt': "Enter custom first name:",
        'type': 'text',
        'validate': "First name cannot be empty.", # Simplified validation for Pygame
        'store_as': 'custom_first_name',
        'instruction': "Type 'back' to go back."
    }
    yield {
        'name': 'custom_last_name',
        'prompt': "Enter custom last name:",
        'type': 'text',
        'validate': "Last name cannot be empty.", # Simplified validation for Pygame
        'store_as': 'custom_last_name',
        'instruction': "Type 'back' to go back."
    }