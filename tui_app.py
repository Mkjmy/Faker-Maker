from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen, ModalScreen
from textual.containers import ScrollableContainer, Container, Vertical
from textual.widgets import Button, Footer, Header, Log, Input, Select, Static
from textual.events import Focus, Blur

from utils.data_loader import load_regions_config
from utils.system_checker import check_system_requirements
from profile_generator import generate_fake_personal_info
from utils.data_loader import load_region_data
import json
import csv
import os
import io
import contextlib

# --- Screens --- #

class InfoModal(ModalScreen):
    """A modal screen to display information."""
    def __init__(self, info_content: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.info_content = info_content

    def compose(self) -> ComposeResult:
        with Vertical(id="info-modal"):
            yield ScrollableContainer(Static(self.info_content, id="info-content"))
            yield Button("Close", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.pop_screen()

class GeneratorScreen(Screen):
    """The main screen for generating profiles."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.regions, _ = load_regions_config('data')
        self.region_options = [(r['name'], r['id']) for r in self.regions]
        self.gender_options = [("Any", "any"), ("Male", "male"), ("Female", "female")]
        self.output_options = [("Console", "console"), ("JSON", "json"), ("CSV", "csv")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="app-grid", classes="grid-layout"):
            with ScrollableContainer(id="input-pane"):
                yield Static("Profile Generation Settings")
                yield Static("Number of Profiles:")
                yield Input(value="1", id="num_profiles")
                
                yield Static("Region:")
                yield Select(self.region_options, id="region", value="US_GENERAL")

                yield Static("Age Range (e.g., 20-30):")
                yield Input(value="20-40", id="age_range")

                yield Static("Gender:")
                yield Select(self.gender_options, id="gender", value="any")

                yield Static("Output Format:")
                yield Select(self.output_options, id="output_format", value="console")

                yield Button("Generate Profile(s)", id="generate", variant="primary")
                yield Button("Back to Main Menu", id="back", variant="default")

            with ScrollableContainer(id="output-pane", can_focus=True):
                yield Static("Generated Output")
                yield Log(id="results")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "generate":
            self.action_generate()
        elif event.button.id == "back":
            self.app.pop_screen()

    def action_generate(self) -> None:
        results_log = self.query_one("#results", Log)
        results_log.clear()
        results_log.write("Processing...")
        try:
            constraints = {
                'num_profiles': int(self.query_one("#num_profiles", Input).value),
                'age_range': self.query_one("#age_range", Input).value,
                'region': self.query_one("#region", Select).value,
                'gender': self.query_one("#gender", Select).value,
                'output_format': self.query_one("#output_format", Select).value,
                'mode': '2',
            }
            if constraints['region'] is None:
                results_log.write("Error: Please select a region.")
                return

            selected_region_config = next((r for r in self.regions if r['id'] == constraints['region']), None)
            region_data_path = f"data/{selected_region_config['file']}"
            region_data = load_region_data(region_data_path, 'data')
            profiles = [generate_fake_personal_info(region_data, constraints, lambda *a, **kw: None, False) for _ in range(constraints['num_profiles'])]
            
            # Format output for Log widget
            output_str = ""
            for i, profile in enumerate(profiles):
                output_str += f"--- Profile {i+1} ---\n"
                for key, value in profile.items():
                    output_str += f"{key}: {value}\n"
                output_str += "\n"
            results_log.write(output_str)

            if constraints['output_format'] in ['json', 'csv']:
                file_path = f"generated_profiles/profiles.{constraints['output_format']}"
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                if constraints['output_format'] == 'json':
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(profiles, f, indent=4)
                elif constraints['output_format'] == 'csv':
                    with open(file_path, 'w', newline='', encoding='utf-8') as f:
                        if profiles:
                            writer = csv.DictWriter(f, fieldnames=profiles[0].keys())
                            writer.writeheader()
                            writer.writerows(profiles)
                results_log.write(f"Profiles saved to {file_path}")

        except Exception as e:
            results_log.write(f"An unexpected error occurred: {e}")

class MainMenuScreen(Screen):
    
    """The initial screen with main menu options."""
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="main-menu"):
            yield Static("Fake Info Generator")
            yield Static("Select an option to continue")
            yield Button("Generate Profiles", id="to_generator", variant="primary")
            yield Button("Project Information", id="project_info", variant="default")
            yield Button("System Check", id="system_check", variant="default")
            yield Button("Exit", id="exit_app", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#to_generator").focus()

    def on_button_focused(self, event: Focus) -> None:
        self.log(f"Button focused: {event.widget.id}")

    def on_button_blurred(self, event: Blur) -> None:
        self.log(f"Button blurred: {event.widget.id}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "to_generator":
            self.app.push_screen(GeneratorScreen())
        elif event.button.id == "project_info":
            try:
                with open('docs/usage.txt', 'r', encoding='utf-8') as f:
                    info = f.read()
            except FileNotFoundError:
                info = "Error: docs/usage.txt not found."
            self.app.push_screen(InfoModal(info))
        elif event.button.id == "system_check":
            string_io = io.StringIO()
            with contextlib.redirect_stdout(string_io):
                check_system_requirements()
            check_result = string_io.getvalue()
            self.app.push_screen(InfoModal(check_result))
        elif event.button.id == "exit_app":
            self.app.exit()

    def on_key(self, event) -> None:
        self.log(f"Key pressed: {event.key}")
        if event.key == "up":
            self.move_focus(-1)
        elif event.key == "down":
            self.move_focus(1)

    def move_focus(self, direction: int) -> None:
        self.log(f"move_focus called with direction: {direction}")
        buttons = self.query(Button)
        if not buttons:
            self.log("No buttons found.")
            return

        focused_widget = self.app.focused
        current_index = -1
        for i, button in enumerate(buttons):
            if button == focused_widget:
                current_index = i
                break
        self.log(f"Current focused index: {current_index}")

        if current_index == -1:
            # If no button is focused, focus the first one
            self.log("No button focused, focusing first.")
            buttons.first().focus()
            return

        new_index = (current_index + direction) % len(buttons)
        self.log(f"New index: {new_index}")
        buttons[new_index].focus()

class FakeInfoApp(App):
    """The main application class."""
    CSS_PATH = "tui_app.css"
    
    def on_mount(self) -> None:
        self.push_screen(MainMenuScreen())

if __name__ == "__main__":
    app = FakeInfoApp()
    app.run()
