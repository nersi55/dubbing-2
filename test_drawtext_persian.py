#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تست استفاده از drawtext برای متن فارسی
Test using drawtext for Persian text
"""

import subprocess
from pathlib import Path

def test_drawtext_persian():
    """تست استفاده از drawtext برای متن فارسی"""
    
    print("🧪 تست drawtext برای متن فارسی")
    print("=" * 50)
    
    # متن تست
    test_text = "مثلاً میگن: \"منظورم رو متوجه نمیشید؟\""
    print(f"📝 متن تست: {test_text}")
    
    # مسیر فایل‌ها
    input_video = Path("dubbing_work/input_video.mp4")
    output_video = Path("dubbing_work/test_drawtext_persian.mp4")
    
    if not input_video.exists():
        print("❌ فایل ویدیو ورودی یافت نشد")
        return
    
    # فیلتر drawtext برای متن فارسی
    drawtext_filter = f"""drawtext=text='{test_text}':fontfile=/Users/nersibayat/Library/Fonts/Vazirmatn-Regular.ttf:fontsize=24:fontcolor=white:x=(w-text_w)/2:y=h-th-20:box=1:boxcolor=black@0.5:boxborderw=5"""
    
    print("🎬 ایجاد ویدیو با drawtext...")
    
    try:
        subprocess.run([
            'ffmpeg', '-i', str(input_video),
            '-vf', drawtext_filter,
            '-c:v', 'libx264', '-c:a', 'copy',
            '-t', '10',  # فقط 10 ثانیه اول
            '-y', str(output_video)
        ], check=True, capture_output=True)
        
        if output_video.exists():
            print(f"✅ ویدیو با drawtext ایجاد شد: {output_video}")
            print("🎉 تست موفقیت‌آمیز بود!")
        else:
            print("❌ خطا در ایجاد ویدیو")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ خطا در FFmpeg: {e}")
        print(f"stderr: {e.stderr.decode()}")
    except Exception as e:
        print(f"❌ خطا: {str(e)}")

if __name__ == "__main__":
    test_drawtext_persian()
