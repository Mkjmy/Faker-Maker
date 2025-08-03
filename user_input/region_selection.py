import random
import questionary
from .exceptions import BackException
from utils.custom_styles import custom_style

def select_region(regions_config, debug_print_func):
    """Returns a dictionary defining the region selection question for Pygame."""
    region_choices = []
    for region_entry in regions_config:
        region_choices.append({"name": region_entry['name'], "value": region_entry['id']})
    region_choices.append({"name": "Back", "value": "back"})

    return {
        'type': 'select',
        'prompt': "Please select a country/region from the list below:",
        'choices': region_choices,
        'default': region_choices[0]["value"],
        'name': 'region'
    }

def select_address_input_method(debug_print_func):
    """Returns a dictionary defining the address input method selection question for Pygame."""
    return {
        'type': 'select',
        'prompt': "How would you like to specify the address?",
        'choices': [
            {"name": "Select detailed location (Province, District, Commune)", "value": "detailed"},
            {"name": "Enter address manually (Free text input)", "value": "manual"},
            {"name": "Go back to previous question", "value": "back"}
        ],
        'default': "detailed",
        'name': 'address_input_method'
    }

def get_manual_address(debug_print_func):
    """Returns a dictionary defining the manual address input question for Pygame."""
    return {
        'type': 'text',
        'prompt': "Please enter the full address: (e.g., 123 Main St, Anytown, Anystate)",
        'validate': "Address cannot be empty.", # Simplified validation for Pygame
        'instruction': "Type 'back' to go back.",
        'name': 'manual_address'
    }

def _get_next_level_options(current_obj):
    """
    Determines the next level of options based on the keys present in current_obj.
    Returns (list_of_options, prompt_name, key_for_selected_location) or (None, None, None).
    """
    if 'regions' in current_obj and current_obj['regions']:
        return current_obj['regions'], "Sub-Region", "sub_region"
    elif 'states' in current_obj and current_obj['states']:
        return current_obj['states'], "State", "state"
    elif 'provinces' in current_obj and current_obj['provinces']:
        return current_obj['provinces'], "Province", "province"
    elif 'counties' in current_obj and current_obj['counties']:
        return current_obj['counties'], "County", "county"
    elif 'principal_areas' in current_obj and current_obj['principal_areas']:
        return current_obj['principal_areas'], "Principal Area", "principal_area"
    elif 'administrative_units' in current_obj and current_obj['administrative_units']:
        return current_obj['administrative_units'], "Administrative Unit", "administrative_unit"
    elif 'sub_units' in current_obj and current_obj['sub_units']:
        return current_obj['sub_units'], "Sub-Unit", "sub_unit"
    return None, None, None

def select_detailed_location(region_data, debug_print_func):
    """
    A generator function that yields questions for selecting a detailed location
    (e.g., Province, District, Commune) based on the provided region data.
    """
    debug_print_func(f"select_detailed_location received region_data keys: {region_data.keys()}")
    selected_location = {}
    current_obj = region_data

    # Level 1: Top-level Region
    regions_options = region_data.get('regions', [])
    debug_print_func(f"Initial regions_options: {regions_options}")
    
    if regions_options:
        yield {
            'name': 'region_level_1',
            'prompt': "Select Region:",
            'type': 'select',
            'choices': [{'name': entry['name'], 'value': entry} for entry in regions_options] + [{'name': "Back", 'value': "back"}],
            'default': regions_options[0]["name"],
            'store_as': 'region',
            'is_location_step': True # Custom flag for wizard
        }

    # Subsequent levels (this part will be handled by the wizard loop based on the yielded value)
    # The wizard in pygame_gui.py will need to handle iterating through these levels
    # based on the 'value' returned from the previous selection.

def get_random_detailed_location(region_data, debug_print_func):
    """
    Generates a random detailed location (e.g., province, district, commune)
    by traversing the provided region_data structure and making random choices
    at each level.
    
    Args:
        region_data (dict): A dictionary containing structured geographical data.
        debug_print_func (function): A function for printing debug messages.
        
    Returns:
        dict: A dictionary representing the randomly selected detailed location,
              with keys like 'province', 'district', 'commune', etc.
    """
    random_location = {}
    current_obj = region_data

    # Randomly select through levels
    while True:
        options, prompt_name, location_key = _get_next_level_options(current_obj)
        if options is None or not options:
            break # No more levels or no options at this level

        selected_obj = random.choice(options)
        random_location[location_key] = selected_obj['name']
        current_obj = selected_obj
        
        # Break if no more sub_units or administrative_units to prevent infinite loops
        if 'sub_units' not in current_obj and 'administrative_units' not in current_obj:
            break

    return random_location
