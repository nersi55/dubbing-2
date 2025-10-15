#!/usr/bin/env python3
"""
تست نهایی ایجاد ویدیو
Final test for video creation
"""

import subprocess
import os
from pathlib import Path

def test_final_video():
    """تست نهایی ایجاد ویدیو"""
    print("🎬 تست نهایی ایجاد ویدیو")
    print("=" * 50)
    
    work_dir = Path("dubbing_work")
    
    # بررسی فایل‌های موجود
    video_file = work_dir / "input_video.mp4"
    srt_file = work_dir / "audio_fa.srt"
    segments_dir = work_dir / "dubbed_segments"
    
    if not video_file.exists():
        print("❌ فایل ویدیو یافت نشد")
        return False
    
    if not srt_file.exists():
        print("❌ فایل زیرنویس یافت نشد")
        return False
    
    if not segments_dir.exists():
        print("❌ پوشه سگمنت‌ها یافت نشد")
        return False
    
    audio_files = list(segments_dir.glob("dub_*.wav"))
    if not audio_files:
        print("❌ هیچ فایل صوتی یافت نشد")
        return False
    
    print(f"✅ فایل‌های مورد نیاز موجود هستند")
    print(f"🎵 تعداد فایل‌های صوتی: {len(audio_files)}")
    
    # ایجاد ویدیو نهایی
    output_file = work_dir / "test_final_video.mp4"
    
    # ایجاد فایل لیست صوتی
    audio_list_file = work_dir / "test_audio_list.txt"
    with open(audio_list_file, 'w') as f:
        for audio_file in sorted(audio_files):
            f.write(f"file '{audio_file.absolute()}'\n")
    
    print("📝 فایل لیست صوتی ایجاد شد")
    
    # ترکیب فایل‌های صوتی
    combined_audio = work_dir / "test_combined_audio.wav"
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
    
    # ایجاد ویدیو نهایی
    print("🎬 ایجاد ویدیو نهایی...")
    
    try:
        subprocess.run([
            'ffmpeg', '-i', str(video_file), '-i', str(combined_audio),
            '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v', '-map', '1:a',
            '-shortest', '-y', str(output_file)
        ], check=True, capture_output=True)
        
        print(f"✅ ویدیو نهایی ایجاد شد: {output_file}")
        
        # بررسی نتیجه
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams',
            str(output_file)
        ], capture_output=True, text=True)
        
        import json
        info = json.loads(result.stdout)
        streams = info['streams']
        
        video_streams = [s for s in streams if s['codec_type'] == 'video']
        audio_streams = [s for s in streams if s['codec_type'] == 'audio']
        
        print(f"📹 تعداد stream های ویدیو: {len(video_streams)}")
        print(f"🎵 تعداد stream های صوتی: {len(audio_streams)}")
        
        if video_streams and audio_streams:
            print("✅ ویدیو دارای هم ویدیو و هم صدا است!")
            
            # نمایش اطلاعات فایل
            file_size = output_file.stat().st_size / (1024 * 1024)
            duration = float(info.get('format', {}).get('duration', 0))
            print(f"📊 حجم فایل: {file_size:.2f} MB")
            print(f"⏱️ مدت زمان: {duration:.2f} ثانیه")
            
            return True
        else:
            print("❌ ویدیو کامل نیست")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ خطا در ایجاد ویدیو: {e}")
        return False

if __name__ == "__main__":
    success = test_final_video()
    if success:
        print("\n🎉 تست موفق بود! ویدیو با صدا ایجاد شد.")
    else:
        print("\n❌ تست ناموفق بود.")
