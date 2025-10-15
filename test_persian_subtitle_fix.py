#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تست رفع مشکل مربع در زیرنویس فارسی
Test script for fixing Persian subtitle square character issue
"""

import os
import sys
from pathlib import Path

# اضافه کردن مسیر پروژه
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dubbing_functions import VideoDubbingApp

def test_persian_subtitle_fix():
    """تست رفع مشکل مربع در زیرنویس فارسی"""
    
    print("🧪 تست رفع مشکل مربع در زیرنویس فارسی")
    print("=" * 50)
    
    # ایجاد نمونه از کلاس
    dubbing_app = VideoDubbingApp("test_key")
    
    # تست متن مشکل‌دار
    problematic_text = "مثلاً میگن: \"منظورم رو متوجه نمیشید؟\""
    print(f"📝 متن اصلی: {problematic_text}")
    
    # تست نرمال‌سازی
    normalized_text = dubbing_app._normalize_persian_text(problematic_text)
    print(f"✅ متن نرمال‌سازی شده: {normalized_text}")
    
    # تست فونت
    print("\n🔍 تست فونت‌های فارسی:")
    fonts_to_test = ["vazirmatn", "Arial", "SF Arabic", "Arial Unicode"]
    
    for font in fonts_to_test:
        font_path = dubbing_app._get_font_path(font)
        if font_path:
            print(f"✅ {font}: {font_path}")
        else:
            print(f"❌ {font}: یافت نشد")
    
    # ایجاد فایل SRT تست
    test_srt_content = f"""1
00:00:00,000 --> 00:00:03,000
{problematic_text}

2
00:00:03,000 --> 00:00:06,000
این یک تست برای بررسی رندر صحیح متن فارسی است.

3
00:00:06,000 --> 00:00:09,000
کلمات مشکل‌دار: مثلاً، مثلا، مثلاً
"""
    
    # ذخیره فایل SRT تست
    test_srt_path = project_root / "dubbing_work" / "test_persian_subtitles.srt"
    test_srt_path.parent.mkdir(exist_ok=True)
    
    with open(test_srt_path, 'w', encoding='utf-8') as f:
        f.write(test_srt_content)
    
    print(f"\n📁 فایل SRT تست ایجاد شد: {test_srt_path}")
    
    # تست ایجاد ویدیو با زیرنویس
    if (project_root / "dubbing_work" / "input_video.mp4").exists():
        print("\n🎬 تست ایجاد ویدیو با زیرنویس...")
        
        # تنظیمات زیرنویس با فونت فارسی
        subtitle_config = {
            "font": "vazirmatn",
            "fontsize": 24,
            "color": "white",
            "outline_color": "black",
            "outline_width": 2,
            "position": "bottom_center"
        }
        
        try:
            # ایجاد ویدیو با زیرنویس
            output_path = dubbing_app.create_subtitled_video(subtitle_config=subtitle_config)
            
            if output_path and Path(output_path).exists():
                print(f"✅ ویدیو با زیرنویس ایجاد شد: {output_path}")
                print("🎉 تست موفقیت‌آمیز بود!")
            else:
                print("❌ خطا در ایجاد ویدیو")
                
        except Exception as e:
            print(f"❌ خطا در تست: {str(e)}")
    else:
        print("⚠️ فایل ویدیو ورودی یافت نشد - فقط تست متن انجام شد")
    
    print("\n" + "=" * 50)
    print("✅ تست کامل شد!")

if __name__ == "__main__":
    test_persian_subtitle_fix()
