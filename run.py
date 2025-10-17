#!/usr/bin/env python3
"""
اسکریپت اجرای برنامه دوبله خودکار ویدیو
Run script for Auto Video Dubbing application
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """بررسی وابستگی‌های مورد نیاز"""
    print("🔍 بررسی وابستگی‌ها...")
    
    # بررسی Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 یا بالاتر مورد نیاز است")
        return False
    
    # بررسی ffmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✅ FFmpeg نصب است")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg نصب نیست. لطفاً آن را نصب کنید:")
        print("   - Windows: https://ffmpeg.org/download.html")
        print("   - macOS: brew install ffmpeg")
        print("   - Ubuntu: sudo apt install ffmpeg")
        return False
    
    # بررسی rubberband-cli
    try:
        subprocess.run(['rubberband', '--version'], capture_output=True, check=True)
        print("✅ Rubberband نصب است")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Rubberband نصب نیست. لطفاً آن را نصب کنید:")
        print("   - Windows: https://breakfastquay.com/rubberband/")
        print("   - macOS: brew install rubberband")
        print("   - Ubuntu: sudo apt install rubberband-cli")
        return False
    
    # بررسی فونت Vazirmatn
    if not check_vazirmatn_font():
        print("⚠️  فونت Vazirmatn یافت نشد. برای نصب خودکار:")
        print("   python install_fonts.py")
        print("   یا دستی از https://github.com/rastikerdar/vazirmatn دانلود کنید")
    
    return True

def check_vazirmatn_font():
    """بررسی وجود فونت Vazirmatn"""
    import platform
    system = platform.system().lower()
    
    font_dirs = []
    if system == "windows":
        font_dirs = [
            os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts"),
            os.path.expanduser("~/Fonts"),
            "C:/Windows/Fonts"
        ]
    elif system == "darwin":  # macOS
        font_dirs = [
            os.path.expanduser("~/Library/Fonts"),
            "/Library/Fonts",
            "/System/Library/Fonts"
        ]
    else:  # Linux
        font_dirs = [
            os.path.expanduser("~/.fonts"),
            os.path.expanduser("~/.local/share/fonts"),
            "/usr/share/fonts/truetype",
            "/usr/local/share/fonts"
        ]
    
    for font_dir in font_dirs:
        if os.path.exists(font_dir):
            for font_file in os.listdir(font_dir):
                if "vazirmatn" in font_file.lower() and font_file.endswith(".ttf"):
                    print("✅ فونت Vazirmatn یافت شد")
                    return True
    
    return False

def install_requirements():
    """نصب وابستگی‌های Python"""
    print("📦 نصب وابستگی‌های Python...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ وابستگی‌ها نصب شدند")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ خطا در نصب وابستگی‌ها: {e}")
        return False

def create_directories():
    """ایجاد پوشه‌های مورد نیاز"""
    print("📁 ایجاد پوشه‌های مورد نیاز...")
    
    directories = [
        "dubbing_work",
        "dubbing_work/dubbed_segments",
        "temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ پوشه‌ها ایجاد شدند")

def run_app():
    """اجرای برنامه Streamlit"""
    print("🚀 اجرای برنامه...")
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'app.py',
            '--server.port', '8501',
            '--server.address', 'localhost',
            '--browser.gatherUsageStats', 'false'
        ])
    except KeyboardInterrupt:
        print("\n👋 برنامه متوقف شد")
    except Exception as e:
        print(f"❌ خطا در اجرای برنامه: {e}")

def main():
    """تابع اصلی"""
    print("🎬 دوبله خودکار ویدیو")
    print("=" * 40)
    
    # بررسی وابستگی‌ها
    if not check_dependencies():
        print("\n❌ وابستگی‌های مورد نیاز نصب نیستند")
        return
    
    # نصب requirements
    if not install_requirements():
        print("\n❌ خطا در نصب وابستگی‌ها")
        return
    
    # ایجاد پوشه‌ها
    create_directories()
    
    print("\n✅ همه چیز آماده است!")
    print("🌐 برنامه در آدرس http://localhost:8501 اجرا خواهد شد")
    print("⏹️  برای توقف برنامه، Ctrl+C را فشار دهید")
    print("=" * 40)
    
    # اجرای برنامه
    run_app()

if __name__ == "__main__":
    main()
