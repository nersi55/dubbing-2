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
from youtube_api_client import YouTubeAPIClient, YouTubeSimpleAPI


class VideoDubbingApp:
    def __init__(self, api_key: str, youtube_api_key: str = None):
        """Initialize the dubbing application with Google API key and optional YouTube API key"""
        self.api_key = api_key
        self.youtube_api_key = youtube_api_key
        genai.configure(api_key=api_key)
        self.client = genai_client.Client(api_key=api_key)
        
        # Initialize YouTube API client if key is provided
        self.youtube_client = None
        if youtube_api_key:
            try:
                self.youtube_client = YouTubeSimpleAPI(youtube_api_key)
                print("✅ YouTube API client initialized")
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize YouTube API client: {e}")
                self.youtube_client = None
        
        # Create necessary directories
        self.work_dir = Path("dubbing_work")
        self.work_dir.mkdir(exist_ok=True)
        self.segments_dir = self.work_dir / "dubbed_segments"
        self.segments_dir.mkdir(exist_ok=True)
        # Shared session identifier used for naming outputs (YouTube ID or derived local ID)
        self.session_id: Optional[str] = None

    # ===== Session/ID helpers =====
    def set_session_id(self, id_str: str) -> None:
        """Set a stable identifier for naming SRTs and output videos."""
        try:
            if not id_str:
                return
            # Sanitize: keep only safe filename chars
            safe = re.sub(r"[^a-zA-Z0-9_-]", "", id_str)
            if not safe:
                return
            # Keep it reasonably short
            self.session_id = safe[:32]
        except Exception:
            pass

    def _generate_random_id(self, length: int = 5) -> str:
        import random, string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def _ensure_session_id(self) -> None:
        if not self.session_id:
            self.session_id = self._generate_random_id(5)

    def set_session_id_from_local_path(self, file_path: str) -> None:
        """Derive identifier from local filename stem, fallback to random if too short."""
        try:
            stem = Path(file_path).stem
            stem = re.sub(r"[^a-zA-Z0-9_-]", "", stem)
            if len(stem) < 6:
                stem = f"{stem}_{self._generate_random_id(5)}" if stem else self._generate_random_id(5)
            self.set_session_id(stem[:11])
        except Exception:
            self._ensure_session_id()

    # ===== Path helpers (ID-aware with legacy fallback) =====
    def _srt_en_path(self) -> Path:
        if self.session_id:
            return self.work_dir / f"audio_{self.session_id}.srt"
        return self.work_dir / 'audio.srt'

    def _srt_fa_path(self) -> Path:
        if self.session_id:
            return self.work_dir / f"audio_{self.session_id}_fa.srt"
        return self.work_dir / 'audio_fa.srt'

    def _output_video_path(self) -> Path:
        # Unified final output name
        if self.session_id:
            return self.work_dir / f"dubbed_video_{self.session_id}.mp4"
        return self.work_dir / 'dubbed_video.mp4'
        
    def clean_previous_files(self):
        """پاکسازی فایل‌های قبلی"""
        files_to_clean = [
            "input_video.mp4", "audio.wav", "final_dubbed_video.mp4"
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
            # Set session id from YouTube URL (11-char ID) when available
            try:
                vid = self._extract_video_id(url)
                if vid:
                    self.set_session_id(vid)
            except Exception:
                pass
            # Clean previous files
            for file in self.work_dir.glob('temp_video*'):
                file.unlink()
            
            format_option = 'bestvideo+bestaudio/best'
            temp_filename = str(self.work_dir / 'temp_video.%(ext)s')

            # استراتژی‌های چندگانه دانلود با استفاده از کوکی‌ها
            strategies = []
            base_opts = {
                'format': format_option,
                'outtmpl': temp_filename,
                'nocheckcertificate': True,
                'ignoreerrors': False,
                'no_warnings': False,
                'quiet': False,
                'socket_timeout': 30,
                'retries': 1,
                'fragment_retries': 1,
                'extractor_retries': 1,
            }

            # افزودن کوکی اگر موجود است
            if os.path.exists('cookies.txt'):
                base_opts['cookiefile'] = 'cookies.txt'
                print("🍪 استفاده از فایل کوکی: cookies.txt")
            else:
                print("⚠️ فایل cookies.txt یافت نشد - دانلود بدون کوکی")

            # 1) IPv6 + پیش‌فرض
            s1 = {**base_opts, 'prefer_ipv6': True, 'source_address': '::'}
            strategies.append(("IPv6+Default", s1))

            # 2) IPv4 + Chrome UA
            s2 = {**base_opts,
                  'prefer_ipv6': False,
                  'source_address': '0.0.0.0',
                  'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                  'referer': 'https://www.youtube.com/'}
            strategies.append(("IPv4+Chrome", s2))

            # 3) IPv4 + Googlebot UA (گاهی 403 را دور می‌زند)
            s3 = {**base_opts,
                  'prefer_ipv6': False,
                  'source_address': '0.0.0.0',
                  'user_agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                  'referer': 'https://www.youtube.com/'}
            strategies.append(("IPv4+Googlebot", s3))

            downloaded_file = None
            last_error = None
            for name, opts in strategies:
                try:
                    print(f"🧪 تلاش دانلود با استراتژی: {name} ...")
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        downloaded_file = ydl.prepare_filename(info)
                    if downloaded_file and os.path.exists(downloaded_file):
                        print(f"✅ دانلود موفق با {name}")
                        break
                except Exception as e:
                    last_error = str(e)
                    print(f"❌ استراتژی {name} شکست خورد: {str(e)[:120]}...")
                    continue
            
            if not downloaded_file:
                # اگر هیچ‌کدام موفق نشد، استراتژی‌های موجود کار نکردند
                if last_error:
                    print(f"❌ همه استراتژی‌ها شکست خوردند. آخرین خطا: {last_error[:200]}...")
                else:
                    print("❌ همه استراتژی‌ها شکست خوردند.")
                raise Exception("strategies_failed")

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
            if not self._fallback_download(url):
                # تلاش با دانلودگر پیشرفته
                if not self._advanced_download(url):
                    # پیشنهاد راه‌حل آپلود فایل
                    self._suggest_file_upload_solution()
                    return False
            return True
    
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
    
    def _advanced_download(self, url: str) -> bool:
        """دانلود با روش‌های پیشرفته"""
        try:
            print("🚀 تلاش با دانلودگر پیشرفته...")
            
            # Import advanced downloader
            from advanced_youtube_downloader import AdvancedYouTubeDownloader
            
            downloader = AdvancedYouTubeDownloader(self.work_dir)
            success = downloader.download_with_retry(url)
            
            if success:
                print("✅ دانلودگر پیشرفته موفق بود!")
                return True
            else:
                print("❌ دانلودگر پیشرفته هم شکست خورد")
                return False
                
        except ImportError:
            print("❌ دانلودگر پیشرفته در دسترس نیست")
            return False
        except Exception as e:
            print(f"❌ خطا در دانلودگر پیشرفته: {str(e)}")
            return False
    
    def _suggest_file_upload_solution(self):
        """پیشنهاد راه‌حل آپلود فایل"""
        print("\n" + "="*60)
        print("🚫 همه روش‌های دانلود از YouTube شکست خوردند!")
        print("="*60)
        print("\n💡 راه‌حل‌های پیشنهادی:")
        print("\n1️⃣ **آپلود فایل ویدیو (پیشنهادی):**")
        print("   • ویدیو را روی کامپیوتر شخصی دانلود کنید")
        print("   • فایل را به سرور آپلود کنید")
        print("   • از راه‌حل آپلود فایل استفاده کنید")
        print("   📖 راهنما: python file_upload_solution.py")
        
        print("\n2️⃣ **استفاده از VPN:**")
        print("   • VPN روی سرور راه‌اندازی کنید")
        print("   • IP سرور را تغییر دهید")
        print("   📖 راهنما: VPN_SETUP_GUIDE.md")
        
        print("\n3️⃣ **تغییر سرور:**")
        print("   • سرور جدید در منطقه‌ای متفاوت ایجاد کنید")
        print("   • پروژه را روی سرور جدید کلون کنید")
        
        print("\n4️⃣ **استفاده از سرویس‌های دانلود:**")
        print("   • از API های دانلود ویدیو استفاده کنید")
        print("   • سرویس‌های Cloud برای دانلود")
        
        print("\n🔧 دستورات مفید:")
        print("   python file_upload_solution.py  # راه‌حل آپلود فایل")
        print("   python setup_proxies.py        # راه‌اندازی پروکسی")
        print("   cat VPN_SETUP_GUIDE.md         # راهنمای VPN")
        
        print("\n" + "="*60)
    
    def get_youtube_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        دریافت اطلاعات ویدیو از YouTube API
        
        Args:
            video_id: شناسه ویدیو YouTube
            
        Returns:
            اطلاعات ویدیو یا None
        """
        if not self.youtube_client:
            print("⚠️ YouTube API client not initialized")
            return None
        
        try:
            return self.youtube_client.get_video_info(video_id)
        except Exception as e:
            print(f"❌ خطا در دریافت اطلاعات ویدیو: {e}")
            return None
    
    def validate_youtube_video(self, url: str) -> bool:
        """
        بررسی معتبر بودن ویدیو YouTube
        
        Args:
            url: لینک ویدیو YouTube
            
        Returns:
            True اگر ویدیو معتبر باشد
        """
        if not self.youtube_client:
            print("⚠️ YouTube API client not initialized, skipping validation")
            return True
        
        try:
            # Extract video ID from URL
            video_id = self._extract_video_id(url)
            if not video_id:
                print("❌ شناسه ویدیو یافت نشد")
                return False
            
            # Get video info from YouTube API
            video_info = self.get_youtube_video_info(video_id)
            if not video_info:
                print("❌ ویدیو یافت نشد یا در دسترس نیست")
                return False
            
            # Check if video is available
            snippet = video_info.get('snippet', {})
            title = snippet.get('title', 'نامشخص')
            duration = video_info.get('contentDetails', {}).get('duration', 'نامشخص')
            
            print(f"✅ ویدیو معتبر: {title}")
            print(f"⏱️ مدت زمان: {duration}")
            
            return True
            
        except Exception as e:
            print(f"❌ خطا در بررسی ویدیو: {e}")
            return False
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """استخراج شناسه ویدیو از URL"""
        patterns = [
            r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})',
            r'(?:youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None

    def extract_transcript_from_youtube(self, url: str, language: str = "Auto-detect") -> bool:
        """استخراج زیرنویس از یوتیوب"""
        try:
            print(f"🔍 استخراج زیرنویس از یوتیوب: {url}")
            
            # Extract video ID from URL
            video_id = self._extract_video_id(url)
            if not video_id:
                print("❌ شناسه ویدیو یافت نشد")
                return False
            
            print(f"📺 شناسه ویدیو: {video_id}")
            # Keep the session id aligned with video id
            self.set_session_id(video_id)
            
            # Validate video with YouTube API if available
            if self.youtube_client and not self.validate_youtube_video(url):
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
                srt_path = self._srt_en_path()
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
            
            # Ensure we have an id for naming when running locally
            if not self.session_id:
                try:
                    # Derive from existing input_video if possible
                    possible_input = self.work_dir / 'input_video.mp4'
                    if possible_input.exists():
                        self.set_session_id_from_local_path(str(possible_input))
                except Exception:
                    self._ensure_session_id()

            srt_path = self._srt_en_path()
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
            srt_path = self._srt_en_path()
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
        """ترجمه زیرنویس‌ها - ترجمه تکه‌ای برای جلوگیری از قطع شدن خروجی مدل"""
        try:
            srt_path = self._srt_en_path()
            if not srt_path.exists():
                print("❌ فایل SRT انگلیسی پیدا نشد")
                return False

            import re, math, time
            with open(srt_path, 'r', encoding='utf-8') as f:
                srt_content = f.read()

            # 1) Parse SRT to entries: index, start, end, text
            pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\d+\n|\Z)'
            src_entries = re.findall(pattern, srt_content, re.DOTALL)
            if not src_entries:
                print("❌ ساختار SRT معتبر نیست")
                return False

            print(f"📝 تعداد زیرنویس‌های انگلیسی: {len(src_entries)}")

            # 2) Chunking helper (limit by count or characters)
            def chunk_entries(entries, max_items=60, max_chars=5000):
                chunks, cur, cur_chars = [], [], 0
                for idx, st, en, tx in entries:
                    block = f"{idx}\n{st} --> {en}\n{tx.strip()}\n\n"
                    if cur and (len(cur) >= max_items or cur_chars + len(block) > max_chars):
                        chunks.append(cur)
                        cur, cur_chars = [], 0
                    cur.append((idx, st, en, tx))
                    cur_chars += len(block)
                if cur:
                    chunks.append(cur)
                return chunks

            chunks = chunk_entries(src_entries)
            print(f"📦 فایل به {len(chunks)} تکه تقسیم شد")

            # 3) Build prompt per chunk and translate
            def build_chunk_srt(chunk):
                # شماره‌ها را از 1 شروع می‌کنیم تا مدل سردرگم نشود
                lines = []
                for i, (idx, st, en, tx) in enumerate(chunk, start=1):
                    lines.append(str(i))
                    lines.append(f"{st} --> {en}")
                    lines.append(tx.strip())
                    lines.append("")
                return "\n".join(lines)

            def translate_chunk(chunk_srt):
                models = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-flash-lite-latest"]
                for m in models:
                    try:
                        model = genai.GenerativeModel(
                            m,
                            safety_settings={
                                genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                                genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
                                genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                                genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                            }
                        )
                        if target_language == "Persian (FA)":
                            prompt = f"""کل همین فایل SRT کوچک را به فارسی ترجمه کن و فقط ساختار SRT را بدون هیچ توضیح اضافه حفظ کن.
اعداد و بازه‌های زمانی را دست نزن، فقط متن را ترجمه کن.

{chunk_srt}

ترجمه:"""
                        else:
                            prompt = f"""Translate this small SRT file to {target_language} preserving exact SRT structure (numbers and timings unchanged), translate text only.

{chunk_srt}

Translation:"""

                        resp = model.generate_content(prompt)
                        time.sleep(2)
                        return self._clean_srt_response(resp.text.strip())
                    except Exception as e:
                        print(f"⚠️ خطا در مدل {m}: {str(e)}")
                        time.sleep(3)
                        continue
                return None

            # 4) Parse translated chunk into (text) list by aligning with original times
            def parse_translated_chunk(translated_srt):
                if not translated_srt:
                    return []
                out = re.findall(pattern, translated_srt, re.DOTALL)
                # returns list of tuples (idx, start, end, text)
                return out

            # 5) Rebuild final FA SRT with original indices and timings
            fa_lines = []
            cursor = 0
            total_translated = 0
            
            for i, chunk in enumerate(chunks, 1):
                print(f"🔄 ترجمه تکه {i}/{len(chunks)} ({len(chunk)} زیرنویس)...")
                chunk_srt = build_chunk_srt(chunk)
                tr_srt = translate_chunk(chunk_srt)
                tr_blocks = parse_translated_chunk(tr_srt)

                # align by order
                n = min(len(tr_blocks), len(chunk))
                for j in range(n):
                    orig_idx, orig_st, orig_en, _ = chunk[j]
                    _, _, _, tr_text = tr_blocks[j]
                    fa_lines.append(str(orig_idx))
                    fa_lines.append(f"{orig_st} --> {orig_en}")
                    fa_lines.append(tr_text.strip())
                    fa_lines.append("")
                    total_translated += 1
                
                print(f"   ✅ {n}/{len(chunk)} زیرنویس ترجمه شد")
                cursor += len(chunk)

            translated_path = self._srt_fa_path()
            with open(translated_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(fa_lines).strip() + "\n")

            # Final check
            src_count = len(src_entries)
            fa_count = total_translated
            print(f"📊 نتیجه نهایی: انگلیسی {src_count} زیرنویس | فارسی {fa_count} زیرنویس")
            
            if fa_count < src_count:
                print(f"⚠️ هشدار: {src_count - fa_count} زیرنویس ترجمه نشدند (خروجی مدل ناقص)")
                print("💡 می‌توانید دوباره اجرا کنید تا تکمیل شود")
            else:
                print("✅ تمام زیرنویس‌ها با موفقیت ترجمه شدند")

            print("✅ ترجمه تکه‌ای SRT با موفقیت انجام شد")
            return True
            
        except Exception as e:
            print(f"❌ خطا در ترجمه: {str(e)}")
            import traceback
            traceback.print_exc()
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
            srt_path = self._srt_fa_path()
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
            srt_path = self._srt_fa_path()
            
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
                output_path = self._output_video_path()
                
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
            srt_path = self._srt_fa_path()
            
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
                    "italic": False,
                    "time_offset_ms": 0
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
                output_path = self._output_video_path()
                print("🎬 ایجاد ویدیو با زیرنویس...")
                
                # ساخت فیلتر زیرنویس با فایل ASS سفارشی
                # پیدا کردن مسیر فونت
                font_name = sub_config['font']
                font_path = self._get_font_path(font_name)
                if font_path:
                    print(f"✅ فونت زیرنویس: {font_name} → {font_path}")
                    # برای libass، نام خانوادهٔ فونت بهتر از مسیر فایل است
                    if font_name.lower() == 'vazirmatn':
                        font_name = 'Vazirmatn'
                else:
                    print(f"⚠️ فونت زیرنویس: {font_name} (فونت سیستم)")
                
                # ایجاد فایل ASS سفارشی برای کنترل بهتر موقعیت
                temp_ass = temp_dir / "custom_subtitles.ass"
                self._create_custom_ass_file(temp_ass, temp_srt, sub_config, font_name)
                
                # استفاده از فایل ASS سفارشی
                # برای جلوگیری از تاخیر ناشی از start_time غیر صفر در ویدیوهای MP4
                # ابتدا PTS ویدیو را به 0 بازنشانی می‌کنیم و سپس زیرنویس را اعمال می‌کنیم
                subtitle_filter = f"setpts=PTS-STARTPTS,subtitles={temp_ass.absolute()}"
                
                # ساخت فیلترهای ترکیبی
                if fixed_config['enabled'] and fixed_config['text'].strip():
                    # اگر متن ثابت فعال است، ابتدا ویدیو با زیرنویس ایجاد کن
                    temp_video = temp_dir / "temp_with_subtitles.mp4"
                    
                    # مرحله 1: ایجاد ویدیو با زیرنویس
                    subprocess.run([
                        'ffmpeg', '-i', str(video_path),
                        '-vf', subtitle_filter,
                        '-af', 'asetpts=PTS-STARTPTS',
                        '-c:v', 'libx264', '-c:a', 'aac',
                        '-y', str(temp_video)
                    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                    # مرحله 2: اضافه کردن متن ثابت
                    fixed_text_filter = self._create_fixed_text_filter(fixed_config)
                    if fixed_text_filter:
                        subprocess.run([
                            'ffmpeg', '-i', str(temp_video),
                            '-vf', fixed_text_filter,
                            '-af', 'asetpts=PTS-STARTPTS',
                            '-c:v', 'libx264', '-c:a', 'aac',
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
                        '-af', 'asetpts=PTS-STARTPTS',
                        '-c:v', 'libx264', '-c:a', 'aac',
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
            
            # نرمال‌سازی ملایم برای جلوگیری از نمایش مربع (ligatures/harakat)
            normalized_text = self._normalize_persian_text(text)
            
            # پیدا کردن فونت
            font_path = self._get_font_path(font_name)
            if font_path:
                print(f"✅ فونت متن ثابت: {font_name} → {font_path}")
                final_font = 'Vazirmatn' if font_name.lower() == 'vazirmatn' else font_name
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
            
            # تنظیم اندازه فونت (برای bold کمی بزرگتر)
            final_fontsize = int(fontsize * 1.2) if config.get('bold', False) else fontsize
            
            # escape کردن متن برای drawtext
            escaped_text = normalized_text.replace("'", "\\'").replace(":", "\\:")
            
            # استفاده از subtitles filter به جای drawtext برای پشتیبانی بهتر از فارسی
            import tempfile
            temp_ass = tempfile.NamedTemporaryFile(mode='w', suffix='.ass', delete=False, encoding='utf-8')
            
            # تنظیم موقعیت برای ASS
            position = config.get('position', 'bottom_center')
            if position == 'bottom_center':
                alignment = 2  # center
                margin_v = margin_bottom
            elif position == 'bottom_left':
                alignment = 1  # left
                margin_v = margin_bottom
            elif position == 'bottom_right':
                alignment = 3  # right
                margin_v = margin_bottom
            elif position == 'top_center':
                alignment = 8  # top center
                margin_v = config.get('margin_v', 10)
            elif position == 'top_left':
                alignment = 7  # top left
                margin_v = config.get('margin_v', 10)
            elif position == 'top_right':
                alignment = 9  # top right
                margin_v = config.get('margin_v', 10)
            else:
                alignment = 2  # center
                margin_v = margin_bottom
            
            # تنظیم رنگ برای ASS (BGR format)
            r = color_hex[4:6]
            g = color_hex[2:4]
            b = color_hex[0:2]
            ass_color = f"&H{b}{g}{r}&"
            
            # تنظیم رنگ زمینه
            background_color = config.get('background_color', 'none')
            if background_color != 'none':
                bg_color_hex = self._color_to_hex(background_color)
                bg_r = bg_color_hex[4:6]
                bg_g = bg_color_hex[2:4]
                bg_b = bg_color_hex[0:2]
                bg_color = f"&H{bg_b}{bg_g}{bg_r}&"
            else:
                bg_color = "&H000000&"  # transparent
            
            # محتوای فایل ASS
            ass_content = f"""[Script Info]
Title: Fixed Text
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: FixedText,{final_font},{final_fontsize},{ass_color},{ass_color},{bg_color},{bg_color},1,0,0,0,100,100,0,0,1,2,0,{alignment},10,10,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,99:59:59.99,FixedText,,0,0,0,,{normalized_text}
"""
            
            temp_ass.write(ass_content)
            temp_ass.close()
            
            # استفاده از subtitles filter
            filter_text = f"subtitles='{temp_ass.name}'"
            
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
            
            # تنظیم فونت
            font_name = config.get('font', 'vazirmatn')
            font_path = self._get_font_path(font_name)
            if font_path:
                print(f"✅ فونت زیرنویس: {font_name} → {font_path}")
                final_font = 'Vazirmatn' if font_name.lower() == 'vazirmatn' else font_name
            else:
                print(f"⚠️ فونت زیرنویس: {font_name} (فونت سیستم)")
                final_font = font_name
            
            # ایجاد فایل ASS
            ass_content = f"""[Script Info]
Title: Persian Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{final_font},{config['fontsize']},&H{self._color_to_hex(config['color'])},&H{self._color_to_hex(config['color'])},&H{self._color_to_hex(config['outline_color'])},&H00000000,{1 if config.get('bold', False) else 0},{1 if config.get('italic', False) else 0},0,0,100,100,0,0,1,{config['outline_width']},0,2,10,10,{config['margin_v']},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
            
            # تبدیل هر زیرنویس
            for sub in subs:
                start_time = self._srt_time_to_ass_time(sub.start)
                end_time = self._srt_time_to_ass_time(sub.end)
                # نرمال‌سازی متن فارسی برای رندر بهتر
                normalized_text = self._normalize_persian_text(sub.text)
                text = normalized_text.replace('\n', '\\N')  # تبدیل خط جدید
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
            import re
            
            # حذف BOM و کنترل‌های جهت‌دهی و فواصل صفرعرض مشکل‌زا
            control_chars = [
                '\ufeff',  # BOM
                '\u200e', '\u200f',  # LRM, RLM
                '\u202a', '\u202b', '\u202c', '\u202d', '\u202e',  # bidi controls
                '\u200b', '\u200c', '\u200d', '\u2060',  # zero-width chars (ZWS, ZWNJ, ZWJ, word joiner)
            ]
            for ch in control_chars:
                text = text.replace(ch, ' ' if ch in ['\u200b', '\u200c', '\u200d', '\u2060'] else '')

            # تبدیل فرم‌های نمایشی عربی به یونیکد سازگار (حل مشکل «لا»)
            # NFKC پرزنتیشن‌فرم‌ها را به حروف پایه تبدیل می‌کند
            normalized_text = unicodedata.normalize('NFKC', text)
            
            # تبدیل کاراکترهای عربی به فارسی
            arabic_to_persian = {
                'ي': 'ی', 'ك': 'ک', 'ة': 'ه', 'أ': 'ا', 'إ': 'ا',
                'آ': 'آ', 'ؤ': 'و', 'ئ': 'ی', 'ء': 'ء', 'ة': 'ه'
            }
            
            for arabic, persian in arabic_to_persian.items():
                normalized_text = normalized_text.replace(arabic, persian)
            
            # حذف کشیده و حرکات عربی که ممکن است مربع نمایش داده شوند
            # Tatweel
            normalized_text = normalized_text.replace('\u0640', '')
            # Harakat: 064B..065F, 0670 (superscript alef), and Quranic marks 06D6..06ED
            normalized_text = re.sub('[\u064B-\u065F\u0670\u06D6-\u06ED]', '', normalized_text)

            # جایگزینی کاراکترهای مشکل‌دار و نمونه‌های رایج
            replacements = {
                'مثلا': 'مثلاً',   # تبدیل به شکل صحیح با لا
                'مثلاًً': 'مثلاً',  # حذف لا اضافی
                # اطمینان از رندر صحیح لا با حروف پایه پس از NFKC
                '\ufefb': 'لا', '\ufefc': 'لا',  # presentation forms
                '\ufef7': 'لا', '\ufef8': 'لا',  # with hamza above
                '\ufef5': 'لا', '\ufef6': 'لا',  # with maddah
                'لی': 'لی',        # اطمینان از رندر صحیح لی
                'لو': 'لو',        # اطمینان از رندر صحیح لو
                'لر': 'لر',        # اطمینان از رندر صحیح لر
                'لم': 'لم',        # اطمینان از رندر صحیح لم
                'لن': 'لن',        # اطمینان از رندر صحیح لن
                'له': 'له',        # اطمینان از رندر صحیح له
                'لی': 'لی',        # اطمینان از رندر صحیح لی
                'لو': 'لو',        # اطمینان از رندر صحیح لو
                'لر': 'لر',        # اطمینان از رندر صحیح لر
                'لم': 'لم',        # اطمینان از رندر صحیح لم
                'لن': 'لن',        # اطمینان از رندر صحیح لن
                'له': 'له',        # اطمینان از رندر صحیح له
            }
            
            for old, new in replacements.items():
                normalized_text = normalized_text.replace(old, new)
            
            # حذف کاراکترهای کنترل و غیرقابل چاپ باقیمانده
            normalized_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', normalized_text)
            
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
    
    def _create_custom_ass_file(self, ass_path, srt_path, config, font_name):
        """ایجاد فایل ASS سفارشی برای کنترل بهتر موقعیت زیرنویس"""
        try:
            # خواندن فایل SRT
            srt_content = srt_path.read_text(encoding='utf-8')
            
            # تنظیم موقعیت و alignment
            position = config.get('position', 'bottom_center')
            if position == 'top_center':
                alignment = 8  # top center
                margin_v = config.get('margin_v', 0)
            elif position == 'top_left':
                alignment = 7  # top left
                margin_v = config.get('margin_v', 0)
            elif position == 'top_right':
                alignment = 9  # top right
                margin_v = config.get('margin_v', 0)
            elif position == 'bottom_center':
                alignment = 2  # bottom center
                margin_v = config.get('margin_v', 20)
            elif position == 'bottom_left':
                alignment = 1  # bottom left
                margin_v = config.get('margin_v', 20)
            elif position == 'bottom_right':
                alignment = 3  # bottom right
                margin_v = config.get('margin_v', 20)
            else:
                alignment = 2  # default bottom center
                margin_v = config.get('margin_v', 20)
            
            # تنظیم رنگ متن (BGR format)
            color_hex = self._color_to_hex(config['color'])
            r = color_hex[4:6]
            g = color_hex[2:4]
            b = color_hex[0:2]
            text_color = f"&H{b}{g}{r}&"
            
            # تنظیم رنگ حاشیه
            outline_color_hex = self._color_to_hex(config['outline_color'])
            outline_r = outline_color_hex[4:6]
            outline_g = outline_color_hex[2:4]
            outline_b = outline_color_hex[0:2]
            outline_color = f"&H{outline_b}{outline_g}{outline_r}&"
            
            # تنظیم رنگ زمینه
            if config.get('background_color', 'none') != 'none':
                bg_color_hex = self._color_to_hex(config['background_color'])
                bg_r = bg_color_hex[4:6]
                bg_g = bg_color_hex[2:4]
                bg_b = bg_color_hex[0:2]
                bg_color = f"&H{bg_b}{bg_g}{bg_r}&"
                border_style = 4  # rounded box
            else:
                bg_color = "&H000000&"  # transparent
                border_style = 0  # no box
            
            # تنظیم سایه
            if config.get('shadow', 0) > 0:
                shadow_color_hex = self._color_to_hex(config['shadow_color'])
                sr = shadow_color_hex[4:6]
                sg = shadow_color_hex[2:4]
                sb = shadow_color_hex[0:2]
                shadow_color = f"&H{sb}{sg}{sr}&"
                shadow = config['shadow']
            else:
                shadow_color = "&H000000&"
                shadow = 0
            
            # ایجاد محتوای فایل ASS
            ass_content = f"""[Script Info]
Title: Custom Subtitles
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{config['fontsize']},{text_color},{text_color},{outline_color},{bg_color},{1 if config.get('bold', False) else 0},{1 if config.get('italic', False) else 0},0,0,100,100,0,0,{border_style},{config.get('outline_width', 0)},{shadow},{alignment},10,10,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
            
            # تبدیل SRT به ASS
            import re
            srt_pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\d+\n|\Z)'
            matches = re.findall(srt_pattern, srt_content, re.DOTALL)
            
            for match in matches:
                index, start_time, end_time, text = match
                # تبدیل فرمت زمان SRT به ASS با دقت صدم ثانیه و امکان offset
                def to_ass(t_str: str) -> str:
                    hh, mm, rest = t_str.split(':')
                    ss, ms = rest.split(',')
                    total_ms = int(hh) * 3600000 + int(mm) * 60000 + int(ss) * 1000 + int(ms)
                    total_ms += int(config.get('time_offset_ms', 0) or 0)
                    if total_ms < 0:
                        total_ms = 0
                    h = total_ms // 3600000
                    rem = total_ms % 3600000
                    m = rem // 60000
                    rem = rem % 60000
                    s = rem // 1000
                    cs = (rem % 1000) // 10  # centiseconds
                    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"
                start_ass = to_ass(start_time)
                end_ass = to_ass(end_time)
                
                # پاک‌سازی متن
                clean_text = text.strip().replace('\n', '\\N')
                
                # اضافه کردن خط به فایل ASS
                ass_content += f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{clean_text}\n"
            
            # نوشتن فایل ASS
            with open(ass_path, 'w', encoding='utf-8') as f:
                f.write(ass_content)
                
            print(f"✅ فایل ASS سفارشی ایجاد شد: {ass_path}")
            print(f"   📍 موقعیت: {position} (alignment: {alignment})")
            print(f"   📏 فاصله: {margin_v}px")
            
        except Exception as e:
            print(f"❌ خطا در ایجاد فایل ASS سفارشی: {str(e)}")
            import traceback
            traceback.print_exc()

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
