#!/usr/bin/env python3
"""
تشخیص مشکل OAuth
OAuth Problem Diagnosis
"""

import os
import json
import sys
from pathlib import Path

def diagnose_oauth():
    """تشخیص مشکل OAuth"""
    print("🔍 تشخیص مشکل OAuth")
    print("=" * 50)
    
    # بررسی فایل credentials
    if not os.path.exists('youtube_credentials.json'):
        print("❌ فایل youtube_credentials.json یافت نشد")
        print("📝 لطفاً فایل credentials را از Google Cloud Console دریافت کنید")
        return False
    
    print("✅ فایل credentials یافت شد")
    
    # بررسی محتوای فایل
    try:
        with open('youtube_credentials.json', 'r') as f:
            creds = json.load(f)
        
        print("📋 بررسی محتوای فایل credentials:")
        
        # بررسی ساختار
        if 'installed' not in creds:
            print("❌ ساختار فایل credentials اشتباه است")
            print("   باید شامل 'installed' باشد")
            return False
        
        installed = creds['installed']
        
        # بررسی فیلدهای ضروری
        required_fields = ['client_id', 'client_secret', 'project_id']
        for field in required_fields:
            if field not in installed:
                print(f"❌ فیلد {field} یافت نشد")
                return False
            else:
                print(f"✅ {field}: {installed[field][:20]}...")
        
        # بررسی redirect URIs
        if 'redirect_uris' in installed:
            redirect_uris = installed['redirect_uris']
            print(f"✅ redirect URIs: {redirect_uris}")
        else:
            print("⚠️ redirect URIs یافت نشد")
        
        # بررسی client ID format
        client_id = installed['client_id']
        if not client_id.endswith('.apps.googleusercontent.com'):
            print("❌ فرمت client_id اشتباه است")
            print("   باید به .apps.googleusercontent.com ختم شود")
            return False
        
        print("✅ فرمت client_id درست است")
        
        # بررسی client secret format
        client_secret = installed['client_secret']
        if not client_secret.startswith('GOCSPX-'):
            print("❌ فرمت client_secret اشتباه است")
            print("   باید با GOCSPX- شروع شود")
            return False
        
        print("✅ فرمت client_secret درست است")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ خطا در خواندن فایل JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ خطای غیرمنتظره: {e}")
        return False

def check_google_console_setup():
    """بررسی تنظیمات Google Cloud Console"""
    print("\n🔍 بررسی تنظیمات Google Cloud Console")
    print("=" * 50)
    
    print("📋 مراحل بررسی:")
    print("1. به https://console.cloud.google.com/ بروید")
    print("2. پروژه gen-lang-client-0683609810 را انتخاب کنید")
    print("3. APIs & Services > OAuth consent screen")
    print("4. بررسی کنید:")
    print("   - User Type: External")
    print("   - App name: Video Dubbing App")
    print("   - Scopes: youtube.readonly, youtube.force-ssl")
    print("   - Test users: ایمیل خود را اضافه کنید")
    print("5. APIs & Services > Credentials")
    print("6. OAuth 2.0 Client ID را انتخاب کنید")
    print("7. Authorized redirect URIs:")
    print("   - http://localhost:8080")
    print("   - http://localhost:50937")
    print("   - http://localhost")

def suggest_fixes():
    """پیشنهاد راه‌حل‌ها"""
    print("\n🛠️ راه‌حل‌های پیشنهادی")
    print("=" * 50)
    
    print("1. 🔄 فایل credentials را دوباره دانلود کنید")
    print("   - Google Cloud Console > Credentials")
    print("   - OAuth 2.0 Client ID > Download JSON")
    print("   - جایگزین کردن فایل موجود")
    
    print("\n2. 🔧 OAuth consent screen را تنظیم کنید")
    print("   - User Type: External")
    print("   - Test users اضافه کنید")
    print("   - Scopes مجاز کنید")
    
    print("\n3. 🌐 Redirect URIs را بررسی کنید")
    print("   - http://localhost:8080")
    print("   - http://localhost:50937")
    print("   - http://localhost")
    
    print("\n4. 🧪 تست با روش جایگزین")
    print("   - استفاده از Service Account")
    print("   - یا استفاده از دانلود معمولی")

def main():
    """اجرای اصلی"""
    print("🚀 تشخیص مشکل OAuth یوتیوب")
    print("=" * 60)
    
    # تشخیص فایل credentials
    if diagnose_oauth():
        print("\n✅ فایل credentials درست است")
        print("🔍 مشکل احتمالاً در Google Cloud Console است")
        check_google_console_setup()
    else:
        print("\n❌ فایل credentials مشکل دارد")
        suggest_fixes()
    
    print("\n📚 راهنمای کامل: OAUTH_403_FIX.md")
    print("🧪 تست: python test_oauth_simple.py")

if __name__ == "__main__":
    main()
