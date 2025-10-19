#!/usr/bin/env python3
"""
حل مشکل OAuth 403
Fix OAuth 403 Error
"""

import os
import json
import webbrowser
from pathlib import Path

def fix_oauth_403():
    """حل مشکل OAuth 403"""
    print("🔧 حل مشکل OAuth 403")
    print("=" * 50)
    
    print("❌ خطای 403: access_denied")
    print("این خطا معمولاً به دلایل زیر رخ می‌دهد:")
    print()
    print("1. 🔐 OAuth consent screen تنظیم نشده")
    print("2. 📧 User type اشتباه انتخاب شده")
    print("3. 🔑 Scopes مجاز نیستند")
    print("4. 🌐 Redirect URI اشتباه است")
    print()
    
    print("🛠️ راه‌حل‌ها:")
    print()
    
    print("📋 مرحله 1: تنظیم OAuth Consent Screen")
    print("1. به Google Cloud Console بروید: https://console.cloud.google.com/")
    print("2. پروژه خود را انتخاب کنید")
    print("3. APIs & Services > OAuth consent screen")
    print("4. User Type: External را انتخاب کنید")
    print("5. App name: Video Dubbing App")
    print("6. User support email: ایمیل خود را وارد کنید")
    print("7. Developer contact: ایمیل خود را وارد کنید")
    print("8. Scopes: Add or Remove Scopes")
    print("   - https://www.googleapis.com/auth/youtube.readonly")
    print("   - https://www.googleapis.com/auth/youtube.force-ssl")
    print("9. Test users: ایمیل خود را اضافه کنید")
    print("10. Save and Continue")
    print()
    
    print("📋 مرحله 2: تنظیم Credentials")
    print("1. APIs & Services > Credentials")
    print("2. OAuth 2.0 Client IDs را انتخاب کنید")
    print("3. روی credential خود کلیک کنید")
    print("4. Authorized redirect URIs:")
    print("   - http://localhost:8080")
    print("   - http://localhost:50937")
    print("   - http://localhost")
    print("5. Save")
    print()
    
    print("📋 مرحله 3: تست مجدد")
    print("1. فایل youtube_credentials.json را دوباره دانلود کنید")
    print("2. در پوشه پروژه قرار دهید")
    print("3. python test_youtube_oauth.py را اجرا کنید")
    print()
    
    # ایجاد فایل credentials جدید
    create_new_credentials_template()

def create_new_credentials_template():
    """ایجاد فایل credentials جدید"""
    print("📝 ایجاد فایل credentials جدید...")
    
    # فایل credentials فعلی را backup کن
    if os.path.exists('youtube_credentials.json'):
        os.rename('youtube_credentials.json', 'youtube_credentials_backup.json')
        print("✅ فایل قبلی backup شد")
    
    # فایل جدید ایجاد کن
    new_template = {
        "installed": {
            "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
            "project_id": "your-project-id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "YOUR_CLIENT_SECRET",
            "redirect_uris": [
                "http://localhost:8080",
                "http://localhost:50937",
                "http://localhost"
            ]
        }
    }
    
    with open('youtube_credentials_new.json', 'w') as f:
        json.dump(new_template, f, indent=2)
    
    print("✅ فایل جدید youtube_credentials_new.json ایجاد شد")
    print("🔧 این فایل را با اطلاعات واقعی از Google Cloud Console پر کنید")

def open_google_console():
    """باز کردن Google Cloud Console"""
    print("🌐 باز کردن Google Cloud Console...")
    
    urls = [
        "https://console.cloud.google.com/apis/credentials",
        "https://console.cloud.google.com/apis/credentials/consent"
    ]
    
    for url in urls:
        try:
            webbrowser.open(url)
            print(f"✅ باز شد: {url}")
        except:
            print(f"❌ خطا در باز کردن: {url}")

def main():
    """اجرای اصلی"""
    fix_oauth_403()
    
    print("\n" + "=" * 50)
    print("🚀 اقدامات بعدی:")
    print("=" * 50)
    
    choice = input("آیا می‌خواهید Google Cloud Console را باز کنم؟ (y/n): ")
    if choice.lower() == 'y':
        open_google_console()
    
    print("\n📚 راهنمای کامل: YOUTUBE_OAUTH_GUIDE.md")
    print("🧪 تست: python test_youtube_oauth.py")

if __name__ == "__main__":
    main()
