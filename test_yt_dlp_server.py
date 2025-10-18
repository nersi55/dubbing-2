#!/usr/bin/env python3
"""
تست yt-dlp روی سرور لینوکس
Test yt-dlp on Linux server
"""

import subprocess
import sys
import os
from pathlib import Path

def test_yt_dlp_basic():
    """تست پایه yt-dlp"""
    print("🔍 تست پایه yt-dlp...")
    try:
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ yt-dlp نصب شده: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ خطا در yt-dlp: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ yt-dlp نصب نشده است")
        return False

def test_youtube_access():
    """تست دسترسی به YouTube"""
    print("\n🌐 تست دسترسی به YouTube...")
    
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    # تنظیمات مختلف برای تست
    test_configs = [
        {
            "name": "تنظیمات پیشرفته",
            "opts": [
                '--user-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                '--referer', 'https://www.youtube.com/',
                '--print-json',
                '--no-download'
            ]
        },
        {
            "name": "تنظیمات ساده",
            "opts": [
                '--user-agent', 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                '--print-json',
                '--no-download'
            ]
        },
        {
            "name": "تنظیمات حداقلی",
            "opts": [
                '--print-json',
                '--no-download'
            ]
        }
    ]
    
    for config in test_configs:
        print(f"\n🧪 تست {config['name']}...")
        try:
            cmd = ['yt-dlp'] + config['opts'] + [test_url]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and result.stdout.strip():
                print(f"✅ {config['name']} موفق بود")
                print(f"📊 اطلاعات ویدیو: {len(result.stdout)} کاراکتر")
                return True
            else:
                print(f"❌ {config['name']} شکست خورد")
                print(f"خطا: {result.stderr[:200]}...")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {config['name']} timeout شد")
        except Exception as e:
            print(f"❌ خطا در {config['name']}: {e}")
    
    return False

def test_download_small():
    """تست دانلود فایل کوچک"""
    print("\n📥 تست دانلود فایل کوچک...")
    
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    output_dir = Path("test_download")
    output_dir.mkdir(exist_ok=True)
    
    try:
        cmd = [
            'yt-dlp',
            '--user-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            '--referer', 'https://www.youtube.com/',
            '--format', 'worst[height<=360]',
            '--output', str(output_dir / 'test_video.%(ext)s'),
            '--max-filesize', '50M',
            test_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            # بررسی فایل دانلود شده
            downloaded_files = list(output_dir.glob('*'))
            if downloaded_files:
                file_size = downloaded_files[0].stat().st_size / (1024 * 1024)  # MB
                print(f"✅ دانلود موفق: {downloaded_files[0].name} ({file_size:.2f} MB)")
                
                # پاک کردن فایل تست
                for file in downloaded_files:
                    file.unlink()
                output_dir.rmdir()
                return True
            else:
                print("❌ فایل دانلود نشد")
        else:
            print(f"❌ خطا در دانلود: {result.stderr[:200]}...")
            
    except subprocess.TimeoutExpired:
        print("⏰ دانلود timeout شد")
    except Exception as e:
        print(f"❌ خطا در دانلود: {e}")
    finally:
        # پاک کردن فایل‌های تست
        if output_dir.exists():
            for file in output_dir.glob('*'):
                file.unlink()
            output_dir.rmdir()
    
    return False

def main():
    """تابع اصلی"""
    print("🧪 تست yt-dlp روی سرور لینوکس")
    print("=" * 40)
    
    # تست 1: بررسی نصب yt-dlp
    if not test_yt_dlp_basic():
        print("\n❌ yt-dlp نصب نشده است. لطفاً آن را نصب کنید:")
        print("pip install yt-dlp")
        return False
    
    # تست 2: دسترسی به YouTube
    if not test_youtube_access():
        print("\n❌ دسترسی به YouTube ممکن نیست")
        print("💡 راه‌حل‌های ممکن:")
        print("1. بررسی اتصال اینترنت")
        print("2. استفاده از VPN یا Proxy")
        print("3. بررسی فایروال سرور")
        return False
    
    # تست 3: دانلود فایل کوچک
    if not test_download_small():
        print("\n❌ دانلود فایل ممکن نیست")
        print("💡 ممکن است YouTube دسترسی از سرور را محدود کرده باشد")
        return False
    
    print("\n🎉 همه تست‌ها موفق بود!")
    print("✅ yt-dlp روی سرور لینوکس کار می‌کند")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
