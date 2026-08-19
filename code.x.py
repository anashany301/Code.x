import os
import sys
import subprocess
import json
import asyncio
import httpx
import uvloop

# تفعيل محرك uvloop للسرعة الفائقة
uvloop.install()

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, TextArea, Input, Static
from textual.containers import Container, Horizontal, Vertical

# وظيفة التثبيت التلقائي للمكتبات في حال عدم وجودها
def auto_install():
    packages = ["textual", "httpx", "uvloop"]
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

auto_install()

class CodeX(App):
    # عنوان التطبيق
    TITLE = "Code.x"
    
    CSS = """
    Screen { background: #1a1b26; }
    #file_input { height: 3; margin: 1; border: solid #7aa2f7; }
    #editor_box { height: 45%; border: solid #7aa2f7; margin: 1; }
    #control_bar { height: 3; margin: 0 1; }
    Button { width: 33%; height: 3; }
    #btn_run { background: #7aa2f7; color: #15161e; }
    #output_box { height: 35%; border: solid #9ece6a; margin: 1; padding: 1; color: #c0caf5; }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="filename.py", id="file_input")
        yield Container(TextArea("# Write code here...", id="editor"), id="editor_box")
        with Horizontal(id="control_bar"):
            yield Button("Load", id="btn_load")
            yield Button("Save", id="btn_save")
            yield Button("Run", id="btn_run")
        yield Container(Static("Output:", id="output"), id="output_box")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        out = self.query_one("#output", Static)
        editor = self.query_one("#editor", TextArea)
        fn = self.query_one("#file_input", Input).value.strip()

        # زر الحفظ
        if event.button.id == "btn_save":
            if not fn:
                out.update("Output:\nPlease enter a filename!")
                return
            with open(fn, "w") as f: f.write(editor.text)
            out.update("Output:\nSaved successfully!")

        # زر التحميل
        elif event.button.id == "btn_load":
            if os.path.exists(fn):
                with open(fn, "r") as f: editor.load_text(f.read())
                out.update("Output:\nFile loaded!")
            else: 
                out.update("Output:\nFile not found!")
        
        # زر التشغيل السحابي
        elif event.button.id == "btn_run":
            out.update("Output:\nConnecting to Cloud...")
            
            # خريطة اللغات
            lang_map = {".py": 71, ".c": 50, ".cpp": 54, ".php": 68, ".js": 63}
            ext = os.path.splitext(fn)[1]
            lang_id = lang_map.get(ext, 71)

            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.post("https://ce.judge0.com/submissions?wait=true", 
                        json={"source_code": editor.text, "language_id": lang_id})
                    
                    data = resp.json()
                    if "stdout" in data and data["stdout"]:
                        out.update(f"Output:\n{data['stdout']}")
                    elif "stderr" in data and data["stderr"]:
                        out.update(f"Error:\n{data['stderr']}")
                    else:
                        out.update(f"Response: {data}")
            except Exception as e:
                out.update(f"Connection Failed: {str(e)}")

if __name__ == "__main__":
    app = CodeX()
    app.run()



