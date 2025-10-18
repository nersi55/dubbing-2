# راهنمای حل مشکل فونت در سرور لینوکس
# Linux Font Fix Guide

## مشکل
در سرور لینوکس، فونت زیرنویس اصلی درست کار می‌کند ولی فونت متن ثابت پایین (fixed text) Vazirmatn نیست.

## علت مشکل
- فونت Vazirmatn در سرور لینوکس نصب نشده است
- کد قبلی فقط مسیر فایل فونت را استفاده می‌کرد، نه نام فونت سیستم
- Linux نیاز به نام فونت سیستم دارد، نه مسیر فایل

## راه‌حل

### مرحله 1: نصب فونت Vazirmatn در سرور لینوکس

```bash
# اجرای اسکریپت نصب خودکار
chmod +x install_vazirmatn_linux.sh
sudo ./install_vazirmatn_linux.sh
```

یا نصب دستی:

```bash
# ایجاد پوشه فونت
sudo mkdir -p /usr/local/share/fonts/vazirmatn

# دانلود فونت‌ها
wget https://github.com/rastikerdar/vazirmatn/releases/download/v33.003/Vazirmatn-Regular.ttf
wget https://github.com/rastikerdar/vazirmatn/releases/download/v33.003/Vazirmatn-Medium.ttf
wget https://github.com/rastikerdar/vazirmatn/releases/download/v33.003/Vazirmatn-Bold.ttf

# کپی فونت‌ها
sudo cp Vazirmatn-*.ttf /usr/local/share/fonts/vazirmatn/

# تنظیم مجوزها
sudo chmod 644 /usr/local/share/fonts/vazirmatn/*.ttf

# به‌روزرسانی کش فونت
sudo fc-cache -fv
```

### مرحله 2: تست فونت‌ها

```bash
# تست فونت‌های نصب شده
python test_linux_font.py

# بررسی فونت‌های موجود در سیستم
fc-list | grep -i vazirmatn
```

### مرحله 3: راه‌اندازی مجدد برنامه

```bash
# توقف برنامه
pkill -f streamlit

# راه‌اندازی مجدد
python run_simple.py
```

## تغییرات اعمال شده

### 1. اصلاح کد فونت متن ثابت
- اضافه شدن منطق مشابه زیرنویس اصلی برای فونت Vazirmatn
- استفاده از نام فونت سیستم به جای مسیر فایل در Linux

### 2. پشتیبانی از مسیرهای مختلف فونت
- فونت‌های محلی پروژه
- فونت‌های سیستم macOS
- فونت‌های سیستم Linux
- فونت‌های جایگزین

### 3. فونت‌های پیش‌فرض Linux
- Vazirmatn (اولویت اول)
- DejaVu Sans
- Liberation Sans
- Arial
- Tahoma

## بررسی عملکرد

### قبل از اصلاح:
```
⚠️ فونت متن ثابت: vazirmatn (فونت سیستم)
```

### بعد از اصلاح:
```
✅ فونت متن ثابت: vazirmatn (فونت سیستم)
```

## عیب‌یابی

### اگر فونت هنوز کار نمی‌کند:

1. **بررسی نصب فونت:**
   ```bash
   fc-list | grep -i vazirmatn
   ```

2. **بررسی مجوزها:**
   ```bash
   ls -la /usr/local/share/fonts/vazirmatn/
   ```

3. **به‌روزرسانی کش فونت:**
   ```bash
   sudo fc-cache -fv
   ```

4. **راه‌اندازی مجدد سیستم:**
   ```bash
   sudo reboot
   ```

### اگر فونت‌های جایگزین استفاده می‌شوند:
- DejaVu Sans: فونت خوب برای فارسی
- Liberation Sans: فونت مناسب برای متن فارسی
- Arial: فونت پیش‌فرض سیستم

## نکات مهم

1. **فونت Vazirmatn بهترین گزینه** برای متن فارسی است
2. **راه‌اندازی مجدد برنامه** بعد از نصب فونت ضروری است
3. **مجوزهای صحیح** برای فایل‌های فونت مهم است
4. **کش فونت** باید به‌روزرسانی شود

## پشتیبانی

اگر مشکل ادامه داشت:
1. لاگ‌های برنامه را بررسی کنید
2. خروجی `test_linux_font.py` را بررسی کنید
3. فونت‌های موجود در سیستم را لیست کنید
4. مجوزهای فایل‌های فونت را بررسی کنید
