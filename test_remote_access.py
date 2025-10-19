#!/usr/bin/env python3
"""
تست دسترسی از راه دور به API
Test Remote Access to API
"""

import requests
import json
import time
import socket

def get_local_ip():
    """دریافت IP محلی"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def test_api_connection(base_url):
    """تست اتصال به API"""
    print(f"🔍 تست اتصال به: {base_url}")
    
    try:
        # تست health endpoint
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ اتصال موفق!")
            print(f"📊 پاسخ: {response.json()}")
            return True
        else:
            print(f"❌ خطا: کد {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ خطا: نمی‌توان به سرور متصل شد")
        return False
    except requests.exceptions.Timeout:
        print("❌ خطا: زمان اتصال تمام شد")
        return False
    except Exception as e:
        print(f"❌ خطا: {e}")
        return False

def test_api_endpoints(base_url):
    """تست endpoints مختلف"""
    print(f"\n🔍 تست endpoints در: {base_url}")
    
    endpoints = [
        "/",
        "/health", 
        "/docs",
        "/redoc"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = "✅" if response.status_code == 200 else "⚠️"
            print(f"{status} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

def main():
    """تست اصلی"""
    print("🚀 تست دسترسی از راه دور به API دوبله")
    print("=" * 50)
    
    # دریافت IP محلی
    local_ip = get_local_ip()
    
    # آدرس‌های تست
    test_urls = [
        f"http://127.0.0.1:8002",  # محلی
        f"http://{local_ip}:8002",  # شبکه محلی
    ]
    
    # تست هر آدرس
    for url in test_urls:
        print(f"\n🌐 تست آدرس: {url}")
        print("-" * 30)
        
        if test_api_connection(url):
            test_api_endpoints(url)
        else:
            print("❌ اتصال برقرار نشد")
        
        print()

if __name__ == "__main__":
    main()
