#!/usr/bin/env python3
"""
اجرای همزمان API و Streamlit
Run API and Streamlit simultaneously
"""

import subprocess
import sys
import time
import threading
import signal
import os

def run_api():
    """اجرای API در thread جداگانه"""
    try:
        print("🚀 شروع API...")
        subprocess.run([
            sys.executable, "-m", "uvicorn", "api_simple:app",
            "--host", "0.0.0.0",
            "--port", "8003",
            "--reload"
        ])
    except Exception as e:
        print(f"❌ خطا در API: {e}")

def run_streamlit():
    """اجرای Streamlit در thread جداگانه"""
    try:
        print("⏳ منتظر شروع API...")
        time.sleep(5)  # کمی صبر تا API شروع شود
        print("🚀 شروع Streamlit...")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "simple_app.py",
            "--server.port", "8580",
            "--server.address", "0.0.0.0",
            "--browser.gatherUsageStats", "false"
        ])
    except Exception as e:
        print(f"❌ خطا در Streamlit: {e}")

def signal_handler(sig, frame):
    """مدیریت signal برای توقف برنامه"""
    print("\n⏹️  در حال توقف برنامه...")
    os._exit(0)

if __name__ == "__main__":
    # تنظیم signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🚀 در حال اجرای API و Streamlit...")
    print("📱 API: http://0.0.0.0:8003")
    print("📱 Streamlit: http://0.0.0.0:8580")
    print("⏹️  برای توقف: Ctrl+C")
    print("-" * 50)
    
    # اجرای API در thread جداگانه
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    
    # اجرای Streamlit در thread اصلی
    try:
        run_streamlit()
    except KeyboardInterrupt:
        print("\n⏹️  برنامه متوقف شد")
    except Exception as e:
        print(f"❌ خطا: {e}")
