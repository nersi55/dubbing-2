# راهنمای سریع دسترسی از راه دور

## 🚀 شروع سریع

### 1. اجرای سرور
```bash
python run_api.py
```

### 2. باز کردن فایروال (macOS)
```bash
sudo ./setup_firewall.sh
```

### 3. تست دسترسی
```bash
python test_remote_access.py
```

## 📱 آدرس‌های دسترسی

- **محلی**: `http://127.0.0.1:8002`
- **شبکه**: `http://[IP_SERVER]:8002`
- **مستندات**: `http://[IP_SERVER]:8002/docs`

## 🔧 تغییرات انجام شده

✅ **فایل `run_api.py`**:
- Host تغییر یافت از `127.0.0.1` به `0.0.0.0`
- نمایش IP محلی اضافه شد
- راهنمای امنیتی اضافه شد

✅ **فایل‌های جدید**:
- `test_remote_access.py` - تست دسترسی
- `setup_firewall.sh` - تنظیم فایروال
- `REMOTE_ACCESS_GUIDE.md` - راهنمای کامل

## ⚠️ نکات امنیتی

- API در حالت عمومی در دسترس است
- برای تولید، Authentication اضافه کنید
- از VPN استفاده کنید
- IP ها را محدود کنید

## 🆘 عیب‌یابی

### مشکل اتصال
1. بررسی فایروال: `sudo ./setup_firewall.sh`
2. بررسی IP: `python test_remote_access.py`
3. بررسی پورت: `lsof -i :8002`

### مشکل امنیتی
- استفاده از HTTPS
- محدود کردن IP ها
- اضافه کردن Authentication
