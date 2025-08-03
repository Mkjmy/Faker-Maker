import json
import sys

file_path = '/home/jmy/fake_info_generator/data/usa/us_addresses.json'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print("JSON file successfully fixed and re-formatted.")
except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}", file=sys.stderr)
except FileNotFoundError:
    print(f"Error: File not found at {file_path}", file=sys.stderr)
