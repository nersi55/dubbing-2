"""
استخراج لینک‌های Reels از صفحه اینستاگرام
Instagram Reels Link Scraper

این برنامه لینک صفحه اینستاگرام را دریافت کرده و تمام لینک‌های Reels را استخراج می‌کند.
"""

import re
import json
import csv
import time
import os
from pathlib import Path
from typing import List, Set, Optional
from urllib.parse import urlparse

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError as e:
    print(f"❌ خطا: کتابخانه‌های مورد نیاز نصب نشده‌اند. لطفاً نصب کنید:")
    print(f"pip install selenium webdriver-manager beautifulsoup4")
    raise


def extract_username_from_url(url: str) -> Optional[str]:
    """
    استخراج نام کاربری از URL اینستاگرام
    
    Args:
        url: لینک صفحه اینستاگرام (مثلاً https://www.instagram.com/innertune.affirmations/)
    
    Returns:
        نام کاربری یا None در صورت خطا
    """
    # حذف trailing slash
    url = url.rstrip('/')
    
    # الگوهای مختلف URL
    patterns = [
        r'instagram\.com/([^/?]+)',  # instagram.com/username
        r'instagram\.com/([^/?]+)/?$',  # instagram.com/username/
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            username = match.group(1)
            # حذف مسیرهای اضافی مثل /reels/, /p/, etc.
            if username not in ['reels', 'p', 'tv', 'stories']:
                return username
    
    return None


def load_cookies_from_file(cookie_file: str) -> Optional[List[dict]]:
    """
    بارگذاری cookies از فایل
    
    Args:
        cookie_file: مسیر فایل cookies (cookies_insta.txt)
    
    Returns:
        لیست cookies برای Selenium یا None
    """
    if not os.path.exists(cookie_file):
        return None
    
    try:
        # تلاش برای بارگذاری به عنوان JSON
        with open(cookie_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
            # اگر فایل JSON است
            if content.startswith('[') or content.startswith('{'):
                cookies_data = json.loads(content)
                
                # اگر لیست است
                if isinstance(cookies_data, list):
                    return cookies_data
                # اگر dict است، تبدیل به لیست
                elif isinstance(cookies_data, dict):
                    return [cookies_data]
            
            # اگر فرمت Netscape است (cookies.txt)
            else:
                cookies = []
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#') and '\t' in line:
                        parts = line.split('\t')
                        if len(parts) >= 7:
                            cookie = {
                                'name': parts[5],
                                'value': parts[6],
                                'domain': parts[0],
                                'path': parts[2],
                                'secure': parts[3] == 'TRUE',
                            }
                            if parts[1] != 'FALSE':
                                cookie['expiry'] = int(parts[4])
                            cookies.append(cookie)
                return cookies if cookies else None
                
    except json.JSONDecodeError:
        print(f"⚠️ فایل {cookie_file} فرمت JSON معتبری ندارد. تلاش با فرمت Netscape...")
        return None
    except Exception as e:
        print(f"⚠️ خطا در بارگذاری cookies: {str(e)}")
        return None


def setup_driver(headless: bool = False) -> webdriver.Chrome:
    """
    راه‌اندازی Chrome WebDriver
    
    Args:
        headless: اجرای مرورگر در حالت headless
    
    Returns:
        WebDriver instance
    """
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument('--headless')
    
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User agent برای جلوگیری از تشخیص bot
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver


def add_cookies_to_driver(driver: webdriver.Chrome, cookies: List[dict], domain: str = 'instagram.com'):
    """
    افزودن cookies به WebDriver
    
    Args:
        driver: WebDriver instance
        cookies: لیست cookies
        domain: دامنه برای cookies
    """
    # ابتدا باید به دامنه برویم تا بتوانیم cookies را اضافه کنیم
    driver.get(f'https://www.{domain}')
    time.sleep(2)
    
    for cookie in cookies:
        try:
            # تبدیل به فرمت Selenium
            selenium_cookie = {
                'name': cookie.get('name', ''),
                'value': cookie.get('value', ''),
            }
            
            # افزودن فیلدهای اختیاری
            if 'domain' in cookie:
                selenium_cookie['domain'] = cookie['domain']
            elif domain:
                selenium_cookie['domain'] = f'.{domain}'
            
            if 'path' in cookie:
                selenium_cookie['path'] = cookie['path']
            
            if 'expiry' in cookie:
                selenium_cookie['expiry'] = cookie['expiry']
            
            if 'secure' in cookie:
                selenium_cookie['secure'] = cookie['secure']
            
            driver.add_cookie(selenium_cookie)
        except Exception as e:
            print(f"⚠️ خطا در افزودن cookie {cookie.get('name', 'unknown')}: {str(e)}")
            continue


def scroll_to_load_all_reels(driver: webdriver.Chrome, max_scrolls: int = 200, scroll_delay: float = 2.0) -> int:
    """
    اسکرول صفحه تا بارگذاری تمام Reels با روش بهبود یافته برای اینستاگرام
    
    Args:
        driver: WebDriver instance
        max_scrolls: حداکثر تعداد اسکرول
        scroll_delay: تاخیر بین اسکرول‌ها (ثانیه)
    
    Returns:
        تعداد اسکرول‌های انجام شده
    """
    print("📜 شروع اسکرول برای بارگذاری تمام Reels...")
    
    # تزریق JavaScript برای Intersection Observer
    driver.execute_script("""
        // ایجاد Intersection Observer برای تشخیص بارگذاری عناصر
        window.instagramReelsLoaded = [];
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    window.instagramReelsLoaded.push(entry.target);
                }
            });
        }, { root: null, rootMargin: '500px', threshold: 0.1 });
        
        // مشاهده تمام عناصر
        const observeElements = () => {
            document.querySelectorAll('a[href*="/reel/"], article, div[role="button"]').forEach(el => {
                observer.observe(el);
            });
        };
        
        observeElements();
        setInterval(observeElements, 2000);
    """)
    
    last_height = 0
    scroll_count = 0
    no_change_count = 0
    last_link_count = 0
    stable_count = 0
    consecutive_same_count = 0  # تعداد دفعاتی که تعداد لینک‌ها ثابت مانده
    
    # صبر اولیه برای بارگذاری محتوای اولیه
    print("⏳ صبر برای بارگذاری اولیه...")
    time.sleep(5)
    
    # اسکرول اولیه برای تحریک بارگذاری
    driver.execute_script("window.scrollTo(0, 500);")
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)
    
    while scroll_count < max_scrolls:
        # روش 1: اسکرول تدریجی با استفاده از viewport
        current_position = driver.execute_script("return window.pageYOffset;")
        viewport_height = driver.execute_script("return window.innerHeight;")
        document_height = driver.execute_script("return document.body.scrollHeight;")
        
        # اسکرول تدریجی (هر بار 70% viewport)
        scroll_increment = int(viewport_height * 0.7)
        steps = max(3, (document_height - current_position) // scroll_increment)
        
        for step in range(min(steps, 5)):  # حداکثر 5 مرحله در هر چرخه
            scroll_to = current_position + (scroll_increment * (step + 1))
            driver.execute_script(f"window.scrollTo({{top: {scroll_to}, behavior: 'smooth'}});")
            time.sleep(scroll_delay * 0.4)
            
            # صبر برای بارگذاری محتوا
            time.sleep(scroll_delay * 0.3)
        
        # اسکرول به انتهای صفحه
        driver.execute_script("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});")
        
        # صبر برای بارگذاری محتوا (اینستاگرام نیاز به زمان دارد)
        time.sleep(scroll_delay * 2)
        
        # استفاده از Page Down برای تحریک بارگذاری
        try:
            body = driver.find_element(By.TAG_NAME, 'body')
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(scroll_delay * 0.5)
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(scroll_delay * 0.5)
        except Exception:
            pass
        
        # محاسبه ارتفاع جدید
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        # شمارش تعداد لینک‌های فعلی با روش‌های مختلف
        try:
            # استفاده از JavaScript برای شمارش دقیق‌تر
            link_count_js = driver.execute_script("""
                var links = new Set();
                // روش 1: تمام لینک‌های <a>
                document.querySelectorAll('a[href*="/reel/"]').forEach(a => {
                    var href = a.href || a.getAttribute('href');
                    if (href && href.includes('/reel/')) {
                        var match = href.match(/\/reel\/([A-Za-z0-9_-]+)/);
                        if (match) links.add(match[1]);
                    }
                });
                // روش 2: جستجو در HTML
                var html = document.documentElement.innerHTML;
                var regex = /\/reel\/([A-Za-z0-9_-]+)/g;
                var match;
                while ((match = regex.exec(html)) !== null) {
                    links.add(match[1]);
                }
                return links.size;
            """)
            
            # روش‌های Selenium برای مقایسه
            current_links_css = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/reel/"]')
            current_links_xpath = driver.find_elements(By.XPATH, "//a[contains(@href, '/reel/')]")
            
            # استفاده از بیشترین تعداد
            current_link_count = max(link_count_js, len(current_links_css), len(current_links_xpath))
            
            if current_link_count > last_link_count:
                increase = current_link_count - last_link_count
                print(f"📊 پیدا شد: {current_link_count} لینک Reels (افزایش: +{increase})")
                last_link_count = current_link_count
                no_change_count = 0
                stable_count = 0
                consecutive_same_count = 0
            elif current_link_count == last_link_count:
                consecutive_same_count += 1
                stable_count += 1
                if stable_count >= 5:
                    no_change_count += 1
            else:
                no_change_count += 1
        except Exception as e:
            print(f"⚠️ خطا در شمارش لینک‌ها: {str(e)}")
            # Fallback به روش قبلی
            try:
                current_links_css = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/reel/"]')
                current_link_count = len(current_links_css)
                if current_link_count > last_link_count:
                    last_link_count = current_link_count
            except Exception:
                pass
        
        # بررسی تغییر ارتفاع
        if new_height == last_height:
            no_change_count += 1
        else:
            no_change_count = 0
            stable_count = 0
        
        # اگر چند بار متوالی تغییر نکرد، تلاش برای تحریک بارگذاری
        if no_change_count >= 3 or consecutive_same_count >= 10:
            print("🔄 تلاش برای تحریک بارگذاری بیشتر...")
            
            # اسکرول به بالا
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            # اسکرول تدریجی به پایین
            for scroll_pos in [500, 1000, 2000, 5000, 10000]:
                driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
                time.sleep(scroll_delay * 0.5)
            
            # اسکرول به انتهای صفحه
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_delay * 2)
            
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            # بررسی مجدد تعداد لینک‌ها
            try:
                current_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/reel/"]')
                current_link_count = len(current_links)
                if current_link_count > last_link_count:
                    print(f"✅ بعد از تحریک: {current_link_count} لینک یافت شد!")
                    last_link_count = current_link_count
                    no_change_count = 0
                    stable_count = 0
            except Exception:
                pass
            
            # اگر بعد از تحریک هم تغییری نکرد، احتمالاً به انتها رسیده‌ایم
            if new_height == last_height and no_change_count >= 5 and consecutive_same_count >= 15:
                print(f"✅ به انتهای صفحه رسیدیم بعد از {scroll_count} اسکرول")
                print(f"📊 مجموع لینک‌های یافت شده: {last_link_count}")
                # یک بار دیگر تلاش نهایی
                if last_link_count < 50:  # اگر تعداد کم است، ادامه بده
                    print("⚠️ تعداد لینک‌ها کم است، ادامه اسکرول...")
                    no_change_count = 0
                    consecutive_same_count = 0
                else:
                    break
        
        last_height = new_height
        scroll_count += 1
        
        # نمایش پیشرفت
        if scroll_count % 3 == 0:
            print(f"📜 اسکرول {scroll_count}/{max_scrolls}... (ارتفاع: {new_height}px, لینک‌ها: {last_link_count}, ثابت: {stable_count})")
    
    # اسکرول نهایی برای اطمینان
    print("🔄 انجام اسکرول نهایی برای اطمینان از بارگذاری کامل...")
    
    # چندین بار اسکرول کامل با روش‌های مختلف
    for i in range(10):
        # اسکرول به بالا
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # اسکرول تدریجی به پایین با مراحل بیشتر
        max_scroll_pos = driver.execute_script("return document.body.scrollHeight;")
        step = max(100, max_scroll_pos // 20)  # مراحل کوچک‌تر
        
        for pos in range(0, max_scroll_pos, step):
            driver.execute_script(f"window.scrollTo({{top: {pos}, behavior: 'smooth'}});")
            time.sleep(scroll_delay * 0.15)
            
            # استفاده از Page Down در هر مرحله
            try:
                body = driver.find_element(By.TAG_NAME, 'body')
                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.3)
            except Exception:
                pass
        
        # اسکرول به انتهای صفحه
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_delay)
        
        # شمارش مجدد
        try:
            current_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/reel/"]')
            current_link_count = len(current_links)
            if current_link_count > last_link_count:
                print(f"✅ در اسکرول نهایی: {current_link_count} لینک یافت شد!")
                last_link_count = current_link_count
        except Exception:
            pass
    
    print(f"✅ اسکرول کامل شد. مجموع: {scroll_count} اسکرول، {last_link_count} لینک یافت شد")
    return scroll_count


def extract_reel_links(driver: webdriver.Chrome) -> Set[str]:
    """
    استخراج تمام لینک‌های Reels از صفحه با روش‌های مختلف
    
    Args:
        driver: WebDriver instance
    
    Returns:
        مجموعه لینک‌های منحصر به فرد Reels
    """
    reel_links = set()
    
    print("🔍 استخراج لینک‌های Reels با روش‌های مختلف...")
    
    try:
        # روش 1: جستجوی تمام لینک‌های حاوی /reel/ با CSS Selector
        try:
            links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/reel/"]')
            print(f"📎 یافت شد {len(links)} لینک با CSS Selector")
            
            for link in links:
                try:
                    href = link.get_attribute('href')
                    if href and '/reel/' in href:
                        # تبدیل به فرمت کامل
                        if href.startswith('/'):
                            href = f'https://www.instagram.com{href}'
                        elif not href.startswith('http'):
                            href = f'https://www.instagram.com/{href}'
                        
                        # حذف query parameters اضافی
                        href = href.split('?')[0].rstrip('/')
                        
                        # استخراج reel ID و ساخت URL استاندارد
                        if '/reel/' in href:
                            parts = href.split('/reel/')
                            if len(parts) == 2:
                                reel_id = parts[1].split('?')[0].split('/')[0]
                                href = f'https://www.instagram.com/reel/{reel_id}'
                        
                        reel_links.add(href)
                except Exception:
                    continue
        except Exception as e:
            print(f"⚠️ خطا در روش CSS Selector: {str(e)}")
        
        # روش 2: جستجوی تمام لینک‌های <a>
        try:
            all_links = driver.find_elements(By.TAG_NAME, 'a')
            print(f"📎 بررسی {len(all_links)} لینک کلی...")
            
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    if href and '/reel/' in href:
                        if href.startswith('/'):
                            href = f'https://www.instagram.com{href}'
                        elif not href.startswith('http'):
                            href = f'https://www.instagram.com/{href}'
                        
                        href = href.split('?')[0].rstrip('/')
                        
                        # استخراج reel ID و ساخت URL استاندارد
                        if '/reel/' in href:
                            parts = href.split('/reel/')
                            if len(parts) == 2:
                                reel_id = parts[1].split('?')[0].split('/')[0]
                                href = f'https://www.instagram.com/reel/{reel_id}'
                        
                        reel_links.add(href)
                except Exception:
                    continue
        except Exception as e:
            print(f"⚠️ خطا در روش Tag Name: {str(e)}")
        
        # روش 3: جستجو در HTML صفحه (برای لینک‌های که در JavaScript هستند)
        try:
            page_source = driver.page_source
            # الگوهای مختلف برای پیدا کردن لینک‌های Reels
            patterns = [
                r'https?://(www\.)?instagram\.com/reel/([A-Za-z0-9_-]+)',
                r'https?://(www\.)?instagram\.com/[^/]+/reel/([A-Za-z0-9_-]+)',
                r'"/reel/([A-Za-z0-9_-]+)"',
                r"'/reel/([A-Za-z0-9_-]+)'",
                r'href=["\']([^"\']*reel/([A-Za-z0-9_-]+)[^"\']*)["\']',
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, page_source)
                for match in matches:
                    reel_url = None
                    if len(match.groups()) >= 1:
                        # اگر گروه‌های capture وجود دارد
                        reel_id = match.group(2) if len(match.groups()) >= 2 else match.group(1)
                        if reel_id:
                            reel_url = f'https://www.instagram.com/reel/{reel_id}'
                    else:
                        reel_url = match.group(0)
                    
                    if reel_url:
                        # پاک کردن quotes و whitespace
                        reel_url = reel_url.strip('"\' \n\t')
                        
                        # حذف href= از ابتدا
                        if reel_url.startswith('href='):
                            reel_url = reel_url[5:].strip('"\'')
                        
                        # تبدیل به URL کامل
                        if reel_url.startswith('/reel/'):
                            reel_url = f'https://www.instagram.com{reel_url}'
                        elif '/reel/' in reel_url and not reel_url.startswith('http'):
                            if not reel_url.startswith('/'):
                                reel_url = f'https://www.instagram.com/reel/{reel_url.split("/reel/")[-1]}'
                            else:
                                reel_url = f'https://www.instagram.com{reel_url}'
                        
                        # فقط URLهای معتبر
                        if '/reel/' in reel_url and reel_url.startswith('http'):
                            reel_url = reel_url.split('?')[0].rstrip('/')
                            # حذف username از URL (فقط reel ID)
                            if '/reel/' in reel_url:
                                parts = reel_url.split('/reel/')
                                if len(parts) == 2:
                                    reel_id = parts[1].split('?')[0].split('/')[0]
                                    reel_url = f'https://www.instagram.com/reel/{reel_id}'
                                reel_links.add(reel_url)
            
            print(f"📎 یافت شد {len(reel_links)} لینک منحصر به فرد از HTML")
        except Exception as e:
            print(f"⚠️ خطا در روش HTML Parsing: {str(e)}")
        
        # روش 4: جستجو در JavaScript variables
        try:
            js_result = driver.execute_script("""
                var links = [];
                var allLinks = document.querySelectorAll('a[href*="/reel/"]');
                allLinks.forEach(function(link) {
                    var href = link.href || link.getAttribute('href');
                    if (href) links.push(href);
                });
                return links;
            """)
            
            if js_result:
                for href in js_result:
                    if href and '/reel/' in href:
                        if href.startswith('/'):
                            href = f'https://www.instagram.com{href}'
                        elif not href.startswith('http'):
                            href = f'https://www.instagram.com/{href}'
                        
                        href = href.split('?')[0].rstrip('/')
                        
                        # استخراج reel ID و ساخت URL استاندارد
                        if '/reel/' in href:
                            parts = href.split('/reel/')
                            if len(parts) == 2:
                                reel_id = parts[1].split('?')[0].split('/')[0]
                                href = f'https://www.instagram.com/reel/{reel_id}'
                        
                        reel_links.add(href)
                
                print(f"📎 یافت شد {len(js_result)} لینک از JavaScript")
        except Exception as e:
            print(f"⚠️ خطا در روش JavaScript: {str(e)}")
        
    except Exception as e:
        print(f"⚠️ خطای کلی در استخراج لینک‌ها: {str(e)}")
    
    print(f"✅ مجموع {len(reel_links)} لینک Reels منحصر به فرد استخراج شد")
    return reel_links


def save_to_csv(reel_links: List[str], filename: str):
    """
    ذخیره لینک‌های Reels در فایل CSV
    
    Args:
        reel_links: لیست لینک‌های Reels
        filename: نام فایل CSV
    """
    # اطمینان از پسوند .csv
    if not filename.endswith('.csv'):
        filename += '.csv'
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['reel_url'])  # هدر
        
        for link in sorted(reel_links):
            writer.writerow([link])
    
    print(f"✅ {len(reel_links)} لینک در فایل {filename} ذخیره شد.")


def scrape_instagram_reels(profile_url: str, output_dir: str = '.', headless: bool = False, 
                          max_scrolls: int = 200, scroll_delay: float = 2.0) -> str:
    """
    تابع اصلی برای استخراج لینک‌های Reels
    
    Args:
        profile_url: لینک صفحه اینستاگرام
        output_dir: مسیر ذخیره فایل CSV
        headless: اجرای مرورگر در حالت headless
        max_scrolls: حداکثر تعداد اسکرول برای بارگذاری Reels
        scroll_delay: تاخیر بین اسکرول‌ها (ثانیه)
    
    Returns:
        مسیر فایل CSV ایجاد شده
    """
    print("=" * 60)
    print("🎬 استخراج لینک‌های Reels اینستاگرام")
    print("=" * 60)
    
    # 1. استخراج نام کاربری
    username = extract_username_from_url(profile_url)
    if not username:
        raise ValueError(f"❌ نتوانستیم نام کاربری را از URL استخراج کنیم: {profile_url}")
    
    print(f"👤 نام کاربری: {username}")
    
    # 2. ساخت URL صفحه reels
    reels_url = f"https://www.instagram.com/{username}/reels/"
    print(f"🔗 URL صفحه Reels: {reels_url}")
    
    # 3. راه‌اندازی WebDriver
    print("🚀 راه‌اندازی مرورگر...")
    driver = setup_driver(headless=headless)
    
    try:
        # 4. بارگذاری cookies اگر موجود باشد
        cookie_file = 'cookies_insta.txt'
        cookies = load_cookies_from_file(cookie_file)
        
        if cookies:
            print(f"🍪 استفاده از فایل {cookie_file} برای احراز هویت")
            add_cookies_to_driver(driver, cookies)
        else:
            print(f"ℹ️ فایل {cookie_file} یافت نشد. ادامه بدون احراز هویت...")
        
        # 5. باز کردن صفحه reels
        print(f"📥 باز کردن صفحه Reels...")
        driver.get(reels_url)
        time.sleep(8)  # صبر بیشتر برای بارگذاری اولیه
        
        # صبر برای بارگذاری محتوای اولیه
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except TimeoutException:
            print("⚠️ تایم‌اوت در بارگذاری اولیه")
        
        time.sleep(3)  # صبر اضافی
        
        # بررسی اگر صفحه خصوصی است یا خطا دارد
        page_source = driver.page_source.lower()
        if 'this account is private' in page_source or 'صفحه خصوصی' in page_source:
            print("⚠️ این صفحه خصوصی است. ممکن است نیاز به احراز هویت داشته باشید.")
        elif 'page not found' in page_source or 'صفحه یافت نشد' in page_source:
            raise ValueError(f"❌ صفحه یافت نشد: {reels_url}")
        
        # 6. اسکرول برای بارگذاری تمام Reels
        scroll_count = scroll_to_load_all_reels(driver, max_scrolls=max_scrolls, scroll_delay=scroll_delay)
        
        # 7. استخراج لینک‌های Reels
        print("🔍 استخراج لینک‌های Reels...")
        reel_links = extract_reel_links(driver)
        
        if not reel_links:
            print("⚠️ هیچ لینک Reels یافت نشد. ممکن است:")
            print("   - صفحه Reels خالی باشد")
            print(" - نیاز به احراز هویت داشته باشید")
            print("   - صفحه به درستی بارگذاری نشده باشد")
            return None
        
        print(f"✅ {len(reel_links)} لینک Reels یافت شد.")
        
        # 8. ذخیره در CSV
        output_path = Path(output_dir) / f"{username}.csv"
        save_to_csv(sorted(reel_links), str(output_path))
        
        return str(output_path)
        
    finally:
        # بستن مرورگر
        print("🔒 بستن مرورگر...")
        driver.quit()


def main():
    """تابع اصلی برای اجرای برنامه از خط فرمان"""
    import sys
    
    if len(sys.argv) < 2:
        print("استفاده:")
        print(f"  python {sys.argv[0]} <instagram_profile_url> [output_dir] [--headless]")
        print("\nمثال:")
        print(f"  python {sys.argv[0]} https://www.instagram.com/innertune.affirmations/")
        print(f"  python {sys.argv[0]} https://www.instagram.com/innertune.affirmations/ ./output --headless")
        sys.exit(1)
    
    profile_url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else '.'
    headless = '--headless' in sys.argv
    
    try:
        csv_path = scrape_instagram_reels(profile_url, output_dir, headless)
        if csv_path:
            print(f"\n✅ موفق! فایل CSV در {csv_path} ذخیره شد.")
        else:
            print("\n❌ استخراج ناموفق بود.")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ خطا: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

