import json
import sys

try:
    with open('/home/jmy/fake_info_generator/data/usa/us_addresses.json', 'r', encoding='utf-8') as f:
        json.load(f)
except json.JSONDecodeError as e:
    print(e, file=sys.stderr)
