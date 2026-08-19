import sys
import os
import subprocess

# --- تثبيت المكتبات تلقائياً في الخفاء دون تدخل من المستخدم ---
def auto_setup():
    required = ["requests"]
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

auto_setup()

import requests
import tkinter as tk
from tkinter import messagebox

JUDGE0_URL = "https://judge0-ce.p.rapidapi.com"

class CodeXApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Code.x - Universal Code Executor")
        self.root.geometry("550x650")
        self.root.configure(bg="#1e1e2e")

        self.languages_map = {}

        # 1. حقل اسم الملف
        self.lbl_file = tk.Label(root, text="Filename (e.g. main.cpp, Main.java, app.rs, script.py):", bg="#1e1e2e", fg="#cdd6f4", anchor="w")
        self.lbl_file.pack(fill="x", padx=15, pady=(15, 2))

        self.filename_entry = tk.Entry(root, bg="#313244", fg="#cdd6f4", insertbackground="white", font=("Consolas", 11), relief="flat")
        self.filename_entry.pack(fill="x", padx=15, pady=5, ipady=6)

        # 2. حقل كتابة الكود
        self.lbl_code = tk.Label(root, text="Source Code:", bg="#1e1e2e", fg="#cdd6f4", anchor="w")
        self.lbl_code.pack(fill="x", padx=15, pady=(10, 2))

        self.code_editor = tk.Text(root, bg="#181825", fg="#a6adc8", insertbackground="white", font=("Consolas", 11), relief="flat", height=12)
        self.code_editor.pack(fill="both", expand=True, padx=15, pady=5)

        # 3. الأزرار
        btn_frame = tk.Frame(root, bg="#1e1e2e")
        btn_frame.pack(fill="x", padx=15, pady=10)

        self.btn_load = tk.Button(btn_frame, text="Load", command=self.load_file, bg="#45475a", fg="white", relief="flat", font=("Arial", 10, "bold"), width=10)
        self.btn_load.pack(side="left", padx=2)

        self.btn_save = tk.Button(btn_frame, text="Save", command=self.save_file, bg="#45475a", fg="white", relief="flat", font=("Arial", 10, "bold"), width=10)
        self.btn_save.pack(side="left", padx=2)

        self.btn_run = tk.Button(btn_frame, text="Run", command=self.run_code, bg="#89b4fa", fg="#11111b", relief="flat", font=("Arial", 10, "bold"), width=10)
        self.btn_run.pack(side="right", padx=2)

        # 4. شاشة عرض النتائج
        self.lbl_out = tk.Label(root, text="Output:", bg="#1e1e2e", fg="#cdd6f4", anchor="w")
        self.lbl_out.pack(fill="x", padx=15, pady=(5, 2))

        self.output_display = tk.Text(root, bg="#11111b", fg="#a6e3a1", font=("Consolas", 11), relief="flat", height=8)
        self.output_display.pack(fill="x", padx=15, pady=(0, 15))

        # جلب كافة لغات العالم تلقائياً
        self.load_all_languages()

    def load_all_languages(self):
        try:
            res = requests.get(f"{JUDGE0_URL}/languages", timeout=5)
            if res.status_code == 200:
                for lang in res.json():
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
        filename = self.filename_entry.get().strip()
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                self.code_editor.delete("1.0", tk.END)
                self.code_editor.insert(tk.END, f.read())

    def save_file(self):
        filename = self.filename_entry.get().strip()
        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.code_editor.get("1.0", tk.END))

    def run_code(self):
        filename = self.filename_entry.get().strip()
        code = self.code_editor.get("1.0", tk.END).strip()

        if not filename or not code:
            messagebox.showerror("Error", "Filename and Code cannot be empty!")
            return

        lang_id = self.get_language_id(filename)
        payload = {"source_code": code, "language_id": lang_id}

        self.output_display.delete("1.0", tk.END)
        self.output_display.insert(tk.END, "Running code on server...\n")
        self.root.update()

        try:
            res = requests.post(f"{JUDGE0_URL}/submissions?wait=true", json=payload, timeout=15)
            data = res.json()

            stdout = data.get("stdout")
            stderr = data.get("stderr")
            compile_output = data.get("compile_output")

            output = ""
            if stdout: output += stdout
            if stderr: output += f"\nError:\n{stderr}"
            if compile_output: output += f"\nCompilation Error:\n{compile_output}"

            self.output_display.delete("1.0", tk.END)
            self.output_display.insert(tk.END, output if output else "Execution finished with no output.")
        except Exception as e:
            self.output_display.delete("1.0", tk.END)
            self.output_display.insert(tk.END, f"Connection Error: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeXApp(root)
    root.mainloop()
