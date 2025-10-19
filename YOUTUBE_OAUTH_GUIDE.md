# راهنمای OAuth یوتیوب برای دوبله ویدیو
# YouTube OAuth Guide for Video Dubbing

## مقدمه
این راهنما نحوه استفاده از OAuth یوتیوب برای دانلود ویدیوها و استخراج متن آن‌ها را توضیح می‌دهد.

## مراحل راه‌اندازی

### 1. ایجاد پروژه در Google Cloud Console

1. به [Google Cloud Console](https://console.cloud.google.com/) بروید
2. یک پروژه جدید ایجاد کنید یا پروژه موجود را انتخاب کنید
3. نام پروژه را به خاطر بسپارید

### 2. فعال‌سازی YouTube Data API v3

1. در Google Cloud Console، به **APIs & Services > Library** بروید
2. "YouTube Data API v3" را جستجو کنید
3. روی آن کلیک کرده و **Enable** را بزنید

### 3. ایجاد OAuth 2.0 Credentials

1. به **APIs & Services > Credentials** بروید
2. روی **+ CREATE CREDENTIALS** کلیک کنید
3. **OAuth 2.0 Client IDs** را انتخاب کنید
4. Application type: **Desktop application** را انتخاب کنید
5. نام مناسب برای credential انتخاب کنید
6. روی **CREATE** کلیک کنید

### 4. دانلود فایل Credentials

1. پس از ایجاد credential، روی آیکون دانلود کلیک کنید
2. فایل JSON دانلود شده را به عنوان `youtube_credentials.json` در پوشه پروژه ذخیره کنید

### 5. تنظیم API Key

API Key شما: `AIzaSyATk52Q35uG1Ups7q-kCatJEUjXAO2C--k`

این کلید در فایل‌های پیکربندی استفاده می‌شود.

## نحوه استفاده

### 1. نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

### 2. اجرای اولین احراز هویت

```bash
python youtube_oauth.py
```

این دستور:
- فایل `youtube_credentials.json` را بررسی می‌کند
- مرورگر را برای احراز هویت باز می‌کند
- توکن OAuth را ذخیره می‌کند

### 3. استفاده از API

#### دانلود با OAuth (جدید)

```bash
curl -X POST "http://localhost:8000/download-youtube-oauth" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "AIzaSyATk52Q35uG1Ups7q-kCatJEUjXAO2C--k",
    "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "target_language": "Persian (FA)",
    "voice": "Fenrir",
    "use_oauth": true,
    "transcript_language": "en"
  }'
```

#### دانلود معمولی (قدیمی)

```bash
curl -X POST "http://localhost:8000/download-youtube" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "AIzaSyATk52Q35uG1Ups7q-kCatJEUjXAO2C--k",
    "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "target_language": "Persian (FA)",
    "voice": "Fenrir"
  }'
```

## مزایای OAuth

### 1. دسترسی بهتر
- دسترسی به ویدیوهای خصوصی (با مجوز)
- کاهش محدودیت‌های دانلود
- کیفیت بهتر استخراج متن

### 2. امنیت بیشتر
- احراز هویت رسمی
- عدم نیاز به کوکی‌های منقضی
- مدیریت بهتر مجوزها

### 3. قابلیت‌های پیشرفته
- دسترسی به metadata کامل ویدیو
- استخراج زیرنویس با کیفیت بالا
- پشتیبانی از زبان‌های مختلف

## عیب‌یابی

### خطای "فایل credentials یافت نشد"
- مطمئن شوید فایل `youtube_credentials.json` در پوشه پروژه موجود است
- نام فایل دقیقاً `youtube_credentials.json` باشد

### خطای "احراز هویت ناموفق"
- API Key را بررسی کنید
- YouTube Data API v3 را فعال کرده باشید
- OAuth credentials را درست ایجاد کرده باشید

### خطای "ویدیو خصوصی است"
- ویدیو باید عمومی باشد
- یا شما باید دسترسی به آن داشته باشید

## فایل‌های مهم

- `youtube_oauth.py`: مدیریت OAuth
- `youtube_credentials.json`: فایل credentials (ایجاد کنید)
- `youtube_token.pickle`: توکن OAuth (خودکار ایجاد می‌شود)
- `api.py`: endpoint های API

## نکات مهم

1. **امنیت**: فایل `youtube_credentials.json` را در git commit نکنید
2. **تازه‌سازی**: توکن OAuth خودکار تازه‌سازی می‌شود
3. **پشتیبان‌گیری**: فایل `youtube_token.pickle` را نگه دارید
4. **محدودیت‌ها**: YouTube API محدودیت‌های روزانه دارد

## مثال کامل

```python
from youtube_oauth import YouTubeOAuthManager

# ایجاد manager
oauth_manager = YouTubeOAuthManager("YOUR_API_KEY")

# احراز هویت
if oauth_manager.authenticate():
    # دریافت اطلاعات ویدیو
    video_info = oauth_manager.get_video_info("VIDEO_ID")
    print(f"عنوان: {video_info['title']}")
    
    # دریافت متن ویدیو
    transcript = oauth_manager.get_video_transcript("VIDEO_ID", "en")
    print(f"متن: {transcript[:100]}...")
```

## پشتیبانی

در صورت بروز مشکل:
1. لاگ‌ها را بررسی کنید
2. API Key را تست کنید
3. فایل‌های credentials را بررسی کنید
4. با تیم پشتیبانی تماس بگیرید
