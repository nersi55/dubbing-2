#!/usr/bin/env python3
"""
تست دانلود ساده با فقط cookies.txt
Test simple download with only cookies.txt
"""

import yt_dlp
import os

def test_simple_download():
    """تست دانلود ساده"""
    print("🧪 تست دانلود ساده با تنظیمات جدید...")
    
    # URL تست
    test_url = "https://youtube.com/shorts/CVtRmmFrSL0"
    
    # تنظیمات ساده
    config = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'test_video.%(ext)s',
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'no_warnings': False,
        'quiet': False,
        # تنظیمات IPv6
        'prefer_ipv6': True,
        'source_address': '::',
        # تنظیمات ساده
        'retries': 1,
        'fragment_retries': 1,
        'extractor_retries': 1,
    }
    
    # فقط استفاده از cookies.txt
    if os.path.exists('cookies.txt'):
        config['cookiefile'] = 'cookies.txt'
        print("🍪 استفاده از فایل کوکی: cookies.txt")
    else:
        print("⚠️ فایل cookies.txt یافت نشد - دانلود بدون کوکی")
    
    try:
        with yt_dlp.YoutubeDL(config) as ydl:
            print("📡 در حال دانلود...")
            info = ydl.extract_info(test_url, download=True)
            
            if info:
                print("✅ دانلود موفقیت‌آمیز!")
                print(f"📹 عنوان: {info.get('title', 'نامشخص')}")
                print(f"⏱️  مدت: {info.get('duration', 'نامشخص')} ثانیه")
                
                # پاک کردن فایل تست
                downloaded_file = ydl.prepare_filename(info)
                if os.path.exists(downloaded_file):
                    os.remove(downloaded_file)
                    print("🗑️ فایل تست پاک شد")
                
                return True
            else:
                print("❌ اطلاعات ویدیو دریافت نشد")
                return False
                
    except Exception as e:
        print(f"❌ خطا در دانلود: {e}")
        return False

def main():
    """اجرای تست"""
    print("🚀 شروع تست دانلود ساده")
    print("=" * 40)
    
    success = test_simple_download()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 تست موفقیت‌آمیز!")
        print("✅ تنظیمات ساده کار می‌کند")
    else:
        print("❌ تست ناموفق!")
        print("⚠️ لطفاً تنظیمات را بررسی کنید")

if __name__ == "__main__":
    main()
