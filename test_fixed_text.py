#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تست متن ثابت
Test fixed text functionality
"""

import sys
from pathlib import Path

# اضافه کردن مسیر پروژه
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dubbing_functions import VideoDubbingApp

def test_fixed_text():
    """تست متن ثابت"""
    
    print("🧪 تست متن ثابت")
    print("=" * 50)
    
    # ایجاد نمونه از کلاس
    dubbing_app = VideoDubbingApp("test_key")
    
    # تنظیمات متن ثابت
    fixed_text_config = {
        "enabled": True,
        "text": "ترجمه و زیرنویس توسط ققنوس شانس",
        "font": "vazirmatn",
        "fontsize": 20,
        "color": "yellow",
        "background_color": "black",
        "position": "bottom_center",
        "margin_bottom": 10,
        "opacity": 0.8,
        "bold": True,
        "italic": False
    }
    
    # تست ایجاد فیلتر متن ثابت
    try:
        fixed_text_filter = dubbing_app._create_fixed_text_filter(fixed_text_config)
        print(f"✅ فیلتر متن ثابت: {fixed_text_filter}")
        
        # تست ایجاد ویدیو با متن ثابت
        if (project_root / "dubbing_work" / "input_video.mp4").exists():
            print("\n🎬 تست ایجاد ویدیو با متن ثابت...")
            
            try:
                # ایجاد ویدیو با متن ثابت
                output_path = dubbing_app.create_subtitled_video(fixed_text_config=fixed_text_config)
                
                if output_path and Path(output_path).exists():
                    print(f"✅ ویدیو با متن ثابت ایجاد شد: {output_path}")
                    print("🎉 تست موفقیت‌آمیز بود!")
                else:
                    print("❌ خطا در ایجاد ویدیو")
                    
            except Exception as e:
                print(f"❌ خطا در تست: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print("⚠️ فایل ویدیو ورودی یافت نشد")
            
    except Exception as e:
        print(f"❌ خطا در ایجاد فیلتر: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("✅ تست کامل شد!")

if __name__ == "__main__":
    test_fixed_text()
