"""
دوبله خودکار ویدیو - توابع اصلی
Auto Video Dubbing - Core Functions
"""

import os
import re
import time
import base64
import struct
import tempfile
import subprocess
import traceback
from pathlib import Path
from typing import Optional, List, Dict, Any

import yt_dlp
import pysrt
import google.generativeai as genai
from google.genai import types
import google.genai as genai_client
try:
    from pydub import AudioSegment
except ImportError:
    # Fallback for Python 3.13 compatibility
    import subprocess
    import tempfile
    import os
    
    class AudioSegment:
        @staticmethod
        def from_file(file_path):
            # Simple fallback implementation
            return SimpleAudioSegment(file_path)
        
        @staticmethod
        def silent(duration):
            return SimpleAudioSegment(None, duration=duration)
    
    class SimpleAudioSegment:
        def __init__(self, file_path=None, duration=None):
            self.file_path = file_path
            self.duration = duration or 0
        
        def __len__(self):
            return int(self.duration * 1000)  # Convert to milliseconds
        
        def __add__(self, other):
            if isinstance(other, (int, float)):
                # Volume adjustment
                return self
            return self
        
        def overlay(self, other, position=0):
            return self
        
        def export(self, output_path, format="wav"):
            if self.file_path and os.path.exists(self.file_path):
                # Copy file
                subprocess.run(['cp', self.file_path, output_path], check=True)
            else:
                # Create silent audio with proper duration
                duration_seconds = max(self.duration, 0.1)  # حداقل 0.1 ثانیه
                subprocess.run([
                    'ffmpeg', '-f', 'lavfi', '-i', f'anullsrc=duration={duration_seconds}',
                    '-ac', '2', '-ar', '44100', '-y', str(output_path)
                ], check=True, capture_output=True)
from youtube_transcript_api import YouTubeTranscriptApi
import whisper


class VideoDubbingApp:
    def __init__(self, api_key: str):
        """Initialize the dubbing application with Google API key"""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.client = genai_client.Client(api_key=api_key)
        
        # Create necessary directories
        self.work_dir = Path("dubbing_work")
        self.work_dir.mkdir(exist_ok=True)
        self.segments_dir = self.work_dir / "dubbed_segments"
        self.segments_dir.mkdir(exist_ok=True)
        
    def clean_previous_files(self):
        """پاکسازی فایل‌های قبلی"""
        files_to_clean = [
            "input_video.mp4", "audio.wav", "audio.srt", 
            "audio_fa.srt", "final_dubbed_video.mp4"
        ]
        
        for file_name in files_to_clean:
            file_path = self.work_dir / file_name
            if file_path.exists():
                file_path.unlink()
                
        # Clean segments directory
        if self.segments_dir.exists():
            for file in self.segments_dir.glob("*"):
                file.unlink()
    
    def download_youtube_video(self, url: str) -> bool:
        """دانلود ویدیو از یوتیوب - نسخه بهینه شده برای سرور لینوکس"""
        try:
            # Clean previous files
            for file in self.work_dir.glob('temp_video*'):
                file.unlink()
            
            format_option = 'bestvideo+bestaudio/best'
            temp_filename = str(self.work_dir / 'temp_video.%(ext)s')
            
            # تنظیمات پایه
            video_opts = {
                'format': format_option,
                'outtmpl': temp_filename,
                'nocheckcertificate': True,
                'ignoreerrors': False,
                'no_warnings': False,
                'quiet': False,
                # تنظیمات مخصوص سرور لینوکس
                'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'referer': 'https://www.youtube.com/',
                'headers': {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Charset': 'UTF-8,*;q=0.7',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0',
                },
                'socket_timeout': 30,
                'retries': 3,
                'fragment_retries': 3,
                'extractor_retries': 3,
                'http_chunk_size': 10485760,  # 10MB chunks
            }
            
            # بررسی وجود فایل کوکی (اختیاری)
            cookies_files = ['cookies.txt', 'cookies.text', 'cookies.json']
            cookies_path = None
            
            for cookie_file in cookies_files:
                if os.path.exists(cookie_file):
                    cookies_path = cookie_file
                    break
            
            # بررسی کوکی‌ها و تست اعتبار آن‌ها
            if cookies_path:
                # تست کوکی‌ها قبل از استفاده
                if self._test_cookies_validity(cookies_path):
                    if cookies_path.endswith('.txt') or cookies_path.endswith('.text'):
                        video_opts['cookiefile'] = cookies_path
                    elif cookies_path.endswith('.json'):
                        video_opts['cookiefile'] = cookies_path
                    print(f"🍪 استفاده از فایل کوکی معتبر: {cookies_path}")
                else:
                    print("⚠️ کوکی‌ها منقضی شده‌اند، استفاده بدون کوکی")
            else:
                print("🌐 استفاده از تنظیمات سرور لینوکس (بدون کوکی)")
            
            with yt_dlp.YoutubeDL(video_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
            
            if os.path.exists(downloaded_file):
                _, file_extension = os.path.splitext(downloaded_file)
                final_filename = self.work_dir / f'input_video{file_extension}'
                os.rename(downloaded_file, str(final_filename))
                
                if file_extension.lower() != '.mp4':
                    mp4_path = self.work_dir / 'input_video.mp4'
                    subprocess.run([
                        'ffmpeg', '-i', str(final_filename), 
                        '-c', 'copy', str(mp4_path), '-y'
                    ], check=True, capture_output=True)
                    final_filename.unlink()
                
                # Extract audio
                audio_path = self.work_dir / 'audio.wav'
                subprocess.run([
                    'ffmpeg', '-i', str(self.work_dir / 'input_video.mp4'), 
                    '-vn', str(audio_path), '-y'
                ], check=True, capture_output=True)
                
                return True
            return False
            
        except Exception as e:
            print(f"خطا در دانلود: {str(e)}")
            # تلاش با تنظیمات جایگزین
            return self._fallback_download(url)
    
    def _fallback_download(self, url: str) -> bool:
        """دانلود با تنظیمات جایگزین در صورت شکست"""
        try:
            print("🔄 تلاش با تنظیمات جایگزین (بدون کوکی)...")
            
            format_option = 'worst[height<=480]/worst'
            temp_filename = str(self.work_dir / 'temp_video.%(ext)s')
            
            # تنظیمات بدون کوکی و با User-Agent های مختلف
            fallback_configs = [
                {
                    'name': 'Googlebot',
                    'user_agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                    'format': 'worst[height<=360]/worst'
                },
                {
                    'name': 'Chrome Linux',
                    'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'format': 'worst[height<=480]/worst'
                },
                {
                    'name': 'Firefox Linux',
                    'user_agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0',
                    'format': 'worst'
                }
            ]
            
            for config in fallback_configs:
                try:
                    print(f"   🧪 تست {config['name']}...")
                    
                    video_opts = {
                        'format': config['format'],
                        'outtmpl': temp_filename,
                        'nocheckcertificate': True,
                        'ignoreerrors': True,
                        'no_warnings': True,
                        'quiet': True,
                        'user_agent': config['user_agent'],
                        'referer': 'https://www.youtube.com/',
                        'socket_timeout': 30,
                        'retries': 1,
                        'fragment_retries': 1,
                        'extractor_retries': 1,
                        'http_chunk_size': 1048576,  # 1MB chunks
                    }
                    
                    with yt_dlp.YoutubeDL(video_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        if info is None:
                            print(f"   ❌ {config['name']} شکست خورد")
                            continue
                        downloaded_file = ydl.prepare_filename(info)
                    
                    if os.path.exists(downloaded_file):
                        _, file_extension = os.path.splitext(downloaded_file)
                        final_filename = self.work_dir / f'input_video{file_extension}'
                        os.rename(downloaded_file, str(final_filename))
                        
                        if file_extension.lower() != '.mp4':
                            mp4_path = self.work_dir / 'input_video.mp4'
                            subprocess.run([
                                'ffmpeg', '-i', str(final_filename), 
                                '-c', 'copy', str(mp4_path), '-y'
                            ], check=True, capture_output=True)
                            final_filename.unlink()
                        
                        # Extract audio
                        audio_path = self.work_dir / 'audio.wav'
                        subprocess.run([
                            'ffmpeg', '-i', str(self.work_dir / 'input_video.mp4'), 
                            '-vn', str(audio_path), '-y'
                        ], check=True, capture_output=True)
                        
                        print(f"✅ دانلود با {config['name']} موفق بود")
                        return True
                    else:
                        print(f"   ❌ {config['name']} فایل دانلود نشد")
                        
                except Exception as e:
                    print(f"   ❌ خطا در {config['name']}: {str(e)[:100]}...")
                    continue
            
            print("❌ همه روش‌های جایگزین شکست خوردند")
            return False
            
        except Exception as e:
            print(f"❌ خطا در دانلود جایگزین: {str(e)}")
            return False
    
    def _test_cookies_validity(self, cookies_path: str) -> bool:
        """تست اعتبار کوکی‌ها"""
        try:
            print("🔍 بررسی اعتبار کوکی‌ها...")
            
            # تست ساده با یک URL کوتاه
            test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            
            test_opts = {
                'quiet': True,
                'no_warnings': True,
                'cookiefile': cookies_path,
                'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
                'referer': 'https://www.youtube.com/',
                'socket_timeout': 10,
                'retries': 1,
            }
            
            with yt_dlp.YoutubeDL(test_opts) as ydl:
                info = ydl.extract_info(test_url, download=False)
                if info and 'title' in info:
                    print("✅ کوکی‌ها معتبر هستند")
                    return True
                else:
                    print("❌ کوکی‌ها منقضی شده‌اند")
                    return False
                    
        except Exception as e:
            print(f"❌ خطا در تست کوکی‌ها: {str(e)[:100]}...")
            return False
    
    def extract_transcript_from_youtube(self, url: str, language: str = "Auto-detect") -> bool:
        """استخراج زیرنویس از یوتیوب"""
        try:
            # Extract video ID
            video_id = None
            patterns = [
                r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})',
                r'(?:youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    video_id = match.group(1)
                    break
            
            if not video_id:
                if 'shorts/' in url:
                    shorts_id = url.split('shorts/')[1].split('?')[0].split('&')[0]
                    if len(shorts_id) == 11:
                        video_id = shorts_id
                elif 'youtu.be/' in url:
                    video_id = url.split('youtu.be/')[1].split('?')[0].split('&')[0]
                elif 'v=' in url:
                    video_id = url.split('v=')[1].split('&')[0].split('?')[0]
            
            if not video_id or len(video_id) != 11:
                return False
            
            # Language mapping
            language_map = {
                "Auto-detect": None,
                "English (EN)": "en",
                "Persian (FA)": "fa",
                "German (DE)": "de",
                "French (FR)": "fr",
                "Italian (IT)": "it",
                "Spanish (ES)": "es",
                "Chinese (ZH)": "zh",
                "Korean (KO)": "ko",
                "Russian (RU)": "ru",
                "Arabic (AR)": "ar",
                "Japanese (JA)": "ja",
                "Hindi (HI)": "hi"
            }
            selected_language = language_map.get(language)
            
            # Get transcript
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            if selected_language:
                transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=[selected_language])
            else:
                # Auto-detect
                transcript_data = None
                for transcript in transcript_list:
                    if transcript.is_generated:
                        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=[transcript.language_code])
                        break
                    elif not transcript.is_translatable:
                        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=[transcript.language_code])
                        break
                
                if not transcript_data:
                    for transcript in transcript_list:
                        if transcript.is_translatable:
                            transcript_data = transcript.translate('en').fetch()
                            break
            
            if transcript_data:
                # Get video duration
                result = subprocess.run([
                    'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1',
                    str(self.work_dir / 'input_video.mp4')
                ], capture_output=True, text=True)
                
                video_duration = float(result.stdout.strip())
                
                # Process transcript data
                processed_data = []
                for entry in transcript_data:
                    processed_data.append({
                        'start': entry['start'],
                        'duration': entry.get('duration', 0),
                        'text': entry['text']
                    })
                
                # Sort by start time
                processed_data.sort(key=lambda x: x['start'])
                
                # Clean overlapping subtitles
                cleaned_data = []
                if processed_data:
                    cleaned_data.append(processed_data[0])
                    for i in range(1, len(processed_data)):
                        current = processed_data[i]
                        previous = cleaned_data[-1]
                        prev_end = previous['start'] + previous['duration']
                        
                        if current['start'] < prev_end:
                            if current['start'] + current['duration'] <= prev_end:
                                previous['text'] += " " + current['text']
                            else:
                                overlap = prev_end - current['start']
                                new_duration = current['duration'] - overlap
                                
                                if new_duration > 0.3:
                                    current['start'] = prev_end
                                    current['duration'] = new_duration
                                    cleaned_data.append(current)
                                else:
                                    previous['text'] += " " + current['text']
                                    previous['duration'] = max(previous['duration'],
                                                             (current['start'] + current['duration']) - previous['start'])
                        else:
                            cleaned_data.append(current)
                
                # Convert to SRT format
                srt_content = []
                for i, entry in enumerate(cleaned_data):
                    start_time = entry['start']
                    duration = entry['duration']
                    end_time = start_time + duration
                    
                    start_str = '{:02d}:{:02d}:{:02d},{:03d}'.format(
                        int(start_time // 3600),
                        int((start_time % 3600) // 60),
                        int(start_time % 60),
                        int((start_time % 1) * 1000)
                    )
                    end_str = '{:02d}:{:02d}:{:02d},{:03d}'.format(
                        int(end_time // 3600),
                        int((end_time % 3600) // 60),
                        int(end_time % 60),
                        int((end_time % 1) * 1000)
                    )
                    srt_content.append(f"{i+1}\n{start_str} --> {end_str}\n{entry['text']}\n")
                
                # Save SRT file
                srt_path = self.work_dir / 'audio.srt'
                with open(srt_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(srt_content))
                
                return True
            
            return False
            
        except Exception as e:
            print(f"خطا در استخراج زیرنویس: {str(e)}")
            return False
    
    def extract_audio_with_whisper(self) -> bool:
        """استخراج متن از صدا با Whisper"""
        try:
            audio_path = self.work_dir / 'audio.wav'
            if not audio_path.exists():
                print("❌ فایل صوتی یافت نشد")
                return False
            
            print("🔄 در حال بارگذاری مدل Whisper...")
            model = whisper.load_model("base")
            
            print("🔄 در حال تشخیص گفتار...")
            result = model.transcribe(str(audio_path), language="en")
            
            # بررسی کیفیت تشخیص
            if not result or not result.get("segments"):
                print("❌ هیچ گفتاری تشخیص داده نشد")
                return False
            
            # بررسی کیفیت متن تشخیص داده شده
            all_text = " ".join([seg['text'] for seg in result["segments"]])
            if len(all_text.strip()) < 10:
                print("❌ متن تشخیص داده شده خیلی کوتاه است")
                return False
            
            # بررسی اینکه آیا متن قابل فهم است
            english_words = all_text.split()
            if len(english_words) < 5:
                print("❌ متن تشخیص داده شده کافی نیست")
                return False
            
            print(f"✅ {len(result['segments'])} بخش گفتار تشخیص داده شد")
            print(f"📝 متن نمونه: {all_text[:100]}...")
            
            # Convert to SRT format
            srt_content = []
            for i, segment in enumerate(result["segments"]):
                start_time = segment['start']
                end_time = segment['end']
                
                # بررسی کیفیت هر بخش
                text = segment['text'].strip()
                if not text or len(text) < 2:
                    continue
                
                start_str = '{:02d}:{:02d}:{:02d},{:03d}'.format(
                    int(start_time // 3600),
                    int((start_time % 3600) // 60),
                    int(start_time % 60),
                    int((start_time % 1) * 1000)
                )
                end_str = '{:02d}:{:02d}:{:02d},{:03d}'.format(
                    int(end_time // 3600),
                    int((end_time % 3600) // 60),
                    int(end_time % 60),
                    int((end_time % 1) * 1000)
                )
                srt_content.append(f"{len(srt_content)+1}\n{start_str} --> {end_str}\n{text}\n")
            
            if not srt_content:
                print("❌ هیچ بخش معتبری برای ذخیره یافت نشد")
                return False
            
            srt_path = self.work_dir / 'audio.srt'
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(srt_content))
            
            print(f"✅ فایل SRT با {len(srt_content)} زیرنویس ایجاد شد")
            return True
            
        except Exception as e:
            print(f"❌ خطا در استخراج صدا با Whisper: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def compress_srt_dialogues(self, merge_count: int = 3) -> bool:
        """فشرده‌سازی دیالوگ‌های SRT"""
        try:
            srt_path = self.work_dir / 'audio.srt'
            if not srt_path.exists():
                return False
            
            with open(srt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse SRT
            subtitle_blocks = content.strip().split('\n\n')
            subtitles = []
            
            for block in subtitle_blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 2:
                    try:
                        time_line_index = -1
                        for i, line in enumerate(lines):
                            if '-->' in line:
                                time_line_index = i
                                break
                        if time_line_index != -1:
                            time_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})', lines[time_line_index])
                            start_time, end_time = time_match.groups()
                            text = '\n'.join(lines[time_line_index+1:])
                            subtitles.append({'start': start_time, 'end': end_time, 'text': text})
                    except Exception:
                        continue
            
            if not subtitles:
                return False
            
            # Merge subtitles
            merged_subs = []
            new_index = 1
            for i in range(0, len(subtitles), merge_count):
                chunk = subtitles[i:i+merge_count]
                if not chunk:
                    continue
                start_time = chunk[0]['start']
                end_time = chunk[-1]['end']
                # ترکیب بهتر متن‌ها با نقطه‌گذاری مناسب
                combined_text = ' '.join([sub['text'].replace('\n', ' ').strip() for sub in chunk])
                # حذف فاصله‌های اضافی
                combined_text = ' '.join(combined_text.split())
                # اضافه کردن نقطه در انتها اگر وجود نداشته باشد
                if combined_text and not combined_text.endswith(('.', '!', '?', '،', ':')):
                    combined_text += '.'
                merged_subs.append({'index': new_index, 'start': start_time, 'end': end_time, 'text': combined_text})
                new_index += 1
            
            # Format SRT
            srt_output = []
            for sub in merged_subs:
                srt_output.append(str(sub['index']))
                srt_output.append(f"{sub['start']} --> {sub['end']}")
                srt_output.append(sub['text'])
                srt_output.append('')
            
            # Save compressed SRT
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(srt_output))
            
            return True
            
        except Exception as e:
            print(f"خطا در فشرده‌سازی: {str(e)}")
            return False
    
    def translate_subtitles(self, target_language: str = "Persian (FA)") -> bool:
        """ترجمه زیرنویس‌ها - ترجمه کامل فایل SRT در یک درخواست"""
        try:
            srt_path = self.work_dir / 'audio.srt'
            if not srt_path.exists():
                return False
            
            # خواندن کل محتوای فایل SRT
            with open(srt_path, 'r', encoding='utf-8') as f:
                srt_content = f.read()
            
            # Translation models (بهترتیب کیفیت)
            translation_models = [
                "gemini-2.5-flash",        # بهترین کیفیت
                "gemini-2.5-flash-lite",   # کیفیت خوب و سریع
                "gemini-flash-lite-latest" # پشتیبان
            ]
            
            def translate_entire_srt_with_fallback(srt_text):
                for model_name in translation_models:
                    try:
                        model = genai.GenerativeModel(
                            model_name,
                            safety_settings={
                                genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                                genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
                                genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                                genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                            }
                        )
                        
                        if target_language == "Persian (FA)":
                            prompt = f"""متن کامل فایل SRT زیر را که شامل زیرنویس‌های یک ویدیو به زبان انگلیسی است، به دقت مطالعه کن تا کاملاً متوجه موضوع و مفهوم کلی آن شوی.
پس از درک کامل محتوا، هر خط از متن زیرنویس (بخش انگلیسی) را به فارسی بسیار روان، طبیعی و قابل فهم برای مخاطب عمومی ترجمه کن. ترجمه نباید حالت ماشینی داشته باشد و باید شبیه متنی باشد که یک فارسی‌زبان بومی می‌نوشت. پیام اصلی هر خط را بدون هیچ گونه ابهام یا دشواری در درک منتقل کن.
نکات بسیار مهم:
حفظ ساختار SRT: لطفاً ساختار زمانی فایل SRT را دقیقاً حفظ کن. یعنی هر خط ترجمه فارسی باید دقیقاً مقابل خط اصلی انگلیسی و با همان شماره و زمان‌بندی قرار گیرد. فقط متن انگلیسی را ترجمه کن و اعداد و زمان‌بندی را بدون تغییر کپی کن.
حفظ اعداد در متن ترجمه: هر عدد یا رقمی که در متن انگلیسی زیرنویس وجود دارد (مثلاً "Gemma 3N", "version 2.5", "100 meters", "5G connectivity")، باید دقیقاً و بدون تغییر در ترجمه فارسی نیز آورده شود. اعداد را ترجمه یا حذف نکن.

فایل SRT:
{srt_text}

ترجمه فارسی:"""
                        else:
                            language_map = {
                                "English (EN)": "English", "German (DE)": "German", 
                                "French (FR)": "French", "Italian (IT)": "Italian", 
                                "Spanish (ES)": "Spanish", "Chinese (ZH)": "Chinese", 
                                "Korean (KO)": "Korean", "Russian (RU)": "Russian", 
                                "Arabic (AR)": "Arabic", "Japanese (JA)": "Japanese", 
                                "Hindi (HI)": "Hindi"
                            }
                            target_lang_name = language_map.get(target_language, "English")
                            prompt = f"""You are an expert subtitle translator. Please carefully read the complete SRT file below which contains subtitles for a video in English, and understand the overall topic and context.
After fully understanding the content, translate each line of subtitle text (English part) to {target_lang_name} in a very fluent, natural and understandable way for general audience. The translation should not sound machine-like and should be like text written by a native speaker. Convey the main message of each line without any ambiguity or difficulty in understanding.
Very important note: Please preserve the exact timing structure of the SRT file. Each translated line should be exactly opposite the original English line with the same number and timing. Only translate the English text and copy the numbers and timing without any changes.

SRT File:
{srt_text}

{target_lang_name} Translation:"""
                        
                        print(f"🔄 ارسال کل فایل SRT به مدل {model_name} برای ترجمه...")
                        response = model.generate_content(prompt)
                        time.sleep(3)  # Rate limiting
                        
                        # پاکسازی پاسخ از خطوط اضافی
                        cleaned_response = self._clean_srt_response(response.text.strip())
                        return cleaned_response
                        
                    except Exception as e:
                        print(f"خطا در مدل {model_name}: {str(e)}")
                        time.sleep(5)
                        continue
                
                return srt_content  # Return original content if all models fail
            
            # ترجمه کل فایل SRT در یک درخواست
            print(f"🔄 شروع ترجمه کامل فایل SRT...")
            translated_content = translate_entire_srt_with_fallback(srt_content)
            
            # ذخیره فایل ترجمه شده
            translated_path = self.work_dir / 'audio_fa.srt'
            with open(translated_path, 'w', encoding='utf-8') as f:
                f.write(translated_content)
            
            print(f"✅ ترجمه کامل فایل SRT با موفقیت انجام شد!")
            return True
            
        except Exception as e:
            print(f"خطا در ترجمه: {str(e)}")
            return False
    
    def parse_audio_mime_type(self, mime_type: str) -> dict:
        """Parse audio MIME type for conversion"""
        parts = mime_type.split(";")
        details = {'bits_per_sample': 16, 'rate': 24000}
        for param in parts:
            param = param.strip()
            if param.lower().startswith("rate="):
                details['rate'] = int(param.split("=", 1)[1])
            elif param.startswith("audio/L"):
                details['bits_per_sample'] = int(param.split("L", 1)[1])
        return details
    
    def convert_to_wav(self, audio_data: bytes, mime_type: str) -> bytes:
        """Convert audio data to WAV format"""
        parameters = self.parse_audio_mime_type(mime_type)
        bits_per_sample = parameters["bits_per_sample"]
        sample_rate = parameters["rate"]
        num_channels = 1
        data_size = len(audio_data)
        bytes_per_sample = bits_per_sample // 8
        block_align = num_channels * bytes_per_sample
        byte_rate = sample_rate * block_align
        chunk_size = 36 + data_size
        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF", chunk_size, b"WAVE", b"fmt ", 16, 1,
            num_channels, sample_rate, byte_rate, block_align,
            bits_per_sample, b"data", data_size
        )
        return header + audio_data
    
    def generate_tts_segment(self, text: str, voice: str, model: str, output_path: str, 
                           speech_prompt: str = "", max_retries: int = 3) -> Optional[str]:
        """تولید سگمنت صوتی با Gemini TTS"""
        for attempt in range(1, max_retries + 1):
            try:
                if speech_prompt and speech_prompt.strip():
                    final_text = f"{speech_prompt.strip()}: \"{text}\""
                else:
                    final_text = text
                
                contents = [types.Content(role="user", parts=[types.Part.from_text(text=final_text)])]
                generate_content_config = types.GenerateContentConfig(
                    response_modalities=["audio"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)
                        )
                    ),
                )
                
                stream = self.client.models.generate_content_stream(
                    model=model, contents=contents, config=generate_content_config,
                )
                
                audio_data_buffer = b""
                mime_type = ""
                for chunk in stream:
                    if chunk.candidates and chunk.candidates[0].content and chunk.candidates[0].content.parts:
                        part = chunk.candidates[0].content.parts[0]
                        if part.inline_data:
                            audio_data_buffer += part.inline_data.data
                            mime_type = part.inline_data.mime_type
                
                if audio_data_buffer and mime_type:
                    final_wav_data = self.convert_to_wav(audio_data_buffer, mime_type)
                    with open(output_path, 'wb') as f:
                        f.write(final_wav_data)
                    return output_path
                else:
                    raise Exception("هیچ داده صوتی از API دریافت نشد.")
                    
            except Exception as e:
                print(f"خطا در تولید صدای Gemini (تلاش {attempt}/{max_retries}): {str(e)}")
                if attempt < max_retries:
                    wait_time = 9 * attempt
                    print(f"انتظار برای {wait_time} ثانیه...")
                    time.sleep(wait_time)
                else:
                    print(f"تولید صدا برای قطعه '{text[:50]}...' ناموفق بود.")
                    return None
        return None
    
    def create_audio_segments(self, voice: str = "Fenrir", model: str = "gemini-2.5-flash-preview-tts",
                            speech_prompt: str = "", sleep_between_requests: int = 30) -> bool:
        """ایجاد سگمنت‌های صوتی با مدیریت هوشمند محدودیت‌ها"""
        try:
            srt_path = self.work_dir / 'audio_fa.srt'
            if not srt_path.exists():
                return False
            
            subs = pysrt.open(str(srt_path), encoding='utf-8')
            total_segments = len(subs)
            
            # محاسبه فشرده‌سازی خودکار
            if total_segments > 15:  # اگر بیشتر از محدودیت روزانه باشد
                auto_merge_count = min(15, max(3, total_segments // 10))
                print(f"⚠️ تعداد سگمنت‌ها ({total_segments}) بیشتر از محدودیت API است.")
                print(f"🔄 فشرده‌سازی خودکار با ضریب {auto_merge_count} فعال می‌شود...")
                self.compress_srt_dialogues(auto_merge_count)
                subs = pysrt.open(str(srt_path), encoding='utf-8')
                total_segments = len(subs)
                print(f"✅ تعداد سگمنت‌ها به {total_segments} کاهش یافت.")
            
            # مدیریت batch ها
            batch_size = 3
            batch_delay = 60
            
            for batch_start in range(0, total_segments, batch_size):
                batch_end = min(batch_start + batch_size, total_segments)
                batch_segments = subs[batch_start:batch_end]
                
                print(f"📦 پردازش batch {batch_start//batch_size + 1}: سگمنت‌های {batch_start+1}-{batch_end}")
                
                for i, sub in enumerate(batch_segments):
                    segment_index = batch_start + i + 1
                    print(f"🎧 پردازش سگمنت {segment_index}/{total_segments}...")
                    
                    temp_audio_path = self.segments_dir / f"temp_{segment_index}.wav"
                    final_segment_path = self.segments_dir / f"dub_{segment_index}.wav"
                    
                    # تولید صدا با مدیریت خطا
                    generated_path = self.generate_tts_segment(
                        sub.text, voice, model, str(temp_audio_path), speech_prompt
                    )
                    
                    # انتظار بین سگمنت‌ها
                    if i < len(batch_segments) - 1:
                        print(f"⏱️ استراحت برای {sleep_between_requests} ثانیه...")
                        time.sleep(sleep_between_requests)
                    
                    # مدیریت فایل‌های خالی
                    if not generated_path or not os.path.exists(generated_path):
                        print(f"⚠️ تولید صدای Gemini برای سگمنت {segment_index} ناموفق بود. فایل سکوت ایجاد می‌شود.")
                        start_ms = sub.start.hours * 3600000 + sub.start.minutes * 60000 + sub.start.seconds * 1000 + sub.start.milliseconds
                        end_ms = sub.end.hours * 3600000 + sub.end.minutes * 60000 + sub.end.seconds * 1000 + sub.end.milliseconds
                        target_duration_ms = max(end_ms - start_ms, 100)  # حداقل 100ms
                        
                        # ایجاد فایل سکوت با FFmpeg
                        try:
                            subprocess.run([
                                'ffmpeg', '-f', 'lavfi', '-i', f'anullsrc=duration={target_duration_ms/1000.0}',
                                '-ac', '2', '-ar', '44100', '-y', str(final_segment_path)
                            ], check=True, capture_output=True)
                            print(f"   ✅ فایل سکوت برای سگمنت {segment_index} ایجاد شد.")
                        except Exception as e:
                            print(f"   ❌ خطا در ایجاد فایل سکوت: {e}")
                        continue
                    
                    try:
                        # تنظیم زمان‌بندی
                        start_ms = sub.start.hours * 3600000 + sub.start.minutes * 60000 + sub.start.seconds * 1000 + sub.start.milliseconds
                        end_ms = sub.end.hours * 3600000 + sub.end.minutes * 60000 + sub.end.seconds * 1000 + sub.end.milliseconds
                        target_duration = (end_ms - start_ms) / 1000.0
                        if target_duration <= 0:
                            target_duration = 0.5
                        
                        sound = AudioSegment.from_file(generated_path)
                        original_duration = len(sound) / 1000.0
                        
                        if original_duration == 0:
                            raise ValueError("فایل صوتی تولید شده خالی است.")
                        
                        speed_factor = original_duration / target_duration
                        speed_factor = max(0.5, min(speed_factor, 2.5))
                        
                        print(f"   - زمان هدف: {target_duration:.2f}s | زمان اصلی: {original_duration:.2f}s | ضریب سرعت: {speed_factor:.2f}")
                        
                        subprocess.run([
                            'ffmpeg', '-i', generated_path,
                            '-filter:a', f'rubberband=tempo={speed_factor}',
                            '-y', str(final_segment_path)
                        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        
                        print(f"   ✅ سگمنت {segment_index} با موفقیت ساخته و زمان‌بندی شد.")
                        
                    except Exception as e:
                        print(f"   ❌ خطا در زمان‌بندی سگمنت {segment_index}: {e}")
                        if os.path.exists(generated_path):
                            os.rename(generated_path, str(final_segment_path))
                
                # انتظار بین batch ها
                if batch_end < total_segments:
                    print(f"⏳ انتظار {batch_delay} ثانیه قبل از batch بعدی...")
                    time.sleep(batch_delay)
            
            print("="*50)
            print("🎉 تمام سگمنت‌های صوتی با مدیریت هوشمند محدودیت‌ها ساخته شدند!")
            return True
            
        except Exception as e:
            print(f"خطا در ایجاد سگمنت‌های صوتی: {str(e)}")
            return False
    
    def create_final_video(self, keep_original_audio: bool = False, 
                          original_audio_volume: float = 0.8) -> Optional[str]:
        """ایجاد ویدیو نهایی دوبله شده"""
        try:
            video_path = self.work_dir / 'input_video.mp4'
            srt_path = self.work_dir / 'audio_fa.srt'
            
            if not video_path.exists() or not srt_path.exists():
                print("❌ فایل ویدیو یا زیرنویس یافت نشد")
                return None
            
            subs = pysrt.open(str(srt_path), encoding='utf-8')
            print(f"📝 تعداد زیرنویس‌ها: {len(subs)}")
            
            # بررسی فایل‌های صوتی موجود
            available_segments = []
            for i in range(1, len(subs) + 1):
                segment_path = self.segments_dir / f"dub_{i}.wav"
                if segment_path.exists():
                    available_segments.append((i, segment_path))
            
            print(f"🎵 فایل‌های صوتی موجود: {len(available_segments)} از {len(subs)}")
            
            if not available_segments:
                print("❌ هیچ فایل صوتی یافت نشد")
                return None
            
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir = Path(temp_dir)
                
                # Extract original audio
                print("🎵 استخراج صدای اصلی...")
                original_audio_path = temp_dir / "original_audio.wav"
                subprocess.run([
                    'ffmpeg', '-i', str(video_path), '-vn',
                    '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2',
                    '-y', str(original_audio_path)
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # Get video duration
                result = subprocess.run([
                    'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1',
                    str(video_path)
                ], capture_output=True, text=True)
                video_duration = float(result.stdout.strip())
                print(f"⏱️ مدت ویدیو: {video_duration:.2f} ثانیه")
                
                # Create base audio (silent or original)
                if keep_original_audio:
                    print("🔊 حفظ صدای اصلی...")
                    base_audio = AudioSegment.from_file(str(original_audio_path))
                    volume_reduction = - (60 * (1 - original_audio_volume))
                    base_audio = base_audio + volume_reduction
                else:
                    print("🔇 ایجاد صدای سکوت...")
                    base_audio = AudioSegment.silent(duration=int(video_duration * 1000))
                
                # Overlay dubbing segments
                print("🎤 اضافه کردن سگمنت‌های دوبله...")
                final_audio = base_audio
                
                for i, (segment_num, segment_path) in enumerate(available_segments):
                    try:
                        print(f"   📁 پردازش سگمنت {segment_num}...")
                        segment_audio = AudioSegment.from_file(str(segment_path))
                        
                        # محاسبه زمان شروع
                        sub = subs[segment_num - 1]
                        start_time_ms = (sub.start.hours * 3600 + sub.start.minutes * 60 + sub.start.seconds) * 1000 + sub.start.milliseconds
                        
                        if start_time_ms < 0:
                            start_time_ms = 0
                        
                        print(f"      ⏰ زمان شروع: {start_time_ms/1000:.2f}s")
                        print(f"      🎵 مدت صدا: {len(segment_audio)/1000:.2f}s")
                        
                        # اضافه کردن به صدا
                        final_audio = final_audio.overlay(segment_audio, position=start_time_ms)
                        print(f"      ✅ سگمنت {segment_num} اضافه شد")
                        
                    except Exception as e:
                        print(f"      ❌ خطا در سگمنت {segment_num}: {str(e)}")
                        continue
                
                # Export final audio
                print("💾 ذخیره صدای نهایی...")
                merged_audio_path = temp_dir / "merged_audio.wav"
                final_audio.export(str(merged_audio_path), format="wav")
                
                # Create final video using the working method
                print("🎬 ایجاد ویدیو نهایی...")
                output_path = self.work_dir / 'final_dubbed_video.mp4'
                
                # روش کارآمد: استفاده از concat برای ترکیب فایل‌های صوتی
                # ابتدا فایل لیست صوتی ایجاد می‌کنیم
                audio_list_file = temp_dir / "audio_list.txt"
                with open(audio_list_file, 'w') as f:
                    for i, (segment_num, segment_path) in enumerate(available_segments):
                        f.write(f"file '{segment_path.absolute()}'\n")
                
                # ترکیب فایل‌های صوتی
                combined_audio = temp_dir / "combined_audio.wav"
                subprocess.run([
                    'ffmpeg', '-f', 'concat', '-safe', '0', '-i', str(audio_list_file),
                    '-c', 'copy', '-y', str(combined_audio)
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # بررسی و تنظیم زمان‌بندی صدا
                print("⏱️ بررسی زمان‌بندی صدا...")
                
                # دریافت مدت زمان ویدیو
                result = subprocess.run([
                    'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format',
                    str(video_path)
                ], capture_output=True, text=True)
                
                import json
                video_info = json.loads(result.stdout)
                video_duration = float(video_info['format']['duration'])
                
                # دریافت مدت زمان صدا
                result = subprocess.run([
                    'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format',
                    str(combined_audio)
                ], capture_output=True, text=True)
                
                audio_info = json.loads(result.stdout)
                audio_duration = float(audio_info['format']['duration'])
                
                print(f"   📹 مدت ویدیو: {video_duration:.2f} ثانیه")
                print(f"   🎵 مدت صدا: {audio_duration:.2f} ثانیه")
                
                # تنظیم سرعت صدا اگر لازم باشد
                if audio_duration > video_duration:
                    speed_factor = audio_duration / video_duration
                    print(f"   ⚡ تنظیم سرعت صدا: {speed_factor:.2f}x")
                    
                    adjusted_audio = temp_dir / "adjusted_audio.wav"
                    subprocess.run([
                        'ffmpeg', '-i', str(combined_audio),
                        '-filter:a', f'rubberband=tempo={speed_factor}',
                        '-y', str(adjusted_audio)
                    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                    # بررسی مدت زمان بعد از تنظیم
                    result = subprocess.run([
                        'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format',
                        str(adjusted_audio)
                    ], capture_output=True, text=True)
                    
                    adjusted_info = json.loads(result.stdout)
                    adjusted_duration = float(adjusted_info['format']['duration'])
                    print(f"   🎵 مدت صدا بعد از تنظیم: {adjusted_duration:.2f} ثانیه")
                    
                    final_audio = adjusted_audio
                else:
                    print("   ✅ زمان‌بندی صدا مناسب است")
                    final_audio = combined_audio
                
                # ایجاد ویدیو نهایی
                subprocess.run([
                    'ffmpeg', '-i', str(video_path), '-i', str(final_audio),
                    '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v', '-map', '1:a',
                    '-shortest', '-y', str(output_path)
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                print(f"✅ ویدیو نهایی ایجاد شد: {output_path}")
                return str(output_path)
                
        except Exception as e:
            print(f"❌ خطا در ایجاد ویدیو نهایی: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _validate_srt_file(self, srt_path: Path) -> bool:
        """اعتبارسنجی فایل SRT"""
        try:
            with open(srt_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # بررسی اینکه فایل خالی نباشد
            if not content:
                print("❌ فایل SRT خالی است")
                return False
            
            # بررسی ساختار اولیه
            lines = content.split('\n')
            if len(lines) < 4:
                print("❌ فایل SRT ساختار ناقص دارد")
                return False
            
            # بررسی اینکه خط اول باید شماره باشد
            if not lines[0].strip().isdigit():
                print("❌ فایل SRT باید با شماره شروع شود")
                return False
            
            # بررسی وجود زمان‌بندی
            has_timing = False
            for line in lines:
                if '-->' in line:
                    has_timing = True
                    break
            
            if not has_timing:
                print("❌ فایل SRT فاقد زمان‌بندی است")
                return False
            
            # بررسی کیفیت متن (برای فایل انگلیسی)
            if 'audio.srt' in str(srt_path):
                all_text = " ".join([line for line in lines if line.strip() and not line.strip().isdigit() and '-->' not in line])
                if len(all_text.strip()) < 10:
                    print("❌ متن فایل SRT خیلی کوتاه است")
                    return False
                
                # بررسی وجود کاراکترهای نامفهوم
                if any(char in all_text for char in ['運', '糾', 'だ', 'の', 'を', 'に', 'は', 'が', 'で', 'と', 'を', 'に', 'は', 'が', 'で', 'と']):
                    print("❌ فایل SRT حاوی کاراکترهای نامفهوم است")
                    return False
            
            print("✅ فایل SRT معتبر است")
            return True
            
        except Exception as e:
            print(f"❌ خطا در اعتبارسنجی فایل SRT: {str(e)}")
            return False
    
    def _backup_srt_files(self) -> bool:
        """پشتیبان‌گیری از فایل‌های SRT معتبر"""
        try:
            srt_en_path = self.work_dir / 'audio.srt'
            srt_fa_path = self.work_dir / 'audio_fa.srt'
            
            # پشتیبان‌گیری از فایل انگلیسی
            if srt_en_path.exists() and self._validate_srt_file(srt_en_path):
                backup_en = self.work_dir / 'audio_backup.srt'
                backup_en.write_text(srt_en_path.read_text(encoding='utf-8'), encoding='utf-8')
                print("✅ فایل SRT انگلیسی پشتیبان‌گیری شد")
            
            # پشتیبان‌گیری از فایل فارسی
            if srt_fa_path.exists() and self._validate_srt_file(srt_fa_path):
                backup_fa = self.work_dir / 'audio_fa_backup.srt'
                backup_fa.write_text(srt_fa_path.read_text(encoding='utf-8'), encoding='utf-8')
                print("✅ فایل SRT فارسی پشتیبان‌گیری شد")
            
            return True
            
        except Exception as e:
            print(f"❌ خطا در پشتیبان‌گیری: {str(e)}")
            return False
    
    def _restore_srt_files(self) -> bool:
        """بازیابی فایل‌های SRT از پشتیبان"""
        try:
            backup_en = self.work_dir / 'audio_backup.srt'
            backup_fa = self.work_dir / 'audio_fa_backup.srt'
            srt_en_path = self.work_dir / 'audio.srt'
            srt_fa_path = self.work_dir / 'audio_fa.srt'
            
            restored = False
            
            # بازیابی فایل انگلیسی
            if backup_en.exists() and self._validate_srt_file(backup_en):
                srt_en_path.write_text(backup_en.read_text(encoding='utf-8'), encoding='utf-8')
                print("✅ فایل SRT انگلیسی از پشتیبان بازیابی شد")
                restored = True
            
            # بازیابی فایل فارسی
            if backup_fa.exists() and self._validate_srt_file(backup_fa):
                srt_fa_path.write_text(backup_fa.read_text(encoding='utf-8'), encoding='utf-8')
                print("✅ فایل SRT فارسی از پشتیبان بازیابی شد")
                restored = True
            
            if not restored:
                print("❌ هیچ فایل پشتیبان معتبری یافت نشد")
            
            return restored
            
        except Exception as e:
            print(f"❌ خطا در بازیابی: {str(e)}")
            return False
    
    def _clean_srt_response(self, response_text: str) -> str:
        """پاکسازی پاسخ Gemini از توضیحات اضافی و حفظ ساختار SRT"""
        try:
            lines = response_text.split('\n')
            cleaned_lines = []
            in_srt_content = False
            subtitle_count = 0
            found_first_subtitle = False
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                # اگر خط خالی است، آن را حفظ کن
                if not line:
                    if in_srt_content:
                        cleaned_lines.append(line)
                    continue
                
                # بررسی اینکه آیا این خط شروع یک زیرنویس است (شماره)
                if line.isdigit() and not found_first_subtitle:
                    # بررسی اینکه آیا این اولین زیرنویس است (شماره 1)
                    if line == "1":
                        found_first_subtitle = True
                        in_srt_content = True
                        subtitle_count += 1
                        cleaned_lines.append(line)
                        continue
                    else:
                        # اگر شماره 1 نیست، نادیده بگیر
                        continue
                elif line.isdigit() and found_first_subtitle:
                    # زیرنویس‌های بعدی
                    in_srt_content = True
                    subtitle_count += 1
                    cleaned_lines.append(line)
                    continue
                
                # اگر در محتوای SRT هستیم، خط را پردازش کن
                if in_srt_content:
                    # اگر خط زمان‌بندی است، آن را حفظ کن
                    if '-->' in line:
                        cleaned_lines.append(line)
                        continue
                    
                    # اگر خط متن است، بررسی کن که آیا شامل هر دو زبان است
                    if not line.isdigit() and '-->' not in line:
                        # بررسی اینکه آیا خط شامل متن انگلیسی و فارسی است
                        cleaned_line = self._extract_persian_text(line)
                        if cleaned_line:
                            cleaned_lines.append(cleaned_line)
                        continue
                    
                    # در غیر این صورت، خط را حفظ کن
                    cleaned_lines.append(line)
                    continue
                
                # اگر هنوز در محتوای SRT نیستیم، بررسی کن که آیا این خط توضیح اضافی است
                explanation_keywords = [
                    'متن کامل فایل SRT', 'ترجمه فارسی', 'فایل SRT', 'زیرنویس', 'ترجمه',
                    'به همین دلیل', 'درک کامل', 'موضوع و مفهوم', 'عملاً غیرممکن', 'متنی بی‌معنی',
                    'انتظارات شما', 'اگر متن اصلی', 'لطفاً زبان', 'در صورت امکان', 'در حال حاضر',
                    'قادر به ارائه', 'بر اساس فرض', 'SRT File', 'Translation', 'subtitle',
                    'translate', 'file', 'content', 'text', 'because', 'unable', 'impossible',
                    'cannot', 'please', 'if you have', 'currently', 'based on', 'در خط', 'به نظر می‌رسد',
                    'تحریف شده', 'احتمالاً', 'باشد', 'است', 'I\'ve', 'Wow', 'amount', 'money'
                ]
                
                # اگر خط حاوی کلمات توضیحی است، آن را نادیده بگیر
                if any(keyword in line for keyword in explanation_keywords):
                    continue
                
                # اگر خط کوتاه است و احتمالاً توضیح است، نادیده بگیر
                if len(line) < 20 and not line[0].isdigit() and '-->' not in line:
                    continue
                
                # در غیر این صورت، خط را حفظ کن
                cleaned_lines.append(line)
            
            # اگر هیچ زیرنویسی پیدا نشد، کل متن را برگردان
            if subtitle_count == 0:
                print("⚠️ هیچ زیرنویسی در پاسخ یافت نشد، کل متن برگردانده می‌شود")
                return response_text
            
            cleaned_text = '\n'.join(cleaned_lines)
            print(f"✅ {subtitle_count} زیرنویس از پاسخ پاکسازی شد")
            return cleaned_text
            
        except Exception as e:
            print(f"❌ خطا در پاکسازی پاسخ: {str(e)}")
            return response_text
    
    def _extract_persian_text(self, line: str) -> str:
        """استخراج متن فارسی از خطی که شامل هر دو زبان است و حفظ اعداد"""
        try:
            # تقسیم خط به کلمات
            words = line.split()
            result_words = []
            
            for word in words:
                # بررسی اینکه آیا کلمه فارسی است یا نه
                if self._is_persian_word(word):
                    result_words.append(word)
                # اگر کلمه شامل عدد است، آن را حفظ کن
                elif self._contains_number(word):
                    result_words.append(word)
                # اگر کلمه فقط عدد است، آن را حفظ کن
                elif word.isdigit():
                    result_words.append(word)
                # اگر کلمه شامل عدد و حروف است (مثل "18th", "2.5", "5G")
                elif any(c.isdigit() for c in word):
                    result_words.append(word)
            
            # اگر کلمه فارسی یا عدد پیدا شد، آن‌ها را برگردان
            if result_words:
                return ' '.join(result_words)
            
            # اگر هیچ کلمه فارسی یا عدد پیدا نشد، بررسی کن که آیا کل خط فارسی است
            if self._is_persian_text(line):
                return line
            
            # در غیر این صورت، خط خالی برگردان
            return ""
            
        except Exception as e:
            print(f"❌ خطا در استخراج متن فارسی: {str(e)}")
            return line
    
    def _is_persian_text(self, text: str) -> bool:
        """بررسی اینکه آیا متن فارسی است یا نه"""
        try:
            # حذف علائم نگارشی و فاصله‌ها
            clean_text = ''.join(c for c in text if c.isalnum())
            
            if not clean_text:
                return False
            
            # بررسی وجود کاراکترهای فارسی
            persian_chars = 'ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی'
            persian_count = sum(1 for c in clean_text if c in persian_chars)
            
            # بررسی وجود کاراکترهای انگلیسی
            english_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
            english_count = sum(1 for c in clean_text if c in english_chars)
            
            # اگر تعداد کاراکترهای فارسی بیشتر از انگلیسی باشد، فارسی است
            return persian_count > english_count
            
        except Exception as e:
            return False
    
    def _is_persian_word(self, word: str) -> bool:
        """بررسی اینکه آیا کلمه فارسی است یا نه"""
        try:
            # حذف علائم نگارشی
            clean_word = ''.join(c for c in word if c.isalnum())
            
            if not clean_word:
                return False
            
            # بررسی وجود کاراکترهای فارسی
            persian_chars = 'ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی'
            has_persian = any(c in persian_chars for c in clean_word)
            
            # بررسی عدم وجود کاراکترهای انگلیسی
            english_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
            has_english = any(c in english_chars for c in clean_word)
            
            # اگر کاراکتر فارسی دارد و کاراکتر انگلیسی ندارد، فارسی است
            return has_persian and not has_english
            
        except Exception as e:
            return False
    
    def _contains_number(self, word: str) -> bool:
        """بررسی اینکه آیا کلمه شامل عدد است یا نه"""
        try:
            # بررسی وجود کاراکترهای عددی
            return any(c.isdigit() for c in word)
        except Exception as e:
            return False
    
    def clean_existing_srt_files(self) -> bool:
        """پاکسازی فایل‌های SRT موجود از توضیحات اضافی"""
        try:
            cleaned_count = 0
            
            # پاکسازی فایل انگلیسی
            srt_en_path = self.work_dir / 'audio.srt'
            if srt_en_path.exists():
                with open(srt_en_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                cleaned_content = self._clean_srt_response(content)
                if cleaned_content != content:
                    with open(srt_en_path, 'w', encoding='utf-8') as f:
                        f.write(cleaned_content)
                    print("✅ فایل SRT انگلیسی پاکسازی شد")
                    cleaned_count += 1
            
            # پاکسازی فایل فارسی
            srt_fa_path = self.work_dir / 'audio_fa.srt'
            if srt_fa_path.exists():
                with open(srt_fa_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                cleaned_content = self._clean_srt_response(content)
                if cleaned_content != content:
                    with open(srt_fa_path, 'w', encoding='utf-8') as f:
                        f.write(cleaned_content)
                    print("✅ فایل SRT فارسی پاکسازی شد")
                    cleaned_count += 1
            
            if cleaned_count > 0:
                print(f"✅ {cleaned_count} فایل SRT پاکسازی شد")
            else:
                print("ℹ️ هیچ فایل SRT نیاز به پاکسازی نداشت")
            
            return True
            
        except Exception as e:
            print(f"❌ خطا در پاکسازی فایل‌های SRT: {str(e)}")
            return False
    
    def create_subtitled_video(self, subtitle_config: dict = None, fixed_text_config: dict = None) -> Optional[str]:
        """ایجاد ویدیو با زیرنویس ترجمه شده و متن ثابت پایین"""
        try:
            video_path = self.work_dir / 'input_video.mp4'
            srt_path = self.work_dir / 'audio_fa.srt'
            
            if not video_path.exists() or not srt_path.exists():
                print("❌ فایل ویدیو یا زیرنویس یافت نشد")
                return None
            
            # اعتبارسنجی فایل SRT
            if not self._validate_srt_file(srt_path):
                print("❌ فایل SRT معتبر نیست")
                return None
            
            subs = pysrt.open(str(srt_path), encoding='utf-8')
            print(f"📝 تعداد زیرنویس‌ها: {len(subs)}")
            
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir = Path(temp_dir)
                
                # تنظیمات پیش‌فرض زیرنویس - استفاده از فونت فارسی
                default_subtitle_config = {
                    "font": "vazirmatn",  # فونت فارسی برای رندر بهتر
                    "fontsize": 24,
                    "color": "white",
                    "background_color": "none",
                    "outline_color": "black",
                    "outline_width": 2,
                    "position": "bottom_center",
                    "margin_v": 20,
                    "shadow": 0,
                    "shadow_color": "black",
                    "bold": False,
                    "italic": False
                }
                
                # تنظیمات پیش‌فرض متن ثابت - استفاده از فونت فارسی
                default_fixed_text_config = {
                    "enabled": False,
                    "text": "",
                    "font": "vazirmatn",  # فونت فارسی برای رندر بهتر
                    "fontsize": 20,
                    "color": "yellow",
                    "background_color": "black",
                    "position": "bottom_center",
                    "margin_bottom": 10,
                    "opacity": 0.8,
                    "bold": True,
                    "italic": False
                }
                
                # ادغام تنظیمات سفارشی با پیش‌فرض
                if subtitle_config:
                    sub_config = {**default_subtitle_config, **subtitle_config}
                else:
                    sub_config = default_subtitle_config
                
                if fixed_text_config:
                    fixed_config = {**default_fixed_text_config, **fixed_text_config}
                else:
                    fixed_config = default_fixed_text_config
                
                print(f"🎨 تنظیمات زیرنویس:")
                print(f"   📝 فونت: {sub_config['font']}")
                print(f"   📏 اندازه: {sub_config['fontsize']}px")
                print(f"   🎨 رنگ: {sub_config['color']}")
                print(f"   📍 موقعیت: {sub_config['position']}")
                
                if fixed_config['enabled']:
                    print(f"🎨 تنظیمات متن ثابت:")
                    print(f"   📝 متن: {fixed_config['text']}")
                    print(f"   📝 فونت: {fixed_config['font']}")
                    print(f"   📏 اندازه: {fixed_config['fontsize']}px")
                    print(f"   🎨 رنگ: {fixed_config['color']}")
                    print(f"   📍 موقعیت: {fixed_config['position']}")
                
                # ایجاد فایل SRT موقت با encoding صحیح و نرمال‌سازی متن فارسی
                temp_srt = temp_dir / "temp_subtitles.srt"
                srt_content = srt_path.read_text(encoding='utf-8')
                
                # نرمال‌سازی متن فارسی
                normalized_content = self._normalize_persian_text(srt_content)
                
                with open(temp_srt, 'w', encoding='utf-8') as f:
                    f.write(normalized_content)
                
                # ایجاد ویدیو با زیرنویس
                output_path = self.work_dir / 'custom_subtitled_video.mp4'
                print("🎬 ایجاد ویدیو با زیرنویس...")
                
                # ساخت فیلتر زیرنویس
                # پیدا کردن مسیر فونت
                font_name = sub_config['font']
                font_path = self._get_font_path(font_name)
                if font_path and font_name.lower() == 'vazirmatn':
                    # برای Vazirmatn از نام فونت استفاده کن نه مسیر
                    print(f"✅ فونت زیرنویس: {font_name} (فونت سیستم)")
                    # font_name را تغییر نده
                elif font_path:
                    print(f"✅ فونت زیرنویس: {font_name} → {font_path}")
                    font_name = font_path
                else:
                    print(f"⚠️ فونت زیرنویس: {font_name} (فونت سیستم)")
                
                subtitle_style_parts = [
                    f"FontName={font_name}",
                    f"FontSize={sub_config['fontsize']}",
                    f"PrimaryColour=&H{self._color_to_hex(sub_config['color'])}",
                    f"OutlineColour=&H{self._color_to_hex(sub_config['outline_color'])}",
                    f"Outline={sub_config['outline_width']}",
                    f"MarginV={sub_config['margin_v']}",
                    f"Shadow={sub_config['shadow']}",
                    f"ShadowColour=&H{self._color_to_hex(sub_config['shadow_color'])}",
                    f"Bold={1 if sub_config['bold'] else 0}",
                    f"Italic={1 if sub_config['italic'] else 0}",
                    f"Alignment={self._get_alignment(sub_config['position'])}"
                ]
                
                # اضافه کردن رنگ زمینه اگر انتخاب شده باشد
                if sub_config['background_color'] != 'none':
                    subtitle_style_parts.append(f"BackColour=&H{self._color_to_hex(sub_config['background_color'])}")
                    subtitle_style_parts.append("BorderStyle=4")  # جعبه گرد
                
                # استفاده از فیلتر subtitles با تنظیمات بهینه برای فارسی
                subtitle_filter = f"subtitles={temp_srt.absolute()}:force_style='{','.join(subtitle_style_parts)}'"
                
                # ساخت فیلترهای ترکیبی
                if fixed_config['enabled'] and fixed_config['text'].strip():
                    # اگر متن ثابت فعال است، ابتدا ویدیو با زیرنویس ایجاد کن
                    temp_video = temp_dir / "temp_with_subtitles.mp4"
                    
                    # مرحله 1: ایجاد ویدیو با زیرنویس
                    subprocess.run([
                        'ffmpeg', '-i', str(video_path),
                        '-vf', subtitle_filter,
                        '-c:v', 'libx264', '-c:a', 'copy',
                        '-y', str(temp_video)
                    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                    # مرحله 2: اضافه کردن متن ثابت
                    fixed_text_filter = self._create_fixed_text_filter(fixed_config)
                    if fixed_text_filter:
                        subprocess.run([
                            'ffmpeg', '-i', str(temp_video),
                            '-vf', fixed_text_filter,
                            '-c:v', 'libx264', '-c:a', 'copy',
                            '-y', str(output_path)
                        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    else:
                        # اگر فیلتر متن ثابت ایجاد نشد، فایل موقت را کپی کن
                        import shutil
                        shutil.copy2(temp_video, output_path)
                else:
                    # فقط زیرنویس
                    subprocess.run([
                        'ffmpeg', '-i', str(video_path),
                        '-vf', subtitle_filter,
                        '-c:v', 'libx264', '-c:a', 'copy',
                        '-y', str(output_path)
                    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                print(f"✅ ویدیو با زیرنویس ایجاد شد: {output_path}")
                return str(output_path)
                
        except Exception as e:
            print(f"❌ خطا در ایجاد ویدیو با زیرنویس: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_fixed_text_filter(self, config: dict) -> str:
        """ایجاد فیلتر FFmpeg برای متن ثابت با پشتیبانی کامل از فارسی"""
        try:
            import platform
            system = platform.system()
            
            # متن و تنظیمات
            text = config['text']
            fontsize = config['fontsize']
            color = config['color']
            margin_bottom = config['margin_bottom']
            font_name = config.get('font', 'Arial')
            
            # نرمال‌سازی متن فارسی
            normalized_text = self._normalize_persian_text(text)
            
            # پیدا کردن فونت
            font_path = self._get_font_path(font_name)
            if font_path and font_name.lower() == 'vazirmatn':
                # برای Vazirmatn از نام فونت استفاده کن نه مسیر
                print(f"✅ فونت متن ثابت: {font_name} (فونت سیستم)")
                final_font = font_name
            elif font_path:
                print(f"✅ فونت متن ثابت: {font_name} → {font_path}")
                final_font = font_path
            else:
                print(f"⚠️ فونت متن ثابت: {font_name} (فونت سیستم)")
                final_font = font_name
            
            # تنظیم موقعیت متن
            position = config.get('position', 'bottom_center')
            if position == 'bottom_center':
                x_pos = '(w-text_w)/2'
                y_pos = f'h-text_h-{margin_bottom}'
            elif position == 'bottom_left':
                x_pos = '10'
                y_pos = f'h-text_h-{margin_bottom}'
            elif position == 'bottom_right':
                x_pos = 'w-text_w-10'
                y_pos = f'h-text_h-{margin_bottom}'
            elif position == 'top_center':
                x_pos = '(w-text_w)/2'
                y_pos = '10'
            elif position == 'top_left':
                x_pos = '10'
                y_pos = '10'
            elif position == 'top_right':
                x_pos = 'w-text_w-10'
                y_pos = '10'
            else:
                x_pos = '(w-text_w)/2'
                y_pos = f'h-text_h-{margin_bottom}'
            
            # تنظیم رنگ
            color_hex = self._color_to_hex(color)
            # تبدیل BGR به RGB برای drawtext
            r = color_hex[4:6]
            g = color_hex[2:4]
            b = color_hex[0:2]
            drawtext_color = f"0x{r}{g}{b}"
            
            # تنظیم فونت برای drawtext
            if system == 'Linux':
                # در Linux از نام فونت استفاده کن
                font_param = f"fontfile='{final_font}'" if final_font.endswith(('.ttf', '.otf')) else f"font='{final_font}'"
            else:
                # در macOS و Windows از مسیر فایل استفاده کن
                font_param = f"fontfile='{final_font}'" if final_font.endswith(('.ttf', '.otf')) else f"font='{final_font}'"
            
            # تنظیمات اضافی
            extra_params = []
            if config.get('bold', False):
                extra_params.append("fontsize=1.2*fontsize")  # شبیه‌سازی bold
            
            # ساخت فیلتر drawtext
            filter_parts = [
                f"drawtext=text='{normalized_text}'",
                font_param,
                f"fontsize={fontsize}",
                f"fontcolor={drawtext_color}",
                f"x={x_pos}",
                f"y={y_pos}",
                "enable='between(t,0,999999)'"  # همیشه نمایش داده شود
            ]
            
            # اضافه کردن تنظیمات اضافی
            filter_parts.extend(extra_params)
            
            # اضافه کردن رنگ زمینه اگر انتخاب شده باشد
            background_color = config.get('background_color', 'none')
            if background_color != 'none':
                bg_color_hex = self._color_to_hex(background_color)
                bg_r = bg_color_hex[4:6]
                bg_g = bg_color_hex[2:4]
                bg_b = bg_color_hex[0:2]
                bg_color = f"0x{bg_r}{bg_g}{bg_b}"
                filter_parts.append(f"box=1:boxcolor={bg_color}@0.8:boxborderw=5")
            
            filter_text = ':'.join(filter_parts)
            
            return filter_text
            
        except Exception as e:
            print(f"❌ خطا در ایجاد فیلتر متن ثابت: {str(e)}")
            import traceback
            traceback.print_exc()
            return ""
    
    def _get_persian_font_path(self) -> str:
        """پیدا کردن فونت مناسب برای متن فارسی"""
        try:
            import platform
            import os
            
            # مسیرهای فونت‌های مختلف که از فارسی پشتیبانی می‌کنند
            # اولویت با فونت‌های Vazirmatn که مخصوص فارسی هستند
            persian_fonts = [
                # فونت‌های Vazirmatn (اولویت اول)
                os.path.expanduser("~/Library/Fonts/Vazirmatn-Regular.ttf"),
                os.path.expanduser("~/Library/Fonts/Vazirmatn-Medium.ttf"),
                os.path.expanduser("~/Library/Fonts/Vazirmatn-Bold.ttf"),
                os.path.expanduser("~/Library/Fonts/Vazirmatn-Light.ttf"),
                
                # فونت‌های Unicode که قطعاً از فارسی پشتیبانی می‌کنند
                "/System/Library/Fonts/Supplemental/Arial Unicode MS.ttf",
                "/Library/Fonts/Supplemental/Arial Unicode MS.ttf",
                "/System/Library/Fonts/Arial Unicode MS.ttf",
                "/Library/Fonts/Arial Unicode MS.ttf",
                
                # فونت‌های کاربر
                os.path.expanduser("~/Library/Fonts/Arial Unicode MS.ttf"),
                os.path.expanduser("~/Library/Fonts/Arial.ttf"),
                
                # فونت‌های سیستم که ممکن است از فارسی پشتیبانی کنند
                "/System/Library/Fonts/Arial.ttf",
                "/Library/Fonts/Arial.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                "/System/Library/Fonts/HelveticaNeue.ttc",
                "/System/Library/Fonts/HelveticaNeue.ttf",
                
                # فونت‌های کتابخانه
                "/Library/Fonts/Helvetica.ttc",
                "/Library/Fonts/HelveticaNeue.ttc"
            ]
            
            # جستجوی فونت مناسب
            for font_path in persian_fonts:
                if os.path.exists(font_path):
                    print(f"✅ فونت فارسی پیدا شد: {font_path}")
                    return font_path
            
            print("⚠️ هیچ فونت فارسی مناسبی پیدا نشد")
            return ""
            
        except Exception as e:
            print(f"❌ خطا در پیدا کردن فونت فارسی: {str(e)}")
            return ""
    
    def _convert_srt_to_ass(self, srt_file: Path, ass_file: Path, config: dict) -> None:
        """تبدیل فایل SRT به ASS برای رندر بهتر متن فارسی"""
        try:
            import pysrt
            
            # خواندن فایل SRT
            subs = pysrt.open(str(srt_file), encoding='utf-8')
            
            # ایجاد فایل ASS
            ass_content = f"""[Script Info]
Title: Persian Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{config['font']},{config['fontsize']},&H{self._color_to_hex(config['color'])},&H{self._color_to_hex(config['color'])},&H{self._color_to_hex(config['outline_color'])},&H00000000,{1 if config.get('bold', False) else 0},{1 if config.get('italic', False) else 0},0,0,100,100,0,0,1,{config['outline_width']},0,2,10,10,{config['margin_v']},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
            
            # تبدیل هر زیرنویس
            for sub in subs:
                start_time = self._srt_time_to_ass_time(sub.start)
                end_time = self._srt_time_to_ass_time(sub.end)
                text = sub.text.replace('\n', '\\N')  # تبدیل خط جدید
                ass_content += f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{text}\n"
            
            # ذخیره فایل ASS
            with open(ass_file, 'w', encoding='utf-8') as f:
                f.write(ass_content)
                
        except Exception as e:
            print(f"❌ خطا در تبدیل SRT به ASS: {str(e)}")
            # در صورت خطا، فایل SRT اصلی را کپی کن
            import shutil
            shutil.copy2(srt_file, ass_file)
    
    def _srt_time_to_ass_time(self, srt_time) -> str:
        """تبدیل زمان SRT به فرمت ASS"""
        try:
            # SRT format: 00:00:01,640
            # ASS format: 0:00:01.64
            time_str = str(srt_time)
            time_str = time_str.replace(',', '.')
            return time_str
        except:
            return "0:00:00.00"
    
    def _normalize_persian_text(self, text: str) -> str:
        """نرمال‌سازی متن فارسی برای رندر بهتر"""
        try:
            import unicodedata
            
            # نرمال‌سازی متن فارسی
            normalized_text = unicodedata.normalize('NFC', text)
            
            # جایگزینی کاراکترهای مشکل‌دار
            replacements = {
                'مثلا': 'مثلاً',   # تبدیل به شکل صحیح با لا
                'مثلاًً': 'مثلاً',  # حذف لا اضافی
            }
            
            for old, new in replacements.items():
                normalized_text = normalized_text.replace(old, new)
            
            return normalized_text
            
        except Exception as e:
            print(f"❌ خطا در نرمال‌سازی متن فارسی: {str(e)}")
            return text
    
    def _get_font_path(self, font_name: str) -> str:
        """پیدا کردن مسیر فونت مناسب برای متن فارسی"""
        try:
            import platform
            import os
            system = platform.system()
            
            # مسیرهای فونت‌های مختلف - اولویت با فونت‌های محلی پروژه
            font_paths = {
                "vazirmatn": [
                    # اولویت اول: فونت‌های محلی پروژه
                    os.path.join(os.path.dirname(__file__), "fonts", "Vazirmatn-Regular.ttf"),
                    os.path.join(os.path.dirname(__file__), "fonts", "Vazirmatn-Medium.ttf"),
                    os.path.join(os.path.dirname(__file__), "fonts", "Vazirmatn-Bold.ttf"),
                    os.path.join(os.path.dirname(__file__), "fonts", "Vazirmatn-ExtraBold.ttf"),
                    os.path.join(os.path.dirname(__file__), "fonts", "Vazirmatn-Black.ttf"),
                    # اولویت دوم: فونت‌های سیستم macOS
                    os.path.expanduser("~/Library/Fonts/Vazirmatn-Regular.ttf"),
                    os.path.expanduser("~/Library/Fonts/Vazirmatn-Medium.ttf"),
                    os.path.expanduser("~/Library/Fonts/Vazirmatn-Bold.ttf"),
                    os.path.expanduser("~/Library/Fonts/Vazirmatn-ExtraBold.ttf"),
                    os.path.expanduser("~/Library/Fonts/Vazirmatn-Black.ttf"),
                    # اولویت سوم: فونت‌های سیستم Linux
                    "/usr/share/fonts/truetype/vazirmatn/Vazirmatn-Regular.ttf",
                    "/usr/share/fonts/truetype/vazirmatn/Vazirmatn-Medium.ttf",
                    "/usr/share/fonts/truetype/vazirmatn/Vazirmatn-Bold.ttf",
                    "/usr/share/fonts/truetype/vazirmatn/Vazirmatn-ExtraBold.ttf",
                    "/usr/share/fonts/truetype/vazirmatn/Vazirmatn-Black.ttf",
                    "/usr/share/fonts/opentype/vazirmatn/Vazirmatn-Regular.ttf",
                    "/usr/share/fonts/opentype/vazirmatn/Vazirmatn-Medium.ttf",
                    "/usr/share/fonts/opentype/vazirmatn/Vazirmatn-Bold.ttf",
                    "/usr/share/fonts/opentype/vazirmatn/Vazirmatn-ExtraBold.ttf",
                    "/usr/share/fonts/opentype/vazirmatn/Vazirmatn-Black.ttf",
                    "/usr/local/share/fonts/Vazirmatn-Regular.ttf",
                    "/usr/local/share/fonts/Vazirmatn-Medium.ttf",
                    "/usr/local/share/fonts/Vazirmatn-Bold.ttf",
                    "/usr/local/share/fonts/Vazirmatn-ExtraBold.ttf",
                    "/usr/local/share/fonts/Vazirmatn-Black.ttf",
                    # فونت‌های جایگزین
                    "/System/Library/Fonts/SFArabic.ttf",  # فونت عربی سیستم
                    "/System/Library/Fonts/Helvetica.ttc",
                    "/System/Library/Fonts/Arial.ttf",
                    "/Library/Fonts/Arial.ttf"
                ],
                "Arial": [
                    "/Library/Fonts/Arial Unicode.ttf",  # Arial Unicode که از فارسی پشتیبانی می‌کند
                    "/System/Library/Fonts/SFArabic.ttf",  # فونت عربی سیستم
                    "/System/Library/Fonts/Arial.ttf",
                    "/Library/Fonts/Arial.ttf"
                ],
                "Times New Roman": [
                    "/System/Library/Fonts/Times.ttc",
                    "/Library/Fonts/Times New Roman.ttf"
                ],
                "Courier New": [
                    "/System/Library/Fonts/Courier.ttc",
                    "/Library/Fonts/Courier New.ttf"
                ],
                "Verdana": [
                    "/Library/Fonts/Verdana.ttf",
                    "/System/Library/Fonts/SFArabic.ttf",  # فونت عربی سیستم
                    "/System/Library/Fonts/Helvetica.ttc"
                ],
                "Tahoma": [
                    "/Library/Fonts/Tahoma.ttf",
                    "/System/Library/Fonts/SFArabic.ttf",  # فونت عربی سیستم
                    "/System/Library/Fonts/Helvetica.ttc"
                ],
                "Georgia": [
                    "/System/Library/Fonts/Georgia.ttf",
                    "/Library/Fonts/Georgia.ttf",
                    "/System/Library/Fonts/SFArabic.ttf"  # فونت عربی سیستم
                ],
                "Impact": [
                    "/System/Library/Fonts/Impact.ttf",
                    "/Library/Fonts/Impact.ttf",
                    "/System/Library/Fonts/SFArabic.ttf"  # فونت عربی سیستم
                ],
                "SF Arabic": [
                    "/System/Library/Fonts/SFArabic.ttf",
                    "/System/Library/Fonts/SFArabicRounded.ttf"
                ],
                "Arial Unicode": [
                    "/Library/Fonts/Arial Unicode.ttf",
                    "/System/Library/Fonts/SFArabic.ttf"
                ]
            }
            
            # جستجوی فونت
            if font_name in font_paths:
                for path in font_paths[font_name]:
                    if os.path.exists(path):
                        # برای Vazirmatn در Linux، نام فونت را برگردان نه مسیر
                        if font_name.lower() == 'vazirmatn' and system == 'Linux':
                            return "Vazirmatn"  # نام فونت سیستم
                        return path
            
            # فونت پیش‌فرض برای متن فارسی
            if system == 'Linux':
                default_fonts = [
                    "Vazirmatn",  # فونت Vazirmatn در سیستم
                    "DejaVu Sans",  # فونت‌های DejaVu که از فارسی پشتیبانی می‌کنند
                    "Liberation Sans",
                    "Arial",
                    "Tahoma"
                ]
            else:
                default_fonts = [
                    "/System/Library/Fonts/Helvetica.ttc",
                    "/System/Library/Fonts/Arial.ttf",
                    "/Library/Fonts/Arial.ttf"
                ]
            
            for font_path in default_fonts:
                if system == 'Linux':
                    # در Linux، نام فونت را مستقیماً برگردان
                    return font_path
                elif os.path.exists(font_path):
                    return font_path
            
            return ""
            
        except Exception as e:
            print(f"❌ خطا در پیدا کردن فونت: {str(e)}")
            return ""
    
    def _color_to_hex(self, color_name: str) -> str:
        """تبدیل نام رنگ به فرمت hex برای FFmpeg (BGR format)"""
        color_map = {
            "white": "ffffff",
            "yellow": "00ffff",  # BGR: yellow = 00ffff
            "red": "0000ff",     # BGR: red = 0000ff
            "green": "00ff00",   # BGR: green = 00ff00
            "blue": "ff0000",    # BGR: blue = ff0000
            "black": "000000",
            "orange": "00a5ff",  # BGR: orange = 00a5ff
            "purple": "800080",  # BGR: purple = 800080
            "pink": "c0c0ff",    # BGR: pink = c0c0ff
            "cyan": "ffff00",    # BGR: cyan = ffff00
            "lime": "00ff00",    # BGR: lime = 00ff00
            "magenta": "ff00ff", # BGR: magenta = ff00ff
            "silver": "c0c0c0",
            "gold": "00d7ff",    # BGR: gold = 00d7ff
            "gray": "808080",
            "none": "00000000"   # شفاف
        }
        return color_map.get(color_name.lower(), "ffffff")
    
    def _get_alignment(self, position: str) -> int:
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
        return alignment_map.get(position.lower(), 2)  # پیش‌فرض: پایین وسط
