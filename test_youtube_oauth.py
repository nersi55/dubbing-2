#!/usr/bin/env python3
"""
تست OAuth یوتیوب
Test YouTube OAuth
"""

import os
import sys
import json
from pathlib import Path

# اضافه کردن مسیر پروژه
sys.path.append(str(Path(__file__).parent))

from youtube_oauth import YouTubeOAuthManager, create_credentials_template

def test_oauth_setup():
    """تست راه‌اندازی OAuth"""
    print("🧪 تست راه‌اندازی OAuth یوتیوب")
    print("=" * 50)
    
    # API Key
    api_key = "AIzaSyATk52Q35uG1Ups7q-kCatJEUjXAO2C--k"
    
    # بررسی وجود فایل credentials
    if not os.path.exists('youtube_credentials.json'):
        print("❌ فایل youtube_credentials.json یافت نشد")
        print("📝 ایجاد فایل نمونه...")
        create_credentials_template()
        print("🔧 لطفاً فایل youtube_credentials_template.json را ویرایش کرده")
        print("   و به عنوان youtube_credentials.json ذخیره کنید")
        return False
    
    print("✅ فایل credentials یافت شد")
    
    # ایجاد OAuth manager
    oauth_manager = YouTubeOAuthManager(api_key)
    
    # تست احراز هویت
    print("🔐 در حال احراز هویت...")
    if oauth_manager.authenticate():
        print("✅ احراز هویت موفقیت‌آمیز بود")
        return True
    else:
        print("❌ احراز هویت ناموفق بود")
        return False

def test_video_info():
    """تست دریافت اطلاعات ویدیو"""
    print("\n🧪 تست دریافت اطلاعات ویدیو")
    print("=" * 50)
    
    api_key = "AIzaSyATk52Q35uG1Ups7q-kCatJEUjXAO2C--k"
    oauth_manager = YouTubeOAuthManager(api_key)
    
    if not oauth_manager.authenticate():
        print("❌ احراز هویت ناموفق")
        return False
    
    # تست با ویدیو معروف
    test_video_id = "dQw4w9WgXcQ"  # Rick Roll
    print(f"📹 تست با ویدیو: {test_video_id}")
    
    video_info = oauth_manager.get_video_info(test_video_id)
    if video_info:
        print("✅ اطلاعات ویدیو دریافت شد:")
        print(f"   عنوان: {video_info['title']}")
        print(f"   کانال: {video_info['channel_title']}")
        print(f"   مدت: {video_info['duration']}")
        print(f"   وضعیت: {video_info['privacy_status']}")
        return True
    else:
        print("❌ خطا در دریافت اطلاعات ویدیو")
        return False

def test_transcript():
    """تست دریافت متن ویدیو"""
    print("\n🧪 تست دریافت متن ویدیو")
    print("=" * 50)
    
    api_key = "AIzaSyATk52Q35uG1Ups7q-kCatJEUjXAO2C--k"
    oauth_manager = YouTubeOAuthManager(api_key)
    
    if not oauth_manager.authenticate():
        print("❌ احراز هویت ناموفق")
        return False
    
    # تست با ویدیو معروف
    test_video_id = "dQw4w9WgXcQ"  # Rick Roll
    print(f"📝 تست دریافت متن ویدیو: {test_video_id}")
    
    transcript = oauth_manager.get_video_transcript(test_video_id, "en")
    if transcript:
        print("✅ متن ویدیو دریافت شد:")
        print(f"   طول متن: {len(transcript)} کاراکتر")
        print(f"   نمونه: {transcript[:200]}...")
        return True
    else:
        print("❌ خطا در دریافت متن ویدیو")
        return False

def test_download_oauth():
    """تست دانلود با OAuth"""
    print("\n🧪 تست دانلود با OAuth")
    print("=" * 50)
    
    try:
        from dubbing_functions import VideoDubbingApp
        
        api_key = "AIzaSyATk52Q35uG1Ups7q-kCatJEUjXAO2C--k"
        dubbing_app = VideoDubbingApp(api_key)
        
        # تست URL
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        print(f"📥 تست دانلود: {test_url}")
        
        success = dubbing_app.download_youtube_video_oauth(test_url, api_key)
        if success:
            print("✅ دانلود با OAuth موفقیت‌آمیز بود")
            
            # بررسی فایل‌های ایجاد شده
            video_file = dubbing_app.work_dir / 'input_video.mp4'
            audio_file = dubbing_app.work_dir / 'audio.wav'
            
            if video_file.exists():
                print(f"   ویدیو: {video_file} ({video_file.stat().st_size} bytes)")
            if audio_file.exists():
                print(f"   صدا: {audio_file} ({audio_file.stat().st_size} bytes)")
            
            return True
        else:
            print("❌ دانلود با OAuth ناموفق بود")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست دانلود: {str(e)}")
        return False

def test_api_endpoint():
    """تست endpoint API"""
    print("\n🧪 تست endpoint API")
    print("=" * 50)
    
    try:
        import requests
        import json
        
        # URL API
        api_url = "http://localhost:8000/download-youtube-oauth"
        
        # داده‌های درخواست
        data = {
            "api_key": "AIzaSyATk52Q35uG1Ups7q-kCatJEUjXAO2C--k",
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "target_language": "Persian (FA)",
            "voice": "Fenrir",
            "use_oauth": True,
            "transcript_language": "en"
        }
        
        print(f"📡 ارسال درخواست به: {api_url}")
        print(f"📋 داده‌ها: {json.dumps(data, indent=2)}")
        
        # ارسال درخواست
        response = requests.post(api_url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ درخواست API موفقیت‌آمیز بود:")
            print(f"   Job ID: {result.get('job_id')}")
            print(f"   وضعیت: {result.get('status')}")
            print(f"   پیام: {result.get('message')}")
            return True
        else:
            print(f"❌ خطا در API: {response.status_code}")
            print(f"   پاسخ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست API: {str(e)}")
        return False

def main():
    """اجرای تمام تست‌ها"""
    print("🚀 شروع تست‌های OAuth یوتیوب")
    print("=" * 60)
    
    tests = [
        ("راه‌اندازی OAuth", test_oauth_setup),
        ("اطلاعات ویدیو", test_video_info),
        ("متن ویدیو", test_transcript),
        ("دانلود OAuth", test_download_oauth),
        ("API Endpoint", test_api_endpoint)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 اجرای تست: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ خطا در تست {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # خلاصه نتایج
    print("\n" + "=" * 60)
    print("📊 خلاصه نتایج:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ موفق" if result else "❌ ناموفق"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📈 نتیجه کلی: {passed}/{total} تست موفق")
    
    if passed == total:
        print("🎉 همه تست‌ها موفقیت‌آمیز بودند!")
    else:
        print("⚠️ برخی تست‌ها ناموفق بودند. لطفاً مشکلات را بررسی کنید.")

if __name__ == "__main__":
    main()
