#!/usr/bin/env python3
"""
اسکریپت برطرف کردن مشکل صدا در ویدیو
Script to fix audio issue in video
"""

import subprocess
import os
from pathlib import Path

def fix_video_audio():
    """برطرف کردن مشکل صدا در ویدیو"""
    print("🔧 برطرف کردن مشکل صدا در ویدیو")
    print("=" * 50)
    
    work_dir = Path("dubbing_work")
    video_path = work_dir / "input_video.mp4"
    output_path = work_dir / "fixed_dubbed_video.mp4"
    
    if not video_path.exists():
        print("❌ فایل ویدیو یافت نشد")
        return False
    
    # بررسی فایل‌های صوتی
    segments_dir = work_dir / "dubbed_segments"
    audio_files = list(segments_dir.glob("dub_*.wav"))
    print(f"🎵 فایل‌های صوتی موجود: {len(audio_files)}")
    
    if not audio_files:
        print("❌ هیچ فایل صوتی یافت نشد")
        return False
    
    # ایجاد فایل لیست برای concat
    concat_file = work_dir / "audio_list.txt"
    with open(concat_file, 'w') as f:
        for audio_file in sorted(audio_files):
            f.write(f"file '{audio_file.absolute()}'\n")
    
    print("📝 فایل لیست صوتی ایجاد شد")
    
    # ترکیب فایل‌های صوتی
    combined_audio = work_dir / "combined_audio.wav"
    print("🎵 ترکیب فایل‌های صوتی...")
    
    try:
        subprocess.run([
            'ffmpeg', '-f', 'concat', '-safe', '0', '-i', str(concat_file),
            '-c', 'copy', '-y', str(combined_audio)
        ], check=True, capture_output=True)
        print("✅ فایل‌های صوتی ترکیب شدند")
    except subprocess.CalledProcessError as e:
        print(f"❌ خطا در ترکیب صدا: {e}")
        return False
    
    # ایجاد ویدیو نهایی با صدا
    print("🎬 ایجاد ویدیو نهایی...")
    
    try:
        subprocess.run([
            'ffmpeg', '-i', str(video_path), '-i', str(combined_audio),
            '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v', '-map', '1:a',
            '-shortest', '-y', str(output_path)
        ], check=True, capture_output=True)
        
        print(f"✅ ویدیو نهایی ایجاد شد: {output_path}")
        
        # بررسی نتیجه
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams',
            str(output_path)
        ], capture_output=True, text=True)
        
        import json
        info = json.loads(result.stdout)
        audio_streams = [s for s in info['streams'] if s['codec_type'] == 'audio']
        
        if audio_streams:
            print(f"🎵 تعداد stream های صوتی: {len(audio_streams)}")
            print("✅ ویدیو دارای صدا است!")
            return True
        else:
            print("❌ ویدیو هنوز صدا ندارد")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ خطا در ایجاد ویدیو: {e}")
        return False

if __name__ == "__main__":
    success = fix_video_audio()
    if success:
        print("\n🎉 مشکل برطرف شد!")
    else:
        print("\n❌ مشکل برطرف نشد")
