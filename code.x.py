import sys
import os
import subprocess

# --- التنزيل التلقائي للمكتبات الأساسية + مكتبة cURL المسرّعة بـ C ---
def install_requirements():
    required_packages = ["PyQt5", "pycurl"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_requirements()

import pycurl
import json
from io import BytesIO
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QTextEdit, QPushButton)
from PyQt5.QtGui import QFont, QColor, QPalette

JUDGE0_URL = "https://judge0-ce.p.rapidapi.com"

class CodeXApp(QWidget):
    def __init__(self):
        super().__init__()
        self.languages_map = {}
        self.initUI()
        self.load_all_languages()

    def initUI(self):
        self.setWindowTitle("Code.x - Fast Ultra Executor")
        self.resize(600, 700)

        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 46))
        palette.setColor(QPalette.WindowText, QColor(205, 214, 244))
        self.setPalette(palette)

        layout = QVBoxLayout()

        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("Enter filename (e.g., main.cpp, Main.java, app.rs, script.py)")
        self.filename_input.setFont(QFont("Consolas", 11))
        layout.addWidget(self.filename_input)

        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Consolas", 12))
        self.code_editor.setPlaceholderText("Write your code here...")
        layout.addWidget(self.code_editor)

        btn_layout = QHBoxLayout()
        self.load_btn = QPushButton("Load")
        self.save_btn = QPushButton("Save")
        self.run_btn = QPushButton("Run")

        self.load_btn.clicked.connect(self.load_file)
        self.save_btn.clicked.connect(self.save_file)
        self.run_btn.clicked.connect(self.run_code)

        btn_layout.addWidget(self.load_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.run_btn)
        layout.addLayout(btn_layout)

        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        self.output_display.setFont(QFont("Consolas", 11))
        layout.addWidget(self.output_display)

        self.setLayout(layout)

    # دالة إرسال الطلبات المسرّعة بمحرك C (pycurl)
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

    def fast_get_request(self, url):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.TIMEOUT, 5)
        c.perform()
        c.close()
        return json.loads(buffer.getvalue().decode('utf-8'))

    def load_all_languages(self):
        try:
            languages = self.fast_get_request(f"{JUDGE0_URL}/languages")
            for lang in languages:
                lang_id = lang["id"]
                lang_name = lang["name"].lower()

                if "python" in lang_name: self.languages_map[".py"] = lang_id
                elif "c++" in lang_name or "g++" in lang_name: self.languages_map[".cpp"] = lang_id
                elif "c (" in lang_name or "gcc" in lang_name: self.languages_map[".c"] = lang_id
                elif "java " in lang_name: self.languages_map[".java"] = lang_id
                elif "rust" in lang_name: self.languages_map[".rs"] = lang_id
                elif "javascript" in lang_name or "node" in lang_name: self.languages_map[".js"] = lang_id
                elif "typescript" in lang_name: self.languages_map[".ts"] = lang_id
                elif "go (" in lang_name: self.languages_map[".go"] = lang_id
                elif "c#" in lang_name: self.languages_map[".cs"] = lang_id
                elif "php" in lang_name: self.languages_map[".php"] = lang_id
                elif "ruby" in lang_name: self.languages_map[".rb"] = lang_id
                elif "kotlin" in lang_name: self.languages_map[".kt"] = lang_id
                elif "swift" in lang_name: self.languages_map[".swift"] = lang_id
                elif "bash" in lang_name: self.languages_map[".sh"] = lang_id
                elif "lua" in lang_name: self.languages_map[".lua"] = lang_id
        except Exception:
            self.languages_map = {
                ".py": 71, ".cpp": 54, ".c": 50, ".java": 62, 
                ".rs": 73, ".js": 63, ".ts": 74, ".go": 60, 
                ".cs": 51, ".php": 68, ".rb": 72, ".kt": 78
            }

    def get_language_id(self, filename):
        ext = os.path.splitext(filename)[1].lower()
        return self.languages_map.get(ext, 71)

    def load_file(self):
        filename = self.filename_input.text()
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                self.code_editor.setText(f.read())

    def save_file(self):
        filename = self.filename_input.text()
        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.code_editor.toPlainText())

    def run_code(self):
        filename = self.filename_input.text()
        code = self.code_editor.toPlainText()
        
        if not filename or not code:
            self.output_display.setText("Error: Filename and Code cannot be empty.")
            return

        lang_id = self.get_language_id(filename)
        payload = {"source_code": code, "language_id": lang_id}

        try:
            self.output_display.setText("Running via Low-Level C Engine...")
            QApplication.processEvents()

            data = self.fast_post_request(f"{JUDGE0_URL}/submissions?wait=true", payload)

            stdout = data.get("stdout")
            stderr = data.get("stderr")
            compile_output = data.get("compile_output")

            output = ""
            if stdout: output += stdout
            if stderr: output += f"\nError:\n{stderr}"
            if compile_output: output += f"\nCompilation Error:\n{compile_output}"

            self.output_display.setText(output if output else "Execution finished with no output.")
        except Exception as e:
            self.output_display.setText(f"Connection Failed: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CodeXApp()
    window.show()
    sys.exit(app.exec_())

