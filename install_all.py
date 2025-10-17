#!/usr/bin/env python3
"""
نصب کامل تمام وابستگی‌های پروژه دوبله خودکار ویدیو
Complete installation of all dependencies for Auto Video Dubbing project
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """اجرای دستور و نمایش نتیجه"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - موفق")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - خطا: {e.stderr}")
        return False

def main():
    """نصب کامل وابستگی‌ها"""
    print("🚀 شروع نصب کامل وابستگی‌های پروژه دوبله خودکار ویدیو")
    print("=" * 60)
    
    # بررسی Python
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8 یا بالاتر مورد نیاز است")
        sys.exit(1)
    
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} - مناسب")
    
    # نصب pip packages
    print("\n📦 نصب پکیج‌های Python...")
    
    # نصب از requirements اصلی
    if not run_command("pip install -r requirements.txt", "نصب وابستگی‌های اصلی"):
        print("⚠️ خطا در نصب وابستگی‌های اصلی")
    
    # نصب وابستگی‌های اضافی
    additional_packages = [
        "fastapi",
        "uvicorn[standard]",
        "pydantic",
        "python-multipart",
        "requests",
        "typing-extensions"
    ]
    
    for package in additional_packages:
        run_command(f"pip install {package}", f"نصب {package}")
    
    # بررسی FFmpeg
    print("\n🎬 بررسی FFmpeg...")
    if run_command("ffmpeg -version", "بررسی FFmpeg"):
        print("✅ FFmpeg نصب شده است")
    else:
        print("❌ FFmpeg نصب نشده است")
        print("📥 لطفاً FFmpeg را از https://ffmpeg.org/download.html نصب کنید")
        print("   macOS: brew install ffmpeg")
        print("   Ubuntu: sudo apt install ffmpeg")
        print("   Windows: از سایت رسمی دانلود کنید")
    
    # بررسی Rubberband
    print("\n🎵 بررسی Rubberband...")
    if run_command("rubberband --version", "بررسی Rubberband"):
        print("✅ Rubberband نصب شده است")
    else:
        print("❌ Rubberband نصب نشده است")
        print("📥 لطفاً Rubberband را نصب کنید:")
        print("   macOS: brew install rubberband")
        print("   Ubuntu: sudo apt install rubberband-cli")
    
    # بررسی فونت Vazirmatn
    print("\n🔤 بررسی فونت Vazirmatn...")
    font_paths = [
        Path.home() / "Library/Fonts/Vazirmatn-Regular.ttf",
        Path.home() / "Library/Fonts/Vazirmatn-Medium.ttf",
        Path.home() / "Library/Fonts/Vazirmatn-Bold.ttf"
    ]
    
    font_found = any(path.exists() for path in font_paths)
    if font_found:
        print("✅ فونت Vazirmatn نصب شده است")
    else:
        print("❌ فونت Vazirmatn نصب نشده است")
        print("📥 لطفاً فونت Vazirmatn را نصب کنید:")
        print("   1. از https://github.com/rastikerdar/vazirmatn دانلود کنید")
        print("   2. فایل‌های .ttf را در ~/Library/Fonts/ کپی کنید")
        print("   3. یا از python install_fonts.py استفاده کنید")
    
    # تست اتصال Google AI
    print("\n🤖 تست اتصال Google AI...")
    try:
        import google.generativeai as genai
        print("✅ کتابخانه Google AI نصب شده است")
    except ImportError:
        print("❌ کتابخانه Google AI نصب نشده است")
    
    # تست Whisper
    print("\n🎤 تست Whisper...")
    try:
        import whisper
        print("✅ کتابخانه Whisper نصب شده است")
    except ImportError:
        print("❌ کتابخانه Whisper نصب نشده است")
    
    # تست FastAPI
    print("\n🌐 تست FastAPI...")
    try:
        import fastapi
        print("✅ کتابخانه FastAPI نصب شده است")
    except ImportError:
        print("❌ کتابخانه FastAPI نصب نشده است")
    
    # تست Streamlit
    print("\n📱 تست Streamlit...")
    try:
        import streamlit
        print("✅ کتابخانه Streamlit نصب شده است")
    except ImportError:
        print("❌ کتابخانه Streamlit نصب نشده است")
    
    print("\n" + "=" * 60)
    print("🎉 نصب کامل شد!")
    print("\n📋 مراحل بعدی:")
    print("1. 🔑 کلید Google API خود را در فایل‌ها قرار دهید")
    print("2. 🚀 صفحه وب: python run_simple.py")
    print("3. 🌐 API: python run_api.py")
    print("4. 📚 مستندات: API_DOCUMENTATION.md")
    
    print("\n🔗 آدرس‌های دسترسی:")
    print("- صفحه وب: http://localhost:8580")
    print("- API: http://127.0.0.1:8002")
    print("- مستندات API: http://127.0.0.1:8002/docs")

if __name__ == "__main__":
    main()
