import sys
import os
import subprocess
import json
from io import BytesIO

def auto_install():
    needed = ["textual", "pycurl"]
    for package in needed:
        try:
            __import__(package)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

auto_install()

import pycurl
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Input, TextArea, RichLog
from textual.containers import Container, Horizontal

# سيرفر Glot المجاني المباشر والمفتوح لجميع اللغات
GLOT_URL = "https://glot.io/api/run"

LANG_MAP = {
    ".rs": "rust", 
    ".py": "python", 
    ".js": "javascript", 
    ".cpp": "cpp", 
    ".c": "c",
    ".java": "java",
    ".go": "go",
    ".cs": "csharp",
    ".php": "php",
    ".sh": "bash"
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

    def fast_post_request(self, url, data_dict):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.POSTFIELDS, json.dumps(data_dict))
        c.setopt(c.HTTPHEADER, [
            'Content-Type: application/json',
            'User-Agent: CodeXApp/1.0'
        ])
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.TIMEOUT, 15)
        try:
            c.perform()
            c.close()
            return json.loads(buffer.getvalue().decode('utf-8'))
        except Exception as e:
            return {"error": str(e)}

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Input(placeholder="filename (e.g., main.rs, Main.java, script.py)", id="filename_input")
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
                log.write("[bold red]Error:[/] Please enter filename and code!")
                return

            ext = os.path.splitext(filename)[1].lower()
            lang = LANG_MAP.get(ext)
            
            if not lang:
                log.write(f"[bold red]Error:[/] Unsupported file extension '{ext}'")
                return

            log.write(f"[bold cyan]Executing via Glot API ({filename})...[/]")
            
            # تجهيز الطلب بالشكل الدقيق الذي يطلبه سيرفر Glot
            payload = {
                "files": [
                    {
                        "name": filename,
                        "content": editor.text
                    }
                ]
            }
            
            request_url = f"{GLOT_URL}/{lang}/latest"
            data = self.fast_post_request(request_url, payload)
            
            if "error" in data:
                log.write(f"[bold red]Execution Error:[/] {data['error']}")
            else:
                stdout = data.get("stdout", "")
                stderr = data.get("stderr", "")
                error = data.get("error", "")
                
                output = ""
                if stdout: output += stdout
                if stderr: output += f"\n[bold red]Stderr:[ philosophy]\n{stderr}"
                if error: output += f"\n[bold red]Error:[ philosophy]\n{error}"
                
                log.write("\n[bold yellow]--- OUTPUT ---[/]")
                log.write(output.strip() if output.strip() else "[Execution finished with no output]")

        elif button_id == "btn_save":
            if filename:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(editor.text)
                log.write(f"[bold green]Saved:[/] {filename}")

        elif button_id == "btn_load":
            if filename and os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as f:
                    editor.text = f.read()
                log.write(f"[bold green]Loaded:[/] {filename}")

if __name__ == "__main__":
    CodeXApp().run()


