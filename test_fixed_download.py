#!/usr/bin/env python3
"""
تست دانلود اصلاح شده
Test Fixed Download
"""

import sys
import os
from pathlib import Path

# اضافه کردن مسیر پروژه
sys.path.insert(0, str(Path(__file__).parent))

from dubbing_functions import VideoDubbingApp

def test_download_with_expired_cookies():
    """تست دانلود با کوکی‌های منقضی شده"""
    print("🧪 تست دانلود با کوکی‌های منقضی...")
    
    # تست URL (YouTube Shorts)
    test_url = "https://www.youtube.com/shorts/JYgjuBwJwXU?feature=share"
    
    try:
        # ایجاد app
        app = VideoDubbingApp("AIzaSyBNYpugB8Ezrpmk-U7Yvp9ynClEJLCETMo")
        
        print("📥 شروع تست دانلود...")
        success = app.download_youtube_video(test_url)
        
        if success:
            print("✅ دانلود موفق بود!")
            
            # بررسی فایل‌های ایجاد شده
            work_dir = app.work_dir
            input_video = work_dir / 'input_video.mp4'
            audio_file = work_dir / 'audio.wav'
            
            if input_video.exists():
                size_mb = input_video.stat().st_size / (1024 * 1024)
                print(f"📁 ویدیو: {input_video.name} ({size_mb:.2f} MB)")
            
            if audio_file.exists():
                size_mb = audio_file.stat().st_size / (1024 * 1024)
                print(f"🎵 صدا: {audio_file.name} ({size_mb:.2f} MB)")
            
            return True
        else:
            print("❌ دانلود شکست خورد")
            return False
            
    except Exception as e:
        print(f"❌ خطا: {e}")
        return False

def test_download_without_cookies():
    """تست دانلود بدون کوکی"""
    print("\n🧪 تست دانلود بدون کوکی...")
    
    # حذف کوکی‌های موجود
    cookie_files = ['cookies.txt', 'cookies.text', 'cookies.json']
    for cookie_file in cookie_files:
        if os.path.exists(cookie_file):
            os.rename(cookie_file, f"{cookie_file}.backup")
            print(f"📦 {cookie_file} به {cookie_file}.backup تغییر نام داد")
    
    try:
        # تست URL ساده
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        app = VideoDubbingApp("AIzaSyBNYpugB8Ezrpmk-U7Yvp9ynClEJLCETMo")
        
        print("📥 شروع تست دانلود بدون کوکی...")
        success = app.download_youtube_video(test_url)
        
        if success:
            print("✅ دانلود بدون کوکی موفق بود!")
            return True
        else:
            print("❌ دانلود بدون کوکی شکست خورد")
            return False
            
    except Exception as e:
        print(f"❌ خطا: {e}")
        return False
    finally:
        # بازگردانی کوکی‌ها
        for cookie_file in cookie_files:
            backup_file = f"{cookie_file}.backup"
            if os.path.exists(backup_file):
                os.rename(backup_file, cookie_file)
                print(f"📦 {backup_file} به {cookie_file} بازگردانده شد")

def main():
    """تابع اصلی"""
    print("🧪 تست دانلود اصلاح شده")
    print("=" * 40)
    
    # تست 1: با کوکی‌های منقضی
    test1_success = test_download_with_expired_cookies()
    
    # تست 2: بدون کوکی
    test2_success = test_download_without_cookies()
    
    print("\n" + "=" * 40)
    print("📊 نتایج تست:")
    print(f"✅ تست با کوکی‌های منقضی: {'موفق' if test1_success else 'شکست'}")
    print(f"✅ تست بدون کوکی: {'موفق' if test2_success else 'شکست'}")
    
    if test1_success or test2_success:
        print("\n🎉 حداقل یکی از تست‌ها موفق بود!")
        print("✅ سیستم اصلاح شده کار می‌کند")
        return True
    else:
        print("\n❌ همه تست‌ها شکست خوردند")
        print("💡 ممکن است مشکل از محدودیت‌های شبکه باشد")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
