#!/usr/bin/env python3
"""
تست YouTube API
Test YouTube API Integration
"""

import os
import sys
from youtube_api_client import YouTubeAPIClient, YouTubeSimpleAPI, test_youtube_api

def test_with_api_key():
    """تست با API Key"""
    print("🧪 تست YouTube API با API Key...")
    
    # دریافت API Key از متغیر محیطی
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("❌ متغیر محیطی YOUTUBE_API_KEY تنظیم نشده")
        print("💡 تنظیم کنید: export YOUTUBE_API_KEY='your_api_key'")
        return False
    
    try:
        client = YouTubeSimpleAPI(api_key)
        
        # تست دریافت اطلاعات ویدیو
        print("📺 تست دریافت اطلاعات ویدیو...")
        video_info = client.get_video_info("dQw4w9WgXcQ")
        
        if video_info:
            snippet = video_info.get('snippet', {})
            title = snippet.get('title', 'نامشخص')
            channel = snippet.get('channelTitle', 'نامشخص')
            duration = video_info.get('contentDetails', {}).get('duration', 'نامشخص')
            
            print(f"✅ عنوان: {title}")
            print(f"📺 کانال: {channel}")
            print(f"⏱️ مدت زمان: {duration}")
            
            # تست جستجو
            print("\n🔍 تست جستجوی ویدیو...")
            search_results = client.search_videos("python programming", max_results=3)
            
            if search_results:
                print(f"✅ {len(search_results)} نتیجه یافت شد:")
                for i, video in enumerate(search_results, 1):
                    title = video.get('snippet', {}).get('title', 'نامشخص')
                    print(f"  {i}. {title}")
            else:
                print("❌ نتیجه جستجو یافت نشد")
            
            return True
        else:
            print("❌ اطلاعات ویدیو دریافت نشد")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست API Key: {e}")
        return False

def test_with_oauth():
    """تست با OAuth2"""
    print("\n🔐 تست YouTube API با OAuth2...")
    
    if not os.path.exists('youtube_credentials.json'):
        print("❌ فایل youtube_credentials.json یافت نشد")
        print("💡 فایل credentials را کپی کنید")
        return False
    
    try:
        client = YouTubeAPIClient()
        
        # تست دریافت اطلاعات ویدیو
        print("📺 تست دریافت اطلاعات ویدیو...")
        video_info = client.get_video_info("dQw4w9WgXcQ")
        
        if video_info:
            snippet = video_info.get('snippet', {})
            title = snippet.get('title', 'نامشخص')
            channel = snippet.get('channelTitle', 'نامشخص')
            
            print(f"✅ عنوان: {title}")
            print(f"📺 کانال: {channel}")
            
            # تست جستجو
            print("\n🔍 تست جستجوی ویدیو...")
            search_results = client.search_videos("python programming", max_results=3)
            
            if search_results:
                print(f"✅ {len(search_results)} نتیجه یافت شد:")
                for i, video in enumerate(search_results, 1):
                    title = video.get('snippet', {}).get('title', 'نامشخص')
                    print(f"  {i}. {title}")
            else:
                print("❌ نتیجه جستجو یافت نشد")
            
            return True
        else:
            print("❌ اطلاعات ویدیو دریافت نشد")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست OAuth2: {e}")
        return False

def test_dubbing_integration():
    """تست یکپارچگی با سیستم دوبله"""
    print("\n🎬 تست یکپارچگی با سیستم دوبله...")
    
    try:
        from dubbing_functions import VideoDubbingApp
        
        # تست با API Key
        api_key = "AIzaSyBNYpugB8Ezrpmk-U7Yvp9ynClEJLCETMo"
        youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        
        app = VideoDubbingApp(api_key, youtube_api_key)
        
        if app.youtube_client:
            print("✅ YouTube API client در سیستم دوبله فعال است")
            
            # تست اعتبارسنجی ویدیو
            test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            is_valid = app.validate_youtube_video(test_url)
            
            if is_valid:
                print("✅ اعتبارسنجی ویدیو موفق")
            else:
                print("❌ اعتبارسنجی ویدیو ناموفق")
            
            return True
        else:
            print("⚠️ YouTube API client در سیستم دوبله فعال نیست")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست یکپارچگی: {e}")
        return False

def main():
    """تست اصلی"""
    print("🚀 تست کامل YouTube API Integration")
    print("=" * 50)
    
    # تست API Key
    api_key_success = test_with_api_key()
    
    # تست OAuth2
    oauth_success = test_with_oauth()
    
    # تست یکپارچگی
    integration_success = test_dubbing_integration()
    
    # خلاصه نتایج
    print("\n📊 خلاصه نتایج:")
    print(f"🔑 API Key: {'✅' if api_key_success else '❌'}")
    print(f"🔐 OAuth2: {'✅' if oauth_success else '❌'}")
    print(f"🎬 یکپارچگی: {'✅' if integration_success else '❌'}")
    
    if api_key_success or oauth_success:
        print("\n🎉 حداقل یک روش اتصال کار می‌کند!")
    else:
        print("\n❌ هیچ روش اتصالی کار نمی‌کند")
        print("\n💡 راه‌حل‌ها:")
        print("1. تنظیم متغیر محیطی: export YOUTUBE_API_KEY='your_key'")
        print("2. کپی فایل youtube_credentials.json")
        print("3. فعال‌سازی YouTube Data API v3 در Google Cloud Console")

if __name__ == "__main__":
    main()
