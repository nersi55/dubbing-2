#!/usr/bin/env python3
"""
تست تنظیمات پیشرفته زیرنویس
Test advanced subtitle settings
"""

import subprocess
import os
from pathlib import Path

def test_advanced_subtitle():
    """تست تنظیمات پیشرفته زیرنویس"""
    print("🎨 تست تنظیمات پیشرفته زیرنویس")
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
    
    # تست تنظیمات مختلف
    test_configs = [
        {
            "name": "elegant",
            "config": {
                "font": "Georgia",
                "fontsize": 26,
                "color": "gold",
                "outline_color": "black",
                "outline_width": 1,
                "position": "bottom_center",
                "margin_v": 30,
                "shadow": 1,
                "shadow_color": "black",
                "bold": False,
                "italic": True
            }
        },
        {
            "name": "bold_red",
            "config": {
                "font": "Impact",
                "fontsize": 30,
                "color": "red",
                "outline_color": "white",
                "outline_width": 4,
                "position": "top_center",
                "margin_v": 20,
                "shadow": 0,
                "shadow_color": "black",
                "bold": True,
                "italic": False
            }
        },
        {
            "name": "colorful",
            "config": {
                "font": "Verdana",
                "fontsize": 24,
                "color": "blue",
                "outline_color": "green",
                "outline_width": 2,
                "position": "middle_center",
                "margin_v": 50,
                "shadow": 1,
                "shadow_color": "white",
                "bold": False,
                "italic": False
            }
        }
    ]
    
    for test in test_configs:
        print(f"\n🎨 تست: {test['name']}")
        print(f"   📝 فونت: {test['config']['font']} {test['config']['fontsize']}px")
        print(f"   🎨 رنگ: {test['config']['color']} با حاشیه {test['config']['outline_color']}")
        print(f"   📍 موقعیت: {test['config']['position']}")
        
        # ایجاد ویدیو
        output_file = work_dir / f"test_advanced_{test['name']}.mp4"
        
        try:
            # ایجاد فایل SRT موقت
            temp_srt = work_dir / f"temp_subtitles_{test['name']}.srt"
            with open(temp_srt, 'w', encoding='utf-8') as f:
                f.write(srt_file.read_text(encoding='utf-8'))
            
            # ساخت فیلتر زیرنویس
            style_parts = [
                f"FontName={test['config']['font']}",
                f"FontSize={test['config']['fontsize']}",
                f"PrimaryColour=&H{_color_to_hex(test['config']['color'])}",
                f"OutlineColour=&H{_color_to_hex(test['config']['outline_color'])}",
                f"Outline={test['config']['outline_width']}",
                f"MarginV={test['config']['margin_v']}",
                f"Shadow={test['config']['shadow']}",
                f"ShadowColour=&H{_color_to_hex(test['config']['shadow_color'])}",
                f"Bold={1 if test['config']['bold'] else 0}",
                f"Italic={1 if test['config']['italic'] else 0}",
                f"Alignment={_get_alignment(test['config']['position'])}"
            ]
            
            subtitle_filter = f"subtitles={temp_srt.absolute()}:force_style='{','.join(style_parts)}'"
            
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
                print(f"   ✅ ویدیو ایجاد شد: {file_size:.2f} MB")
                
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
    advanced_files = list(work_dir.glob("test_advanced_*.mp4"))
    for file_path in sorted(advanced_files):
        file_size = file_path.stat().st_size / (1024 * 1024)
        print(f"   📹 {file_path.name} - {file_size:.2f} MB")
    
    return len(advanced_files) > 0

def _color_to_hex(color_name: str) -> str:
    """تبدیل نام رنگ به فرمت hex برای FFmpeg"""
    color_map = {
        "white": "ffffff",
        "yellow": "ffff00",
        "red": "ff0000",
        "green": "00ff00",
        "blue": "0000ff",
        "black": "000000",
        "orange": "ffa500",
        "purple": "800080",
        "pink": "ffc0cb",
        "cyan": "00ffff",
        "lime": "00ff00",
        "magenta": "ff00ff",
        "silver": "c0c0c0",
        "gold": "ffd700"
    }
    return color_map.get(color_name.lower(), "ffffff")

def _get_alignment(position: str) -> int:
    """تبدیل موقعیت به کد alignment برای FFmpeg"""
    # FFmpeg subtitle alignment codes:
    # 1=bottom_left, 2=bottom_center, 3=bottom_right
    # 4=middle_left, 5=middle_center, 6=middle_right  
    # 7=top_left, 8=top_center, 9=top_right
    alignment_map = {
        "top_left": 7,
        "top_center": 8,
        "top_right": 9,
        "middle_left": 4,
        "middle_center": 5,
        "middle_right": 6,
        "bottom_left": 1,
        "bottom_center": 2,
        "bottom_right": 3,
        "top": 8,
        "bottom": 2,
        "center": 5,
        "left": 4,
        "right": 6
    }
    return alignment_map.get(position.lower(), 2)

if __name__ == "__main__":
    success = test_advanced_subtitle()
    if success:
        print("\n🎉 تست تنظیمات پیشرفته موفق بود!")
    else:
        print("\n❌ تست تنظیمات پیشرفته ناموفق بود.")
