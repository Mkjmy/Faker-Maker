import json
import os

data_dir = "/home/jmy/fake_info_generator/data"

files_to_check = [
    "vietnam/vn_names.json",
    "vietnam/vn_addresses.json",
    "vietnam/vn_occupations.json",
    "vietnam/vn_physical_characteristics.json",
    "vietnam/vn_email_rules.json",
    "occupation_rules.json",
    "physical_characteristics_rules.json",
    "family_details_rules.json",
    "hobbies_rules.json",
    "vietnam/vn_emails.json",
    "vietnam/vn_phone_numbers.json",
    "vietnam/vn_street_data.json",
    "vietnam/vn_nicknames.json",
    "unconventional_data.json"
]

for relative_path in files_to_check:
    full_path = os.path.join(data_dir, relative_path)
    print(f"Checking: {full_path}")
    try:
        with open(full_path, 'r') as f:
            json.load(f)
        print(f"  {relative_path}: OK")
    except json.JSONDecodeError as e:
        print(f"  {relative_path}: ERROR - {e}")
    except FileNotFoundError:
        print(f"  {relative_path}: FILE NOT FOUND")
