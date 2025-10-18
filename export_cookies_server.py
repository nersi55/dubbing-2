#!/usr/bin/env python3
"""
اسکریپت صادرات کوکی‌ها برای سرور لینوکس
Browser Cookies Export Script for Linux Server
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

def check_yt_dlp():
    """بررسی نصب yt-dlp"""
    try:
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ yt-dlp نصب شده: {result.stdout.strip()}")
            return True
        else:
            print("❌ yt-dlp نصب نشده است")
            return False
    except FileNotFoundError:
        print("❌ yt-dlp نصب نشده است")
        return False

def create_server_cookies():
    """ایجاد کوکی‌های سرور (بدون مرورگر)"""
    print("🌐 ایجاد کوکی‌های سرور...")
    
    # کوکی‌های پایه برای سرور
    server_cookies = {
        "cookies": [
            {
                "name": "VISITOR_INFO1_LIVE",
                "value": "server_session_" + str(int(time.time())),
                "domain": ".youtube.com",
                "path": "/",
                "expires": int(time.time()) + 86400,  # 24 ساعت
                "httpOnly": False,
                "secure": True
            },
            {
                "name": "YSC",
                "value": "server_ysc_" + str(int(time.time())),
                "domain": ".youtube.com",
                "path": "/",
                "expires": int(time.time()) + 86400,
                "httpOnly": True,
                "secure": True
            },
            {
                "name": "PREF",
                "value": "tz=UTC&f5=30000&f7=100",
                "domain": ".youtube.com",
                "path": "/",
                "expires": int(time.time()) + 31536000,  # 1 سال
                "httpOnly": False,
                "secure": True
            }
        ]
    }
    
    # ذخیره کوکی‌ها
    with open('cookies.json', 'w', encoding='utf-8') as f:
        json.dump(server_cookies, f, indent=2)
    
    print("✅ کوکی‌های سرور ایجاد شدند")
    return True

def test_cookies():
    """تست کوکی‌های ایجاد شده"""
    print("\n🧪 تست کوکی‌های ایجاد شده...")
    
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        cmd = [
            'yt-dlp',
            '--cookies', 'cookies.json',
            '--user-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            '--referer', 'https://www.youtube.com/',
            '--print-json',
            '--no-download',
            test_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout.strip():
            print("✅ کوکی‌ها کار می‌کنند")
            return True
        else:
            print("❌ کوکی‌ها کار نمی‌کنند")
            print(f"خطا: {result.stderr[:200]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ تست timeout شد")
        return False
    except Exception as e:
        print(f"❌ خطا در تست: {e}")
        return False

def create_alternative_config():
    """ایجاد تنظیمات جایگزین"""
    print("\n🔧 ایجاد تنظیمات جایگزین...")
    
    config = {
        "server_mode": True,
        "no_cookies": True,
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "referer": "https://www.youtube.com/",
        "headers": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        },
        "timeout": 30,
        "retries": 3,
        "fallback_formats": [
            "best[height<=720]",
            "best[height<=480]",
            "worst"
        ]
    }
    
    with open('server_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print("✅ تنظیمات سرور ایجاد شدند")
    return True

def main():
    """تابع اصلی"""
    print("🍪 ابزار کوکی‌های سرور لینوکس")
    print("=" * 40)
    
    # بررسی yt-dlp
    if not check_yt_dlp():
        print("\n❌ ابتدا yt-dlp را نصب کنید:")
        print("pip install yt-dlp")
        return False
    
    # ایجاد کوکی‌های سرور
    if not create_server_cookies():
        print("\n❌ خطا در ایجاد کوکی‌ها")
        return False
    
    # تست کوکی‌ها
    if not test_cookies():
        print("\n⚠️ کوکی‌ها کار نمی‌کنند، اما تنظیمات جایگزین ایجاد می‌شود")
    
    # ایجاد تنظیمات جایگزین
    create_alternative_config()
    
    print("\n🎉 تنظیمات سرور آماده شد!")
    print("\n📁 فایل‌های ایجاد شده:")
    print("- cookies.json: کوکی‌های سرور")
    print("- server_config.json: تنظیمات سرور")
    
    print("\n💡 راه‌حل‌های اضافی:")
    print("1. استفاده از VPN یا Proxy")
    print("2. آپلود فایل ویدیو به جای دانلود از YouTube")
    print("3. استفاده از سرویس‌های دانلود ویدیو")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
