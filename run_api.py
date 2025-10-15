#!/usr/bin/env python3
"""
اجرای API ساده دوبله خودکار ویدیو
Run Simple Auto Video Dubbing API
"""

import subprocess
import sys
import os

def main():
    """اجرای API"""
    try:
        print("🚀 در حال اجرای API دوبله خودکار ویدیو...")
        print("📱 API در آدرس: http://127.0.0.1:8002")
        print("📚 مستندات: http://127.0.0.1:8002/docs")
        print("⏹️  برای توقف: Ctrl+C")
        print("-" * 50)
        
        # اجرای FastAPI
        subprocess.run([
            sys.executable, "-m", "uvicorn", "api_simple:app",
            "--host", "127.0.0.1",
            "--port", "8002",
            "--reload"
        ])
        
    except KeyboardInterrupt:
        print("\n⏹️  API متوقف شد")
    except Exception as e:
        print(f"❌ خطا در اجرای API: {e}")

if __name__ == "__main__":
    main()