# Changelog - دوبله خودکار ویدیو

## [v2.0.0] - 2024-12-19

### 🔐 OAuth یوتیوب (جدید)
- **احراز هویت OAuth** با Google Cloud Console
- **endpoint جدید** `/download-youtube-oauth`
- **مدیریت خودکار توکن‌ها** و تازه‌سازی
- **fallback هوشمند** به دانلود معمولی

### ✨ ویژگی‌های جدید
- 🔐 **OAuth یوتیوب**: احراز هویت رسمی برای دسترسی بهتر
- 📥 **دانلود پیشرفته**: دسترسی به ویدیوهای خصوصی (با مجوز)
- 📝 **استخراج متن بهتر**: کیفیت بالاتر با OAuth
- 🛡️ **امنیت بیشتر**: عدم نیاز به کوکی‌های منقضی
- 🔄 **fallback خودکار**: در صورت خطای OAuth، از دانلود معمولی استفاده می‌کند

### 📁 فایل‌های جدید
- `youtube_oauth.py` - مدیریت OAuth یوتیوب
- `test_oauth_*.py` - تست‌های OAuth
- `setup_oauth.py` - راه‌اندازی خودکار OAuth
- `OAUTH_403_FIX.md` - راهنمای حل مشکل OAuth
- `YOUTUBE_OAUTH_GUIDE.md` - راهنمای کامل OAuth
- `README_OAUTH.md` - خلاصه OAuth

### 🔧 بهبودها
- **به‌روزرسانی requirements.txt** با کتابخانه‌های OAuth
- **بهبود مدیریت خطاها** در OAuth
- **اضافه شدن .gitignore** برای فایل‌های حساس
- **بهبود API endpoints** با پشتیبانی از OAuth
- **بهبود مستندات** و راهنماها

### 🎯 مزایای OAuth
1. **دسترسی بهتر**: کاهش محدودیت‌های دانلود یوتیوب
2. **امنیت بیشتر**: احراز هویت رسمی با Google
3. **کیفیت بالاتر**: استخراج متن بهتر
4. **قابلیت‌های پیشرفته**: دسترسی به metadata کامل ویدیو

### 🚀 نحوه استفاده

#### راه‌اندازی OAuth:
```bash
# راه‌اندازی خودکار
python setup_oauth.py

# یا راه‌اندازی دستی
# 1. فایل youtube_credentials.json را از Google Cloud Console دریافت کنید
# 2. در پوشه پروژه قرار دهید
# 3. API را اجرا کنید
```

#### استفاده از API:
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

# دانلود معمولی (قدیمی)
curl -X POST "http://localhost:8000/download-youtube" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "YOUR_API_KEY",
    "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "target_language": "Persian (FA)",
    "voice": "Fenrir"
  }'
```

### 📚 مستندات
- **راهنمای کامل OAuth**: [YOUTUBE_OAUTH_GUIDE.md](YOUTUBE_OAUTH_GUIDE.md)
- **حل مشکل OAuth**: [OAUTH_403_FIX.md](OAUTH_403_FIX.md)
- **خلاصه OAuth**: [README_OAUTH.md](README_OAUTH.md)

### 🔒 امنیت
- فایل‌های حساس (`youtube_credentials.json`, `youtube_token.pickle`) در `.gitignore` قرار گرفته‌اند
- OAuth credentials باید از Google Cloud Console دریافت شوند
- توکن‌ها خودکار تازه‌سازی می‌شوند

---

## [v1.0.0] - 2024-12-18

### ویژگی‌های اولیه
- 📥 دانلود از یوتیوب
- 🎤 استخراج صدا با Whisper
- 🌐 ترجمه با Google Gemini AI
- 🎵 تولید صدا با 30+ گوینده
- 🎬 ترکیب نهایی ویدیو
- 🎛️ تنظیمات پیشرفته
