#!/usr/bin/env python3
"""
اسکریپت صادرات کوکی‌ها از مرورگر
Browser Cookies Export Script
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def export_cookies_from_browser():
    """صادرات کوکی‌ها از مرورگر"""
    print("🍪 راهنمای صادرات کوکی‌ها از مرورگر")
    print("=" * 50)
    
    # Check if yt-dlp is available
    try:
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ yt-dlp نصب شده: {result.stdout.strip()}")
        else:
            print("❌ yt-dlp نصب نشده است")
            return False
    except FileNotFoundError:
        print("❌ yt-dlp نصب نشده است")
        return False
    
    print("\n📋 مراحل صادرات کوکی‌ها:")
    print("1. مرورگر خود را باز کنید")
    print("2. به YouTube بروید و وارد حساب کاربری خود شوید")
    print("3. یکی از روش‌های زیر را انتخاب کنید:")
    print()
    
    print("🔧 روش 1: استفاده از yt-dlp (پیشنهادی)")
    print("   دستور زیر را در ترمینال اجرا کنید:")
    print("   yt-dlp --cookies-from-browser chrome --print-json 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' > cookies.json")
    print()
    print("   یا برای مرورگرهای دیگر:")
    print("   yt-dlp --cookies-from-browser firefox --print-json 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' > cookies.json")
    print("   yt-dlp --cookies-from-browser safari --print-json 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' > cookies.json")
    print()
    
    print("🔧 روش 2: استفاده از افزونه مرورگر")
    print("   1. افزونه 'Get cookies.txt' را نصب کنید")
    print("   2. به YouTube بروید")
    print("   3. روی آیکون افزونه کلیک کنید")
    print("   4. فایل cookies.txt را دانلود کنید")
    print()
    
    print("🔧 روش 3: دستی")
    print("   1. در مرورگر F12 را فشار دهید")
    print("   2. به تب Application/Storage بروید")
    print("   3. Cookies > https://www.youtube.com را انتخاب کنید")
    print("   4. کوکی‌ها را کپی کنید و در فایل cookies.txt ذخیره کنید")
    print()
    
    # Try to export cookies automatically
    print("🤖 تلاش برای صادرات خودکار کوکی‌ها...")
    
    browsers = ['chrome', 'firefox', 'safari', 'edge']
    for browser in browsers:
        try:
            print(f"   تلاش با {browser}...")
            result = subprocess.run([
                'yt-dlp', 
                '--cookies-from-browser', browser,
                '--print-json',
                'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and result.stdout.strip():
                # Save cookies
                with open('cookies.json', 'w', encoding='utf-8') as f:
                    f.write(result.stdout)
                print(f"✅ کوکی‌ها با موفقیت از {browser} صادر شدند")
                print("📁 فایل cookies.json ایجاد شد")
                return True
            else:
                print(f"   ❌ {browser} در دسترس نیست")
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            print(f"   ❌ خطا در {browser}: {e}")
            continue
    
    print("\n❌ نتوانستیم کوکی‌ها را خودکار صادر کنیم")
    print("📝 لطفاً یکی از روش‌های بالا را به صورت دستی انجام دهید")
    return False

def check_cookies_file():
    """بررسی وجود فایل کوکی"""
    cookies_files = ['cookies.txt', 'cookies.text', 'cookies.json']
    
    for cookie_file in cookies_files:
        if os.path.exists(cookie_file):
            print(f"✅ فایل کوکی پیدا شد: {cookie_file}")
            return cookie_file
    
    print("❌ هیچ فایل کوکی پیدا نشد")
    return None

def main():
    """تابع اصلی"""
    print("🍪 ابزار صادرات کوکی‌های YouTube")
    print("=" * 40)
    
    # Check if cookies already exist
    existing_cookies = check_cookies_file()
    if existing_cookies:
        print(f"✅ فایل کوکی موجود است: {existing_cookies}")
        return
    
    # Try to export cookies
    success = export_cookies_from_browser()
    
    if success:
        print("\n🎉 کوکی‌ها با موفقیت صادر شدند!")
        print("✅ حالا می‌توانید از برنامه دوبله استفاده کنید")
    else:
        print("\n⚠️  لطفاً کوکی‌ها را به صورت دستی صادر کنید")
        print("📖 راهنمای کامل در بالا آمده است")

if __name__ == "__main__":
    main()
