#!/usr/bin/env python3
"""
دانلودگر پیشرفته YouTube با دور زدن محدودیت‌ها
Advanced YouTube Downloader with Bypass Methods
"""

import os
import sys
import subprocess
import time
import random
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

class AdvancedYouTubeDownloader:
    def __init__(self, work_dir: Path):
        self.work_dir = work_dir
        self.user_agents = [
            # Desktop browsers
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            
            # Mobile browsers
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            
            # Bots and crawlers
            'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)',
            'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)',
        ]
        
        self.proxy_list = self._load_proxy_list()
        self.retry_delays = [1, 2, 5, 10, 30]  # seconds
        
    def _load_proxy_list(self) -> List[str]:
        """بارگذاری لیست پروکسی‌ها"""
        proxy_file = Path("proxy_list.txt")
        if proxy_file.exists():
            try:
                with open(proxy_file, 'r') as f:
                    return [line.strip() for line in f if line.strip()]
            except:
                pass
        return []
    
    def _get_random_user_agent(self) -> str:
        """انتخاب تصادفی User-Agent"""
        return random.choice(self.user_agents)
    
    def _get_random_proxy(self) -> Optional[str]:
        """انتخاب تصادفی پروکسی"""
        if self.proxy_list:
            return random.choice(self.proxy_list)
        return None
    
    def _create_advanced_config(self, method: str) -> Dict[str, Any]:
        """ایجاد تنظیمات پیشرفته"""
        base_config = {
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'no_warnings': True,
            'quiet': True,
            # 🔥 تنظیمات IPv6
            'prefer_ipv6': True,  # اجبار به استفاده از IPv6
            'source_address': '::',  # استفاده از IPv6 برای اتصال
            'user_agent': self._get_random_user_agent(),
            'referer': 'https://www.youtube.com/',
            'socket_timeout': 30,
            'retries': 1,
            'fragment_retries': 1,
            'extractor_retries': 1,
            'http_chunk_size': 1048576,
            'headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            }
        }
        
        if method == "mobile":
            base_config.update({
                'format': 'worst[height<=480]/worst',
                'user_agent': random.choice([
                    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
                    'Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
                ]),
                'headers': {
                    **base_config['headers'],
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                }
            })
        elif method == "bot":
            base_config.update({
                'format': 'worst[height<=360]/worst',
                'user_agent': random.choice([
                    'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                    'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)'
                ]),
            })
        elif method == "minimal":
            base_config.update({
                'format': 'worst',
                'user_agent': 'Mozilla/5.0 (compatible; yt-dlp)',
                'headers': {
                    'Accept': '*/*',
                    'User-Agent': 'Mozilla/5.0 (compatible; yt-dlp)',
                }
            })
        
        # اضافه کردن پروکسی اگر موجود باشد
        proxy = self._get_random_proxy()
        if proxy:
            base_config['proxy'] = proxy
            print(f"🌐 استفاده از پروکسی: {proxy}")
        
        return base_config
    
    def download_with_method(self, url: str, method: str) -> bool:
        """دانلود با روش مشخص"""
        try:
            print(f"🧪 تست روش {method}...")
            
            config = self._create_advanced_config(method)
            temp_filename = str(self.work_dir / f'temp_video_{method}.%(ext)s')
            config['outtmpl'] = temp_filename
            
            import yt_dlp
            
            with yt_dlp.YoutubeDL(config) as ydl:
                info = ydl.extract_info(url, download=True)
                if info is None:
                    print(f"   ❌ {method}: اطلاعات ویدیو دریافت نشد")
                    return False
                
                downloaded_file = ydl.prepare_filename(info)
                
                if os.path.exists(downloaded_file):
                    # تغییر نام فایل
                    _, file_extension = os.path.splitext(downloaded_file)
                    final_filename = self.work_dir / f'input_video{file_extension}'
                    os.rename(downloaded_file, str(final_filename))
                    
                    # تبدیل به MP4 اگر لازم باشد
                    if file_extension.lower() != '.mp4':
                        mp4_path = self.work_dir / 'input_video.mp4'
                        subprocess.run([
                            'ffmpeg', '-i', str(final_filename), 
                            '-c', 'copy', str(mp4_path), '-y'
                        ], check=True, capture_output=True)
                        final_filename.unlink()
                    
                    # استخراج صدا
                    audio_path = self.work_dir / 'audio.wav'
                    subprocess.run([
                        'ffmpeg', '-i', str(self.work_dir / 'input_video.mp4'), 
                        '-vn', str(audio_path), '-y'
                    ], check=True, capture_output=True)
                    
                    print(f"✅ {method} موفق بود!")
                    return True
                else:
                    print(f"   ❌ {method}: فایل دانلود نشد")
                    return False
                    
        except Exception as e:
            print(f"   ❌ {method}: {str(e)[:100]}...")
            return False
    
    def download_with_retry(self, url: str) -> bool:
        """دانلود با تلاش‌های متعدد"""
        methods = ["mobile", "bot", "minimal"]
        
        for attempt in range(3):  # 3 تلاش
            print(f"\n🔄 تلاش {attempt + 1}/3...")
            
            for method in methods:
                # تاخیر تصادفی بین درخواست‌ها
                if attempt > 0:
                    delay = random.uniform(2, 8)
                    print(f"⏳ تاخیر {delay:.1f} ثانیه...")
                    time.sleep(delay)
                
                if self.download_with_method(url, method):
                    return True
            
            # تاخیر بیشتر بین تلاش‌ها
            if attempt < 2:
                delay = self.retry_delays[attempt]
                print(f"⏳ تاخیر {delay} ثانیه قبل از تلاش بعدی...")
                time.sleep(delay)
        
        return False
    
    def create_proxy_list_template(self):
        """ایجاد قالب لیست پروکسی"""
        template = """# لیست پروکسی‌ها
# هر خط یک پروکسی به فرمت: http://user:pass@host:port
# یا: http://host:port
# یا: socks5://host:port

# مثال:
# http://proxy1.example.com:8080
# http://user:pass@proxy2.example.com:3128
# socks5://proxy3.example.com:1080

# برای دریافت پروکسی‌های رایگان:
# https://www.proxy-list.download/
# https://free-proxy-list.net/
"""
        
        with open('proxy_list_template.txt', 'w', encoding='utf-8') as f:
            f.write(template)
        
        print("📝 قالب لیست پروکسی ایجاد شد: proxy_list_template.txt")

def main():
    """تابع اصلی"""
    print("🚀 دانلودگر پیشرفته YouTube")
    print("=" * 40)
    
    # تست URL
    test_url = "https://www.youtube.com/shorts/JYgjuBwJwXU?feature=share"
    
    # ایجاد پوشه کار
    work_dir = Path("dubbing_work")
    work_dir.mkdir(exist_ok=True)
    
    # ایجاد دانلودگر
    downloader = AdvancedYouTubeDownloader(work_dir)
    
    # ایجاد قالب پروکسی
    downloader.create_proxy_list_template()
    
    # تلاش دانلود
    print(f"📥 تلاش دانلود: {test_url}")
    success = downloader.download_with_retry(test_url)
    
    if success:
        print("\n🎉 دانلود موفق بود!")
        return True
    else:
        print("\n❌ دانلود شکست خورد")
        print("\n💡 راه‌حل‌های پیشنهادی:")
        print("1. استفاده از VPN")
        print("2. اضافه کردن پروکسی به proxy_list.txt")
        print("3. تغییر IP سرور")
        print("4. آپلود فایل ویدیو به جای دانلود")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
