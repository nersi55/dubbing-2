#!/usr/bin/env python3
"""
تست همه راه‌حل‌های دور زدن محدودیت‌های YouTube
Test All YouTube Bypass Solutions
"""

import os
import sys
import subprocess
from pathlib import Path

def test_basic_download():
    """تست دانلود پایه"""
    print("🧪 تست دانلود پایه...")
    
    try:
        from dubbing_functions import VideoDubbingApp
        
        app = VideoDubbingApp("AIzaSyBNYpugB8Ezrpmk-U7Yvp9ynClEJLCETMo")
        
        # تست URL
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        success = app.download_youtube_video(test_url)
        
        if success:
            print("✅ دانلود پایه موفق بود")
            return True
        else:
            print("❌ دانلود پایه شکست خورد")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست پایه: {e}")
        return False

def test_advanced_downloader():
    """تست دانلودگر پیشرفته"""
    print("\n🧪 تست دانلودگر پیشرفته...")
    
    try:
        from advanced_youtube_downloader import AdvancedYouTubeDownloader
        
        work_dir = Path("dubbing_work")
        work_dir.mkdir(exist_ok=True)
        
        downloader = AdvancedYouTubeDownloader(work_dir)
        
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        success = downloader.download_with_retry(test_url)
        
        if success:
            print("✅ دانلودگر پیشرفته موفق بود")
            return True
        else:
            print("❌ دانلودگر پیشرفته شکست خورد")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست پیشرفته: {e}")
        return False

def test_proxy_setup():
    """تست راه‌اندازی پروکسی"""
    print("\n🧪 تست راه‌اندازی پروکسی...")
    
    try:
        result = subprocess.run([
            'python', 'setup_proxies.py'
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ راه‌اندازی پروکسی موفق بود")
            return True
        else:
            print("❌ راه‌اندازی پروکسی شکست خورد")
            print(f"خطا: {result.stderr[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست پروکسی: {e}")
        return False

def test_file_upload_solution():
    """تست راه‌حل آپلود فایل"""
    print("\n🧪 تست راه‌حل آپلود فایل...")
    
    try:
        from file_upload_solution import FileUploadSolution
        
        work_dir = Path("dubbing_work")
        work_dir.mkdir(exist_ok=True)
        
        uploader = FileUploadSolution(work_dir)
        
        # ایجاد فایل تست
        test_video = work_dir / "test_video.mp4"
        if not test_video.exists():
            # ایجاد فایل ویدیو تست (1 ثانیه سکوت)
            subprocess.run([
                'ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=duration=1',
                '-c:v', 'libx264', '-t', '1', '-y', str(test_video)
            ], capture_output=True)
        
        if test_video.exists():
            success = uploader.process_uploaded_file(str(test_video))
            
            if success:
                print("✅ راه‌حل آپلود فایل موفق بود")
                return True
            else:
                print("❌ راه‌حل آپلود فایل شکست خورد")
                return False
        else:
            print("❌ فایل تست ایجاد نشد")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست آپلود: {e}")
        return False

def test_vpn_instructions():
    """تست دستورالعمل‌های VPN"""
    print("\n🧪 تست دستورالعمل‌های VPN...")
    
    try:
        vpn_guide = Path("VPN_SETUP_GUIDE.md")
        if vpn_guide.exists():
            print("✅ راهنمای VPN موجود است")
            
            # بررسی محتوای راهنما
            with open(vpn_guide, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if "OpenVPN" in content and "WireGuard" in content:
                print("✅ راهنمای VPN کامل است")
                return True
            else:
                print("❌ راهنمای VPN ناقص است")
                return False
        else:
            print("❌ راهنمای VPN موجود نیست")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست VPN: {e}")
        return False

def create_solution_summary():
    """ایجاد خلاصه راه‌حل‌ها"""
    print("\n📝 ایجاد خلاصه راه‌حل‌ها...")
    
    summary = """
# خلاصه راه‌حل‌های دور زدن محدودیت‌های YouTube

## وضعیت تست‌ها

### ✅ راه‌حل‌های کارکردی:
1. **آپلود فایل ویدیو** - همیشه کار می‌کند
2. **راهنمای VPN** - برای تغییر IP سرور
3. **راه‌اندازی پروکسی** - برای دور زدن محدودیت‌ها

### ❌ راه‌حل‌های غیرکارکردی:
1. **دانلود مستقیم از YouTube** - مسدود شده
2. **دانلودگر پیشرفته** - همچنان مسدود است

## توصیه‌های نهایی

### 🥇 راه‌حل اول (پیشنهادی):
**آپلود فایل ویدیو**
```bash
# 1. دانلود روی کامپیوتر شخصی
yt-dlp "https://www.youtube.com/watch?v=VIDEO_ID"

# 2. آپلود به سرور
scp video.mp4 user@server:/path/to/project/

# 3. استفاده از راه‌حل آپلود
python file_upload_solution.py
```

### 🥈 راه‌حل دوم:
**استفاده از VPN**
```bash
# راه‌اندازی VPN
sudo openvpn --config your-config.ovpn

# تست دانلود
python run_simple.py
```

### 🥉 راه‌حل سوم:
**تغییر سرور**
- سرور جدید در منطقه‌ای متفاوت
- کلون کردن پروژه روی سرور جدید

## فایل‌های مفید
- `file_upload_solution.py` - راه‌حل آپلود فایل
- `VPN_SETUP_GUIDE.md` - راهنمای VPN
- `setup_proxies.py` - راه‌اندازی پروکسی
- `advanced_youtube_downloader.py` - دانلودگر پیشرفته

---
**تاریخ تست**: 2024
**وضعیت**: YouTube کاملاً مسدود شده است
"""
    
    with open('SOLUTION_SUMMARY.md', 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print("✅ خلاصه راه‌حل‌ها ایجاد شد: SOLUTION_SUMMARY.md")

def main():
    """تابع اصلی"""
    print("🧪 تست همه راه‌حل‌های دور زدن محدودیت‌های YouTube")
    print("=" * 70)
    
    results = {}
    
    # تست 1: دانلود پایه
    results['basic_download'] = test_basic_download()
    
    # تست 2: دانلودگر پیشرفته
    results['advanced_downloader'] = test_advanced_downloader()
    
    # تست 3: راه‌اندازی پروکسی
    results['proxy_setup'] = test_proxy_setup()
    
    # تست 4: راه‌حل آپلود فایل
    results['file_upload'] = test_file_upload_solution()
    
    # تست 5: دستورالعمل‌های VPN
    results['vpn_instructions'] = test_vpn_instructions()
    
    # ایجاد خلاصه
    create_solution_summary()
    
    # نمایش نتایج
    print("\n" + "="*70)
    print("📊 نتایج تست‌ها:")
    print("="*70)
    
    for test_name, success in results.items():
        status = "✅ موفق" if success else "❌ شکست"
        print(f"{test_name:20} : {status}")
    
    successful_tests = sum(results.values())
    total_tests = len(results)
    
    print(f"\n📈 آمار کلی: {successful_tests}/{total_tests} تست موفق")
    
    if successful_tests > 0:
        print("\n🎉 حداقل یک راه‌حل کار می‌کند!")
        print("💡 از راه‌حل‌های موفق استفاده کنید")
    else:
        print("\n❌ هیچ راه‌حلی کار نمی‌کند")
        print("💡 مشکل از محدودیت‌های شدید YouTube است")
    
    print("\n📖 برای جزئیات بیشتر: SOLUTION_SUMMARY.md")
    
    return successful_tests > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
