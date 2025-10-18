#!/usr/bin/env python3
"""
راه‌اندازی پروکسی‌های رایگان
Setup Free Proxies
"""

import requests
import re
import time
import random
from pathlib import Path

def get_free_proxies():
    """دریافت پروکسی‌های رایگان از منابع مختلف"""
    print("🌐 جستجوی پروکسی‌های رایگان...")
    
    proxies = []
    
    # منابع پروکسی رایگان
    sources = [
        "https://www.proxy-list.download/api/v1/get?type=http",
        "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    ]
    
    for source in sources:
        try:
            print(f"   📡 دریافت از: {source}")
            response = requests.get(source, timeout=10)
            
            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and ':' in line and not line.startswith('#'):
                        # فرمت: ip:port
                        if re.match(r'^\d+\.\d+\.\d+\.\d+:\d+$', line):
                            proxies.append(f"http://{line}")
                        # فرمت: http://ip:port
                        elif line.startswith('http://'):
                            proxies.append(line)
                
                print(f"   ✅ {len([p for p in proxies if source in str(p)])} پروکسی یافت شد")
            else:
                print(f"   ❌ خطا: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ خطا در {source}: {str(e)[:50]}...")
        
        # تاخیر بین درخواست‌ها
        time.sleep(random.uniform(1, 3))
    
    # حذف تکراری‌ها
    unique_proxies = list(set(proxies))
    print(f"\n📊 مجموع پروکسی‌های منحصر به فرد: {len(unique_proxies)}")
    
    return unique_proxies

def test_proxy(proxy: str) -> bool:
    """تست پروکسی"""
    try:
        proxies = {'http': proxy, 'https': proxy}
        response = requests.get(
            'https://httpbin.org/ip', 
            proxies=proxies, 
            timeout=10
        )
        return response.status_code == 200
    except:
        return False

def test_proxies(proxies: list, max_test: int = 20) -> list:
    """تست پروکسی‌ها"""
    print(f"\n🧪 تست {min(len(proxies), max_test)} پروکسی...")
    
    working_proxies = []
    
    for i, proxy in enumerate(proxies[:max_test]):
        print(f"   🔍 تست {i+1}/{min(len(proxies), max_test)}: {proxy}")
        
        if test_proxy(proxy):
            working_proxies.append(proxy)
            print(f"   ✅ کار می‌کند")
        else:
            print(f"   ❌ کار نمی‌کند")
        
        # تاخیر بین تست‌ها
        time.sleep(0.5)
    
    print(f"\n✅ {len(working_proxies)} پروکسی کار می‌کند")
    return working_proxies

def save_proxies(proxies: list):
    """ذخیره پروکسی‌ها"""
    if not proxies:
        print("❌ هیچ پروکسی کارکردی یافت نشد")
        return False
    
    # ذخیره در فایل
    with open('proxy_list.txt', 'w', encoding='utf-8') as f:
        for proxy in proxies:
            f.write(f"{proxy}\n")
    
    print(f"💾 {len(proxies)} پروکسی در proxy_list.txt ذخیره شد")
    return True

def create_proxy_config():
    """ایجاد تنظیمات پروکسی"""
    config = {
        "proxy_rotation": True,
        "proxy_timeout": 10,
        "proxy_retries": 3,
        "fallback_to_direct": True,
        "proxy_headers": {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        }
    }
    
    import json
    with open('proxy_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print("⚙️ تنظیمات پروکسی ایجاد شد: proxy_config.json")

def main():
    """تابع اصلی"""
    print("🌐 راه‌اندازی پروکسی‌های رایگان")
    print("=" * 40)
    
    try:
        import requests
    except ImportError:
        print("❌ requests نصب نشده است")
        print("💡 برای نصب: pip install requests")
        return False
    
    # دریافت پروکسی‌ها
    all_proxies = get_free_proxies()
    
    if not all_proxies:
        print("❌ هیچ پروکسی یافت نشد")
        return False
    
    # تست پروکسی‌ها
    working_proxies = test_proxies(all_proxies)
    
    # ذخیره پروکسی‌های کارکردی
    if save_proxies(working_proxies):
        create_proxy_config()
        print("\n🎉 راه‌اندازی پروکسی کامل شد!")
        print("💡 حالا دانلودگر پیشرفته از پروکسی‌ها استفاده خواهد کرد")
        return True
    else:
        print("\n❌ راه‌اندازی پروکسی شکست خورد")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
