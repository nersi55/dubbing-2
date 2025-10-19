# راهنمای دسترسی از راه دور به API

## تغییرات انجام شده

فایل `run_api.py` اصلاح شده تا بتواند از راه دور قابل دسترسی باشد:

### تغییرات کلیدی:
1. **Host تغییر یافت**: از `127.0.0.1` به `0.0.0.0` 
2. **نمایش IP محلی**: IP واقعی شبکه نمایش داده می‌شود
3. **راهنمای امنیتی**: نکات مهم امنیتی اضافه شد

## نحوه استفاده

### 1. اجرای سرور
```bash
python run_api.py
```

### 2. دسترسی محلی
- API: `http://127.0.0.1:8002`
- مستندات: `http://127.0.0.1:8002/docs`

### 3. دسترسی از راه دور
- API: `http://[IP_SERVER]:8002`
- مستندات: `http://[IP_SERVER]:8002/docs`

## تنظیمات امنیتی

### 1. فایروال
```bash
# macOS - باز کردن پورت
sudo pfctl -f /etc/pf.conf
echo "pass in proto tcp from any to any port 8002" | sudo pfctl -f -

# Linux - UFW
sudo ufw allow 8002

# Windows - Windows Firewall
# Windows Defender Firewall > Advanced Settings > Inbound Rules > New Rule
```

### 2. محدود کردن دسترسی (اختیاری)
اگر می‌خواهید فقط IP های خاص دسترسی داشته باشند:

```python
# در فایل api_simple.py اضافه کنید:
from fastapi import Request, HTTPException

@app.middleware("http")
async def limit_remote_access(request: Request, call_next):
    allowed_ips = ["192.168.1.0/24", "10.0.0.0/8"]  # IP های مجاز
    client_ip = request.client.host
    
    # بررسی IP (کد کامل نیاز به پیاده‌سازی دارد)
    # ...
    
    response = await call_next(request)
    return response
```

### 3. استفاده از VPN (توصیه شده)
- راه‌اندازی VPN سرور
- اتصال از طریق VPN
- امنیت بیشتر

## تست دسترسی

### 1. تست محلی
```bash
curl http://127.0.0.1:8002/health
```

### 2. تست از راه دور
```bash
curl http://[IP_SERVER]:8002/health
```

### 3. تست از مرورگر
- باز کردن `http://[IP_SERVER]:8002/docs`
- تست API endpoints

## عیب‌یابی

### 1. مشکل اتصال
- بررسی فایروال
- بررسی IP صحیح
- بررسی پورت باز

### 2. مشکل امنیتی
- استفاده از HTTPS (نیاز به SSL)
- محدود کردن IP ها
- استفاده از Authentication

## نکات مهم

⚠️ **هشدار امنیتی**: 
- API در حالت عمومی در دسترس است
- برای تولید، حتماً Authentication اضافه کنید
- از HTTPS استفاده کنید
- IP ها را محدود کنید

✅ **توصیه‌ها**:
- استفاده از VPN
- محدود کردن دسترسی
- نظارت بر لاگ‌ها
- به‌روزرسانی منظم
