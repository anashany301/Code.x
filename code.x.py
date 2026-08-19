import sys
import os
import subprocess
import requests

def auto_install():
    needed = ["textual", "requests"]
    for package in needed:
        try:
            __import__(package)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

auto_install()

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Input, TextArea, RichLog
from textual.containers import Container, Horizontal

# سيرفر Piston المستقر مع مكتبة requests
PISTON_URL = "https://emkc.org/api/v2/piston/execute"

LANG_MAP = {
    ".rs": "rust",
    ".py": "python",
    ".js": "javascript",
    ".cpp": "cpp",
    ".c": "c"
}

class CodeXApp(App):
    CSS = """
    Screen { background: $surface-darken-3; }
    #filename_input { margin: 1 1 0 1; }
    #editor_container { height: 50%; margin: 1; }
    #button_bar { height: 3; margin: 0 1 0 1; }
    Button { margin-right: 1; }
    #output_log { height: 35%; margin: 0 1 1 1; border: solid $accent; background: $surface; }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Input(placeholder="filename (e.g., main.rs)", id="filename_input")
        with Container(id="editor_container"):
            yield TextArea(placeholder="Write code here...", id="code_editor")
        with Horizontal(id="button_bar"):
            yield Button("Load", id="btn_load")
            yield Button("Save", id="btn_save")
            yield Button("Run", id="btn_run", variant="success")
        yield RichLog(id="output_log", highlight=True)
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        filename = self.query_one("#filename_input", Input).value.strip()
        editor = self.query_one("#code_editor", TextArea)
        log = self.query_one("#output_log", RichLog)

        if button_id == "btn_run":
            if not filename or not editor.text.strip():
                log.write("[bold red]Error:[/] Enter filename and code!")
                return

            ext = os.path.splitext(filename)[1].lower()
            lang = LANG_MAP.get(ext)
            
            if not lang:
                log.write(f"[bold red]Error:[/] Unsupported extension '{ext}'")
                return

            log.write(f"[bold cyan]Running code ({filename})...[/]")
            
            payload = {
                "language": lang,
                "version": "*",
                "files": [{"name": filename, "content": editor.text}]
            }
            
            try:
                response = requests.post(PISTON_URL, json=payload, timeout=15)
                data = response.json()
                
                run_data = data.get("run", {})
                stdout = run_data.get("stdout", "")
                stderr = run_data.get("stderr", "")
                
                log.write("\n[bold yellow]--- OUTPUT ---[/]")
                if stdout:
                    log.write(stdout)
                elif stderr:
                    log.write(f"[bold red]{stderr}[/]")
                else:
                    log.write("[Execution finished with no output]")
            except Exception as e:
                log.write(f"[bold red]Connection Error:[/] {str(e)}")

        elif button_id == "btn_save" and filename:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(editor.text)
            log.write(f"[bold green]Saved:[/] {filename}")

        elif button_id == "btn_load" and filename and os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                editor.text = f.read()
            log.write(f"[bold green]Loaded:[/] {filename}")

if __name__ == "__main__":
    CodeXApp().run()

