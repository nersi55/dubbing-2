#!/usr/bin/env python3
"""
اجرای ساده API و Streamlit با background process
Simple API and Streamlit runner with background process
"""

import subprocess
import sys
import time
import os

def main():
    """اجرای اصلی"""
    print("🚀 در حال اجرای API و Streamlit...")
    print("📱 API: http://0.0.0.0:8003")
    print("📱 Streamlit: http://0.0.0.0:8580")
    print("⏹️  برای توقف: Ctrl+C")
    print("-" * 50)
    
    try:
        # اجرای API در background
        print("🚀 شروع API در background...")
        api_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "api_simple:app",
            "--host", "0.0.0.0",
            "--port", "8003",
            "--reload"
        ])
        
        # کمی صبر تا API شروع شود
        print("⏳ منتظر شروع API...")
        time.sleep(3)
        
        # اجرای Streamlit در foreground
        print("🚀 شروع Streamlit...")
        streamlit_process = subprocess.run([
            sys.executable, "-m", "streamlit", "run", "simple_app.py",
            "--server.port", "8580",
            "--server.address", "0.0.0.0",
            "--browser.gatherUsageStats", "false",
            "--server.fileWatcherType", "none"
        ])
        
    except KeyboardInterrupt:
        print("\n⏹️  در حال توقف برنامه...")
        try:
            api_process.terminate()
            print("✅ API متوقف شد")
        except:
            pass
        print("✅ برنامه متوقف شد")
    except Exception as e:
        print(f"❌ خطا: {e}")
        try:
            api_process.terminate()
        except:
            pass

if __name__ == "__main__":
    main()
