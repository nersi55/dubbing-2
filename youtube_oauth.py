"""
YouTube OAuth Authentication for Video Dubbing
احراز هویت OAuth یوتیوب برای دوبله ویدیو
"""

import os
import json
import pickle
from pathlib import Path
from typing import Optional, Dict, Any
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# تنظیمات OAuth
SCOPES = [
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/youtube.force-ssl'
]

# فایل‌های ذخیره‌سازی
CREDENTIALS_FILE = 'youtube_credentials.json'
TOKEN_FILE = 'youtube_token.pickle'

logger = logging.getLogger(__name__)

class YouTubeOAuthManager:
    """مدیریت احراز هویت OAuth یوتیوب"""
    
    def __init__(self, api_key: str):
        """
        Initialize OAuth manager
        
        Args:
            api_key: YouTube Data API v3 key
        """
        self.api_key = api_key
        self.credentials = None
        self.youtube_service = None
        
    def authenticate(self) -> bool:
        """
        احراز هویت OAuth
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # بررسی وجود فایل توکن
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, 'rb') as token:
                    self.credentials = pickle.load(token)
            
            # بررسی اعتبار توکن
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    # تازه‌سازی توکن
                    self.credentials.refresh(Request())
                else:
                    # شروع فرآیند OAuth جدید
                    if not self._start_oauth_flow():
                        return False
                
                # ذخیره توکن جدید
                with open(TOKEN_FILE, 'wb') as token:
                    pickle.dump(self.credentials, token)
            
            # ایجاد سرویس YouTube
            self.youtube_service = build('youtube', 'v3', 
                                       credentials=self.credentials,
                                       developerKey=self.api_key)
            
            logger.info("✅ احراز هویت OAuth موفقیت‌آمیز بود")
            return True
            
        except Exception as e:
            logger.error(f"❌ خطا در احراز هویت OAuth: {str(e)}")
            return False
    
    def _start_oauth_flow(self) -> bool:
        """
        شروع فرآیند OAuth
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(CREDENTIALS_FILE):
                logger.error(f"❌ فایل {CREDENTIALS_FILE} یافت نشد")
                logger.info("📝 برای دریافت فایل credentials:")
                logger.info("1. به Google Cloud Console بروید")
                logger.info("2. پروژه خود را انتخاب کنید")
                logger.info("3. APIs & Services > Credentials")
                logger.info("4. Create Credentials > OAuth 2.0 Client IDs")
                logger.info("5. Application type: Desktop application")
                logger.info("6. فایل JSON را دانلود و به عنوان youtube_credentials.json ذخیره کنید")
                return False
            
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            
            # تنظیمات اضافی برای حل مشکل 400/403
            # استفاده از redirect URI موجود در فایل credentials
            if 'redirect_uris' in flow.client_config.get('installed', {}):
                redirect_uris = flow.client_config['installed']['redirect_uris']
                if redirect_uris:
                    flow.redirect_uri = redirect_uris[0]
                else:
                    flow.redirect_uri = 'http://localhost:8080'
            else:
                flow.redirect_uri = 'http://localhost:8080'
            
            self.credentials = flow.run_local_server(
                port=0,  # استفاده از پورت تصادفی
                open_browser=True,
                success_message='احراز هویت موفقیت‌آمیز بود! می‌توانید این پنجره را ببندید.',
                authorization_prompt_message='برای ادامه، لطفاً در مرورگر احراز هویت کنید.'
            )
            
            logger.info("✅ فرآیند OAuth تکمیل شد")
            return True
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ خطا در فرآیند OAuth: {error_msg}")
            
            if "access_denied" in error_msg or "403" in error_msg:
                logger.error("🔧 خطای 403: access_denied")
                logger.info("📋 راه‌حل:")
                logger.info("1. OAuth consent screen را تنظیم کنید")
                logger.info("2. User type: External انتخاب کنید")
                logger.info("3. Test users اضافه کنید")
                logger.info("4. Scopes مجاز کنید")
                logger.info("5. python fix_oauth_403.py را اجرا کنید")
            
            return False
    
    def get_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        دریافت اطلاعات ویدیو
        
        Args:
            video_id: شناسه ویدیو یوتیوب
            
        Returns:
            Dict: اطلاعات ویدیو یا None در صورت خطا
        """
        try:
            if not self.youtube_service:
                if not self.authenticate():
                    return None
            
            request = self.youtube_service.videos().list(
                part='snippet,contentDetails,status',
                id=video_id
            )
            response = request.execute()
            
            if response['items']:
                video = response['items'][0]
                return {
                    'id': video['id'],
                    'title': video['snippet']['title'],
                    'description': video['snippet']['description'],
                    'channel_title': video['snippet']['channelTitle'],
                    'duration': video['contentDetails']['duration'],
                    'view_count': video.get('statistics', {}).get('viewCount', '0'),
                    'upload_date': video['snippet']['publishedAt'],
                    'thumbnail': video['snippet']['thumbnails']['high']['url'],
                    'privacy_status': video['status']['privacyStatus']
                }
            return None
            
        except HttpError as e:
            logger.error(f"❌ خطا در دریافت اطلاعات ویدیو: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ خطای غیرمنتظره: {str(e)}")
            return None
    
    def get_video_transcript(self, video_id: str, language: str = 'en') -> Optional[str]:
        """
        دریافت متن ویدیو از YouTube
        
        Args:
            video_id: شناسه ویدیو یوتیوب
            language: زبان متن (پیش‌فرض: en)
            
        Returns:
            str: متن ویدیو یا None در صورت خطا
        """
        try:
            if not self.youtube_service:
                if not self.authenticate():
                    return None
            
            # دریافت لیست captions
            captions = self.youtube_service.captions().list(
                part='snippet',
                videoId=video_id
            ).execute()
            
            if not captions['items']:
                logger.warning("⚠️ زیرنویس برای این ویدیو یافت نشد")
                return None
            
            # جستجوی زیرنویس با زبان مورد نظر
            caption_id = None
            for caption in captions['items']:
                if caption['snippet']['language'] == language:
                    caption_id = caption['id']
                    break
            
            if not caption_id:
                # استفاده از اولین زیرنویس موجود
                caption_id = captions['items'][0]['id']
                logger.info(f"📝 استفاده از زیرنویس زبان: {captions['items'][0]['snippet']['language']}")
            
            # دانلود زیرنویس
            caption_response = self.youtube_service.captions().download(
                id=caption_id,
                tfmt='srt'
            ).execute()
            
            return caption_response.decode('utf-8')
            
        except HttpError as e:
            logger.error(f"❌ خطا در دریافت متن ویدیو: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ خطای غیرمنتظره: {str(e)}")
            return None
    
    def is_authenticated(self) -> bool:
        """
        بررسی وضعیت احراز هویت
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        return self.credentials is not None and self.credentials.valid
    
    def revoke_credentials(self):
        """لغو مجوزهای OAuth"""
        try:
            if self.credentials:
                self.credentials.revoke(Request())
            
            # حذف فایل توکن
            if os.path.exists(TOKEN_FILE):
                os.remove(TOKEN_FILE)
            
            self.credentials = None
            self.youtube_service = None
            
            logger.info("✅ مجوزهای OAuth لغو شدند")
            
        except Exception as e:
            logger.error(f"❌ خطا در لغو مجوزها: {str(e)}")

def create_credentials_template():
    """ایجاد فایل نمونه برای credentials"""
    template = {
        "installed": {
            "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
            "project_id": "your-project-id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "YOUR_CLIENT_SECRET",
            "redirect_uris": ["http://localhost"]
        }
    }
    
    with open('youtube_credentials_template.json', 'w') as f:
        json.dump(template, f, indent=2)
    
    print("📝 فایل نمونه youtube_credentials_template.json ایجاد شد")
    print("🔧 این فایل را ویرایش کرده و به عنوان youtube_credentials.json ذخیره کنید")

if __name__ == "__main__":
    # تست عملکرد
    api_key = "AIzaSyATk52Q35uG1Ups7q-kCatJEUjXAO2C--k"
    
    oauth_manager = YouTubeOAuthManager(api_key)
    
    if oauth_manager.authenticate():
        print("✅ احراز هویت موفقیت‌آمیز بود")
        
        # تست دریافت اطلاعات ویدیو
        video_id = "dQw4w9WgXcQ"  # Rick Roll
        video_info = oauth_manager.get_video_info(video_id)
        
        if video_info:
            print(f"📹 عنوان ویدیو: {video_info['title']}")
            print(f"📺 کانال: {video_info['channel_title']}")
        else:
            print("❌ خطا در دریافت اطلاعات ویدیو")
    else:
        print("❌ احراز هویت ناموفق بود")
        create_credentials_template()
