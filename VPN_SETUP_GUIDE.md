# راهنمای راه‌اندازی VPN برای دور زدن محدودیت‌های YouTube
# VPN Setup Guide for Bypassing YouTube Restrictions

## مشکل
YouTube دسترسی از سرور شما را کاملاً مسدود کرده است.

## راه‌حل: استفاده از VPN

### روش 1: OpenVPN (پیشنهادی)

#### نصب OpenVPN
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install openvpn

# CentOS/RHEL
sudo yum install openvpn
# یا
sudo dnf install openvpn
```

#### دریافت فایل پیکربندی VPN
1. از سرویس‌های VPN رایگان یا پولی استفاده کنید:
   - **رایگان**: ProtonVPN, Windscribe, TunnelBear
   - **پولی**: NordVPN, ExpressVPN, Surfshark

2. فایل `.ovpn` را دانلود کنید

3. فایل را به سرور آپلود کنید:
```bash
scp your-config.ovpn user@server:/path/to/project/
```

#### اتصال به VPN
```bash
# اتصال
sudo openvpn --config your-config.ovpn

# اتصال در پس‌زمینه
sudo openvpn --config your-config.ovpn --daemon

# قطع اتصال
sudo pkill openvpn
```

### روش 2: WireGuard (سریع‌تر)

#### نصب WireGuard
```bash
# Ubuntu/Debian
sudo apt install wireguard

# CentOS/RHEL
sudo yum install epel-release
sudo yum install wireguard-tools
```

#### پیکربندی WireGuard
```bash
# ایجاد کلید خصوصی
wg genkey | sudo tee /etc/wireguard/private.key
sudo chmod 600 /etc/wireguard/private.key

# ایجاد کلید عمومی
sudo cat /etc/wireguard/private.key | wg pubkey | sudo tee /etc/wireguard/public.key
```

#### فایل پیکربندی
```ini
# /etc/wireguard/wg0.conf
[Interface]
PrivateKey = YOUR_PRIVATE_KEY
Address = 10.0.0.2/24
DNS = 8.8.8.8

[Peer]
PublicKey = SERVER_PUBLIC_KEY
Endpoint = server-ip:51820
AllowedIPs = 0.0.0.0/0
```

#### اتصال
```bash
# اتصال
sudo wg-quick up wg0

# قطع اتصال
sudo wg-quick down wg0
```

### روش 3: استفاده از Docker با VPN

#### ایجاد Dockerfile
```dockerfile
FROM python:3.9-slim

# نصب yt-dlp
RUN pip install yt-dlp

# کپی فایل‌های پروژه
COPY . /app
WORKDIR /app

# اجرای برنامه
CMD ["python", "run_simple.py"]
```

#### اجرا با VPN
```bash
# اجرای کانتینر با VPN
docker run --rm -it \
  --cap-add=NET_ADMIN \
  --device /dev/net/tun \
  -v $(pwd):/app \
  your-image
```

### روش 4: استفاده از سرویس‌های Cloud

#### تغییر سرور
1. سرور جدید در منطقه‌ای متفاوت ایجاد کنید
2. پروژه را روی سرور جدید کلون کنید
3. برنامه را روی سرور جدید اجرا کنید

#### استفاده از سرویس‌های Cloud
- **AWS EC2**: سرور در منطقه‌ای متفاوت
- **Google Cloud**: تغییر منطقه
- **DigitalOcean**: سرور جدید
- **Vultr**: سرور در کشور متفاوت

## تست VPN

### بررسی IP
```bash
# بررسی IP فعلی
curl ifconfig.me

# بررسی IP بعد از VPN
curl ifconfig.me
```

### تست دسترسی به YouTube
```bash
# تست دسترسی
curl -I https://youtube.com

# تست yt-dlp
yt-dlp --print-json 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
```

## راه‌حل‌های جایگزین

### 1. آپلود فایل ویدیو
```bash
# دانلود روی کامپیوتر شخصی
yt-dlp "https://www.youtube.com/watch?v=VIDEO_ID"

# آپلود به سرور
scp video.mp4 user@server:/path/to/project/

# استفاده از راه‌حل آپلود
python file_upload_solution.py
```

### 2. استفاده از Proxy
```bash
# راه‌اندازی پروکسی
python setup_proxies.py

# تست پروکسی
python advanced_youtube_downloader.py
```

### 3. تغییر DNS
```bash
# تغییر DNS
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
echo "nameserver 1.1.1.1" | sudo tee -a /etc/resolv.conf
```

## عیب‌یابی

### مشکل 1: VPN اتصال برقرار نمی‌کند
```bash
# بررسی وضعیت
sudo systemctl status openvpn

# بررسی لاگ‌ها
sudo journalctl -u openvpn -f
```

### مشکل 2: سرعت کم
```bash
# تست سرعت
speedtest-cli

# تغییر سرور VPN
# از سرور نزدیک‌تر استفاده کنید
```

### مشکل 3: YouTube همچنان مسدود است
```bash
# پاک کردن کش DNS
sudo systemctl flush-dns

# راه‌اندازی مجدد شبکه
sudo systemctl restart networking
```

## نکات مهم

1. **همیشه از VPN معتبر استفاده کنید**
2. **سرور VPN را در منطقه‌ای متفاوت انتخاب کنید**
3. **فایل‌های پیکربندی را امن نگه دارید**
4. **در صورت مشکل، از روش آپلود فایل استفاده کنید**

## پشتیبانی

در صورت مشکل:
1. لاگ‌های VPN را بررسی کنید
2. IP را چک کنید
3. از روش‌های جایگزین استفاده کنید
4. با پشتیبانی VPN تماس بگیرید

---
**تاریخ به‌روزرسانی**: 2024
**نسخه**: 1.0
