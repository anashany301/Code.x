import asyncio
import re
import sys
import httpx
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TextArea, Button, Static
from textual.containers import Horizontal, Vertical

MY_API_URL = "https://my-fastapi-server.vercel.app/run"

# مكتبات بايثون المدمجة التي لا تحتاج لتثبيت
STDLIB = {
    'sys', 'os', 'math', 'json', 'time', 'random', 'asyncio', 
    're', 'datetime', 'subprocess', 'urllib', 'typing', 'string'
}

class CodeXApp(App):
    CSS = """
    Screen {
        background: $surface;
    }
    #editor {
        height: 60%;
        border: solid green;
    }
    #output {
        height: 30%;
        border: solid blue;
        background: $panel;
        padding: 1;
    }
    #controls {
        height: 10%;
        align: center middle;
    }
    Button {
        margin: 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Vertical(
            TextArea(
                "import requests\nprint(requests.__name__)", 
                id="editor", 
                language="python"
            ),
            Horizontal(
                Button("Run Code", id="run_btn", variant="success"),
                Button("Clear Output", id="clear_btn", variant="error"),
                id="controls"
            ),
            Static("Output will appear here...", id="output"),
        )
        yield Footer()

    async def auto_install_missing_packages(self, code_text: str, output_widget: Static):
        """فحص الكود وتثبيت المكتبات الناقصة محلياً في Termux"""
        imports = re.findall(r'^(?:import|from)\s+([a-zA-Z0-9_]+)', code_text, re.MULTILINE)
        needed_libs = set(imports) - STDLIB

        for lib in needed_libs:
            output_widget.update(f"[Yellow]Checking/Installing library: {lib}...[/Yellow]")
            # تشغيل أمر pip install لتنزيل المكتبة
            proc = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "pip", "install", lib,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        output_widget = self.query_one("#output", Static)
        editor = self.query_one("#editor", TextArea)

        if event.button.id == "run_btn":
            code_text = editor.text
            
            # 1. تثبيت المكتبات الناقصة أولاً
            await self.auto_install_missing_packages(code_text, output_widget)

            # 2. إرسال الكود للـ API
            output_widget.update("[Yellow]Running code on Server API...[/Yellow]")
            payload = {
                "code": code_text,
                "filename": "script.py"
            }

            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    response = await client.post(MY_API_URL, json=payload)
                    
                if response.status_code == 200:
                    result = response.json().get("output", "No output returned.")
                    output_widget.update(f"[Green]Result:[/Green]\n{result}")
                else:
                    output_widget.update(f"[Red]Server Error ({response.status_code}):[/Red]\n{response.text}")

            except httpx.TimeoutException:
                output_widget.update("[Red]Error: Request timed out (20s limit).[/Red]")
            except Exception as e:
                output_widget.update(f"[Red]Connection Error:[/Red]\n{str(e)}")

        elif event.button.id == "clear_btn":
            output_widget.update("Output cleared.")

if __name__ == "__main__":
    app = CodeXApp()
    app.run()

