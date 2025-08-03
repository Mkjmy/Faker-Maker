import os
# from questionary import Style # Not needed for plain text output
# from rich.console import Console # Not needed for plain text output
# from rich.panel import Panel # Not needed for plain text output
# from rich.text import Text # Not needed for plain text output

# custom_style = Style([ # Not needed for plain text output
#     ('qmark', 'fg:#28a745 bold'),        # question mark
#     ('question', 'fg:#28a745 bold'),       # question text
#     ('answer', 'fg:#218838 bold'),        # selected choice
#     ('pointer', 'fg:#28a745 bold'),       # pointer to current choice
#     ('highlighted', 'fg:#28a745 bold'),    # highlighted choice
#     ('selected', 'fg:#218838'),          # selected item from the list
#     ('separator', 'fg:#218838'),          # separator in lists
#     ('instruction', 'fg:#6c757d'),       # user instructions for select/checkbox
#     ('text', 'fg:#f8f9fa'),              # plain text
#     ('disabled', 'fg:#adb5bd italic')    # disabled choices
# ])

def check_system_requirements(console=None, data_dir: str = None, debug_print_func=None):
    output_content = ""

    output_content += "\nSystem Requirements Check\n\n"
    output_content += "Checking essential data files...\n"

    required_data_files = [
        # Global rules
        'regions.json',
        'email_rules.json',
        'family_details_rules.json',
        'hobbies_rules.json',
        'occupation_rules.json',
        'physical_characteristics_rules.json',
        'skills_interests_rules.json',
        'unconventional_data.json',

        # China data
        'china/cn_addresses.json',
        'china/cn_email_rules.json',
        'china/cn_emails.json',
        'china/cn_general.json',
        'china/cn_names.json',
        'china/cn_nicknames.json',
        'china/cn_occupations.json',
        'china/cn_phone_numbers.json',
        'china/cn_physical_characteristics.json',
        'china/cn_street_data.json',

        # UK data
        'uk/uk_addresses.json',
        'uk/uk_email_rules.json',
        'uk/uk_emails.json',
        'uk/uk_general.json',
        'uk/uk_names.json',
        'uk/uk_nicknames.json',
        'uk/uk_occupations.json',
        'uk/uk_phone_numbers.json',
        'uk/uk_physical_characteristics.json',
        'uk/uk_street_data.json',

        # USA data
        'usa/us_addresses.json',
        'usa/us_email_rules.json',
        'usa/us_emails.json',
        'usa/us_general.json',
        'usa/us_names.json',
        'usa/us_nicknames.json',
        'usa/us_occupations.json',
        'usa/us_phone_numbers.json',
        'usa/us_physical_characteristics.json',
        'usa/us_street_data.json',

        # Vietnam data
        'vietnam/vn_addresses.json',
        'vietnam/vn_email_rules.json',
        'vietnam/vn_emails.json',
        'vietnam/vn_general.json',
        'vietnam/vn_names.json',
        'vietnam/vn_nicknames.json',
        'vietnam/vn_occupations.json',
        'vietnam/vn_phone_numbers.json',
        'vietnam/vn_physical_characteristics.json',
        'vietnam/vn_street_data.json',
    ]

    all_files_present = True
    for filename in required_data_files:
        file_path = os.path.join(data_dir, filename)
        if os.path.exists(file_path):
            output_content += f"  ✔ {filename}\n"
        else:
            output_content += f"  ✖ {filename} (Missing)\n"
            all_files_present = False
    
    if all_files_present:
        output_content += "All essential data files are present.\n"
    else:
        output_content += "Some essential data files are missing. Please ensure your data directory is complete.\n"

    output_content += "\nChecking required Python libraries...\n"

    required_libraries = [
        'rich',
        'Faker',
        'geopy',
        'geographiclib',
        'geonamescache',
        'questionary',
        'pygame', # Added pygame to the check
    ]

    all_libs_installed = True
    for lib_name in required_libraries:
        try:
            __import__(lib_name)
            output_content += f"  ✔ {lib_name}\n"
        except ImportError:
            output_content += f"  ✖ {lib_name} (Not Installed)\n"
            all_libs_installed = False

    if all_libs_installed:
        output_content += "All required Python libraries are installed.\n"
    else:
        output_content += "Some required Python libraries are not installed. Please install them using 'pip install -r requirements.txt'.\n"

    return output_content
