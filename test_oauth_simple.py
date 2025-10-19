#!/usr/bin/env python3
"""
تست ساده OAuth
Simple OAuth Test
"""

import os
import sys
from pathlib import Path

# اضافه کردن مسیر پروژه
sys.path.append(str(Path(__file__).parent))

def test_oauth_simple():
    """تست ساده OAuth"""
    print("🧪 تست ساده OAuth یوتیوب")
    print("=" * 40)
    
    try:
        from youtube_oauth import YouTubeOAuthManager
        
        # API Key
        api_key = "AIzaSyATk52Q35uG1Ups7q-kCatJEUjXAO2C--k"
        
        # بررسی فایل credentials
        if not os.path.exists('youtube_credentials.json'):
            print("❌ فایل youtube_credentials.json یافت نشد")
            print("📝 لطفاً فایل credentials را از Google Cloud Console دریافت کنید")
            return False
        
        print("✅ فایل credentials یافت شد")
        
        # ایجاد OAuth manager
        oauth_manager = YouTubeOAuthManager(api_key)
        
        # تست احراز هویت
        print("🔐 در حال احراز هویت...")
        print("📱 مرورگر باز می‌شود...")
        
        if oauth_manager.authenticate():
            print("✅ احراز هویت موفقیت‌آمیز بود!")
            
            # تست دریافت اطلاعات ویدیو
            print("\n📹 تست دریافت اطلاعات ویدیو...")
            video_id = "dQw4w9WgXcQ"  # Rick Roll
            video_info = oauth_manager.get_video_info(video_id)
            
            if video_info:
                print("✅ اطلاعات ویدیو دریافت شد:")
                print(f"   عنوان: {video_info['title']}")
                print(f"   کانال: {video_info['channel_title']}")
                print(f"   مدت: {video_info['duration']}")
            else:
                print("❌ خطا در دریافت اطلاعات ویدیو")
            
            return True
        else:
            print("❌ احراز هویت ناموفق بود")
            print("\n🔧 راه‌حل:")
            print("1. OAuth consent screen را تنظیم کنید")
            print("2. User type: External انتخاب کنید")
            print("3. Test users اضافه کنید")
            print("4. Scopes مجاز کنید")
            print("5. فایل OAUTH_403_FIX.md را مطالعه کنید")
            return False
            
    except Exception as e:
        print(f"❌ خطا: {str(e)}")
        return False

def main():
    """اجرای اصلی"""
    success = test_oauth_simple()
    
    if success:
        print("\n🎉 OAuth کار می‌کند!")
        print("📚 می‌توانید از API استفاده کنید:")
        print("   POST /download-youtube-oauth")
    else:
        print("\n❌ OAuth کار نمی‌کند")
        print("📚 راهنمای حل مشکل: OAUTH_403_FIX.md")

if __name__ == "__main__":
    main()
