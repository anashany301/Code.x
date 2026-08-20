import subprocess
import sys
import importlib.util

# المكتبات اللي أداتك بتحتاجها
required_packages = ['textual', 'httpx']

def check_and_install():
    for package in required_packages:
        # فحص هل المكتبة موجودة أم لا
        if importlib.util.find_spec(package) is None:
            print(f"--- جاري إعداد أداتك (تثبيت {package})... ---")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"--- تم تثبيت {package} بنجاح ---")
            except Exception as e:
                print(f"--- خطأ أثناء تثبيت {package}: {e} ---")
                sys.exit(1)

if __name__ == "__main__":
    # 1. التأكد من المكتبات أولاً
    check_and_install()
    
    # 2. تشغيل الأداة مباشرة
    print("--- code.x.py ---")
    try:
        # استخدام subprocess لتشغيل الملف مباشرة لتجنب أي مشاكل في الاسم
        subprocess.run([sys.executable, "code.x.py"])
    except Exception as e:
        print(f"--- Error {e} ---")
