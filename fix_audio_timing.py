#!/usr/bin/env python3
"""
برطرف کردن مشکل زمان‌بندی صدا
Fix audio timing issue
"""

import subprocess
import os
from pathlib import Path

def fix_audio_timing():
    """برطرف کردن مشکل زمان‌بندی صدا"""
    print("🔧 برطرف کردن مشکل زمان‌بندی صدا")
    print("=" * 50)
    
    work_dir = Path("dubbing_work")
    video_path = work_dir / "input_video.mp4"
    
    if not video_path.exists():
        print("❌ فایل ویدیو یافت نشد")
        return False
    
    # دریافت مدت زمان ویدیو
    result = subprocess.run([
        'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format',
        str(video_path)
    ], capture_output=True, text=True)
    
    import json
    video_info = json.loads(result.stdout)
    video_duration = float(video_info['format']['duration'])
    print(f"⏱️ مدت ویدیو: {video_duration:.2f} ثانیه")
    
    # بررسی فایل‌های صوتی موجود
    segments_dir = work_dir / "dubbed_segments"
    audio_files = list(segments_dir.glob("dub_*.wav"))
    
    if not audio_files:
        print("❌ هیچ فایل صوتی یافت نشد")
        return False
    
    print(f"🎵 تعداد فایل‌های صوتی: {len(audio_files)}")
    
    # ایجاد فایل لیست صوتی
    audio_list_file = work_dir / "timed_audio_list.txt"
    with open(audio_list_file, 'w') as f:
        for audio_file in sorted(audio_files):
            f.write(f"file '{audio_file.absolute()}'\n")
    
    # ترکیب فایل‌های صوتی
    combined_audio = work_dir / "timed_combined_audio.wav"
    print("🎵 ترکیب فایل‌های صوتی...")
    
    try:
        subprocess.run([
            'ffmpeg', '-f', 'concat', '-safe', '0', '-i', str(audio_list_file),
            '-c', 'copy', '-y', str(combined_audio)
        ], check=True, capture_output=True)
        print("✅ فایل‌های صوتی ترکیب شدند")
    except subprocess.CalledProcessError as e:
        print(f"❌ خطا در ترکیب صدا: {e}")
        return False
    
    # دریافت مدت زمان صدا
    result = subprocess.run([
        'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format',
        str(combined_audio)
    ], capture_output=True, text=True)
    
    audio_info = json.loads(result.stdout)
    audio_duration = float(audio_info['format']['duration'])
    print(f"🎵 مدت صدا: {audio_duration:.2f} ثانیه")
    
    # محاسبه ضریب سرعت
    speed_factor = audio_duration / video_duration
    print(f"⚡ ضریب سرعت مورد نیاز: {speed_factor:.2f}x")
    
    # تنظیم سرعت صدا برای تطبیق با ویدیو
    adjusted_audio = work_dir / "adjusted_audio.wav"
    print("🎛️ تنظیم سرعت صدا...")
    
    try:
        subprocess.run([
            'ffmpeg', '-i', str(combined_audio),
            '-filter:a', f'rubberband=tempo={speed_factor}',
            '-y', str(adjusted_audio)
        ], check=True, capture_output=True)
        print("✅ سرعت صدا تنظیم شد")
    except subprocess.CalledProcessError as e:
        print(f"❌ خطا در تنظیم سرعت: {e}")
        return False
    
    # بررسی مدت زمان صدا بعد از تنظیم
    result = subprocess.run([
        'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format',
        str(adjusted_audio)
    ], capture_output=True, text=True)
    
    adjusted_info = json.loads(result.stdout)
    adjusted_duration = float(adjusted_info['format']['duration'])
    print(f"🎵 مدت صدا بعد از تنظیم: {adjusted_duration:.2f} ثانیه")
    
    # ایجاد ویدیو نهایی
    output_file = work_dir / "timed_final_video.mp4"
    print("🎬 ایجاد ویدیو نهایی با زمان‌بندی صحیح...")
    
    try:
        subprocess.run([
            'ffmpeg', '-i', str(video_path), '-i', str(adjusted_audio),
            '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v', '-map', '1:a',
            '-shortest', '-y', str(output_file)
        ], check=True, capture_output=True)
        
        print(f"✅ ویدیو نهایی ایجاد شد: {output_file}")
        
        # بررسی نتیجه نهایی
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams',
            str(output_file)
        ], capture_output=True, text=True)
        
        final_info = json.loads(result.stdout)
        streams = final_info['streams']
        
        video_streams = [s for s in streams if s['codec_type'] == 'video']
        audio_streams = [s for s in streams if s['codec_type'] == 'audio']
        
        print(f"📹 تعداد stream های ویدیو: {len(video_streams)}")
        print(f"🎵 تعداد stream های صوتی: {len(audio_streams)}")
        
        if video_streams and audio_streams:
            print("✅ ویدیو دارای هم ویدیو و هم صدا است!")
            
            # نمایش اطلاعات فایل نهایی
            file_size = output_file.stat().st_size / (1024 * 1024)
            final_duration = float(final_info.get('format', {}).get('duration', 0))
            print(f"📊 حجم فایل: {file_size:.2f} MB")
            print(f"⏱️ مدت زمان نهایی: {final_duration:.2f} ثانیه")
            
            return True
        else:
            print("❌ ویدیو کامل نیست")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ خطا در ایجاد ویدیو: {e}")
        return False

if __name__ == "__main__":
    success = fix_audio_timing()
    if success:
        print("\n🎉 مشکل زمان‌بندی برطرف شد!")
    else:
        print("\n❌ مشکل برطرف نشد.")
