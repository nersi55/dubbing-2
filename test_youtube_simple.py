#!/usr/bin/env python3
"""
تست ساده YouTube API
Simple YouTube API Test
"""

import os
import sys

def test_imports():
    """تست import کردن وابستگی‌ها"""
    print("🧪 تست import وابستگی‌ها...")
    
    try:
        from youtube_api_client import YouTubeAPIClient, YouTubeSimpleAPI
        print("✅ youtube_api_client import شد")
    except ImportError as e:
        print(f"❌ خطا در import youtube_api_client: {e}")
        return False
    
    try:
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        print("✅ Google API libraries import شدند")
    except ImportError as e:
        print(f"❌ خطا در import Google API libraries: {e}")
        return False
    
    return True

def test_api_key():
    """تست با API Key"""
    print("\n🔑 تست API Key...")
    
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("⚠️ متغیر محیطی YOUTUBE_API_KEY تنظیم نشده")
        print("💡 تنظیم کنید: export YOUTUBE_API_KEY='your_api_key'")
        return False
    
    try:
        from youtube_api_client import YouTubeSimpleAPI
        client = YouTubeSimpleAPI(api_key)
        
        # تست ساده
        video_info = client.get_video_info("dQw4w9WgXcQ")
        if video_info:
            title = video_info.get('snippet', {}).get('title', 'نامشخص')
            print(f"✅ API Key کار می‌کند - عنوان: {title}")
            return True
        else:
            print("❌ API Key کار نمی‌کند")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست API Key: {e}")
        return False

def test_oauth():
    """تست با OAuth2"""
    print("\n🔐 تست OAuth2...")
    
    if not os.path.exists('youtube_credentials.json'):
        print("⚠️ فایل youtube_credentials.json یافت نشد")
        print("💡 فایل credentials را کپی کنید")
        return False
    
    try:
        from youtube_api_client import YouTubeAPIClient
        client = YouTubeAPIClient()
        
        # تست ساده
        video_info = client.get_video_info("dQw4w9WgXcQ")
        if video_info:
            title = video_info.get('snippet', {}).get('title', 'نامشخص')
            print(f"✅ OAuth2 کار می‌کند - عنوان: {title}")
            return True
        else:
            print("❌ OAuth2 کار نمی‌کند")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست OAuth2: {e}")
        return False

def main():
    """تست اصلی"""
    print("🚀 تست ساده YouTube API")
    print("=" * 30)
    
    # تست import
    if not test_imports():
        print("\n❌ تست import ناموفق")
        print("💡 نصب کنید: ./install_youtube_api.sh")
        return
    
    # تست API Key
    api_success = test_api_key()
    
    # تست OAuth2
    oauth_success = test_oauth()
    
    # خلاصه
    print("\n📊 خلاصه:")
    print(f"🔑 API Key: {'✅' if api_success else '❌'}")
    print(f"🔐 OAuth2: {'✅' if oauth_success else '❌'}")
    
    if api_success or oauth_success:
        print("\n🎉 حداقل یک روش کار می‌کند!")
    else:
        print("\n❌ هیچ روشی کار نمی‌کند")
        print("\n💡 راه‌حل‌ها:")
        print("1. نصب وابستگی‌ها: ./install_youtube_api.sh")
        print("2. تنظیم API Key: export YOUTUBE_API_KEY='your_key'")
        print("3. کپی فایل credentials: cp youtube_credentials.json .")

if __name__ == "__main__":
    main()
