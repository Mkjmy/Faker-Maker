#!/home/jmy/fake_info_generator/.venv/bin/python
import os
import argparse
import json
import sys
import csv

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.json import JSON

from auth.auth import check_login_status
from utils.data_loader import load_region_data, load_regions_config
from user_input import get_user_input_generator
from profile_generator import generate_fake_personal_info
from profile_generator.validation_checks.profile_checker import check_profile
from profile_generator.validation_checks.profile_logic_checker import check_profile_logic
from profile_generator.validation_checks.config_checker import check_email_phone_age_config

from utils.system_checker import check_system_requirements
from utils.custom_styles import custom_style
from utils.output_formatter import _output_console


DEBUG_MODE = False # Initialize at module level, will be set by args.debug
display_logo_on_start = True
apply_consistency_checks_for_generation = False

def debug_print(*args, is_error=False, **kwargs):
    global DEBUG_MODE
    if DEBUG_MODE or is_error:
        # Use a plain print for debug to avoid interfering with Rich rendering
        print("DEBUG:", *args, **kwargs)

generated_profiles = [] # Global variable to store generated profiles

def run_generator(args, console: Console, debug_print_func, is_cli_direct_mode=False):
    """Main function to run the fake personal information generator."""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(script_dir, 'data')
    regions, region_aliases = load_regions_config(data_dir)

    constraints = get_user_input_generator(regions, data_dir, console, debug_print_func, args, is_cli_direct_mode)
    # The generator yields, so we get the first result
    if hasattr(constraints, '__iter__') and not isinstance(constraints, dict):
        constraints = next(constraints, {})

    if not constraints or 'mode' not in constraints:
        console.print("[bold red]Profile generation cancelled or an error occurred. Exiting.[/bold red]")
        return

    selected_region_config = next((r for r in regions if r['id'] == constraints['region']), None)
    if not selected_region_config:
        console.print(f"[bold red]Error: Invalid region ID '{constraints['region']}'. Please provide a valid region ID from the configuration.[/bold red]")
        return

    data_file_name = selected_region_config['file']
    region_data_path = os.path.join(data_dir, data_file_name)
    region_data = load_region_data(region_data_path, data_dir)

    config_warnings = check_email_phone_age_config(region_data)
    if config_warnings:
        console.print("[bold yellow]Configuration Warnings:[/bold yellow]")
        for warning in config_warnings:
            console.print(f"  - {warning}")

    console.print("\n[bold cyan]--- Generating Profiles ---\n")

    global generated_profiles
    profiles = []
    
    # This is now handled by a prompt after generation
    apply_consistency_checks_for_generation = False

    for _ in range(constraints['num_profiles']):
        profiles.append(generate_fake_personal_info(region_data, constraints, debug_print_func, apply_consistency_checks_for_generation))

    generated_profiles = profiles
    debug_print_func(f"Generated {len(profiles)} profiles.")
    debug_print_func(f"Profiles content: {profiles}")

    if not profiles:
        console.print("[yellow]No profiles were generated.[/yellow]")
        return

    # --- Output and Saving ---
    output_format = constraints.get('output_format', 'console')
    if output_format == 'console':
        _output_console(profiles, console, constraints)
    
    elif output_format in ['json', 'csv']:
        console.print(f"Generated {len(profiles)} profiles.")
        save_output = True
        if not args.non_interactive:
            save_output = questionary.confirm(f"Save the generated profiles to a .{output_format} file?", style=custom_style).ask()
        
        if save_output:
            output_dir = os.path.join(script_dir, 'generated_profiles')
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, f"profiles.{output_format}")
            
            try:
                if output_format == 'json':
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(profiles, f, indent=4)
                elif output_format == 'csv':
                    with open(file_path, 'w', newline='', encoding='utf-8') as f:
                        if profiles:
                            writer = csv.DictWriter(f, fieldnames=profiles[0].keys())
                            writer.writeheader()
                            writer.writerows(profiles)
                console.print(f"[bold green]Profiles saved to {file_path}[/bold green]")
            except IOError as e:
                console.print(f"[bold red]Error saving file: {e}[/bold red]")

    # --- Consistency Checks ---
    if not args.non_interactive:
        run_checks = questionary.confirm("Run consistency checks on the generated profiles?", style=custom_style).ask()
        if run_checks:
            console.print("\n[bold cyan]--- Running Consistency Checks ---\n")
            for i, profile in enumerate(profiles):
                console.print(f"\n[bold green]Checking Profile {i+1}...[/bold green]")
                
                # Run basic profile checks
                is_valid, basic_reasons = check_profile(profile, region_data, constraints, debug_print_func)
                if not is_valid:
                    console.print("[bold red]Basic Profile Check Failed:[/bold red]")
                    for reason in basic_reasons:
                        console.print(f"  - {reason}")
                else:
                    console.print("[bold green]Basic Profile Check Passed.[/bold green]")

                # Run logic consistency checks
                logic_errors = check_profile_logic(profile, debug_print_func)
                if logic_errors:
                    console.print("[bold yellow]Logic Consistency Check Warnings/Errors:[/bold yellow]")
                    for error in logic_errors:
                        console.print(f"  - {error}")
                else:
                    console.print("[bold green]Logic Consistency Check Passed.[/bold green]")

                if is_valid and not logic_errors:
                    console.print("[bold green]Profile is consistent.[/bold green]")
                else:
                    console.print("[bold yellow]Profile has inconsistencies or warnings.[/bold yellow]")

def run_system_check(console: Console):
    """Runs a check for essential files and libraries."""
    console.print("\n[bold cyan]--- Running System Check ---\n")
    script_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(script_dir, 'data')
    # The check function returns a string, so we print it.
    check_results = check_system_requirements(console=console, data_dir=data_dir)
    console.print(check_results)
    console.print("[bold cyan]--- System Check Complete ---\n")


def display_logo(console: Console):
    """Displays the ASCII art logo from assets/logo.txt."""
    try:
        logo_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'assets', 'logo.txt')
        with open(logo_path, 'r', encoding='utf-8') as f:
            logo_content = f.read()
        console.print(f"[bold green]{logo_content}[/bold green]")
    except FileNotFoundError:
        # Fallback or silent fail if logo not found
        pass
    except Exception as e:
        debug_print(f"Could not display logo: {e}", is_error=True)


def show_main_menu(console: Console):
    """Displays the main menu and returns the user's choice."""
    console.print(Panel("Fake Personal Information Generator - Main Menu", style="bold blue", expand=False, border_style="blue"))
    choice = questionary.select(
        "What would you like to do?",
        choices=[
            questionary.Choice(title="[1] Launch TUI Application", value="tui", description="Launches the Textual User Interface for a more interactive and feature-rich experience."),
            questionary.Choice(title="[2] Generate Profiles", value="generator", description="Starts the command-line wizard to generate fake personal profiles based on your specifications."),
            questionary.Choice(title="[3] View Project Information", value="info", description="Displays detailed information about this project, including version, description, and usage instructions."),
            questionary.Choice(title="[4] System File Check", value="check", description="Performs a check to ensure all necessary system files and dependencies are present and correctly configured."),
            questionary.Separator(),
            questionary.Choice(title="[5] Exit", value="exit", description="Exits the application."),
        ],
        use_indicator=True,
        style=custom_style
    ).ask()
    if choice is None: # Handle Ctrl+C
        return "exit"
    return choice


def main():
    console = Console()

    class CustomArgumentParser(argparse.ArgumentParser):
        def error(self, message):
            console.print(f"[bold red]Error: {message}[/bold red]")
            self.print_help()
            sys.exit(1)

    parser = CustomArgumentParser(description="Fake Personal Information Generator", add_help=False)
    parser.add_argument("--non-interactive", action="store_true", help="Run in non-interactive mode.")
    parser.add_argument("--debug", action="store_true", help="Enable debug output.")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0.0")
    parser.add_argument("--num-profiles", type=int, default=1, help="Number of profiles to generate.")
    parser.add_argument("--name", type=str, help="Set the name for the generated profile.")
    parser.add_argument("--age", type=str, help="Set the age for the generated profile.")
    parser.add_argument("--gender", type=str, help="Set the gender.")
    parser.add_argument("--occupation", type=str, help="Set the occupation.")
    parser.add_argument("--region", type=str, help="Set the region for the generated profile.")
    parser.add_argument("--marital-status", type=str, help="Set the marital status.")
    parser.add_argument("--education-level", type=str, help="Set the education level.")
    parser.add_argument("--num-children", type=str, help="Set the number of children.")
    parser.add_argument("--hobbies", type=str, help="Set a list of hobbies (comma-separated).")
    parser.add_argument("--skills", type=str, help="Set a list of skills (comma-separated).")
    parser.add_argument("--include-unconventional", action="store_true", help="Include unconventional data.")
    parser.add_argument("--physical-details", action="store_true", help="Include detailed physical description.")
    parser.add_argument("--address-manual-input", type=str, help="Manually enter the address.")
    parser.add_argument("--location", type=str, help="Set the detailed location (e.g., province, district, commune).")
    parser.add_argument("--personality-trait", type=str, help="Set the personality trait for the generated profile.")
    parser.add_argument("--exceptionality-score", type=int, help="Set the exceptionality score for the generated profile (1-100).")
    parser.add_argument("--custom-first-name", type=str, help="Custom first name.")
    parser.add_argument("--custom-last-name", type=str, help="Custom last name.")
    parser.add_argument("--include-hidden-attributes", action="store_true", help="Include hidden attributes (e.g., Personality Trait, Exceptionality Score).")
    parser.add_argument('-h', '--help', action='store_true', help='Show this help message and exit')
    # --tui is now effectively handled by the menu, but we keep it for direct access
    parser.add_argument("--tui", action="store_true", help="Run the Textual UI.")

    try:
        args, unknown = parser.parse_known_args()
    except ValueError:
        # CustomArgumentParser's error method handles the exit, so we can just pass.
        pass

    global DEBUG_MODE
    if args.debug:
        DEBUG_MODE = True
        debug_print("Debug mode enabled.")

    if args.help:
        display_project_information(console, wait_for_input=False)
        sys.exit(0)

    # The TUI app is now launched via the menu, but this allows direct launch
    if args.tui:
        from tui_app import FakeInfoApp
        app = FakeInfoApp()
        app.run()
        sys.exit(0)

    if not check_login_status(console, debug_print):
         console.print("[bold red]Login failed. Exiting.[/bold red]")
         sys.exit(1)

    # Check if any generator-specific args were passed to bypass the menu
    generator_args_passed = any([
        args.num_profiles != 1,
        args.name,
        args.age,
        args.gender,
        args.occupation,
        args.region,
        args.marital_status,
        args.education_level,
        args.hobbies,
        args.skills,
        args.include_unconventional,
        args.custom_first_name,
        args.custom_last_name,
    ])

    if args.non_interactive or generator_args_passed:
        run_generator(args, console, debug_print, is_cli_direct_mode=True)
        sys.exit(0)

    # Interactive menu loop
    while True:
        display_logo(console)
        choice = show_main_menu(console)
        if choice == "tui":
            from tui_app import FakeInfoApp
            app = FakeInfoApp()
            app.run()
        elif choice == "generator":
            run_generator(args, console, debug_print)
        elif choice == "info":
            try:
                project_info_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'docs', 'project_info.json')
                with open(project_info_path, 'r', encoding='utf-8') as f:
                    project_info_content = json.load(f)
                
                # Define paths to highlight
                highlight_paths = [
                    "project_name",
                    "version",
                    "description",
                    "author"
                ]

                console.print("\n[bold cyan]--- Project Information ---\n")
                # Pass the Python dictionary directly to rich.json.JSON
                console.print(JSON(project_info_content, highlight_paths=highlight_paths))
                console.print("\n[bold cyan]--- End Project Information ---\n")

            except FileNotFoundError:
                console.print("[bold red]Could not find project_info.json.[/bold red]")
            except json.JSONDecodeError:
                console.print("[bold red]Error decoding project_info.json. Please check its format.[/bold red]")
            except Exception as e:
                console.print(f"[bold red]An error occurred: {e}[/bold red]")
        elif choice == "check":
            run_system_check(console)
        elif choice == "exit":
            console.print("[bold yellow]Goodbye![/bold yellow]")
            break

        # After an action, ask to return to the menu
        if choice != "exit":
            if not questionary.confirm("Return to main menu?", style=custom_style).ask():
                console.print("[bold yellow]Goodbye![/bold yellow]")
                break

if __name__ == "__main__":
    main()