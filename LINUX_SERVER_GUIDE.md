# راهنمای استفاده روی سرور لینوکس
# Linux Server Usage Guide

## مشکل اصلی
روی سرور لینوکس مرورگر وجود ندارد و کوکی‌های YouTube منقضی می‌شوند.

## راه‌حل‌های پیاده‌سازی شده

### 1. **بهبود تابع دانلود**
- ✅ اضافه شدن User-Agent و Headers مناسب برای سرور
- ✅ سیستم Fallback برای دانلود در صورت شکست
- ✅ مدیریت خطاهای بهتر
- ✅ پشتیبانی از کوکی‌های اختیاری

### 2. **اسکریپت‌های تست**
- `test_yt_dlp_server.py`: تست yt-dlp روی سرور
- `test_server_setup.py`: تست کامل تنظیمات سرور
- `export_cookies_server.py`: ایجاد کوکی‌های سرور

## نحوه استفاده

### مرحله 1: تست سیستم
```bash
# تست کامل سیستم
python test_server_setup.py

# تست yt-dlp
python test_yt_dlp_server.py

# تست سریع دوبله
python quick_test.py
```

### مرحله 2: اجرای برنامه
```bash
# اجرای صفحه ساده
python run_simple.py

# یا اجرای API
python run_api.py
```

## تنظیمات جدید

### User-Agent و Headers
```python
'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
'referer': 'https://www.youtube.com/'
'headers': {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}
```

### سیستم Fallback
اگر دانلود اصلی شکست بخورد، سیستم خودکار با تنظیمات ساده‌تر تلاش می‌کند:
- User-Agent متفاوت (Googlebot)
- فرمت ویدیو محدودتر
- Timeout بیشتر

## عیب‌یابی

### مشکل 1: "Sign in to confirm you're not a bot"
**راه‌حل:**
```bash
# تست دسترسی
python test_yt_dlp_server.py

# اگر شکست خورد، از VPN استفاده کنید
```

### مشکل 2: "No title found in player responses"
**راه‌حل:**
- این هشدار طبیعی است و مشکل جدی نیست
- برنامه ادامه خواهد داد

### مشکل 3: دانلود شکست می‌خورد
**راه‌حل:**
1. بررسی اتصال اینترنت
2. استفاده از VPN
3. آپلود فایل ویدیو به جای دانلود

## راه‌حل‌های جایگزین

### 1. استفاده از VPN
```bash
# نصب OpenVPN (مثال)
sudo apt install openvpn

# اتصال به VPN
sudo openvpn --config your-config.ovpn
```

### 2. آپلود فایل ویدیو
به جای دانلود از YouTube، فایل ویدیو را آپلود کنید:
- از طریق رابط وب
- از طریق API

### 3. استفاده از Proxy
```python
# در dubbing_functions.py
video_opts.update({
    'proxy': 'http://your-proxy:port',
})
```

## مانیتورینگ

### بررسی لاگ‌ها
```bash
# بررسی لاگ‌های برنامه
tail -f /var/log/syslog | grep dubing

# بررسی استفاده از منابع
htop
```

### بررسی وضعیت yt-dlp
```bash
# تست دسترسی
yt-dlp --user-agent "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
       --referer "https://www.youtube.com/" \
       --print-json 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
```

## نکات مهم

1. **همیشه ابتدا تست کنید**: قبل از استفاده، `test_server_setup.py` را اجرا کنید
2. **از VPN استفاده کنید**: اگر دسترسی محدود است
3. **فایل‌های موقت را پاک کنید**: `cleanup_files.py` را اجرا کنید
4. **مانیتورینگ کنید**: استفاده از منابع را بررسی کنید

## پشتیبانی

در صورت مشکل:
1. لاگ‌ها را بررسی کنید
2. تست‌ها را اجرا کنید
3. تنظیمات را بررسی کنید
4. از راه‌حل‌های جایگزین استفاده کنید

---
**تاریخ به‌روزرسانی**: 2024
**نسخه**: 1.0
