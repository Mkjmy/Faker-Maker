import os
import json
import subprocess
import tempfile

from rich.console import Console

def edit_profile_with_editor(profile: dict, console: Console, debug_print_func) -> dict:
    """Opens the given profile in a text editor for editing and returns the modified profile."""
    debug_print_func("Opening profile in external editor...")

    # Create a temporary file to store the profile data
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json', encoding='utf-8') as temp_file:
        json.dump(profile, temp_file, indent=4, ensure_ascii=False)
        temp_file_path = temp_file.name

    editor = os.environ.get('EDITOR', 'vi') # Get default editor from environment, fallback to vi

    try:
        # Open the temporary file with the chosen editor
        subprocess.run([editor, temp_file_path], check=True)

        # Read the modified content back from the temporary file
        with open(temp_file_path, 'r', encoding='utf-8') as temp_file:
            modified_content = temp_file.read()
        
        # Parse the modified content as JSON
        modified_profile = json.loads(modified_content)
        debug_print_func("Profile successfully edited in external editor.")
        return modified_profile

    except FileNotFoundError:
        console.print(f"[bold red]Error: Editor '{editor}' not found. Please ensure it's installed and in your PATH.[/bold red]")
        return profile # Return original profile if editor not found
    except subprocess.CalledProcessError:
        console.print("[bold red]Error: Editor exited with an error. Changes might not be saved.[/bold red]")
        return profile # Return original profile if editor had an error
    except json.JSONDecodeError:
        console.print("[bold red]Error: Invalid JSON format after editing. Please ensure the file content is valid JSON.[/bold red]")
        console.print(f"[yellow]Attempting to load original profile from: {temp_file_path}[/yellow]")
        try:
            with open(temp_file_path, 'r', encoding='utf-8') as temp_file:
                original_content = temp_file.read()
            return json.loads(original_content) # Try to return the original content if JSON is invalid
        except Exception as e:
            console.print(f"[bold red]Could not load original profile after invalid JSON: {e}[/bold red]")
            return {} # Fallback to empty dict if even original cannot be loaded
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred during external editing: {e}[/bold red]")
        return profile # Return original profile on other unexpected errors
    finally:
        # Clean up the temporary file
        os.remove(temp_file_path)
