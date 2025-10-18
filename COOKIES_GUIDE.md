# راهنمای حل مشکل احراز هویت YouTube
# YouTube Authentication Guide

## مشکل
YouTube گاهی اوقات نیاز به احراز هویت دارد تا مطمئن شود شما ربات نیستید.

## راه‌حل‌ها

### روش 1: استفاده از اسکریپت خودکار (پیشنهادی)
```bash
python export_cookies.py
```

### روش 2: صادرات دستی کوکی‌ها

#### با yt-dlp:
```bash
# برای Chrome
yt-dlp --cookies-from-browser chrome --print-json 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' > cookies.json

# برای Firefox
yt-dlp --cookies-from-browser firefox --print-json 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' > cookies.json

# برای Safari
yt-dlp --cookies-from-browser safari --print-json 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' > cookies.json
```

#### با افزونه مرورگر:
1. افزونه "Get cookies.txt" را نصب کنید
2. به YouTube بروید و وارد حساب کاربری شوید
3. روی آیکون افزونه کلیک کنید
4. فایل `cookies.txt` را دانلود کنید

### روش 3: صادرات دستی
1. در مرورگر F12 را فشار دهید
2. به تب Application/Storage بروید
3. Cookies > https://www.youtube.com را انتخاب کنید
4. کوکی‌ها را کپی کنید و در فایل `cookies.txt` ذخیره کنید

## فرمت فایل کوکی

### cookies.txt (Netscape format):
```
# Netscape HTTP Cookie File
.youtube.com	TRUE	/	FALSE	1234567890	VISITOR_INFO1_LIVE	abc123
.youtube.com	TRUE	/	FALSE	1234567890	YSC	def456
```

### cookies.json (JSON format):
```json
{
  "cookies": [
    {
      "name": "VISITOR_INFO1_LIVE",
      "value": "abc123",
      "domain": ".youtube.com",
      "path": "/"
    }
  ]
}
```

## استفاده
پس از ایجاد فایل کوکی، برنامه به طور خودکار از آن استفاده خواهد کرد.

## نکات مهم
- کوکی‌ها را به‌روز نگه دارید
- فایل کوکی را با کسی به اشتراک نگذارید
- کوکی‌ها ممکن است منقضی شوند
