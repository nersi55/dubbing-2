#!/usr/bin/env python3
"""
حذف کوکی‌های منقضی شده
Cleanup Expired Cookies
"""

import os
import sys
import subprocess
from pathlib import Path

def remove_expired_cookies():
    """حذف کوکی‌های منقضی شده"""
    print("🧹 حذف کوکی‌های منقضی شده...")
    
    cookie_files = ['cookies.txt', 'cookies.text', 'cookies.json']
    
    for cookie_file in cookie_files:
        if os.path.exists(cookie_file):
            try:
                # تست کوکی‌ها
                test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                
                test_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'cookiefile': cookie_file,
                    'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
                    'referer': 'https://www.youtube.com/',
                    'socket_timeout': 10,
                    'retries': 1,
                }
                
                with yt_dlp.YoutubeDL(test_opts) as ydl:
                    info = ydl.extract_info(test_url, download=False)
                    if info and 'title' in info:
                        print(f"✅ {cookie_file} معتبر است")
                    else:
                        print(f"❌ {cookie_file} منقضی شده، حذف می‌شود")
                        os.remove(cookie_file)
                        print(f"🗑️ {cookie_file} حذف شد")
                        
            except Exception as e:
                print(f"❌ خطا در تست {cookie_file}: {str(e)[:100]}...")
                print(f"🗑️ {cookie_file} حذف می‌شود")
                os.remove(cookie_file)
                print(f"🗑️ {cookie_file} حذف شد")

def create_no_cookie_config():
    """ایجاد تنظیمات بدون کوکی"""
    print("\n🔧 ایجاد تنظیمات بدون کوکی...")
    
    config = {
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
            "worst[height<=360]",
            "worst[height<=480]",
            "worst"
        ]
    }
    
    import json
    with open('no_cookie_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print("✅ تنظیمات بدون کوکی ایجاد شد: no_cookie_config.json")

def main():
    """تابع اصلی"""
    print("🧹 ابزار پاکسازی کوکی‌های منقضی")
    print("=" * 40)
    
    try:
        import yt_dlp
    except ImportError:
        print("❌ yt-dlp نصب نشده است")
        print("💡 برای نصب: pip install yt-dlp")
        return False
    
    # حذف کوکی‌های منقضی
    remove_expired_cookies()
    
    # ایجاد تنظیمات بدون کوکی
    create_no_cookie_config()
    
    print("\n🎉 پاکسازی کامل شد!")
    print("💡 حالا برنامه بدون کوکی کار خواهد کرد")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
