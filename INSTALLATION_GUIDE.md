# 🚀 راهنمای نصب کامل - دوبله خودکار ویدیو

## 📋 پیش‌نیازها

### 1. Python
- **نسخه مورد نیاز:** Python 3.8 یا بالاتر
- **بررسی نسخه:** `python --version` یا `python3 --version`

### 2. سیستم‌عامل
- **macOS:** 10.14 یا بالاتر
- **Windows:** 10 یا بالاتر
- **Linux:** Ubuntu 18.04 یا بالاتر

## 🔧 نصب خودکار (توصیه می‌شود)

### روش 1: نصب کامل خودکار
```bash
python install_all.py
```

این اسکریپت تمام وابستگی‌ها را نصب و بررسی می‌کند.

## 📦 نصب دستی

### 1. نصب وابستگی‌های Python

#### برای صفحه وب:
```bash
pip install -r requirements.txt
```

#### برای API:
```bash
pip install -r requirements_api.txt
```

### 2. نصب پیش‌نیازهای سیستم

#### macOS:
```bash
# نصب Homebrew (اگر نصب نشده)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# نصب FFmpeg و Rubberband
brew install ffmpeg rubberband

# نصب فونت Vazirmatn
python install_fonts.py
```

#### Ubuntu/Debian:
```bash
# نصب FFmpeg و Rubberband
sudo apt update
sudo apt install ffmpeg rubberband-cli

# نصب فونت Vazirmatn
python install_fonts.py
```

#### Windows:
1. **FFmpeg:** از [ffmpeg.org](https://ffmpeg.org/download.html) دانلود کنید
2. **Rubberband:** از [breakfastquay.com](https://breakfastquay.com/rubberband/) دانلود کنید
3. **فونت Vazirmatn:** از [GitHub](https://github.com/rastikerdar/vazirmatn) دانلود کنید

## 🔑 تنظیم کلید Google API

### 1. دریافت کلید API
1. به [Google AI Studio](https://aistudio.google.com/) بروید
2. حساب Google خود را وارد کنید
3. کلید API جدید ایجاد کنید
4. کلید را کپی کنید

### 2. قرار دادن کلید در فایل‌ها
کلید API در فایل‌های زیر قرار دارد:
- `simple_app.py` - خط 82
- `api_simple.py` - خط 35

## 🚀 اجرای برنامه

### 1. صفحه وب (Streamlit)
```bash
python run_simple.py
```
**آدرس:** http://localhost:8580

### 2. API (FastAPI)
```bash
python run_api.py
```
**آدرس:** http://127.0.0.1:8002
**مستندات:** http://127.0.0.1:8002/docs

## 🧪 تست نصب

### 1. تست وابستگی‌ها
```bash
python -c "import streamlit, fastapi, whisper, google.generativeai; print('✅ تمام وابستگی‌ها نصب شده‌اند')"
```

### 2. تست FFmpeg
```bash
ffmpeg -version
```

### 3. تست Rubberband
```bash
rubberband --version
```

### 4. تست API
```bash
curl http://127.0.0.1:8002/health
```

## 📁 ساختار پروژه

```
dubbing-2/
├── simple_app.py              # صفحه وب اصلی
├── api_simple.py              # API اصلی
├── run_simple.py              # اجرای صفحه وب
├── run_api.py                 # اجرای API
├── requirements.txt           # وابستگی‌های صفحه وب
├── requirements_api.txt       # وابستگی‌های API
├── install_all.py             # نصب خودکار
├── dubbing_functions.py       # توابع اصلی
├── config.py                  # تنظیمات
├── dubbing_work/              # پوشه کار
└── docs/                      # مستندات
```

## ⚠️ حل مشکلات رایج

### 1. خطای "Address already in use"
```bash
# پیدا کردن پروسه‌ای که پورت را استفاده می‌کند
lsof -i :8580  # برای صفحه وب
lsof -i :8002  # برای API

# متوقف کردن پروسه
kill -9 PID
```

### 2. خطای "Module not found"
```bash
# نصب مجدد وابستگی‌ها
pip install -r requirements.txt
```

### 3. خطای FFmpeg
```bash
# بررسی مسیر FFmpeg
which ffmpeg

# اضافه کردن به PATH
export PATH="/usr/local/bin:$PATH"
```

### 4. خطای فونت
```bash
# نصب فونت Vazirmatn
python install_fonts.py

# یا دانلود دستی از GitHub
```

## 🔧 تنظیمات پیشرفته

### 1. تغییر پورت‌ها
- **صفحه وب:** فایل `run_simple.py` - خط 16
- **API:** فایل `run_api.py` - خط 15

### 2. تغییر تنظیمات زیرنویس
- **صفحه وب:** فایل `simple_app.py` - خطوط 91-104
- **API:** فایل `api_simple.py` - خطوط 90-104

### 3. تغییر کلید API
- **صفحه وب:** فایل `simple_app.py` - خط 82
- **API:** فایل `api_simple.py` - خط 35

## 📞 پشتیبانی

در صورت بروز مشکل:
1. فایل `install_all.py` را اجرا کنید
2. لاگ‌های خطا را بررسی کنید
3. با تیم ققنوس شانس تماس بگیرید

## 📚 مستندات بیشتر

- **راهنمای API:** `API_DOCUMENTATION.md`
- **راهنمای صفحه وب:** `SIMPLE_APP_README.md`
- **راهنمای کلی:** `README.md`

---
**🎬 دوبله خودکار ویدیو - ققنوس شانس**
