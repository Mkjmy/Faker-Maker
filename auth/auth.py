import os
import json
import time

from rich.console import Console
from rich.prompt import Prompt

AUTH_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'auth.json')
LOCKOUT_STATE_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lockout_state.json')

def load_lockout_state():
    if os.path.exists(LOCKOUT_STATE_FILE):
        with open(LOCKOUT_STATE_FILE, 'r') as f:
            return json.load(f)
    return {'failed_attempts': 0, 'lockout_until': 0}

def save_lockout_state(state):
    with open(LOCKOUT_STATE_FILE, 'w') as f:
        json.dump(state, f)

def get_user_credentials(console: Console):
    """Gets username and password from the user."""
    username = Prompt.ask("[bold green]Enter your username[/bold green]", console=console)
    password = Prompt.ask("[bold green]Enter your password[/bold green]", password=True, console=console)
    return username, password

def create_account(console: Console):
    """Creates a new user account and saves it to the auth file."""
    console.print("[bold blue]Create a new account[/bold blue]")
    while True:
        username, password = get_user_credentials(console)
        if not username or not password:
            console.print("[bold red]Username and password cannot be empty.[/bold red]")
            continue
        
        confirm_password = Prompt.ask("[bold green]Confirm your password[/bold green]", password=True, console=console)
        
        if password == confirm_password:
            break
        else:
            console.print("[bold red]Passwords do not match. Please try again.[/bold red]")

    stay_logged_in = Prompt.ask("[bold green]Do you want to stay logged in? [/bold green]", choices=["y", "n"], default="n", console=console) == 'y'

    with open(AUTH_FILE, 'w') as f:
        json.dump({'username': username, 'password': password, 'stay_logged_in': stay_logged_in}, f)
    
    # Initialize and save lockout state for the new account
    save_lockout_state({'failed_attempts': 0, 'lockout_until': 0})
    
    console.print("[bold green]Account created successfully![/bold green]")

def login(console: Console):
    """Logs in the user by verifying their credentials."""
    if not os.path.exists(AUTH_FILE):
        console.print("[bold yellow]No accounts found. Please create one.[/bold yellow]")
        create_account(console)
        return True

    with open(AUTH_FILE, 'r') as f:
        credentials = json.load(f)

    lockout_state = load_lockout_state()

    username_attempt = None

    while True:
        current_time = time.time()
        if current_time < lockout_state.get('lockout_until', 0):
            remaining_time = int(lockout_state['lockout_until'] - current_time)
            console.print(f"[bold red]Account locked. Please wait {remaining_time} seconds.[/bold red]")
            time.sleep(remaining_time + 1) # Wait a bit longer to ensure lockout expires
            lockout_state = load_lockout_state() # Reload state after waiting
            continue

        if username_attempt is None: # First attempt or previous username was wrong
            username = Prompt.ask("[bold green]Enter your username[/bold green]", console=console)
        else: # Username was correct in previous attempt, only ask for password
            username = username_attempt
            console.print(f"[bold green]Username: {username}[/bold green]") # Display username for context

        password = Prompt.ask("[bold green]Enter your password[/bold green]", password=True, console=console)

        if username == credentials['username'] and password == credentials['password']:
            console.print("[bold green]Login successful![/bold green]")
            lockout_state['failed_attempts'] = 0 # Reset on successful login
            lockout_state['lockout_until'] = 0
            save_lockout_state(lockout_state)

            stay_logged_in = Prompt.ask("[bold green]Do you want to stay logged in? [/bold green]", choices=["y", "n"], default="n", console=console) == 'y'
            credentials['stay_logged_in'] = stay_logged_in
            with open(AUTH_FILE, 'w') as f:
                json.dump(credentials, f)

            return True
        else:
            lockout_state['failed_attempts'] += 1
            
            if username != credentials['username']:
                console.print("[bold red]Invalid username.[/bold red]")
                username_attempt = None # Reset username attempt if username is wrong
            else:
                console.print("[bold red]Invalid password.[/bold red]")
                username_attempt = username # Keep username if it was correct

            console.print(f"[bold red]Attempts: {lockout_state['failed_attempts']}[/bold red]")

            if lockout_state['failed_attempts'] % 5 == 0:
                current_lockout = 5 * (2 ** ((lockout_state['failed_attempts'] // 5) - 1))
                lockout_state['lockout_until'] = current_time + current_lockout
                console.print(f"[bold red]Too many failed attempts. Locking for {current_lockout} seconds.[/bold red]")
            
            save_lockout_state(lockout_state)


def check_login_status(console: Console, debug_print_func):
    """Checks if the user is logged in and handles the login process."""
    debug_print_func(f"Checking for auth file at: {AUTH_FILE}")
    if not os.path.exists(AUTH_FILE):
        choice = Prompt.ask("[bold yellow]No account found. Do you want to create one? [/bold yellow]", choices=["y", "n"], default="y", console=console)
        if choice == 'y':
            create_account(console)
            return True
        else:
            console.print("[bold red]Exiting. You need an account to use this application.[/bold red]")
            exit()
    else:
        with open(AUTH_FILE, 'r') as f:
            credentials = json.load(f)
        if credentials.get('stay_logged_in', False):
            console.print("[bold green]Automatically logged in.[/bold green]")
            return True
        else:
            return login(console)
