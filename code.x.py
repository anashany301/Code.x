import sys, os, subprocess, json, pycurl
from io import BytesIO
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Input, TextArea, RichLog
from textual.containers import Container, Horizontal

# 1. وظيفة قراءة الإعدادات لكل جهاز على حدة
def load_config():
    config_path = "api_config.json"
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    # الإعدادات الافتراضية (سيرفر Piston المجاني)
    return {
        "url": "https://emkc.org/api/v2/piston/execute",
        "key": None,
        "mode": "public"
    }

CONFIG = load_config()

class CodeXApp(App):
    # ... (نفس الـ CSS السابق) ...
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
        if CONFIG["key"]: # لو فيه مفتاح خاص، بنضيفه في الهيدر
            c.setopt(c.HTTPHEADER, ['Content-Type: application/json', f'X-RapidAPI-Key: {CONFIG["key"]}'])
        c.setopt(c.WRITEDATA, buffer)
        try:
            c.perform()
            c.close()
            return json.loads(buffer.getvalue().decode('utf-8'))
        except Exception as e:
            return {"error": str(e)}

    # ... (نفس دالة compose والـ UI) ...
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Input(placeholder="filename (e.g., main.rs)", id="filename_input")
        with Container(id="editor_container"):
            yield TextArea(placeholder="Write code here...", id="code_editor")
        with Horizontal(id="button_bar"):
            yield Button("Run", id="btn_run", variant="success")
        yield RichLog(id="output_log", highlight=True)
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_run":
            # ... (نفس منطق التشغيل) ...
            filename = self.query_one("#filename_input", Input).value.strip()
            editor = self.query_one("#code_editor", TextArea)
            log = self.query_one("#output_log", RichLog)
            
            ext = os.path.splitext(filename)[1].lower()
            lang = {"rs":"rust", "py":"python", "js":"javascript", "cpp":"cpp"}.get(ext.replace(".",""))
            
            log.write(f"[bold cyan]Executing using mode: {CONFIG['mode']}...[/]")
            
            payload = {"language": lang, "version": "*", "files": [{"content": editor.text}]}
            data = self.fast_post_request(CONFIG["url"], payload)
            
            # عرض النتيجة
            run_data = data.get("run", {})
            log.write(f"\n[bold yellow]--- OUTPUT ---[/]\n{run_data.get('stdout', '') or data.get('error', '[No Output]')}")

if __name__ == "__main__":
    CodeXApp().run()

