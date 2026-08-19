import sys
import os
import subprocess
import base64
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

JUDGE0_URL = "https://judge0-ce.p.rapidapi.com"

STRICT_EXTENSION_MAP = {
    ".rs": 73,     # Rust
    ".java": 62,   # Java
    ".py": 71,     # Python 3
    ".cpp": 54,    # C++
    ".c": 50,      # C
    ".js": 63,     # JavaScript
    ".ts": 74,     # TypeScript
    ".go": 60,     # Go
    ".cs": 51,     # C#
    ".php": 68,    # PHP
    ".rb": 72,     # Ruby
    ".kt": 78,     # Kotlin
    ".sh": 46      # Bash
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
        c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.TIMEOUT, 15)
        c.perform()
        c.close()
        return json.loads(buffer.getvalue().decode('utf-8'))

    def decode_b64(self, text):
        if not text:
            return ""
        try:
            return base64.b64decode(text).decode('utf-8')
        except Exception:
            return text

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Input(placeholder="Enter filename (e.g., main.rs, Main.java, app.py)", id="filename_input")
        
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
            lang_id = STRICT_EXTENSION_MAP.get(ext)

            if not lang_id:
                log.write(f"[bold red]Error:[/] Unsupported file extension '{ext}'")
                return

            log.write(f"[bold cyan]Fast Execution via pycurl ({filename})...[/]")

            # تحويل الكود لـ Base64 لمنع ضياع السطور أو السلسلة النصية
            encoded_code = base64.b64encode(code.encode('utf-8')).decode('utf-8')

            payload = {
                "source_code": encoded_code,
                "language_id": lang_id
            }

            try:
                # إرسال طلب التشفير بالـ base64
                url = f"{JUDGE0_URL}/submissions?wait=true&base64_encoded=true"
                data = self.fast_post_request(url, payload)

                stdout = self.decode_b64(data.get("stdout"))
                stderr = self.decode_b64(data.get("stderr"))
                compile_output = self.decode_b64(data.get("compile_output"))

                output = ""
                if stdout: output += stdout
                if stderr: output += f"\n[bold red]Error:[/]\n{stderr}"
                if compile_output: output += f"\n[bold red]Compilation Error:[/]\n{compile_output}"

                log.write("\n[bold yellow]--- OUTPUT ---[/]")
                log.write(output if output.strip() else "[Execution finished with no output]")

            except Exception as e:
                log.write(f"[bold red]Connection Error:[/] {str(e)}")

if __name__ == "__main__":
    app = CodeXApp()
    app.run()
