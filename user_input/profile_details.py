import difflib # Added for fuzzy matching

import questionary
from .exceptions import BackException
from utils.custom_styles import custom_style

def select_num_profiles(debug_print_func):
    """
    Returns a dictionary defining the question for specifying the number of profiles to generate.
    This function is intended for use with the Pygame GUI.
    
    Args:
        debug_print_func (function): A function for printing debug messages.
        
    Returns:
        dict: A dictionary representing the 'text' type question for the number of profiles.
    """
    return {
        'type': 'text',
        'prompt': "How many profiles would you like to generate?",
        'default': "1",
        'validate': "Enter a positive number or 'back'.", # Simplified validation for Pygame
        'instruction': "Enter a positive number or 'back' to return to the previous question.",
        'name': 'num_profiles'
    }

def select_age_range(debug_print_func):
    """
    Returns a dictionary defining the question for selecting the desired age range.
    This function is intended for use with the Pygame GUI.
    
    Args:
        debug_print_func (function): A function for printing debug messages.
        
    Returns:
        dict: A dictionary representing the 'text' type question for the age range.
    """
    return {
        'type': 'text',
        'prompt': "Enter the desired age range for the profiles: (e.g., '18-30', '40+', '25', or 'any' for no age constraint)",
        'default': "any",
        'name': 'age_range'
    }

def select_gender(debug_print_func):
    """
    Returns a dictionary defining the question for selecting the preferred gender.
    This function is intended for use with the Pygame GUI.
    
    Args:
        debug_print_func (function): A function for printing debug messages.
        
    Returns:
        dict: A dictionary representing the 'select' type question for gender selection.
    """
    gender_choices = ["male", "female", "other", "any"]
    choices = [{'name': c.capitalize(), 'value': c} for c in gender_choices]
    choices.append({'name': "Back", 'value': "back"})
    return {
        'type': 'select',
        'prompt': "Enter preferred gender:",
        'choices': choices,
        'default': 'any',
        'name': 'gender'
    }

def select_hidden_attributes_inclusion(debug_print_func) -> dict:
    """
    Returns a dictionary defining the question for including hidden attributes.
    
    Args:
        debug_print_func (function): A function for printing debug messages.
        
    Returns:
        dict: A dictionary representing the 'confirm' type question for hidden attributes inclusion.
    """
    return {
        'type': 'confirm',
        'prompt': "Do you want to display hidden attributes (e.g., Cognitive Style Score, Personality Trait)?",
        'default': False,
        'name': 'include_hidden_attributes'
    }
