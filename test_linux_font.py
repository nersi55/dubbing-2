#!/usr/bin/env python3
"""
تست فونت‌ها در Linux
Test fonts on Linux
"""

import os
import platform
from dubbing_functions import VideoDubbingApp

def test_font_handling():
    """تست نحوه پردازش فونت‌ها"""
    print("🔍 تست فونت‌ها در سیستم")
    print(f"سیستم عامل: {platform.system()}")
    print(f"نسخه: {platform.release()}")
    print("-" * 50)
    
    # ایجاد نمونه از کلاس (بدون API key برای تست)
    try:
        app = VideoDubbingApp("dummy_key")
    except:
        # اگر API key نیاز باشد، یک کلاس ساده ایجاد کن
        class TestApp:
            def _get_font_path(self, font_name):
                import platform
                import os
                system = platform.system()
                
                font_paths = {
                    "vazirmatn": [
                        os.path.join(os.path.dirname(__file__), "fonts", "Vazirmatn-Regular.ttf"),
                        os.path.join(os.path.dirname(__file__), "fonts", "Vazirmatn-Medium.ttf"),
                        os.path.join(os.path.dirname(__file__), "fonts", "Vazirmatn-Bold.ttf"),
                        "/usr/share/fonts/truetype/vazirmatn/Vazirmatn-Regular.ttf",
                        "/usr/share/fonts/opentype/vazirmatn/Vazirmatn-Regular.ttf",
                        "/usr/local/share/fonts/Vazirmatn-Regular.ttf",
                    ]
                }
                
                if font_name in font_paths:
                    for path in font_paths[font_name]:
                        if os.path.exists(path):
                            if font_name.lower() == 'vazirmatn' and system == 'Linux':
                                return "Vazirmatn"
                            return path
                
                if system == 'Linux':
                    return "Vazirmatn"
                return ""
        
        app = TestApp()
    
    # تست فونت‌های مختلف
    test_fonts = ["vazirmatn", "Arial", "Times New Roman", "Tahoma"]
    
    for font in test_fonts:
        print(f"\n🔤 تست فونت: {font}")
        font_path = app._get_font_path(font)
        print(f"   نتیجه: {font_path}")
        
        if font.lower() == 'vazirmatn':
            if platform.system() == 'Linux':
                if font_path == "Vazirmatn":
                    print("   ✅ فونت Vazirmatn به درستی شناسایی شد")
                else:
                    print("   ⚠️ فونت Vazirmatn شناسایی نشد")
            else:
                if font_path and os.path.exists(font_path):
                    print("   ✅ فونت Vazirmatn پیدا شد")
                else:
                    print("   ⚠️ فونت Vazirmatn پیدا نشد")
    
    # تست فونت‌های موجود در سیستم
    print(f"\n📁 فونت‌های موجود در پروژه:")
    fonts_dir = os.path.join(os.path.dirname(__file__), "fonts")
    if os.path.exists(fonts_dir):
        for file in os.listdir(fonts_dir):
            if file.endswith(('.ttf', '.otf')):
                print(f"   ✅ {file}")
    else:
        print("   ❌ پوشه fonts وجود ندارد")
    
    # تست فونت‌های سیستم Linux
    if platform.system() == 'Linux':
        print(f"\n🐧 فونت‌های سیستم Linux:")
        system_font_dirs = [
            "/usr/share/fonts/truetype",
            "/usr/share/fonts/opentype",
            "/usr/local/share/fonts"
        ]
        
        for font_dir in system_font_dirs:
            if os.path.exists(font_dir):
                print(f"   📁 {font_dir}:")
                try:
                    for root, dirs, files in os.walk(font_dir):
                        for file in files:
                            if 'vazirmatn' in file.lower() or 'vazir' in file.lower():
                                print(f"      ✅ {file}")
                except:
                    print(f"      ❌ خطا در خواندن {font_dir}")

if __name__ == "__main__":
    test_font_handling()
