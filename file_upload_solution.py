#!/usr/bin/env python3
"""
راه‌حل آپلود فایل ویدیو - جایگزین دانلود از YouTube
File Upload Solution - Alternative to YouTube Download
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path
from typing import Optional

class FileUploadSolution:
    def __init__(self, work_dir: Path):
        self.work_dir = work_dir
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv']
        
    def process_uploaded_file(self, file_path: str) -> bool:
        """پردازش فایل آپلود شده"""
        try:
            print(f"📁 پردازش فایل آپلود شده: {file_path}")
            
            # بررسی وجود فایل
            if not os.path.exists(file_path):
                print("❌ فایل یافت نشد")
                return False
            
            # بررسی فرمت فایل
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in self.supported_formats:
                print(f"❌ فرمت فایل پشتیبانی نمی‌شود: {file_ext}")
                print(f"✅ فرمت‌های پشتیبانی شده: {', '.join(self.supported_formats)}")
                return False
            
            # کپی فایل به پوشه کار
            input_video_path = self.work_dir / 'input_video.mp4'
            
            if file_ext == '.mp4':
                # اگر MP4 است، مستقیماً کپی کن
                shutil.copy2(file_path, str(input_video_path))
                print("✅ فایل MP4 کپی شد")
            else:
                # تبدیل به MP4
                print(f"🔄 تبدیل {file_ext} به MP4...")
                success = self._convert_to_mp4(file_path, str(input_video_path))
                if not success:
                    return False
            
            # استخراج صدا
            print("🎵 استخراج صدا...")
            audio_path = self.work_dir / 'audio.wav'
            success = self._extract_audio(str(input_video_path), str(audio_path))
            if not success:
                return False
            
            print("✅ فایل با موفقیت پردازش شد")
            return True
            
        except Exception as e:
            print(f"❌ خطا در پردازش فایل: {str(e)}")
            return False
    
    def _convert_to_mp4(self, input_path: str, output_path: str) -> bool:
        """تبدیل فایل به MP4"""
        try:
            import subprocess
            
            cmd = [
                'ffmpeg', '-i', input_path,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'fast',
                '-crf', '23',
                '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ تبدیل به MP4 موفق بود")
                return True
            else:
                print(f"❌ خطا در تبدیل: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ خطا در تبدیل: {str(e)}")
            return False
    
    def _extract_audio(self, video_path: str, audio_path: str) -> bool:
        """استخراج صدا از ویدیو"""
        try:
            import subprocess
            
            cmd = [
                'ffmpeg', '-i', video_path,
                '-vn', '-acodec', 'pcm_s16le',
                '-ar', '44100', '-ac', '2',
                '-y', audio_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ استخراج صدا موفق بود")
                return True
            else:
                print(f"❌ خطا در استخراج صدا: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ خطا در استخراج صدا: {str(e)}")
            return False
    
    def create_upload_instructions(self):
        """ایجاد دستورالعمل‌های آپلود"""
        instructions = """
# راهنمای آپلود فایل ویدیو

## مشکل
YouTube دسترسی از سرور را مسدود کرده است.

## راه‌حل: آپلود فایل ویدیو

### مرحله 1: دانلود ویدیو روی کامپیوتر شخصی
1. ویدیو را از YouTube دانلود کنید (روی کامپیوتر شخصی)
2. از نرم‌افزارهای دانلود استفاده کنید:
   - yt-dlp (روی کامپیوتر شخصی)
   - 4K Video Downloader
   - JDownloader
   - یا هر نرم‌افزار دانلود دیگر

### مرحله 2: آپلود فایل به سرور
1. فایل ویدیو را به سرور آپلود کنید
2. از طریق SCP, SFTP, یا رابط وب
3. فایل را در پوشه پروژه قرار دهید

### مرحله 3: استفاده از برنامه
```python
from file_upload_solution import FileUploadSolution
from pathlib import Path

# ایجاد instance
work_dir = Path("dubbing_work")
uploader = FileUploadSolution(work_dir)

# پردازش فایل
success = uploader.process_uploaded_file("your_video.mp4")
```

## فرمت‌های پشتیبانی شده
- MP4 (پیشنهادی)
- AVI
- MOV
- MKV
- WEBM
- FLV
- WMV

## نکات مهم
1. فایل‌های MP4 مستقیماً پردازش می‌شوند
2. سایر فرمت‌ها به MP4 تبدیل می‌شوند
3. کیفیت ویدیو حفظ می‌شود
4. صدا به فرمت WAV استخراج می‌شود
"""
        
        with open('UPLOAD_INSTRUCTIONS.md', 'w', encoding='utf-8') as f:
            f.write(instructions)
        
        print("📝 دستورالعمل‌های آپلود ایجاد شد: UPLOAD_INSTRUCTIONS.md")

def main():
    """تابع اصلی"""
    print("📁 راه‌حل آپلود فایل ویدیو")
    print("=" * 40)
    
    # ایجاد پوشه کار
    work_dir = Path("dubbing_work")
    work_dir.mkdir(exist_ok=True)
    
    # ایجاد راه‌حل آپلود
    uploader = FileUploadSolution(work_dir)
    
    # ایجاد دستورالعمل‌ها
    uploader.create_upload_instructions()
    
    print("\n💡 راه‌حل‌های پیشنهادی:")
    print("1. فایل ویدیو را روی کامپیوتر شخصی دانلود کنید")
    print("2. فایل را به سرور آپلود کنید")
    print("3. از این راه‌حل استفاده کنید")
    print("\n📖 راهنمای کامل: UPLOAD_INSTRUCTIONS.md")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
