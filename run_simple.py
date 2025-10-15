#!/usr/bin/env python3
"""
اجرای صفحه ساده دوبله خودکار ویدیو
Run Simple Auto Video Dubbing Page
"""

import subprocess
import sys
import os

def main():
    """اجرای صفحه ساده"""
    try:
        print("🚀 در حال اجرای صفحه ساده دوبله خودکار ویدیو...")
        print("📱 صفحه در مرورگر باز خواهد شد")
        print("🔗 آدرس: http://localhost:8580")
        print("⏹️  برای توقف: Ctrl+C")
        print("-" * 50)
        
        # اجرای Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "simple_app.py",
            "--server.port", "8580",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
        
    except KeyboardInterrupt:
        print("\n⏹️  برنامه متوقف شد")
    except Exception as e:
        print(f"❌ خطا در اجرای برنامه: {e}")

if __name__ == "__main__":
    main()
