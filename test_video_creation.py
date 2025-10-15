#!/usr/bin/env python3
"""
تست ایجاد ویدیو نهایی
Test script for final video creation
"""

import os
import sys
from pathlib import Path
from dubbing_functions import VideoDubbingApp

def test_video_creation():
    """تست ایجاد ویدیو نهایی"""
    print("🎬 تست ایجاد ویدیو نهایی")
    print("=" * 50)
    
    # بررسی فایل‌های موجود
    work_dir = Path("dubbing_work")
    segments_dir = work_dir / "dubbed_segments"
    
    print(f"📁 پوشه کار: {work_dir}")
    print(f"📁 پوشه سگمنت‌ها: {segments_dir}")
    
    # بررسی فایل ویدیو
    video_file = work_dir / "input_video.mp4"
    if video_file.exists():
        print(f"✅ فایل ویدیو موجود: {video_file}")
        file_size = video_file.stat().st_size / (1024 * 1024)
        print(f"   📊 حجم: {file_size:.2f} MB")
    else:
        print(f"❌ فایل ویدیو یافت نشد: {video_file}")
        return False
    
    # بررسی فایل زیرنویس
    srt_file = work_dir / "audio_fa.srt"
    if srt_file.exists():
        print(f"✅ فایل زیرنویس موجود: {srt_file}")
        with open(srt_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print(f"   📝 تعداد خطوط: {len(lines)}")
    else:
        print(f"❌ فایل زیرنویس یافت نشد: {srt_file}")
        return False
    
    # بررسی فایل‌های صوتی
    if segments_dir.exists():
        audio_files = list(segments_dir.glob("dub_*.wav"))
        print(f"🎵 فایل‌های صوتی موجود: {len(audio_files)}")
        
        for i, audio_file in enumerate(sorted(audio_files)[:5]):  # نمایش 5 فایل اول
            file_size = audio_file.stat().st_size / 1024
            print(f"   {i+1}. {audio_file.name} - {file_size:.1f} KB")
        
        if len(audio_files) > 5:
            print(f"   ... و {len(audio_files) - 5} فایل دیگر")
    else:
        print(f"❌ پوشه سگمنت‌ها یافت نشد: {segments_dir}")
        return False
    
    # تست ایجاد ویدیو
    print("\n🎬 شروع تست ایجاد ویدیو...")
    try:
        # ایجاد instance (بدون API key برای تست)
        app = VideoDubbingApp("test_key")
        
        # تست ایجاد ویدیو
        output_path = app.create_final_video(keep_original_audio=False)
        
        if output_path and os.path.exists(output_path):
            file_size = os.path.getsize(output_path) / (1024 * 1024)
            print(f"✅ ویدیو نهایی با موفقیت ایجاد شد!")
            print(f"📁 مسیر: {output_path}")
            print(f"📊 حجم: {file_size:.2f} MB")
            return True
        else:
            print("❌ ویدیو نهایی ایجاد نشد")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_video_creation()
    sys.exit(0 if success else 1)
