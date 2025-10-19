#!/usr/bin/env python3
"""
YouTube Data API v3 Client
کلاینت YouTube Data API v3
"""

import os
import pickle
import requests
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from typing import Optional, Dict, Any, List
import json

class YouTubeAPIClient:
    """کلاینت YouTube Data API v3"""
    
    def __init__(self, credentials_file: str = 'youtube_credentials.json', api_key: str = None):
        """
        Initialize YouTube API Client
        
        Args:
            credentials_file: مسیر فایل credentials
            api_key: API Key ساده (اختیاری)
        """
        self.credentials_file = credentials_file
        self.api_key = api_key
        self.service = None
        self.setup_api()
    
    def setup_api(self):
        """تنظیم YouTube Data API"""
        if self.api_key:
            # استفاده از API Key ساده
            self.service = build('youtube', 'v3', developerKey=self.api_key)
            return
        
        # استفاده از OAuth2
        SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
        creds = None
        
        # بررسی وجود token ذخیره شده
        if os.path.exists('youtube_token.pickle'):
            try:
                with open('youtube_token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            except Exception as e:
                print(f"خطا در خواندن token: {e}")
                creds = None
        
        # اگر credentials معتبر نیست، از فایل credentials استفاده کن
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"خطا در refresh token: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(f"فایل credentials یافت نشد: {self.credentials_file}")
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    raise Exception(f"خطا در احراز هویت: {e}")
            
            # ذخیره credentials برای استفاده بعدی
            try:
                with open('youtube_token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            except Exception as e:
                print(f"خطا در ذخیره token: {e}")
        
        self.service = build('youtube', 'v3', credentials=creds)
    
    def get_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        دریافت اطلاعات ویدیو
        
        Args:
            video_id: شناسه ویدیو YouTube
            
        Returns:
            اطلاعات ویدیو یا None در صورت خطا
        """
        try:
            request = self.service.videos().list(
                part="snippet,contentDetails,statistics,status",
                id=video_id
            )
            response = request.execute()
            
            if response['items']:
                return response['items'][0]
            else:
                print(f"ویدیو یافت نشد: {video_id}")
                return None
                
        except Exception as e:
            print(f"خطا در دریافت اطلاعات ویدیو {video_id}: {e}")
            return None
    
    def search_videos(self, query: str, max_results: int = 10) -> Optional[List[Dict[str, Any]]]:
        """
        جستجوی ویدیوها
        
        Args:
            query: عبارت جستجو
            max_results: حداکثر تعداد نتایج
            
        Returns:
            لیست ویدیوها یا None در صورت خطا
        """
        try:
            request = self.service.search().list(
                part="snippet",
                q=query,
                type="video",
                maxResults=max_results,
                order="relevance"
            )
            response = request.execute()
            return response.get('items', [])
            
        except Exception as e:
            print(f"خطا در جستجوی ویدیو: {e}")
            return None
    
    def get_video_duration(self, video_id: str) -> Optional[str]:
        """
        دریافت مدت زمان ویدیو
        
        Args:
            video_id: شناسه ویدیو
            
        Returns:
            مدت زمان به فرمت ISO 8601 یا None
        """
        video_info = self.get_video_info(video_id)
        if video_info:
            return video_info.get('contentDetails', {}).get('duration')
        return None
    
    def get_video_statistics(self, video_id: str) -> Optional[Dict[str, str]]:
        """
        دریافت آمار ویدیو
        
        Args:
            video_id: شناسه ویدیو
            
        Returns:
            آمار ویدیو یا None
        """
        video_info = self.get_video_info(video_id)
        if video_info:
            return video_info.get('statistics', {})
        return None
    
    def get_video_snippet(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        دریافت اطلاعات کلی ویدیو
        
        Args:
            video_id: شناسه ویدیو
            
        Returns:
            اطلاعات کلی یا None
        """
        video_info = self.get_video_info(video_id)
        if video_info:
            return video_info.get('snippet', {})
        return None
    
    def is_video_available(self, video_id: str) -> bool:
        """
        بررسی در دسترس بودن ویدیو
        
        Args:
            video_id: شناسه ویدیو
            
        Returns:
            True اگر ویدیو در دسترس باشد
        """
        video_info = self.get_video_info(video_id)
        if not video_info:
            return False
        
        status = video_info.get('status', {})
        return status.get('uploadStatus') == 'processed' and status.get('privacyStatus') == 'public'
    
    def get_channel_info(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """
        دریافت اطلاعات کانال
        
        Args:
            channel_id: شناسه کانال
            
        Returns:
            اطلاعات کانال یا None
        """
        try:
            request = self.service.channels().list(
                part="snippet,statistics",
                id=channel_id
            )
            response = request.execute()
            
            if response['items']:
                return response['items'][0]
            else:
                print(f"کانال یافت نشد: {channel_id}")
                return None
                
        except Exception as e:
            print(f"خطا در دریافت اطلاعات کانال {channel_id}: {e}")
            return None

class YouTubeSimpleAPI:
    """کلاینت ساده YouTube API با API Key"""
    
    def __init__(self, api_key: str):
        """
        Initialize Simple YouTube API Client
        
        Args:
            api_key: YouTube Data API v3 Key
        """
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
    
    def get_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """دریافت اطلاعات ویدیو با API Key"""
        url = f"{self.base_url}/videos"
        params = {
            'part': 'snippet,contentDetails,statistics',
            'id': video_id,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('items'):
                return data['items'][0]
            else:
                print(f"ویدیو یافت نشد: {video_id}")
                return None
                
        except Exception as e:
            print(f"خطا در دریافت اطلاعات ویدیو: {e}")
            return None
    
    def search_videos(self, query: str, max_results: int = 10) -> Optional[List[Dict[str, Any]]]:
        """جستجوی ویدیوها"""
        url = f"{self.base_url}/search"
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'maxResults': max_results,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('items', [])
            
        except Exception as e:
            print(f"خطا در جستجوی ویدیو: {e}")
            return None

def test_youtube_api():
    """تست YouTube API"""
    print("🧪 تست YouTube API...")
    
    # تست با API Key (اگر موجود باشد)
    api_key = os.getenv('YOUTUBE_API_KEY')
    if api_key:
        print("📱 تست با API Key...")
        client = YouTubeSimpleAPI(api_key)
        
        # تست دریافت اطلاعات ویدیو
        video_info = client.get_video_info("dQw4w9WgXcQ")
        if video_info:
            print("✅ دریافت اطلاعات ویدیو موفق")
            print(f"📺 عنوان: {video_info.get('snippet', {}).get('title', 'نامشخص')}")
        else:
            print("❌ دریافت اطلاعات ویدیو ناموفق")
    
    # تست با OAuth2 (اگر فایل credentials موجود باشد)
    if os.path.exists('youtube_credentials.json'):
        print("🔐 تست با OAuth2...")
        try:
            client = YouTubeAPIClient()
            
            # تست دریافت اطلاعات ویدیو
            video_info = client.get_video_info("dQw4w9WgXcQ")
            if video_info:
                print("✅ دریافت اطلاعات ویدیو با OAuth2 موفق")
                print(f"📺 عنوان: {video_info.get('snippet', {}).get('title', 'نامشخص')}")
            else:
                print("❌ دریافت اطلاعات ویدیو با OAuth2 ناموفق")
        except Exception as e:
            print(f"❌ خطا در OAuth2: {e}")
    
    print("🏁 تست تمام شد")

if __name__ == "__main__":
    test_youtube_api()
