#!/usr/bin/env python3
"""
تست ویژگی زیرنویس
Test subtitle feature
"""

import subprocess
import os
from pathlib import Path

def test_subtitle_feature():
    """تست ویژگی زیرنویس"""
    print("📝 تست ویژگی زیرنویس")
    print("=" * 50)
    
    work_dir = Path("dubbing_work")
    
    # بررسی فایل‌های مورد نیاز
    video_file = work_dir / "input_video.mp4"
    srt_file = work_dir / "audio_fa.srt"
    
    if not video_file.exists():
        print("❌ فایل ویدیو یافت نشد")
        return False
    
    if not srt_file.exists():
        print("❌ فایل زیرنویس یافت نشد")
        return False
    
    print("✅ فایل‌های مورد نیاز موجود هستند")
    
    # تست استایل‌های مختلف
    styles = ["default", "modern", "minimal"]
    
    for style in styles:
        print(f"\n🎨 تست استایل: {style}")
        
        # ایجاد ویدیو با زیرنویس
        output_file = work_dir / f"test_subtitled_{style}.mp4"
        
        try:
            # ایجاد فایل SRT موقت
            temp_srt = work_dir / f"temp_subtitles_{style}.srt"
            with open(temp_srt, 'w', encoding='utf-8') as f:
                f.write(srt_file.read_text(encoding='utf-8'))
            
            # تنظیمات زیرنویس
            subtitle_styles = {
                "default": {
                    "font": "Arial",
                    "fontsize": 24,
                    "color": "white",
                    "outline": "black",
                    "outline_width": 2
                },
                "modern": {
                    "font": "Arial",
                    "fontsize": 28,
                    "color": "yellow",
                    "outline": "black",
                    "outline_width": 3
                },
                "minimal": {
                    "font": "Arial",
                    "fontsize": 20,
                    "color": "white",
                    "outline": "black",
                    "outline_width": 1
                }
            }
            
            style_config = subtitle_styles[style]
            
            # فیلتر زیرنویس
            subtitle_filter = f"subtitles={temp_srt.absolute()}:force_style='FontName={style_config['font']},FontSize={style_config['fontsize']},PrimaryColour=&H{_color_to_hex(style_config['color'])},OutlineColour=&H{_color_to_hex(style_config['outline'])},Outline={style_config['outline_width']},Alignment=2'"
            
            # ایجاد ویدیو
            subprocess.run([
                'ffmpeg', '-i', str(video_file),
                '-vf', subtitle_filter,
                '-c:v', 'libx264', '-c:a', 'copy',
                '-y', str(output_file)
            ], check=True, capture_output=True)
            
            # بررسی نتیجه
            if output_file.exists():
                file_size = output_file.stat().st_size / (1024 * 1024)
                print(f"   ✅ ویدیو با زیرنویس ایجاد شد: {file_size:.2f} MB")
                
                # بررسی streams
                result = subprocess.run([
                    'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams',
                    str(output_file)
                ], capture_output=True, text=True)
                
                import json
                info = json.loads(result.stdout)
                streams = info['streams']
                
                video_streams = [s for s in streams if s['codec_type'] == 'video']
                audio_streams = [s for s in streams if s['codec_type'] == 'audio']
                
                print(f"   📹 Stream های ویدیو: {len(video_streams)}")
                print(f"   🎵 Stream های صوتی: {len(audio_streams)}")
                
                if video_streams and audio_streams:
                    print(f"   ✅ ویدیو کامل است")
                else:
                    print(f"   ❌ ویدیو ناقص است")
            else:
                print(f"   ❌ ویدیو ایجاد نشد")
                
        except subprocess.CalledProcessError as e:
            print(f"   ❌ خطا در ایجاد ویدیو: {e}")
        except Exception as e:
            print(f"   ❌ خطا: {e}")
        finally:
            # حذف فایل موقت
            if temp_srt.exists():
                temp_srt.unlink()
    
    print(f"\n📁 فایل‌های ایجاد شده:")
    subtitle_files = list(work_dir.glob("test_subtitled_*.mp4"))
    for file_path in sorted(subtitle_files):
        file_size = file_path.stat().st_size / (1024 * 1024)
        print(f"   📹 {file_path.name} - {file_size:.2f} MB")
    
    return len(subtitle_files) > 0

def _color_to_hex(color_name: str) -> str:
    """تبدیل نام رنگ به فرمت hex برای FFmpeg"""
    color_map = {
        "white": "ffffff",
        "yellow": "ffff00",
        "red": "ff0000",
        "green": "00ff00",
        "blue": "0000ff",
        "black": "000000"
    }
    return color_map.get(color_name.lower(), "ffffff")

if __name__ == "__main__":
    success = test_subtitle_feature()
    if success:
        print("\n🎉 تست زیرنویس موفق بود!")
    else:
        print("\n❌ تست زیرنویس ناموفق بود.")
