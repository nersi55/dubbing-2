# راهنمای OAuth یوتیوب برای دوبله ویدیو

## خلاصه تغییرات

✅ **تکمیل شده:**
- اضافه شدن کتابخانه‌های OAuth به `requirements.txt`
- ایجاد کلاس `YouTubeOAuthManager` در `youtube_oauth.py`
- اضافه شدن توابع OAuth به `dubbing_functions.py`
- ایجاد endpoint جدید `/download-youtube-oauth` در `api.py`
- ایجاد فایل‌های راهنما و تست

## فایل‌های جدید

1. **`youtube_oauth.py`** - مدیریت OAuth یوتیوب
2. **`YOUTUBE_OAUTH_GUIDE.md`** - راهنمای کامل OAuth
3. **`test_youtube_oauth.py`** - تست‌های OAuth
4. **`youtube_credentials_template.json`** - فایل نمونه credentials

## نحوه استفاده

### 1. راه‌اندازی اولیه

```bash
# نصب وابستگی‌ها
pip install -r requirements.txt

# ایجاد فایل credentials
cp youtube_credentials_template.json youtube_credentials.json
# ویرایش فایل با اطلاعات واقعی از Google Cloud Console
```

### 2. استفاده از API

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

## مراحل راه‌اندازی Google Cloud Console

### 1. ایجاد پروژه
1. به [Google Cloud Console](https://console.cloud.google.com/) بروید
2. یک پروژه جدید ایجاد کنید
3. نام پروژه را به خاطر بسپارید

### 2. فعال‌سازی API
1. به **APIs & Services > Library** بروید
2. "YouTube Data API v3" را جستجو کنید
3. روی آن کلیک کرده و **Enable** را بزنید

### 3. ایجاد OAuth Credentials
1. به **APIs & Services > Credentials** بروید
2. روی **+ CREATE CREDENTIALS** کلیک کنید
3. **OAuth 2.0 Client IDs** را انتخاب کنید
4. Application type: **Desktop application** را انتخاب کنید
5. نام مناسب برای credential انتخاب کنید
6. روی **CREATE** کلیک کنید

### 4. دانلود فایل Credentials
1. پس از ایجاد credential، روی آیکون دانلود کلیک کنید
2. فایل JSON دانلود شده را به عنوان `youtube_credentials.json` در پوشه پروژه ذخیره کنید

## تست عملکرد

```bash
# اجرای تست‌ها
python test_youtube_oauth.py

# تست ساده OAuth
python youtube_oauth.py
```

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
