import asyncio
import re
import sys
import os
import httpx
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TextArea, Button, Static, Input
from textual.containers import Horizontal, Vertical

# رابط الـ API الخاص بك على Vercel
MY_API_URL = "https://my-fastapi-server.vercel.app/run"

STDLIB = {
    'sys', 'os', 'math', 'json', 'time', 'random', 'asyncio', 
    're', 'datetime', 'subprocess', 'urllib', 'typing', 'string'
}

class CodeXApp(App):
    CSS = """
    Screen {
        background: $surface;
    }
    #file_bar {
        height: 12%;
        align: center middle;
        padding: 0 1;
    }
    #filename_input {
        width: 70%;
    }
    .file_btn {
        margin: 0 1;
    }
    #editor {
        height: 50%;
        border: solid green;
    }
    #output {
        height: 28%;
        border: solid blue;
        background: $panel;
        padding: 1;
    }
    #controls {
        height: 10%;
        align: center middle;
    }
    .action_btn {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        # إطار الملفات (بقى فيه Save بس)
        yield Horizontal(
            Input(value="script.py", placeholder="Filename (e.g. main.py)", id="filename_input"),
            Button("Save", id="save_btn", variant="primary", classes="file_btn"),
            id="file_bar"
        )
        yield Vertical(
            TextArea(
                "print('Hello from CodeX App!')", 
                id="editor", 
                language="python"
            ),
            # إطار التحكم (بقى فيه Run، Load، Clear)
            Horizontal(
                Button("Run Code", id="run_btn", variant="success", classes="action_btn"),
                Button("Load", id="load_btn", variant="default", classes="action_btn"),
                Button("Clear Output", id="clear_btn", variant="error", classes="action_btn"),
                id="controls"
            ),
            Static("Output will appear here...", id="output"),
        )
        yield Footer()

    async def auto_install_missing_packages(self, code_text: str, output_widget: Static):
        imports = re.findall(r'^(?:import|from)\s+([a-zA-Z0-9_]+)', code_text, re.MULTILINE)
        needed_libs = set(imports) - STDLIB

        for lib in needed_libs:
            output_widget.update(f"[Yellow]Checking/Installing library: {lib}...[/Yellow]")
            proc = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "pip", "install", lib,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        output_widget = self.query_one("#output", Static)
        editor = self.query_one("#editor", TextArea)
        filename_input = self.query_one("#filename_input", Input)
        filename = filename_input.value.strip() or "script.py"

        # 1. زر تشغيل الكود
        if event.button.id == "run_btn":
            code_text = editor.text
            await self.auto_install_missing_packages(code_text, output_widget)

            output_widget.update("[Yellow]Running code on Server API...[/Yellow]")
            payload = {"code": code_text, "filename": filename}

            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    response = await client.post(MY_API_URL, json=payload)
                    
                if response.status_code == 200:
                    result = response.json().get("output", "No output returned.")
                    output_widget.update(f"[Green]Result:[/Green]\n{result}")
                else:
                    output_widget.update(f"[Red]Server Error ({response.status_code}):[/Red]\n{response.text}")
            except Exception as e:
                output_widget.update(f"[Red]Connection Error:[/Red]\n{str(e)}")

        # 2. زر حفظ الملف (Save)
        elif event.button.id == "save_btn":
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(editor.text)
                output_widget.update(f"[Green]File saved successfully as '{filename}'[/Green]")
            except Exception as e:
                output_widget.update(f"[Red]Error saving file:[/Red] {str(e)}")

        # 3. زر تحميل الملف (Load)
        elif event.button.id == "load_btn":
            if os.path.exists(filename):
                try:
                    with open(filename, "r", encoding="utf-8") as f:
                        editor.text = f.read()
                    output_widget.update(f"[Green]Loaded file '{filename}' into editor.[/Green]")
                except Exception as e:
                    output_widget.update(f"[Red]Error loading file:[/Red] {str(e)}")
            else:
                output_widget.update(f"[Red]Error:[/Red] File '{filename}' does not exist.")

        # 4. زر مسح المخرجات
        elif event.button.id == "clear_btn":
            output_widget.update("Output cleared.")

if __name__ == "__main__":
    app = CodeXApp()
    app.run()
