# 🎉 Release v2.0.0 - OAuth یوتیوب

## 🔐 OAuth یوتیوب اضافه شد!

این نسخه شامل پیاده‌سازی کامل OAuth یوتیوب برای دسترسی بهتر و امن‌تر به ویدیوهای یوتیوب است.

## ✨ ویژگی‌های جدید

### 🔐 احراز هویت OAuth
- احراز هویت رسمی با Google Cloud Console
- مدیریت خودکار توکن‌ها و تازه‌سازی
- پشتیبانی از scopes مختلف یوتیوب

### 📥 دانلود پیشرفته
- endpoint جدید `/download-youtube-oauth`
- دسترسی به ویدیوهای خصوصی (با مجوز)
- کاهش محدودیت‌های دانلود یوتیوب
- fallback هوشمند به دانلود معمولی

### 🛡️ امنیت بهتر
- عدم نیاز به کوکی‌های منقضی
- احراز هویت رسمی
- مدیریت بهتر مجوزها

## 🚀 نحوه استفاده

### 1. راه‌اندازی OAuth
```bash
# راه‌اندازی خودکار
python setup_oauth.py

# یا راه‌اندازی دستی
# 1. فایل youtube_credentials.json را از Google Cloud Console دریافت کنید
# 2. در پوشه پروژه قرار دهید
```

### 2. استفاده از API
```bash
# دانلود با OAuth (جدید)
curl -X POST "http://localhost:8000/download-youtube-oauth" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "YOUR_API_KEY",
    "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "target_language": "Persian (FA)",
    "voice": "Fenrir",
    "use_oauth": true
  }'
```

## 📁 فایل‌های جدید

- `youtube_oauth.py` - مدیریت OAuth یوتیوب
- `test_oauth_*.py` - تست‌های OAuth
- `setup_oauth.py` - راه‌اندازی خودکار
- `OAUTH_403_FIX.md` - راهنمای حل مشکل
- `YOUTUBE_OAUTH_GUIDE.md` - راهنمای کامل
- `README_OAUTH.md` - خلاصه OAuth

## 🔧 بهبودها

- به‌روزرسانی `requirements.txt` با کتابخانه‌های OAuth
- بهبود مدیریت خطاها
- اضافه شدن `.gitignore` برای فایل‌های حساس
- بهبود API endpoints
- بهبود مستندات

## 📚 مستندات

- **راهنمای کامل OAuth**: [YOUTUBE_OAUTH_GUIDE.md](YOUTUBE_OAUTH_GUIDE.md)
- **حل مشکل OAuth**: [OAUTH_403_FIX.md](OAUTH_403_FIX.md)
- **خلاصه OAuth**: [README_OAUTH.md](README_OAUTH.md)

## 🎯 مزایای OAuth

1. **دسترسی بهتر**: کاهش محدودیت‌های دانلود
2. **امنیت بیشتر**: احراز هویت رسمی
3. **کیفیت بالاتر**: استخراج متن بهتر
4. **قابلیت‌های پیشرفته**: دسترسی به metadata کامل

## 🔒 امنیت

- فایل‌های حساس در `.gitignore` قرار گرفته‌اند
- OAuth credentials باید از Google Cloud Console دریافت شوند
- توکن‌ها خودکار تازه‌سازی می‌شوند

## 🧪 تست

```bash
# تست OAuth
python test_oauth_simple.py

# تست API
python test_oauth_api.py

# تست کامل
python test_youtube_oauth.py
```

---

**نکته**: این نسخه با نسخه‌های قبلی سازگار است و می‌توانید از هر دو روش (OAuth و معمولی) استفاده کنید.
