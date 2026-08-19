import sys
import os
import subprocess

# --- تنزيل المكتبات الناقصة تلقائياً عبر أمر pip install ---
def check_and_install_dependencies():
    required_packages = ["requests"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"[!] Library '{package}' is missing. Running: pip install {package}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

check_and_install_dependencies()

import requests

PISTON_URL = "https://emkc.org/api/v2/piston"

# خريطة الامتدادات للغات
EXT_MAP = {
    ".py": "python", ".cpp": "cpp", ".c": "c", ".java": "java",
    ".rs": "rust", ".js": "javascript", ".ts": "typescript",
    ".go": "go", ".cs": "csharp", ".php": "php", ".rb": "ruby",
    ".kt": "kotlin", ".swift": "swift", ".sh": "bash", ".lua": "lua"
}

def show_menu():
    print("\n" + "=" * 40)
    print("        Code.x - Universal Terminal       ")
    print("=" * 40)
    print("[1] Run Code / File  (▶️ RUN)")
    print("[2] Exit             (❌ EXIT)")
    print("=" * 40)

def run_code():
    filename = input("\nEnter filename (e.g., main.cpp, script.py, Main.java): ").strip()
    if not filename:
        print("[!] Error: Filename is required.")
        return

    ext = os.path.splitext(filename)[1].lower()
    language = EXT_MAP.get(ext, ext.replace(".", ""))

    if not os.path.exists(filename):
        print(f"\n[+] File '{filename}' not found. Enter code below (Type 'RUN' on a new line to execute):")
        lines = []
        while True:
            line = input()
            if line.strip().upper() == "RUN":
                break
            lines.append(line)
        code = "\n".join(lines)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code)
    else:
        with open(filename, "r", encoding="utf-8") as f:
            code = f.read()

    if not code.strip():
        print("[!] Code is empty!")
        return

    print(f"\n[>] Executing via Piston Engine ({language})...")

    payload = {
        "language": language,
        "version": "*",
        "files": [{"name": filename, "content": code}]
    }

    try:
        res = requests.post(f"{PISTON_URL}/execute", json=payload, timeout=15)
        data = res.json()

        if "run" in data:
            print("\n" + "-" * 15 + " OUTPUT " + "-" * 15)
            print(data["run"]["output"] or "[No Output]")
            print("-" * 38)
        else:
            print(f"\n[!] Error: {data.get('message', 'Execution failed')}")
    except Exception as e:
        print(f"\n[!] Connection Error: {str(e)}")

def main():
    while True:
        show_menu()
        choice = input("Select Option [1-2]: ").strip()
        if choice == "1":
            run_code()
        elif choice == "2":
            print("Exiting Code.x...")
            break
        else:
            print("[!] Invalid option!")

if __name__ == "__main__":
    main()
