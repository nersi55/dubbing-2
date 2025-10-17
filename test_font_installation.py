#!/usr/bin/env python3
"""
تست نصب فونت Vazirmatn
Font Installation Test Script
"""

import os
import sys
from pathlib import Path

def test_font_installation():
    """تست نصب فونت Vazirmatn"""
    print("🎨 تست نصب فونت Vazirmatn")
    print("=" * 50)
    
    # بررسی فونت‌های محلی
    print("\n📁 بررسی فونت‌های محلی پروژه:")
    local_fonts = [
        "fonts/Vazirmatn-Regular.ttf",
        "fonts/Vazirmatn-Medium.ttf",
        "fonts/Vazirmatn-Bold.ttf"
    ]
    
    local_found = 0
    for font_path in local_fonts:
        if os.path.exists(font_path):
            size = os.path.getsize(font_path)
            print(f"✅ {font_path} ({size:,} bytes)")
            local_found += 1
        else:
            print(f"❌ {font_path} - یافت نشد")
    
    # بررسی فونت‌های سیستم
    print("\n🖥️  بررسی فونت‌های سیستم:")
    import platform
    system = platform.system().lower()
    
    system_font_dirs = []
    if system == "windows":
        system_font_dirs = [
            os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts"),
            os.path.expanduser("~/Fonts"),
            "C:/Windows/Fonts"
        ]
    elif system == "darwin":  # macOS
        system_font_dirs = [
            os.path.expanduser("~/Library/Fonts"),
            "/Library/Fonts",
            "/System/Library/Fonts"
        ]
    else:  # Linux
        system_font_dirs = [
            os.path.expanduser("~/.fonts"),
            os.path.expanduser("~/.local/share/fonts"),
            "/usr/share/fonts/truetype",
            "/usr/local/share/fonts"
        ]
    
    system_found = 0
    for font_dir in system_font_dirs:
        if os.path.exists(font_dir):
            print(f"\n📂 بررسی {font_dir}:")
            try:
                for font_file in os.listdir(font_dir):
                    if "vazirmatn" in font_file.lower() and font_file.endswith(".ttf"):
                        font_path = os.path.join(font_dir, font_file)
                        size = os.path.getsize(font_path)
                        print(f"  ✅ {font_file} ({size:,} bytes)")
                        system_found += 1
            except PermissionError:
                print(f"  ⚠️  دسترسی به {font_dir} محدود است")
            except Exception as e:
                print(f"  ❌ خطا در بررسی {font_dir}: {e}")
    
    # تست عملکرد فونت در کد
    print("\n🔧 تست عملکرد فونت در کد:")
    try:
        # Import کردن کلاس اصلی
        sys.path.append(os.path.dirname(__file__))
        from dubbing_functions import DubbingApp
        
        app = DubbingApp()
        font_path = app._get_font_path("vazirmatn")
        
        if font_path:
            print(f"✅ فونت یافت شد: {font_path}")
            
            # بررسی وجود فایل
            if os.path.exists(font_path):
                size = os.path.getsize(font_path)
                print(f"✅ فایل فونت موجود است ({size:,} bytes)")
            else:
                print(f"❌ فایل فونت موجود نیست: {font_path}")
        else:
            print("❌ فونت Vazirmatn یافت نشد")
            
    except ImportError as e:
        print(f"❌ خطا در import کردن کلاس: {e}")
    except Exception as e:
        print(f"❌ خطا در تست عملکرد: {e}")
    
    # خلاصه نتایج
    print("\n📊 خلاصه نتایج:")
    print(f"فونت‌های محلی یافت شده: {local_found}/3")
    print(f"فونت‌های سیستم یافت شده: {system_found}")
    
    if local_found > 0:
        print("✅ فونت‌های محلی موجود است - پروژه روی سرور کار خواهد کرد")
    elif system_found > 0:
        print("✅ فونت‌های سیستم موجود است - پروژه کار خواهد کرد")
    else:
        print("❌ هیچ فونت Vazirmatn یافت نشد")
        print("💡 برای نصب فونت: python install_fonts.py")
    
    return local_found > 0 or system_found > 0

def test_font_usage():
    """تست استفاده از فونت در تولید ویدیو"""
    print("\n🎬 تست استفاده از فونت در تولید ویدیو:")
    
    try:
        from dubbing_functions import DubbingApp
        app = DubbingApp()
        
        # تست تنظیمات پیش‌فرض
        print("📝 تنظیمات پیش‌فرض زیرنویس:")
        default_config = {
            "font": "vazirmatn",
            "fontsize": 24,
            "color": "white"
        }
        
        font_path = app._get_font_path(default_config["font"])
        if font_path:
            print(f"✅ فونت زیرنویس: {font_path}")
        else:
            print("❌ فونت زیرنویس یافت نشد")
        
        # تست تنظیمات متن ثابت
        print("\n📝 تنظیمات پیش‌فرض متن ثابت:")
        fixed_config = {
            "font": "vazirmatn",
            "fontsize": 20,
            "color": "yellow"
        }
        
        font_path = app._get_font_path(fixed_config["font"])
        if font_path:
            print(f"✅ فونت متن ثابت: {font_path}")
        else:
            print("❌ فونت متن ثابت یافت نشد")
            
    except Exception as e:
        print(f"❌ خطا در تست استفاده: {e}")

def main():
    """تابع اصلی"""
    print("🎨 تست کامل نصب فونت Vazirmatn")
    print("=" * 60)
    
    # تست نصب
    installation_ok = test_font_installation()
    
    # تست استفاده
    test_font_usage()
    
    print("\n" + "=" * 60)
    if installation_ok:
        print("🎉 تست موفق - فونت Vazirmatn آماده استفاده است!")
        print("✅ پروژه روی سرور بدون مشکل کار خواهد کرد")
    else:
        print("❌ تست ناموفق - فونت Vazirmatn نصب نیست")
        print("💡 برای حل مشکل:")
        print("   1. python install_fonts.py")
        print("   2. یا فونت‌ها را دستی در پوشه fonts/ قرار دهید")
    
    return installation_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
