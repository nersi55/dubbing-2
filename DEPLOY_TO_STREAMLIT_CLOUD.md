# 🚀 راهنمای استقرار در Streamlit Cloud
# Deploy to Streamlit Cloud Guide

## 📋 مراحل استقرار (Deployment Steps)

### 1. آماده‌سازی Repository
```bash
# اطمینان از وجود فایل‌های مورد نیاز
ls -la
# باید شامل موارد زیر باشد:
# - simple_app.py (فایل اصلی)
# - requirements.txt (وابستگی‌ها)
# - .streamlit/config.toml (تنظیمات)
# - dubbing_functions.py (توابع دوبله)
# - install_fonts.py (نصب فونت)
# - fonts/ (پوشه فونت‌ها)
```

### 2. آپلود به GitHub
1. **ایجاد Repository جدید در GitHub:**
   - نام: `dubbing-2` (یا هر نام دلخواه)
   - Public یا Private (Streamlit Cloud از هر دو پشتیبانی می‌کند)

2. **آپلود فایل‌ها:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Auto Video Dubbing App"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/dubbing-2.git
   git push -u origin main
   ```

### 3. استقرار در Streamlit Cloud
1. **ورود به Streamlit Cloud:**
   - آدرس: https://share.streamlit.io
   - ورود با حساب GitHub

2. **ایجاد اپلیکیشن جدید:**
   - کلیک روی "New app"
   - Repository: `YOUR_USERNAME/dubbing-2`
   - Branch: `main`
   - Main file path: `simple_app.py`
   - Requirements file: `requirements.txt`

3. **تنظیمات پیشرفته (اختیاری):**
   - App URL: `dubbing-2` (برای آدرس کوتاه‌تر)
   - Environment variables: (در صورت نیاز)

### 4. تست و بررسی
1. **بررسی لاگ‌ها:**
   - در صفحه اپلیکیشن، روی "Manage app" کلیک کنید
   - بخش "Logs" را بررسی کنید

2. **تست عملکرد:**
   - وارد کردن لینک YouTube
   - بررسی مراحل پردازش
   - دانلود ویدیو نهایی

## 🔧 تنظیمات مهم (Important Settings)

### فایل‌های کلیدی:
- **`simple_app.py`** - اپلیکیشن اصلی Streamlit
- **`requirements.txt`** - وابستگی‌های Python
- **`.streamlit/config.toml`** - تنظیمات Streamlit
- **`dubbing_functions.py`** - توابع دوبله ویدیو
- **`install_fonts.py`** - نصب فونت Vazirmatn

### متغیرهای محیطی (Environment Variables):
```
# در صورت نیاز می‌توانید این متغیرها را تنظیم کنید:
GOOGLE_API_KEY=your_api_key_here
HOST=0.0.0.0
PORT=8501
```

## 🎯 آدرس نهایی (Final URL)
پس از استقرار موفق، اپلیکیشن شما در آدرس زیر در دسترس خواهد بود:
```
https://dubbing-2-YOUR_APP_ID.streamlit.app/
```

## 🐛 عیب‌یابی (Troubleshooting)

### خطاهای رایج:
1. **ModuleNotFoundError:**
   - بررسی `requirements.txt`
   - اطمینان از وجود تمام وابستگی‌ها

2. **Font not found:**
   - بررسی وجود فایل `install_fonts.py`
   - اطمینان از وجود پوشه `fonts/`

3. **FFmpeg not found:**
   - `ffmpeg-python` در requirements موجود است
   - Streamlit Cloud خودکار FFmpeg را نصب می‌کند

4. **Memory issues:**
   - کاهش اندازه ویدیوهای ورودی
   - استفاده از فشرده‌سازی

### بررسی وضعیت:
```bash
# بررسی لاگ‌های محلی
streamlit run simple_app.py --server.port 8501

# بررسی وابستگی‌ها
pip install -r requirements.txt
```

## 📊 ویژگی‌های اپلیکیشن
- ✅ دانلود خودکار از YouTube
- ✅ استخراج متن با Whisper
- ✅ ترجمه به فارسی
- ✅ زیرنویس سفارشی
- ✅ متن ثابت پایین
- ✅ دانلود ویدیو نهایی

## 🔄 به‌روزرسانی (Updates)
برای به‌روزرسانی اپلیکیشن:
1. تغییرات را در GitHub commit کنید
2. Streamlit Cloud خودکار اپلیکیشن را به‌روزرسانی می‌کند
3. چند دقیقه صبر کنید تا تغییرات اعمال شود

## 📞 پشتیبانی (Support)
در صورت بروز مشکل:
1. بررسی لاگ‌های Streamlit Cloud
2. تست محلی اپلیکیشن
3. بررسی وابستگی‌ها و تنظیمات
