import sys
import os
import subprocess
import base64
import json
from io import BytesIO

# محاولة تثبيت المكتبات المطلوبة تلقائياً
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

# الإعدادات
JUDGE0_URL = "https://judge0-ce.p.rapidapi.com"
STRICT_EXTENSION_MAP = {".rs": 73, ".py": 71, ".cpp": 54, ".c": 50, ".js": 63, ".java": 62}

class CodeXApp(App):
    CSS = """
    Screen { background: $surface-darken-3; }
    #editor_container { height: 50%; margin: 1; }
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
        
        try:
            c.perform()
            status_code = c.getinfo(c.RESPONSE_CODE)
            c.close()
            
            # إذا كان الكود غير 200 أو 201، يعني فيه مشكلة (رفض من السيرفر)
            if status_code not in [200, 201]:
                return {"error": f"Server rejected request. Status Code: {status_code}"}
            
            return json.loads(buffer.getvalue().decode('utf-8'))
        except Exception as e:
            return {"error": f"Connection failed: {str(e)}"}

    def decode_b64(self, text):
        if not text: return ""
        try: return base64.b64decode(text).decode('utf-8')
        except: return text

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
            code = editor.text.strip()
            ext = os.path.splitext(filename)[1].lower()
            lang_id = STRICT_EXTENSION_MAP.get(ext)

            if not lang_id:
                log.write(f"[bold red]Error:[/] Unsupported extension {ext}")
                return

            log.write(f"[bold cyan]Executing...[/]")
            encoded_code = base64.b64encode(code.encode('utf-8')).decode('utf-8')
            payload = {"source_code": encoded_code, "language_id": lang_id}
            
            url = f"{JUDGE0_URL}/submissions?wait=true&base64_encoded=true"
            data = self.fast_post_request(url, payload)

            if "error" in data:
                log.write(f"[bold red]{data['error']}[/]")
            else:
                stdout = self.decode_b64(data.get("stdout"))
                stderr = self.decode_b64(data.get("stderr"))
                log.write(f"[bold yellow]--- OUTPUT ---[/]\n{stdout or stderr or '[No Output]'}")

        elif button_id == "btn_save":
            with open(filename, "w") as f: f.write(editor.text)
            log.write("Saved!")

if __name__ == "__main__":
    CodeXApp().run()
