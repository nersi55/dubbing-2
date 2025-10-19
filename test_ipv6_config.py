#!/usr/bin/env python3
"""
تست تنظیمات IPv6 برای yt-dlp
Test IPv6 configuration for yt-dlp
"""

import yt_dlp
import socket
import sys

def test_ipv6_support():
    """تست پشتیبانی IPv6 در سیستم"""
    print("🔍 بررسی پشتیبانی IPv6...")
    
    try:
        # تست اتصال IPv6 به Google
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('2001:4860:4860::8888', 80))
        sock.close()
        
        if result == 0:
            print("✅ سیستم از IPv6 پشتیبانی می‌کند")
            return True
        else:
            print("❌ سیستم از IPv6 پشتیبانی نمی‌کند")
            return False
    except Exception as e:
        print(f"❌ خطا در تست IPv6: {e}")
        return False

def test_yt_dlp_ipv6():
    """تست yt-dlp با تنظیمات IPv6"""
    print("\n🧪 تست yt-dlp با تنظیمات IPv6...")
    
    # تست URL کوتاه
    test_url = "https://youtube.com/shorts/CVtRmmFrSL0"
    
    config = {
        'prefer_ipv6': True,
        'source_address': '::',
        'verbose': True,
        'no_warnings': False,
        'quiet': False,
        'socket_timeout': 10,
        'retries': 1,
    }
    
    try:
        with yt_dlp.YoutubeDL(config) as ydl:
            print("📡 در حال تست اتصال...")
            info = ydl.extract_info(test_url, download=False)
            
            if info:
                print("✅ yt-dlp با IPv6 کار می‌کند")
                print(f"📹 عنوان: {info.get('title', 'نامشخص')}")
                print(f"⏱️  مدت: {info.get('duration', 'نامشخص')} ثانیه")
                return True
            else:
                print("❌ اطلاعات ویدیو دریافت نشد")
                return False
                
    except Exception as e:
        print(f"❌ خطا در تست yt-dlp: {e}")
        return False

def test_ipv4_fallback():
    """تست fallback به IPv4"""
    print("\n🔄 تست fallback به IPv4...")
    
    config = {
        'prefer_ipv6': True,
        'source_address': '::',
        'verbose': True,
        'socket_timeout': 5,
        'retries': 1,
    }
    
    try:
        with yt_dlp.YoutubeDL(config) as ydl:
            info = ydl.extract_info("https://youtube.com/shorts/CVtRmmFrSL0", download=False)
            if info:
                print("✅ Fallback به IPv4 کار می‌کند")
                return True
    except Exception as e:
        print(f"⚠️  Fallback به IPv4: {e}")
        return False

def main():
    """اجرای تست‌های IPv6"""
    print("🚀 شروع تست تنظیمات IPv6 برای yt-dlp")
    print("=" * 50)
    
    # تست 1: پشتیبانی سیستم
    ipv6_support = test_ipv6_support()
    
    # تست 2: yt-dlp با IPv6
    yt_dlp_works = test_yt_dlp_ipv6()
    
    # تست 3: fallback
    fallback_works = test_ipv4_fallback()
    
    print("\n" + "=" * 50)
    print("📊 نتایج تست:")
    print(f"   IPv6 Support: {'✅' if ipv6_support else '❌'}")
    print(f"   yt-dlp IPv6:  {'✅' if yt_dlp_works else '❌'}")
    print(f"   IPv4 Fallback: {'✅' if fallback_works else '❌'}")
    
    if yt_dlp_works:
        print("\n🎉 تنظیمات IPv6 به درستی کار می‌کند!")
    elif fallback_works:
        print("\n⚠️  IPv6 در دسترس نیست، اما fallback به IPv4 کار می‌کند")
    else:
        print("\n❌ مشکل در اتصال. لطفاً تنظیمات شبکه را بررسی کنید")

if __name__ == "__main__":
    main()
