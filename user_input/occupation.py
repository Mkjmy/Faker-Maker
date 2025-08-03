import difflib # Added for fuzzy matching

import questionary
from user_input.exceptions import BackException
from utils.custom_styles import custom_style

def select_occupation(occupation_data, debug_print_func):
    """
    Returns a dictionary defining the question for selecting an occupation.
    This function is intended for use with the Pygame GUI and provides an
    autocomplete feature for available occupations.
    
    Args:
        occupation_data (dict): A dictionary containing occupation data, typically
                                 loaded from a JSON file (e.g., 'occupations': [...]).
        debug_print_func (function): A function for printing debug messages.
        
    Returns:
        dict: A dictionary representing the 'autocomplete' type question for occupation selection.
              It includes a list of available occupations as choices.
    """
    debug_print_func("Selecting occupation.")
    
    # Extract occupation names from the data
    available_occupations = [occ['name'] for occ in occupation_data]

    if not available_occupations:
        debug_print_func("No occupations available for this region. Skipping occupation selection.")
        return {'type': 'skipped', 'value': 'any', 'store_as': 'occupation'}

    return {
        'type': 'autocomplete',
        'prompt': "Enter desired occupation (leave blank for random):",
        'choices': available_occupations,
        'validate': "Occupation must be in the list or blank.", # Simplified validation for Pygame
        'instruction': "Type to filter, or leave blank for random. Type 'back' to go back.",
        'name': 'occupation'
    }