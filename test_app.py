#!/usr/bin/env python3
"""
تست ساده برای بررسی عملکرد برنامه دوبله خودکار ویدیو
Simple test for Auto Video Dubbing application
"""

import os
import sys
from pathlib import Path

def test_imports():
    """تست import کردن ماژول‌ها"""
    print("🔍 تست import کردن ماژول‌ها...")
    
    try:
        import streamlit as st
        print("✅ Streamlit")
    except ImportError as e:
        print(f"❌ Streamlit: {e}")
        return False
    
    try:
        import google.generativeai as genai
        print("✅ Google Generative AI")
    except ImportError as e:
        print(f"❌ Google Generative AI: {e}")
        return False
    
    try:
        import yt_dlp
        print("✅ yt-dlp")
    except ImportError as e:
        print(f"❌ yt-dlp: {e}")
        return False
    
    try:
        import pysrt
        print("✅ pysrt")
    except ImportError as e:
        print(f"❌ pysrt: {e}")
        return False
    
    try:
        from pydub import AudioSegment
        print("✅ pydub")
    except ImportError as e:
        print(f"⚠️  pydub: {e} (using fallback)")
        # This is expected on Python 3.13, we have a fallback
    
    try:
        import whisper
        print("✅ whisper")
    except ImportError as e:
        print(f"❌ whisper: {e}")
        return False
    
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        print("✅ youtube-transcript-api")
    except ImportError as e:
        print(f"❌ youtube-transcript-api: {e}")
        return False
    
    return True

def test_external_tools():
    """تست ابزارهای خارجی"""
    print("\n🔍 تست ابزارهای خارجی...")
    
    # تست FFmpeg
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✅ FFmpeg")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg نصب نیست")
        return False
    
    # تست Rubberband
    try:
        result = subprocess.run(['rubberband', '--version'], capture_output=True, check=True)
        print("✅ Rubberband")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Rubberband نصب نیست")
        return False
    
    return True

def test_config():
    """تست فایل تنظیمات"""
    print("\n🔍 تست فایل تنظیمات...")
    
    try:
        from config import get_config, get_safety_settings
        config = get_config()
        safety = get_safety_settings()
        print("✅ فایل تنظیمات")
        return True
    except Exception as e:
        print(f"❌ فایل تنظیمات: {e}")
        return False

def test_dubbing_functions():
    """تست توابع دوبله"""
    print("\n🔍 تست توابع دوبله...")
    
    try:
        from dubbing_functions import VideoDubbingApp
        print("✅ کلاس VideoDubbingApp")
        
        # تست ایجاد instance (بدون API key)
        try:
            app = VideoDubbingApp("test_key")
            print("✅ ایجاد instance")
        except Exception as e:
            print(f"⚠️  ایجاد instance: {e}")
        
        return True
    except Exception as e:
        print(f"❌ توابع دوبله: {e}")
        return False

def test_directories():
    """تست ایجاد پوشه‌ها"""
    print("\n🔍 تست ایجاد پوشه‌ها...")
    
    try:
        work_dir = Path("dubbing_work")
        work_dir.mkdir(exist_ok=True)
        print("✅ پوشه کار")
        
        segments_dir = work_dir / "dubbed_segments"
        segments_dir.mkdir(exist_ok=True)
        print("✅ پوشه سگمنت‌ها")
        
        return True
    except Exception as e:
        print(f"❌ ایجاد پوشه‌ها: {e}")
        return False

def main():
    """تابع اصلی تست"""
    print("🎬 تست برنامه دوبله خودکار ویدیو")
    print("=" * 50)
    
    tests = [
        ("Import ها", test_imports),
        ("ابزارهای خارجی", test_external_tools),
        ("فایل تنظیمات", test_config),
        ("توابع دوبله", test_dubbing_functions),
        ("پوشه‌ها", test_directories)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"❌ تست {test_name} ناموفق بود")
    
    print("\n" + "=" * 50)
    print(f"📊 نتیجه: {passed}/{total} تست موفق")
    
    if passed == total:
        print("🎉 همه تست‌ها موفق بودند! برنامه آماده اجرا است.")
        print("🚀 برای اجرا: python run.py")
        return True
    else:
        print("❌ برخی تست‌ها ناموفق بودند. لطفاً مشکلات را برطرف کنید.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
