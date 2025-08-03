import json
import os

def load_region_data(region_data_path, data_dir):
    """Loads the data for the specified region and its associated files."""
    with open(region_data_path, 'r', encoding='utf-8') as f:
        region_data = json.load(f)

    # Load default email rules first
    default_email_rules_path = os.path.join(data_dir, 'email_rules.json')
    try:
        with open(default_email_rules_path, 'r', encoding='utf-8') as f:
            region_data['email_rules'] = json.load(f)
    except FileNotFoundError:
        print(f"Error: Default email_rules.json not found at {default_email_rules_path}. Email generation may be affected.")
        region_data['email_rules'] = {}
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {default_email_rules_path}: {e}. Email generation may be affected.")
        region_data['email_rules'] = {}

    # Define how each file should be loaded
    # 'merge': content of the file is merged directly into region_data
    # 'assign': content of the file is assigned to a new key in region_data
    files_config = {
        "names_file": {"type": "merge"},
        
        "occupations_file": {"type": "assign", "key": "occupations"},
        "physical_characteristics_file": {"type": "merge"},
        "email_rules_file": {"type": "update_email_rules"},
        "occupation_rules_file": {"type": "assign", "key": "occupation_rules"},
        "physical_characteristics_rules_file": {"type": "assign", "key": "physical_characteristics_rules"},
        "family_details_rules_file": {"type": "assign", "key": "family_details_rules"},
        "hobbies_rules_file": {"type": "assign", "key": "hobbies_rules"},
        "addresses_file": {"type": "assign", "key": "address_data"},
        "emails_file": {"type": "merge"},
        "phone_numbers_file": {"type": "assign", "key": "phone_number_data"},
        "street_data_file": {"type": "assign", "key": "street_data_content"},
        "nicknames_file": {"type": "assign", "key": "nicknames"},
        "unconventional_data_file": {"type": "assign", "key": "unconventional_data_rules"},
        "skills_interests_rules_file": {"type": "assign", "key": "skills_interests_rules"},
        "validation_data_file": {"type": "assign", "key": "validation_data"},
        "location_biases_file": {"type": "assign", "key": "location_biases"}
    }

    # Load and integrate referenced files
    for file_key, config in files_config.items():
        if file_key in region_data: # Check if the file reference exists in region_data
            relative_path = region_data[file_key]
            full_path = os.path.join(data_dir, relative_path)
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
            except FileNotFoundError:
                print(f"Error: File not found at {full_path}. Skipping this data.")
                continue
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON in {full_path}: {e}. Skipping this data.")
                continue

            if config["type"] == "merge":
                region_data.update(loaded_data)
            elif config["type"] == "assign":
                if file_key == "addresses_file":
                    region_data[config["key"]] = loaded_data
                elif file_key == "occupations_file":
                    region_data[config["key"]] = loaded_data.get('occupations', [])
                else:
                    region_data[config["key"]] = loaded_data
            elif config["type"] == "update_email_rules":
                # Merge specific email rules on top of default ones
                # This handles nested dictionaries by updating them recursively
                def deep_update(target, source):
                    for k, v in source.items():
                        if isinstance(v, dict) and k in target and isinstance(target[k], dict):
                            target[k] = deep_update(target[k], v)
                        else:
                            target[k] = v
                    return target
                region_data['email_rules'] = deep_update(region_data.get('email_rules', {}), loaded_data)
            del region_data[file_key] # Delete the file reference key after processing

    # Always load skills_interests_rules.json
    skills_interests_rules_path = os.path.join(data_dir, 'skills_interests_rules.json')
    try:
        with open(skills_interests_rules_path, 'r', encoding='utf-8') as f:
            skills_interests_data = json.load(f)
            if 'skills_interests_rules' not in region_data:
                region_data['skills_interests_rules'] = {}
            region_data['skills_interests_rules'].update(skills_interests_data)
    except FileNotFoundError:
        print(f"Error: skills_interests_rules.json not found at {skills_interests_rules_path}. Skipping this data.")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {skills_interests_rules_path}: {e}. Skipping this data.")

    # Extract phone_number_formats, street_types, and sub_commune_units
    if 'phone_number_data' in region_data:
        region_data['phone_number_formats'] = region_data['phone_number_data']['phone_number_formats']
        del region_data['phone_number_data'] # Clean up the intermediate key
    if 'street_data_content' in region_data:
        region_data['street_types'] = region_data['street_data_content']['street_types']
        region_data['sub_commune_units'] = region_data['street_data_content']['sub_commune_units']
        del region_data['street_data_content'] # Clean up the intermediate key

    return region_data

def load_regions_config(data_dir):
    """Loads the regions configuration and region aliases."""
    regions_file_path = os.path.join(data_dir, 'regions.json')
    aliases_file_path = os.path.join(data_dir, 'region_aliases.json')
    
    regions_data = []
    try:
        with open(regions_file_path, 'r', encoding='utf-8') as f:
            regions_data = json.load(f)['regions']
    except FileNotFoundError:
        print(f"Error: regions.json not found at {regions_file_path}.")
        return [], {}
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {regions_file_path}: {e}.")
        return [], {}

    aliases_data = {}
    try:
        with open(aliases_file_path, 'r', encoding='utf-8') as f:
            aliases_data = json.load(f)
    except FileNotFoundError:
        print(f"Warning: region_aliases.json not found at {aliases_file_path}. No region aliases will be available.")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {aliases_file_path}: {e}. No region aliases will be available.")

    return regions_data, aliases_data
