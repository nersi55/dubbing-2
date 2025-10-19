#!/usr/bin/env python3
"""
راه‌اندازی OAuth یوتیوب
Setup YouTube OAuth
"""

import os
import json
import sys
from pathlib import Path

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

def check_credentials():
    """بررسی وجود فایل credentials"""
    if os.path.exists('youtube_credentials.json'):
        print("✅ فایل youtube_credentials.json موجود است")
        return True
    else:
        print("❌ فایل youtube_credentials.json یافت نشد")
        return False

def install_oauth_dependencies():
    """نصب وابستگی‌های OAuth"""
    print("📦 نصب وابستگی‌های OAuth...")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "-m", "pip", "install",
            "google-auth", "google-auth-oauthlib", 
            "google-auth-httplib2", "google-api-python-client"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ وابستگی‌های OAuth نصب شدند")
            return True
        else:
            print(f"❌ خطا در نصب وابستگی‌ها: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ خطا در نصب: {str(e)}")
        return False

def test_oauth():
    """تست OAuth"""
    print("🧪 تست OAuth...")
    
    try:
        from youtube_oauth import YouTubeOAuthManager
        
        api_key = "AIzaSyATk52Q35uG1Ups7q-kCatJEUjXAO2C--k"
        oauth_manager = YouTubeOAuthManager(api_key)
        
        if oauth_manager.authenticate():
            print("✅ OAuth کار می‌کند")
            return True
        else:
            print("❌ OAuth کار نمی‌کند")
            return False
    except Exception as e:
        print(f"❌ خطا در تست OAuth: {str(e)}")
        return False

def main():
    """راه‌اندازی اصلی"""
    print("🚀 راه‌اندازی OAuth یوتیوب")
    print("=" * 50)
    
    # بررسی فایل credentials
    if not check_credentials():
        print("\n📝 ایجاد فایل نمونه...")
        create_credentials_template()
        print("\n🔧 مراحل بعدی:")
        print("1. به Google Cloud Console بروید")
        print("2. پروژه خود را انتخاب کنید")
        print("3. APIs & Services > Credentials")
        print("4. Create Credentials > OAuth 2.0 Client IDs")
        print("5. Application type: Desktop application")
        print("6. فایل JSON را دانلود و به عنوان youtube_credentials.json ذخیره کنید")
        print("\nسپس این اسکریپت را دوباره اجرا کنید.")
        return
    
    # نصب وابستگی‌ها
    print("\n📦 بررسی وابستگی‌ها...")
    if not install_oauth_dependencies():
        print("❌ خطا در نصب وابستگی‌ها")
        return
    
    # تست OAuth
    print("\n🧪 تست OAuth...")
    if test_oauth():
        print("\n🎉 OAuth با موفقیت راه‌اندازی شد!")
        print("\n📚 نحوه استفاده:")
        print("- API Endpoint: /download-youtube-oauth")
        print("- مستندات: http://localhost:8002/docs")
        print("- راهنما: README_OAUTH.md")
    else:
        print("\n❌ OAuth راه‌اندازی نشد")
        print("لطفاً فایل youtube_credentials.json را بررسی کنید")

if __name__ == "__main__":
    main()
