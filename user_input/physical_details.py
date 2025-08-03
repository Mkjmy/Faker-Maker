import questionary
from .exceptions import BackException
from utils.custom_styles import custom_style

def select_physical_details(debug_print_func):
    """
    Returns a dictionary defining the question for including detailed physical characteristics.
    This function is intended for use with the Pygame GUI.
    
    Args:
        debug_print_func (function): A function for printing debug messages.
        
    Returns:
        dict: A dictionary representing the 'confirm' type question for physical details.
    """
    return {
        'type': 'confirm',
        'prompt': "Do you want to include a detailed physical description (e.g., eye color, hair color, height)? (Type 'yes' or 'no', or 'back')",
        'default': False,
        'name': 'physical_details'
    }