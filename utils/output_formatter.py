import csv
import json
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel

HIDDEN_ATTRIBUTES = [
    'cognitive_style_score',
    'stability_index',
    'social_web_density',
    'communication_formality',
    'routine_predictability',
    'impulse_control',
    'performative_tendency',
    'verbosity_level',
    'self_memory_accuracy',
    'internal_consistency',
    'personality_trait',
    'exceptionality_score',
    'curiosity_drive',
    'autonomy_level',
    'context_switching_agility',
    'ambiguity_tolerance',
    'metacognition_awareness',
    'trust_propensity',
    'delayed_gratification_score',
    'moral_flexibility',
    'cognitive_load_tolerance',
    'inner_narrative_intensity'
]

def _output_console(profiles, console: Console, constraints: dict, is_quick_generation: bool = False):
    for i, profile in enumerate(profiles):
        console.print(Panel(Text(f"Profile {i+1}", justify="center", style="bold white"), style="cyan"))

        main_table = Table(show_header=True, header_style="bold green")
        main_table.add_column("Attribute", style="dim", width=25)
        main_table.add_column("Value")

        hidden_table = Table(show_header=True, header_style="bold magenta")
        hidden_table.add_column("Hidden Attribute", style="dim", width=25)
        hidden_table.add_column("Value")

        # Define display categories and their keys
        display_categories = {
            "Core Information": [
                "first_name", "middle_name", "last_name", "age", "dob", "gender",
                "Address", "phone_number", "Occupation", "Email"
            ],
            "Physical Description": [
                "eye_color", "hair_color", "hair_style", "height_cm", "build", "distinguishing_marks"
            ],
            "Unconventional Data": [
                "life_events", "online_behavior", "texting_typing_style",
                "digital_footprint", "device_habits"
            ],
            "Skills & Interests": [
                "skills", "interests"
            ]
        }

        # Populate main_table
        for category_title, keys in display_categories.items():
            category_added = False
            for key in keys:
                if key in profile and key not in HIDDEN_ATTRIBUTES: # Ensure it's not a hidden attribute
                    if not category_added:
                        main_table.add_section()
                        main_table.add_row(Text(category_title, style="bold blue"), "")
                        category_added = True
                    
                    value = profile[key]
                    if isinstance(value, dict):
                        main_table.add_row(f"  {key.replace('_', ' ').title()}", "")
                        for sub_key, sub_value in value.items():
                            if isinstance(sub_value, list):
                                main_table.add_row(f"    {sub_key.replace('_', ' ').title()}", ", ".join(map(str, sub_value)))
                            else:
                                main_table.add_row(f"    {sub_key.replace('_', ' ').title()}", str(sub_value))
                    elif isinstance(value, list):
                        main_table.add_row(f"  {key.replace('_', ' ').title()}", ", ".join(map(str, value)))
                    else:
                        main_table.add_row(f"  {key.replace('_', ' ').title()}", str(value) if value is not None else "None")

        # Populate hidden_table
        hidden_attributes_found = False
        for key in HIDDEN_ATTRIBUTES:
            if key in profile:
                hidden_table.add_row(Text(key.replace('_', ' ').title(), style="bold yellow"), str(profile[key]))
                hidden_attributes_found = True

        console.print(main_table)
        if constraints.get('include_hidden_attributes', False): # Only print hidden attributes panel if user opted to include them
            console.print(Panel(hidden_table, title="[bold magenta]Hidden Attributes[/bold magenta]", border_style="magenta"))

def _output_csv(profiles, console: Console, constraints: dict, file_path="output.csv"):
    if not profiles:
        return
    # Flatten the profiles for CSV output
    flat_profiles = []
    for profile in profiles:
        flat_profile = {}
        for key, value in profile.items():
            if key in HIDDEN_ATTRIBUTES and not constraints.get('include_hidden_attributes', False):
                continue # Skip hidden attributes if not requested
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    flat_profile[f"{key}_{sub_key}"] = sub_value
            else:
                flat_profile[key] = value
        flat_profiles.append(flat_profile)
    
    all_keys = set().union(*(d.keys() for d in flat_profiles))
    
    with open(file_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=sorted(list(all_keys)))
        writer.writeheader()
        writer.writerows(flat_profiles)
    console.print(f"\n[bold green]Successfully wrote {len(profiles)} profiles to {file_path}[/bold green]")

def _output_json(profiles, console: Console, constraints: dict, file_path="output.json"):
    # Filter out hidden attributes if not requested
    filtered_profiles = []
    for profile in profiles:
        if not constraints.get('include_hidden_attributes', False):
            filtered_profile = {k: v for k, v in profile.items() if k not in HIDDEN_ATTRIBUTES}
            filtered_profiles.append(filtered_profile)
        else:
            filtered_profiles.append(profile)

    with open(file_path, 'w') as f:
        json.dump(filtered_profiles, f, indent=4)
    console.print(f"\n[bold green]Successfully wrote {len(profiles)} profiles to {file_path}[/bold green]")

