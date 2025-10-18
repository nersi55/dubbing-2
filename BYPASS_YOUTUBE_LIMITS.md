# راهنمای دور زدن محدودیت‌های YouTube
# YouTube Limits Bypass Guide

## مشکل
YouTube دسترسی از سرور شما را کاملاً مسدود کرده است:
```
ERROR: [youtube] Sign in to confirm you're not a bot
```

## راه‌حل‌های پیاده‌سازی شده

### 1. **دانلودگر پیشرفته** (پیشنهادی)
```bash
# تست دانلودگر پیشرفته
python advanced_youtube_downloader.py
```

**ویژگی‌ها:**
- ✅ 12 User-Agent مختلف
- ✅ پشتیبانی از پروکسی
- ✅ 3 روش دانلود (Mobile, Bot, Minimal)
- ✅ تاخیر تصادفی بین درخواست‌ها
- ✅ تلاش‌های متعدد

### 2. **راه‌اندازی پروکسی‌های رایگان**
```bash
# دریافت و تست پروکسی‌های رایگان
python setup_proxies.py
```

**مراحل:**
1. دریافت پروکسی‌های رایگان از منابع مختلف
2. تست پروکسی‌ها
3. ذخیره پروکسی‌های کارکردی
4. استفاده خودکار در دانلودگر

### 3. **استفاده از VPN**
```bash
# نصب OpenVPN (مثال)
sudo apt install openvpn

# اتصال به VPN
sudo openvpn --config your-config.ovpn
```

## راه‌حل‌های جایگزین

### **گزینه 1: آپلود فایل ویدیو**
به جای دانلود از YouTube، فایل را آپلود کنید:

1. ویدیو را از YouTube دانلود کنید (روی کامپیوتر شخصی)
2. فایل را به سرور آپلود کنید
3. از طریق رابط وب آپلود کنید

### **گزینه 2: استفاده از سرویس‌های دانلود**
```python
# استفاده از سرویس‌های دیگر
import requests

def download_via_service(url):
    # استفاده از API های دانلود ویدیو
    pass
```

### **گزینه 3: تغییر IP سرور**
```bash
# تغییر IP سرور (اگر امکان‌پذیر باشد)
# یا استفاده از سرور جدید
```

## نحوه استفاده

### **مرحله 1: راه‌اندازی پروکسی‌ها**
```bash
python setup_proxies.py
```

### **مرحله 2: تست دانلودگر پیشرفته**
```bash
python advanced_youtube_downloader.py
```

### **مرحله 3: اجرای برنامه اصلی**
```bash
python run_simple.py
```

## تنظیمات پیشرفته

### **فایل proxy_list.txt**
```
http://proxy1.example.com:8080
http://user:pass@proxy2.example.com:3128
socks5://proxy3.example.com:1080
```

### **فایل proxy_config.json**
```json
{
  "proxy_rotation": true,
  "proxy_timeout": 10,
  "proxy_retries": 3,
  "fallback_to_direct": true
}
```

## عیب‌یابی

### **مشکل 1: پروکسی‌ها کار نمی‌کنند**
```bash
# تست دستی پروکسی
curl --proxy http://proxy:port https://httpbin.org/ip
```

### **مشکل 2: همه روش‌ها شکست می‌خورند**
```bash
# بررسی اتصال اینترنت
ping youtube.com

# بررسی DNS
nslookup youtube.com

# بررسی فایروال
sudo ufw status
```

### **مشکل 3: محدودیت ISP**
- استفاده از VPN
- تغییر DNS (8.8.8.8, 1.1.1.1)
- تماس با ISP

## مانیتورینگ

### **بررسی لاگ‌ها**
```bash
# بررسی لاگ‌های دانلود
tail -f dubbing_work/download.log

# بررسی استفاده از پروکسی
grep "proxy" dubbing_work/download.log
```

### **بررسی عملکرد**
```bash
# تست سرعت پروکسی
python -c "
import requests
import time
start = time.time()
requests.get('https://httpbin.org/ip', proxies={'http': 'your-proxy'})
print(f'زمان: {time.time() - start:.2f} ثانیه')
"
```

## نکات مهم

1. **همیشه ابتدا پروکسی‌ها را راه‌اندازی کنید**
2. **از VPN استفاده کنید اگر پروکسی‌ها کار نکنند**
3. **فایل‌های ویدیو را آپلود کنید اگر همه روش‌ها شکست بخورند**
4. **لاگ‌ها را بررسی کنید تا مشکل را پیدا کنید**

## پشتیبانی

در صورت مشکل:
1. لاگ‌ها را بررسی کنید
2. پروکسی‌ها را تست کنید
3. VPN را امتحان کنید
4. از روش آپلود فایل استفاده کنید

---
**تاریخ به‌روزرسانی**: 2024
**نسخه**: 2.0
