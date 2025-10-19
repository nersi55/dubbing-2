#!/usr/bin/env python3
"""
اجرای API ساده دوبله خودکار ویدیو
Run Simple Auto Video Dubbing API
"""

import subprocess
import sys
import os
import socket

def get_local_ip():
    """دریافت IP محلی"""
    try:
        # اتصال به یک آدرس خارجی برای دریافت IP محلی
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def main():
    """اجرای API"""
    try:
        local_ip = get_local_ip()
        
        print("🚀 در حال اجرای API دوبله خودکار ویدیو...")
        print("📱 API در آدرس محلی: http://127.0.0.1:8002")
        print(f"🌐 API در آدرس شبکه: http://{local_ip}:8002")
        print("📚 مستندات محلی: http://127.0.0.1:8002/docs")
        print(f"📚 مستندات شبکه: http://{local_ip}:8002/docs")
        print("⏹️  برای توقف: Ctrl+C")
        print("-" * 50)
        print("🔧 نکات امنیتی:")
        print("   - مطمئن شوید فایروال پورت 8002 را باز کرده‌اید")
        print("   - برای امنیت بیشتر از VPN استفاده کنید")
        print("   - در صورت نیاز، IP را در فایروال محدود کنید")
        print("-" * 50)
        
        # اجرای FastAPI با دسترسی از همه IP ها
        subprocess.run([
            sys.executable, "-m", "uvicorn", "api_simple:app",
            "--host", "0.0.0.0",  # تغییر از 127.0.0.1 به 0.0.0.0
            "--port", "8002",
            "--reload"
        ])
        
    except KeyboardInterrupt:
        print("\n⏹️  API متوقف شد")
    except Exception as e:
        print(f"❌ خطا در اجرای API: {e}")

if __name__ == "__main__":
    main()