# راهنمای استقرار در Streamlit Cloud
# Streamlit Cloud Deployment Guide

## مشکل اصلی (Main Issue)
خطای signal handling در uvicorn که در محیط‌های cloud رخ می‌دهد.

## راه‌حل‌های اعمال شده (Applied Solutions)

### 1. اصلاح api_simple.py
- غیرفعال کردن reload mode در uvicorn
- استفاده از متغیرهای محیطی برای تنظیمات
- حذف signal handling که در cloud مجاز نیست

### 2. فایل‌های پیکربندی جدید
- `.streamlit/config.toml` - تنظیمات Streamlit
- `requirements_streamlit.txt` - وابستگی‌های مخصوص cloud
- `run_streamlit_cloud.py` - اسکریپت اجرای cloud

## مراحل استقرار (Deployment Steps)

### 1. آماده‌سازی فایل‌ها
```bash
# کپی کردن فایل‌های مورد نیاز
cp requirements_streamlit.txt requirements.txt
cp run_streamlit_cloud.py run.py
```

### 2. تنظیمات Streamlit Cloud
1. وارد [Streamlit Cloud](https://share.streamlit.io) شوید
2. روی "New app" کلیک کنید
3. Repository را انتخاب کنید
4. Main file path را `simple_app.py` قرار دهید
5. Requirements file را `requirements_streamlit.txt` قرار دهید

### 3. متغیرهای محیطی (Environment Variables)
در Streamlit Cloud، متغیرهای زیر را تنظیم کنید:
```
HOST=0.0.0.0
PORT=8501
RELOAD=false
```

## تست محلی (Local Testing)
```bash
# اجرای محلی
python run_streamlit_cloud.py

# یا
streamlit run simple_app.py --server.port 8501 --server.address 0.0.0.0
```

## نکات مهم (Important Notes)

### محدودیت‌های Streamlit Cloud
- FFmpeg باید در requirements باشد
- فونت‌ها باید در کد نصب شوند
- فایل‌های بزرگ ممکن است مشکل ایجاد کنند

### بهینه‌سازی
- استفاده از `requirements_streamlit.txt` برای وابستگی‌های کمتر
- غیرفعال کردن reload mode
- تنظیم headless mode

## عیب‌یابی (Troubleshooting)

### خطای Signal Handling
```
signal.signal(sig, self.signal_handler)
```
**راه‌حل:** reload=False در uvicorn.run()

### خطای FFmpeg
```
ffmpeg not found
```
**راه‌حل:** اضافه کردن ffmpeg-python به requirements

### خطای فونت
```
Font not found
```
**راه‌حل:** نصب فونت در کد با install_fonts.py

## فایل‌های کلیدی (Key Files)
- `simple_app.py` - اپلیکیشن اصلی Streamlit
- `requirements_streamlit.txt` - وابستگی‌های cloud
- `.streamlit/config.toml` - تنظیمات Streamlit
- `run_streamlit_cloud.py` - اسکریپت اجرا
