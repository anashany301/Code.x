import sys
import subprocess

REQUIRED_PACKAGES = ["textual", "requests"]

def auto_install_packages():
    for package in REQUIRED_PACKAGES:
        try:
            __import__(package)
        except ImportError:
            print(f"[!] Package '{package}' is missing. Installing automatically...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

auto_install_packages()

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, TextArea, Input, RichLog
from textual.containers import Horizontal
import requests
import os

class CodeXApp(App):
    TITLE = "Code.x - Cloud Multi-Language IDE"

    CSS = """
    #file_input { margin-bottom: 1; }
    TextArea { height: 40%; border: solid cyan; }
    .buttons { height: 3; margin: 1 0; }
    Button { width: 30%; margin: 0 1; }
    RichLog { height: 40%; border: solid green; }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="Filename with extension (e.g., test.c, main.rs, script.py)", id="file_input")
        yield TextArea(placeholder="Write your code here...", id="code_input")
        with Horizontal(classes="buttons"):
            yield Button("Load", id="load_btn", variant="warning")
            yield Button("Save", id="save_btn", variant="primary")
            yield Button("Run Code", id="run_btn", variant="success")
        yield RichLog(id="output_log", highlight=True, markup=True)
        yield Footer()

    def run_code_online(self, filename: str, code: str) -> str:
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        
        language_ids = {
            "c": 50,
            "cpp": 54,
            "py": 71,
            "js": 63,
            "java": 62,
            "rs": 73,
            "go": 60,
            "rb": 72,
            "php": 68,
            "cs": 51,
            "sh": 46
        }

        lang_id = language_ids.get(ext)
        if not lang_id:
            return f"Error: Extension '.{ext}' is not supported."

        url_free = "https://ce.judge0.com/submissions?wait=true"
        payload = {
            "source_code": code,
            "language_id": lang_id
        }

        try:
            response = requests.post(url_free, json=payload, timeout=15)
            if response.status_code in [200, 201]:
                data = response.json()
                stdout = data.get("stdout")
                stderr = data.get("stderr")
                compile_output = data.get("compile_output")

                if stdout:
                    return stdout
                elif compile_output:
                    return f"Compile Error:\n{compile_output}"
                elif stderr:
                    return f"Runtime Error:\n{stderr}"
                else:
                    return "Executed successfully with no output."
            else:
                return f"Server Error: {response.status_code}"
        except Exception as e:
            return f"Connection Error: {str(e)}"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        file_input = self.query_one("#file_input", Input)
        text_area = self.query_one("#code_input", TextArea)
        log = self.query_one("#output_log", RichLog)
        
        filename = file_input.value.strip()
        code = text_area.text

        if event.button.id == "load_btn":
            if filename and os.path.exists(filename):
                with open(filename, "r") as f:
                    text_area.text = f.read()
                log.write(f"[bold yellow]Loaded: {filename}[/bold yellow]")
            else:
                log.write("[bold red]File not found![/bold red]")

        elif event.button.id == "save_btn":
            if filename:
                with open(filename, "w") as f:
                    f.write(code)
                log.write(f"[bold yellow]Saved: {filename}[/bold yellow]")

        elif event.button.id == "run_btn":
            if filename and code:
                log.write(f"[bold blue]>>> Compiling & Running {filename}...[/bold blue]")
                result = self.run_code_online(filename, code)
                log.write(f"[bold green]Result:[/bold green]\n{result}")
            else:
                log.write("[bold red]Please specify a filename and write code![/bold red]")

if __name__ == "__main__":
    app = CodeXApp()
    app.run()


