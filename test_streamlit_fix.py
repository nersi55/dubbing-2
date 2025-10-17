#!/usr/bin/env python3
"""
تست اصلاحات Streamlit Cloud
Test Streamlit Cloud Fixes
"""

import os
import sys
import subprocess
import time
import signal
import threading

def test_uvicorn_fix():
    """تست اصلاح uvicorn"""
    print("🧪 تست اصلاح uvicorn...")
    
    # تنظیم متغیرهای محیطی
    os.environ["HOST"] = "127.0.0.1"
    os.environ["PORT"] = "8003"
    os.environ["RELOAD"] = "false"
    
    try:
        # اجرای uvicorn در background
        process = subprocess.Popen([
            sys.executable, "api_simple.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # صبر برای شروع سرور
        time.sleep(3)
        
        # بررسی وضعیت
        if process.poll() is None:
            print("✅ uvicorn با موفقیت شروع شد")
            process.terminate()
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ uvicorn خطا داشت: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست uvicorn: {e}")
        return False

def test_streamlit_fix():
    """تست اصلاح Streamlit"""
    print("🧪 تست اصلاح Streamlit...")
    
    try:
        # اجرای Streamlit در background
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "simple_app.py",
            "--server.port", "8502",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false",
            "--server.headless", "true"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # صبر برای شروع سرور
        time.sleep(5)
        
        # بررسی وضعیت
        if process.poll() is None:
            print("✅ Streamlit با موفقیت شروع شد")
            process.terminate()
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Streamlit خطا داشت: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست Streamlit: {e}")
        return False

def main():
    """تست اصلی"""
    print("🚀 شروع تست اصلاحات Streamlit Cloud...")
    print("=" * 50)
    
    # تست uvicorn
    uvicorn_ok = test_uvicorn_fix()
    print()
    
    # تست Streamlit
    streamlit_ok = test_streamlit_fix()
    print()
    
    # نتیجه نهایی
    print("=" * 50)
    if uvicorn_ok and streamlit_ok:
        print("🎉 همه تست‌ها موفق بود!")
        print("✅ اپلیکیشن آماده استقرار در Streamlit Cloud است")
    else:
        print("❌ برخی تست‌ها ناموفق بود")
        if not uvicorn_ok:
            print("  - uvicorn نیاز به بررسی دارد")
        if not streamlit_ok:
            print("  - Streamlit نیاز به بررسی دارد")

if __name__ == "__main__":
    main()
