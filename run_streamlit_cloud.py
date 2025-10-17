#!/usr/bin/env python3
"""
اجرای اپلیکیشن Streamlit برای Cloud
Run Streamlit App for Cloud Deployment
"""

import os
import sys
import subprocess

def main():
    """اجرای اپلیکیشن Streamlit"""
    try:
        print("🚀 در حال اجرای اپلیکیشن دوبله خودکار ویدیو...")
        print("📱 صفحه در مرورگر باز خواهد شد")
        print("⏹️  برای توقف: Ctrl+C")
        print("-" * 50)
        
        # تنظیمات محیط
        os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
        os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "false"
        os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
        
        # اجرای Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "simple_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--browser.gatherUsageStats", "false",
            "--server.headless", "true"
        ])
        
    except KeyboardInterrupt:
        print("\n⏹️  برنامه متوقف شد")
    except Exception as e:
        print(f"❌ خطا در اجرای برنامه: {e}")

if __name__ == "__main__":
    main()
