# راهنمای تنظیم YouTube Data API v3
# YouTube Data API v3 Setup Guide

## 🎯 هدف
تنظیم YouTube Data API v3 برای بهبود عملکرد و اعتبارسنجی ویدیوها

## 🔧 روش‌های تنظیم

### **روش 1: استفاده از API Key (ساده‌ترین)**

#### 1. ایجاد پروژه در Google Cloud Console
1. به [Google Cloud Console](https://console.cloud.google.com/) بروید
2. پروژه جدید ایجاد کنید یا پروژه موجود را انتخاب کنید
3. YouTube Data API v3 را فعال کنید

#### 2. ایجاد API Key
1. به بخش "Credentials" بروید
2. "Create Credentials" > "API Key" را انتخاب کنید
3. API Key را کپی کنید

#### 3. تنظیم روی سرور
```bash
# تنظیم متغیر محیطی
export YOUTUBE_API_KEY="YOUR_API_KEY_HERE"

# یا در فایل .env
echo "YOUTUBE_API_KEY=YOUR_API_KEY_HERE" >> .env
```

### **روش 2: استفاده از OAuth2 (پیشرفته‌تر)**

#### 1. ایجاد OAuth2 Credentials
1. در Google Cloud Console، "Create Credentials" > "OAuth client ID" را انتخاب کنید
2. Application type: "Desktop application" را انتخاب کنید
3. فایل JSON را دانلود کنید

#### 2. کپی فایل credentials
```bash
# کپی فایل credentials به سرور
scp youtube_credentials.json user@server:/path/to/project/
```

## 🧪 تست تنظیمات

### **تست کامل**
```bash
python test_youtube_api.py
```

### **تست ساده**
```bash
python -c "from youtube_api_client import test_youtube_api; test_youtube_api()"
```

## 📊 مزایای استفاده از YouTube API

### **✅ مزایا:**
- **اعتبارسنجی ویدیو**: بررسی معتبر بودن ویدیو قبل از دانلود
- **اطلاعات کامل**: دریافت عنوان، مدت زمان، کانال و غیره
- **جستجوی پیشرفته**: جستجوی ویدیوها با فیلترهای مختلف
- **محدودیت کمتر**: کمتر احتمال مسدود شدن توسط YouTube

### **⚠️ محدودیت‌ها:**
- **Quota محدود**: 10,000 واحد در روز (رایگان)
- **فقط اطلاعات**: نمی‌تواند ویدیو دانلود کند
- **نیاز به احراز هویت**: API Key یا OAuth2

## 🔄 نحوه کار سیستم

### **بدون YouTube API:**
```
URL → yt-dlp → دانلود ویدیو
```

### **با YouTube API:**
```
URL → YouTube API (اعتبارسنجی) → yt-dlp → دانلود ویدیو
```

## 🛠️ تنظیمات پیشرفته

### **محدود کردن API Key**
```bash
# در Google Cloud Console:
# 1. API Key را انتخاب کنید
# 2. "Application restrictions" را تنظیم کنید
# 3. "API restrictions" را تنظیم کنید
```

### **نظارت بر استفاده**
```bash
# بررسی quota استفاده شده
# در Google Cloud Console > APIs & Services > Quotas
```

## 🚨 عیب‌یابی

### **مشکل: API Key نامعتبر**
```bash
# بررسی API Key
echo $YOUTUBE_API_KEY

# تست API Key
curl "https://www.googleapis.com/youtube/v3/videos?part=snippet&id=dQw4w9WgXcQ&key=YOUR_API_KEY"
```

### **مشکل: Quota تمام شده**
```bash
# صبر تا reset (24 ساعت)
# یا upgrade به پلن پولی
```

### **مشکل: OAuth2 کار نمی‌کند**
```bash
# بررسی فایل credentials
cat youtube_credentials.json

# حذف token قدیمی
rm youtube_token.pickle
```

## 📝 مثال استفاده

### **در کد Python:**
```python
from dubbing_functions import VideoDubbingApp

# با YouTube API
app = VideoDubbingApp(
    api_key="YOUR_GOOGLE_AI_KEY",
    youtube_api_key="YOUR_YOUTUBE_API_KEY"
)

# اعتبارسنجی ویدیو
is_valid = app.validate_youtube_video("https://youtube.com/watch?v=VIDEO_ID")

# دریافت اطلاعات ویدیو
video_info = app.get_youtube_video_info("VIDEO_ID")
```

### **در API:**
```bash
# API به طور خودکار از YouTube API استفاده می‌کند
curl -X POST "http://localhost:8002/process-youtube" \
  -H "Content-Type: application/json" \
  -d '{"youtube_url": "https://youtube.com/watch?v=VIDEO_ID"}'
```

## 🔒 امنیت

### **نکات مهم:**
- API Key را در کد hardcode نکنید
- از متغیرهای محیطی استفاده کنید
- API Key را محدود کنید
- نظارت بر استفاده داشته باشید

### **فایل‌های امنیتی:**
```bash
# اضافه کردن به .gitignore
echo "youtube_credentials.json" >> .gitignore
echo "youtube_token.pickle" >> .gitignore
echo ".env" >> .gitignore
```

## 🎉 نتیجه

پس از تنظیم صحیح، سیستم شما:
- ویدیوها را قبل از دانلود اعتبارسنجی می‌کند
- اطلاعات کامل ویدیو را نمایش می‌دهد
- کمتر توسط YouTube مسدود می‌شود
- عملکرد بهتری دارد
