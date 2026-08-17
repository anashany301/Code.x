from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, TextArea, Input, RichLog
from textual.containers import Horizontal
import io
import sys
import os

class PythonRunnerGUI(App):
    CSS = """
    #file_input { margin-bottom: 1; }
    TextArea { height: 40%; border: solid cyan; }
    .buttons { height: 3; margin: 1 0; }
    Button { width: 30%; margin: 0 1; }
    RichLog { height: 40%; border: solid green; }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="Enter file name (e.g., anas.py)", id="file_input")
        yield TextArea(placeholder="Write your Python code here...", id="code_input")
        with Horizontal(classes="buttons"):
            yield Button("Load", id="load_btn", variant="warning")
            yield Button("Save", id="save_btn", variant="primary")
            yield Button("Run Code", id="run_btn", variant="success")
        yield RichLog(id="output_log", highlight=True, markup=True)
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        file_input = self.query_one("#file_input", Input)
        text_area = self.query_one("#code_input", TextArea)
        log = self.query_one("#output_log", RichLog)
        
        filename = file_input.value.strip()
        code = text_area.text

        # Action 1: Load Existing File
        if event.button.id == "load_btn":
            if filename:
                if os.path.exists(filename):
                    try:
                        with open(filename, "r") as f:
                            content = f.read()
                        text_area.text = content
                        log.write(f"[bold yellow]Loaded file: {filename}[/bold yellow]")
                    except Exception as e:
                        log.write(f"[bold red]Error reading file: {str(e)}[/bold red]")
                else:
                    log.write(f"[bold red]File '{filename}' does not exist![/bold red]")
            else:
                log.write("[bold red]Please enter a filename to load![/bold red]")

        # Action 2: Save File
        elif event.button.id == "save_btn":
            if filename:
                try:
                    with open(filename, "w") as f:
                        f.write(code)
                    log.write(f"[bold yellow]File saved: {filename}[/bold yellow]")
                except Exception as e:
                    log.write(f"[bold red]Error saving file: {str(e)}[/bold red]")
            else:
                log.write("[bold red]Please enter a filename![/bold red]")

        # Action 3: Run Code
        elif event.button.id == "run_btn":
            if filename:
                try:
                    with open(filename, "w") as f:
                        f.write(code)
                except:
                    pass
            
            log.write("[bold blue]>>> Executing Code...[/bold blue]")
            buffer = io.StringIO()
            sys.stdout = buffer
            try:
                exec(code)
                result = buffer.getvalue()
                log.write(f"[bold green]Output:[/bold green]\n{result if result else '(No output)'}")
            except Exception as e:
                log.write(f"[bold red]Error:[/bold red] {str(e)}")
            finally:
                sys.stdout = sys.__stdout__

if __name__ == "__main__":
    app = PythonRunnerGUI()
    app.run()

