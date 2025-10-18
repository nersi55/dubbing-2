#!/usr/bin/env python3
"""
تست کامل تنظیمات سرور لینوکس
Complete Linux Server Setup Test
"""

import subprocess
import sys
import os
import json
from pathlib import Path

def test_system_requirements():
    """تست پیش‌نیازهای سیستم"""
    print("🔍 تست پیش‌نیازهای سیستم...")
    
    requirements = {
        'python': ['python3', '--version'],
        'ffmpeg': ['ffmpeg', '-version'],
        'yt-dlp': ['yt-dlp', '--version'],
    }
    
    results = {}
    
    for name, cmd in requirements.items():
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {name}: {result.stdout.split()[0] if result.stdout else 'نصب شده'}")
                results[name] = True
            else:
                print(f"❌ {name}: نصب نشده")
                results[name] = False
        except FileNotFoundError:
            print(f"❌ {name}: نصب نشده")
            results[name] = False
    
    return results

def test_youtube_access():
    """تست دسترسی به YouTube"""
    print("\n🌐 تست دسترسی به YouTube...")
    
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    # تست بدون کوکی
    print("🧪 تست بدون کوکی...")
    try:
        cmd = [
            'yt-dlp',
            '--user-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            '--referer', 'https://www.youtube.com/',
            '--print-json',
            '--no-download',
            test_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout.strip():
            print("✅ دسترسی بدون کوکی موفق")
            return True
        else:
            print("❌ دسترسی بدون کوکی شکست خورد")
            print(f"خطا: {result.stderr[:200]}...")
    except Exception as e:
        print(f"❌ خطا در تست: {e}")
    
    return False

def test_dubbing_functions():
    """تست توابع دوبله"""
    print("\n🎬 تست توابع دوبله...")
    
    try:
        from dubbing_functions import VideoDubbingApp
        
        # ایجاد instance
        app = VideoDubbingApp("test_key")
        print("✅ کلاس VideoDubbingApp بارگذاری شد")
        
        # تست متدهای اصلی
        methods_to_test = [
            'download_youtube_video',
            '_fallback_download',
            'extract_audio_with_whisper',
            'translate_subtitles',
            'create_subtitled_video'
        ]
        
        for method_name in methods_to_test:
            if hasattr(app, method_name):
                print(f"✅ متد {method_name} موجود است")
            else:
                print(f"❌ متد {method_name} موجود نیست")
        
        return True
        
    except ImportError as e:
        print(f"❌ خطا در بارگذاری dubbing_functions: {e}")
        return False
    except Exception as e:
        print(f"❌ خطا در تست توابع: {e}")
        return False

def test_fonts():
    """تست فونت‌ها"""
    print("\n🔤 تست فونت‌ها...")
    
    font_dir = Path("fonts")
    if not font_dir.exists():
        print("❌ پوشه fonts موجود نیست")
        return False
    
    required_fonts = [
        "Vazirmatn-Regular.ttf",
        "Vazirmatn-Medium.ttf", 
        "Vazirmatn-Bold.ttf"
    ]
    
    for font in required_fonts:
        font_path = font_dir / font
        if font_path.exists():
            print(f"✅ {font} موجود است")
        else:
            print(f"❌ {font} موجود نیست")
    
    return True

def create_test_script():
    """ایجاد اسکریپت تست"""
    print("\n📝 ایجاد اسکریپت تست...")
    
    test_script = '''#!/usr/bin/env python3
"""
تست سریع دوبله روی سرور
Quick dubbing test on server
"""

import sys
import os
from pathlib import Path

# اضافه کردن مسیر پروژه
sys.path.insert(0, str(Path(__file__).parent))

from dubbing_functions import VideoDubbingApp

def test_quick_dubbing():
    """تست سریع دوبله"""
    print("🧪 تست سریع دوبله...")
    
    # تست URL
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        # ایجاد app
        app = VideoDubbingApp("AIzaSyBNYpugB8Ezrpmk-U7Yvp9ynClEJLCETMo")
        
        # تست دانلود
        print("📥 تست دانلود...")
        success = app.download_youtube_video(test_url)
        
        if success:
            print("✅ دانلود موفق")
            return True
        else:
            print("❌ دانلود شکست خورد")
            return False
            
    except Exception as e:
        print(f"❌ خطا: {e}")
        return False

if __name__ == "__main__":
    success = test_quick_dubbing()
    sys.exit(0 if success else 1)
'''
    
    with open('quick_test.py', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    # قابل اجرا کردن
    os.chmod('quick_test.py', 0o755)
    
    print("✅ اسکریپت تست ایجاد شد: quick_test.py")
    return True

def main():
    """تابع اصلی"""
    print("🧪 تست کامل تنظیمات سرور لینوکس")
    print("=" * 50)
    
    all_tests_passed = True
    
    # تست 1: پیش‌نیازهای سیستم
    system_results = test_system_requirements()
    if not all(system_results.values()):
        print("\n❌ برخی پیش‌نیازها نصب نشده‌اند")
        all_tests_passed = False
    
    # تست 2: دسترسی به YouTube
    if not test_youtube_access():
        print("\n⚠️ دسترسی به YouTube محدود است")
        print("💡 راه‌حل‌های ممکن:")
        print("- استفاده از VPN یا Proxy")
        print("- آپلود فایل ویدیو به جای دانلود")
        all_tests_passed = False
    
    # تست 3: توابع دوبله
    if not test_dubbing_functions():
        print("\n❌ توابع دوبله مشکل دارند")
        all_tests_passed = False
    
    # تست 4: فونت‌ها
    if not test_fonts():
        print("\n⚠️ فونت‌ها نصب نشده‌اند")
        print("💡 برای نصب: python install_fonts.py")
    
    # ایجاد اسکریپت تست
    create_test_script()
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 همه تست‌ها موفق بود!")
        print("✅ سرور آماده استفاده است")
    else:
        print("⚠️ برخی تست‌ها شکست خوردند")
        print("💡 لطفاً مشکلات را برطرف کنید")
    
    print("\n🔧 برای تست سریع:")
    print("python quick_test.py")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
