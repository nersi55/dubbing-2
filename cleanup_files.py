#!/usr/bin/env python3
"""
پاکسازی فایل‌های اضافی
Cleanup unnecessary files
"""

import os
from pathlib import Path

def cleanup_files():
    """پاکسازی فایل‌های اضافی"""
    print("🧹 پاکسازی فایل‌های اضافی")
    print("=" * 50)
    
    work_dir = Path("dubbing_work")
    
    # فایل‌های موقت برای حذف
    temp_files = [
        "test_audio_list.txt",
        "test_combined_audio.wav",
        "timed_audio_list.txt",
        "timed_combined_audio.wav",
        "complete_audio_list.txt",
        "complete_combined_audio.wav",
        "complete_adjusted_audio.wav",
        "test_final_video.mp4",
        "fixed_dubbed_video.mp4",
        "timed_final_video.mp4"
    ]
    
    # حذف فایل‌های موقت
    removed_count = 0
    for file_name in temp_files:
        file_path = work_dir / file_name
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"🗑️ حذف شد: {file_name}")
                removed_count += 1
            except Exception as e:
                print(f"❌ خطا در حذف {file_name}: {e}")
    
    print(f"\n✅ {removed_count} فایل موقت حذف شد")
    
    # نمایش فایل‌های باقی‌مانده
    print("\n📁 فایل‌های باقی‌مانده:")
    remaining_files = list(work_dir.glob("*.mp4"))
    for file_path in sorted(remaining_files):
        file_size = file_path.stat().st_size / (1024 * 1024)
        print(f"   📹 {file_path.name} - {file_size:.2f} MB")
    
    # نمایش فایل‌های صوتی
    segments_dir = work_dir / "dubbed_segments"
    if segments_dir.exists():
        audio_files = list(segments_dir.glob("*.wav"))
        print(f"\n🎵 فایل‌های صوتی ({len(audio_files)} فایل):")
        for file_path in sorted(audio_files):
            file_size = file_path.stat().st_size / 1024
            print(f"   🎵 {file_path.name} - {file_size:.1f} KB")

if __name__ == "__main__":
    cleanup_files()
    print("\n🎉 پاکسازی کامل شد!")
