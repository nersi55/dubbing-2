#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تست ترکیبی زیرنویس و متن ثابت
Test combined subtitle and fixed text functionality
"""

import sys
from pathlib import Path

# اضافه کردن مسیر پروژه
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dubbing_functions import VideoDubbingApp

def test_combined():
    """تست ترکیبی زیرنویس و متن ثابت"""
    
    print("🧪 تست ترکیبی زیرنویس و متن ثابت")
    print("=" * 50)
    
    # ایجاد نمونه از کلاس
    dubbing_app = VideoDubbingApp("test_key")
    
    # تنظیمات زیرنویس
    subtitle_config = {
        "font": "vazirmatn",
        "fontsize": 24,
        "color": "white",
        "outline_color": "black",
        "outline_width": 2,
        "position": "bottom_center"
    }
    
    # تنظیمات متن ثابت
    fixed_text_config = {
        "enabled": True,
        "text": "ترجمه و زیرنویس توسط ققنوس شانس",
        "font": "vazirmatn",
        "fontsize": 20,
        "color": "yellow",
        "background_color": "black",
        "position": "top_center",
        "margin_bottom": 10,
        "opacity": 0.8,
        "bold": True,
        "italic": False
    }
    
    # تست ایجاد ویدیو با هر دو
    if (project_root / "dubbing_work" / "input_video.mp4").exists():
        print("🎬 تست ایجاد ویدیو با زیرنویس و متن ثابت...")
        
        try:
            # ایجاد ویدیو با هر دو
            output_path = dubbing_app.create_subtitled_video(
                subtitle_config=subtitle_config,
                fixed_text_config=fixed_text_config
            )
            
            if output_path and Path(output_path).exists():
                print(f"✅ ویدیو با زیرنویس و متن ثابت ایجاد شد: {output_path}")
                print("🎉 تست موفقیت‌آمیز بود!")
            else:
                print("❌ خطا در ایجاد ویدیو")
                
        except Exception as e:
            print(f"❌ خطا در تست: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print("⚠️ فایل ویدیو ورودی یافت نشد")
    
    print("\n" + "=" * 50)
    print("✅ تست کامل شد!")

if __name__ == "__main__":
    test_combined()
