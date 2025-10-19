#!/usr/bin/env python3
"""
تست OAuth با API
Test OAuth with API
"""

import requests
import json
import time

def test_oauth_api():
    """تست OAuth با API"""
    print("🧪 تست OAuth با API")
    print("=" * 50)
    
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
    
    try:
        # ارسال درخواست
        response = requests.post(api_url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ درخواست OAuth API موفقیت‌آمیز بود:")
            print(f"   Job ID: {result.get('job_id')}")
            print(f"   وضعیت: {result.get('status')}")
            print(f"   پیام: {result.get('message')}")
            
            # بررسی وضعیت کار
            job_id = result.get('job_id')
            if job_id:
                check_job_status(job_id)
            
            return True
        else:
            print(f"❌ خطا در API: {response.status_code}")
            print(f"   پاسخ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست API: {str(e)}")
        return False

def check_job_status(job_id):
    """بررسی وضعیت کار"""
    print(f"\n🔍 بررسی وضعیت کار: {job_id}")
    
    status_url = f"http://localhost:8000/job-status/{job_id}"
    
    for i in range(20):  # حداکثر 20 بار بررسی
        try:
            response = requests.get(status_url, timeout=10)
            if response.status_code == 200:
                status = response.json()
                print(f"   وضعیت: {status.get('status')}")
                print(f"   پیشرفت: {status.get('progress')}%")
                print(f"   مرحله: {status.get('current_step')}")
                print(f"   پیام: {status.get('message')}")
                
                if status.get('status') == 'completed':
                    print("✅ کار تکمیل شد!")
                    print(f"   نتیجه: {status.get('result')}")
                    return True
                elif status.get('status') == 'failed':
                    print("❌ کار ناموفق بود!")
                    return False
                
                time.sleep(10)  # 10 ثانیه صبر
            else:
                print(f"❌ خطا در بررسی وضعیت: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ خطا در بررسی وضعیت: {str(e)}")
            return False
    
    print("⏰ زمان انتظار به پایان رسید")
    return False

def test_regular_api():
    """تست API معمولی"""
    print("\n🧪 تست API معمولی")
    print("=" * 50)
    
    # URL API
    api_url = "http://localhost:8000/download-youtube"
    
    # داده‌های درخواست
    data = {
        "api_key": "AIzaSyATk52Q35uG1Ups7q-kCatJEUjXAO2C--k",
        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "target_language": "Persian (FA)",
        "voice": "Fenrir",
        "extraction_method": "whisper"
    }
    
    try:
        response = requests.post(api_url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ درخواست API معمولی موفقیت‌آمیز بود:")
            print(f"   Job ID: {result.get('job_id')}")
            print(f"   وضعیت: {result.get('status')}")
            return True
        else:
            print(f"❌ خطا در API معمولی: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست API معمولی: {str(e)}")
        return False

def main():
    """اجرای اصلی"""
    print("🚀 تست کامل OAuth و API")
    print("=" * 60)
    
    # بررسی API
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API در دسترس است")
        else:
            print("❌ API در دسترس نیست")
            print("   لطفاً API را اجرا کنید: python -m uvicorn api:app --host 127.0.0.1 --port 8000")
            return
    except:
        print("❌ API در دسترس نیست")
        print("   لطفاً API را اجرا کنید: python -m uvicorn api:app --host 127.0.0.1 --port 8000")
        return
    
    # تست OAuth
    print("\n🔐 تست OAuth API...")
    oauth_success = test_oauth_api()
    
    # تست معمولی
    print("\n📥 تست API معمولی...")
    regular_success = test_regular_api()
    
    # خلاصه نتایج
    print("\n" + "=" * 60)
    print("📊 خلاصه نتایج:")
    print("=" * 60)
    print(f"OAuth API: {'✅ موفق' if oauth_success else '❌ ناموفق'}")
    print(f"API معمولی: {'✅ موفق' if regular_success else '❌ ناموفق'}")
    
    if oauth_success:
        print("\n🎉 OAuth کاملاً کار می‌کند!")
        print("📚 می‌توانید از endpoint زیر استفاده کنید:")
        print("   POST /download-youtube-oauth")
    elif regular_success:
        print("\n✅ API معمولی کار می‌کند!")
        print("📚 می‌توانید از endpoint زیر استفاده کنید:")
        print("   POST /download-youtube")
    else:
        print("\n❌ هیچ‌کدام کار نمی‌کند")
        print("📚 لطفاً API را بررسی کنید")

if __name__ == "__main__":
    main()
