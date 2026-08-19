import sys
import os
import subprocess

# --- تثبيت المكتبات أوتوماتيكياً بواسطة pip ---
def auto_install():
    needed = ["textual", "requests"]
    for package in needed:
        try:
            __import__(package)
        except ImportError:
            print(f"[+] Installing {package} via pip...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

auto_install()

import requests
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Input, TextArea, RichLog
from textual.containers import Container, Horizontal, Vertical

PISTON_URL = "https://emkc.org/api/v2/piston"

EXT_MAP = {
    ".py": "python", ".cpp": "cpp", ".c": "c", ".java": "java",
    ".rs": "rust", ".js": "javascript", ".ts": "typescript",
    ".go": "go", ".cs": "csharp", ".php": "php", ".rb": "ruby",
    ".kt": "kotlin", ".swift": "swift", ".sh": "bash", ".lua": "lua",
    ".hs": "haskell", ".r": "r", ".pl": "perl", ".scala": "scala"
}

class CodeXApp(App):
    CSS = """
    Screen {
        background: $surface-darken-3;
    }
    #filename_input {
        margin: 1 1 0 1;
    }
    #editor_container {
        height: 50%;
        margin: 1;
    }
    #button_bar {
        height: 3;
        margin: 0 1 0 1;
    }
    Button {
        margin-right: 1;
    }
    #output_log {
        height: 35%;
        margin: 0 1 1 1;
        border: solid $accent;
        background: $surface;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Input(placeholder="Enter filename (e.g., main.cpp, Main.java, app.rs, script.py)", id="filename_input")
        
        with Container(id="editor_container"):
            yield TextArea(placeholder="Write or paste your code here...", id="code_editor")

        with Horizontal(id="button_bar"):
            yield Button("Load", id="btn_load", variant="default")
            yield Button("Save", id="btn_save", variant="primary")
            yield Button("Run", id="btn_run", variant="success")

        yield RichLog(id="output_log", highlight=True, markup=True)
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        filename = self.query_one("#filename_input", Input).value.strip()
        editor = self.query_one("#code_editor", TextArea)
        log = self.query_one("#output_log", RichLog)

        if button_id == "btn_load":
            if filename and os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as f:
                    editor.text = f.read()
                log.write(f"[bold green]Loaded:[/] {filename}")
            else:
                log.write(f"[bold red]Error:[/] File '{filename}' not found.")

        elif button_id == "btn_save":
            if filename:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(editor.text)
                log.write(f"[bold green]Saved successfully to:[/] {filename}")
            else:
                log.write("[bold red]Error:[/] Specify a filename first!")

        elif button_id == "btn_run":
            code = editor.text.strip()
            if not filename or not code:
                log.write("[bold red]Error:[/] Filename and Code cannot be empty.")
                return

            ext = os.path.splitext(filename)[1].lower()
            language = EXT_MAP.get(ext, ext.replace(".", ""))

            log.write(f"[bold cyan]Executing {filename} via Piston ({language})...[/]")

            payload = {
                "language": language,
                "version": "*",
                "files": [{"name": filename, "content": code}]
            }

            try:
                res = requests.post(f"{PISTON_URL}/execute", json=payload, timeout=15)
                data = res.json()

                if "run" in data:
                    output = data["run"]["output"]
                    log.write("\n[bold yellow]--- OUTPUT ---[/]")
                    log.write(output if output else "[No output generated]")
                else:
                    log.write(f"[bold red]Server Error:[/] {data.get('message', 'Failed')}")
            except Exception as e:
                log.write(f"[bold red]Connection Error:[/] {str(e)}")

if __name__ == "__main__":
    app = CodeXApp()
    app.run()

