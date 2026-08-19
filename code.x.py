import sys
import os
import subprocess

# --- دالة التثبيت التلقائي للمكتبات الناقصة ---
def install_requirements():
    required_packages = ["PyQt5", "requests"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# تنفيذ التثبيت التلقائي قبل استدعاء المكتبات
install_requirements()

import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QTextEdit, QPushButton, QLabel)
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt

# رابط سيرفر Judge0 API
JUDGE0_URL = "https://judge0-ce.p.rapidapi.com"

class CodeXApp(QWidget):
    def __init__(self):
        super().__init__()
        self.languages_map = {}
        self.initUI()
        self.load_all_languages()

    def initUI(self):
        self.setWindowTitle("Code.x - Universal Code Executor")
        self.resize(600, 700)

        # تحسين الألوان والتصميم الداكن
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 46))
        palette.setColor(QPalette.WindowText, QColor(205, 214, 244))
        self.setPalette(palette)

        layout = QVBoxLayout()

        # شريط اسم الملف
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("Enter filename (e.g., main.cpp, Main.java, app.rs, script.py)")
        self.filename_input.setFont(QFont("Consolas", 11))
        layout.addWidget(self.filename_input)

        # منطقة كتابة الكود
        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Consolas", 12))
        self.code_editor.setPlaceholderText("Write your code here...")
        layout.addWidget(self.code_editor)

        # أزرار التحكم
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

        # شاشة عرض النتائج (Output)
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        self.output_display.setFont(QFont("Consolas", 11))
        layout.addWidget(self.output_display)

        self.setLayout(layout)

    def load_all_languages(self):
        """جلب كل لغات العالم المدعومة من API تلقائياً"""
        try:
            response = requests.get(f"{JUDGE0_URL}/languages", timeout=5)
            if response.status_code == 200:
                languages = response.json()
                for lang in languages:
                    lang_id = lang["id"]
                    lang_name = lang["name"].lower()

                    # ربط الامتدادات باللغات تلقائياً
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
                    elif "haskell" in lang_name: self.languages_map[".hs"] = lang_id
                    elif "r (" in lang_name: self.languages_map[".r"] = lang_id
                    elif "perl" in lang_name: self.languages_map[".pl"] = lang_id
                    elif "scala" in lang_name: self.languages_map[".scala"] = lang_id
        except Exception:
            # خريطة احتياطية في حال عدم وجود إنترنت أثناء بداية التشغيل
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

        payload = {
            "source_code": code,
            "language_id": lang_id
        }

        try:
            self.output_display.setText("Running on Server...")
            QApplication.processEvents()

            # إرسال الكود
            res = requests.post(f"{JUDGE0_URL}/submissions?wait=true", json=payload, timeout=15)
            data = res.json()

            # عرض النتيجة
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
