import questionary
from .exceptions import BackException
from utils.custom_styles import custom_style

def select_unconventional_data_inclusion(debug_print_func) -> dict:
    """
    Returns a dictionary defining the question for selecting categories of unconventional data to include.
    This function is intended for use with the Pygame GUI and provides a checkbox interface.
    
    Args:
        debug_print_func (function): A function for printing debug messages.
        
    Returns:
        dict: A dictionary representing the 'checkbox' type question for unconventional data selection.
              It includes various categories like Personality Traits, Life Events, etc.
    """
    choices = [
        {"name": "Personality Traits", "value": "personality_traits"},
        {"name": "Life Events", "value": "life_events"},
        {"name": "Online Behaviors", "value": "online_behaviors"},
        {"name": "Texting & Typing Style", "value": "texting_typing_style"},
        {"name": "Digital Footprint", "value": "digital_footprint"},
        {"name": "Device Habits", "value": "device_habits"}
    ]

    return {
        'type': 'checkbox',
        'prompt': "Select categories of unconventional data to include (press space to select, enter to confirm):",
        'choices': choices,
        'validate': "Please select at least one category.", # Simplified validation for Pygame
        'instruction': "Use spacebar to select/deselect, Enter to confirm.",
        'name': 'unconventional_data_selection'
    }