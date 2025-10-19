#!/usr/bin/env python3
"""
استفاده از دانلود معمولی به جای OAuth
Use Regular Download Instead of OAuth
"""

import requests
import json
import time

def test_regular_download():
    """تست دانلود معمولی"""
    print("🧪 تست دانلود معمولی یوتیوب")
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
    
    print(f"📡 ارسال درخواست به: {api_url}")
    print(f"📋 داده‌ها: {json.dumps(data, indent=2)}")
    
    try:
        # ارسال درخواست
        response = requests.post(api_url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ درخواست API موفقیت‌آمیز بود:")
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
    
    for i in range(10):  # حداکثر 10 بار بررسی
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
                    return True
                elif status.get('status') == 'failed':
                    print("❌ کار ناموفق بود!")
                    return False
                
                time.sleep(5)  # 5 ثانیه صبر
            else:
                print(f"❌ خطا در بررسی وضعیت: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ خطا در بررسی وضعیت: {str(e)}")
            return False
    
    print("⏰ زمان انتظار به پایان رسید")
    return False

def main():
    """اجرای اصلی"""
    print("🚀 استفاده از دانلود معمولی یوتیوب")
    print("=" * 60)
    
    print("📝 این روش از OAuth استفاده نمی‌کند")
    print("   و از yt-dlp معمولی برای دانلود استفاده می‌کند")
    print()
    
    # بررسی API
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API در دسترس است")
        else:
            print("❌ API در دسترس نیست")
            print("   لطفاً API را اجرا کنید: python run_api.py")
            return
    except:
        print("❌ API در دسترس نیست")
        print("   لطفاً API را اجرا کنید: python run_api.py")
        return
    
    # تست دانلود
    if test_regular_download():
        print("\n🎉 دانلود معمولی کار می‌کند!")
        print("📚 می‌توانید از API استفاده کنید:")
        print("   POST /download-youtube")
    else:
        print("\n❌ دانلود معمولی کار نمی‌کند")
        print("📚 لطفاً API را بررسی کنید")

if __name__ == "__main__":
    main()
