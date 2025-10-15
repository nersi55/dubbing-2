# 🚀 راهنمای سریع - دوبله خودکار ویدیو

## ⚡ نصب و اجرای سریع

### 1️⃣ نصب وابستگی‌ها

#### Windows:
```cmd
install_dependencies.bat
```

#### macOS/Linux:
```bash
chmod +x install_dependencies.sh
./install_dependencies.sh
```

### 2️⃣ اجرای برنامه

```bash
python run.py
```

### 3️⃣ باز کردن مرورگر
- آدرس: http://localhost:8501

## 🔑 دریافت کلید API

1. به [Google AI Studio](https://aistudio.google.com/) بروید
2. وارد حساب Google خود شوید
3. روی "Get API Key" کلیک کنید
4. کلید را کپی کنید

## 📝 مراحل استفاده

1. **کلید API** را وارد کنید
2. **لینک یوتیوب** یا **فایل ویدیو** آپلود کنید
3. **زبان مقصد** را انتخاب کنید
4. **گوینده** را انتخاب کنید
5. **دکمه‌ها** را به ترتیب فشار دهید
6. **ویدیو نهایی** را دانلود کنید

## 🆘 حل مشکلات

### خطای FFmpeg:
- Windows: از [اینجا](https://ffmpeg.org/download.html) دانلود کنید
- macOS: `brew install ffmpeg`
- Ubuntu: `sudo apt install ffmpeg`

### خطای Rubberband:
- Windows: از [اینجا](https://breakfastquay.com/rubberband/) دانلود کنید
- macOS: `brew install rubberband`
- Ubuntu: `sudo apt install rubberband-cli`

### خطای Python:
- Python 3.8+ نصب کنید
- pip را به‌روزرسانی کنید: `python -m pip install --upgrade pip`

## 📁 فایل‌های مهم

- `app.py` - رابط کاربری اصلی
- `dubbing_functions.py` - توابع دوبله
- `run.py` - اسکریپت اجرا
- `test_app.py` - تست برنامه
- `config.py` - تنظیمات

## 🎯 نکات مهم

- برای ویدیوهای طولانی، زمان انتظار را افزایش دهید
- در صورت خطا، دکمه "پاکسازی" را فشار دهید
- فایل‌های موقت در پوشه `dubbing_work` ذخیره می‌شوند

---

**🎬 آماده دوبله کردن ویدیوهایتان هستید!**
