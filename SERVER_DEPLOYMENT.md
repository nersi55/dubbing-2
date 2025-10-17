# 🚀 راهنمای استقرار سرور - دوبله خودکار ویدیو

این راهنما برای استقرار پروژه دوبله خودکار ویدیو روی سرورهای مختلف طراحی شده است.

## 📋 پیش‌نیازها

### 1. سیستم عامل
- **Ubuntu/Debian** (توصیه شده)
- **CentOS/RHEL**
- **Windows Server**
- **macOS Server**

### 2. نرم‌افزارهای مورد نیاز
- **Python 3.8+**
- **FFmpeg**
- **Rubberband**
- **Git**

## 🔧 نصب خودکار (توصیه شده)

### Ubuntu/Debian:
```bash
# به‌روزرسانی سیستم
sudo apt update && sudo apt upgrade -y

# نصب پیش‌نیازها
sudo apt install -y python3 python3-pip python3-venv git ffmpeg rubberband-cli

# کلون کردن پروژه
git clone <repository-url>
cd dubing-2

# اجرای اسکریپت نصب
chmod +x install_dependencies.sh
./install_dependencies.sh
```

### CentOS/RHEL:
```bash
# نصب EPEL repository
sudo yum install -y epel-release

# نصب پیش‌نیازها
sudo yum install -y python3 python3-pip git ffmpeg rubberband

# کلون کردن پروژه
git clone <repository-url>
cd dubing-2

# اجرای اسکریپت نصب
chmod +x install_dependencies.sh
./install_dependencies.sh
```

## 🎨 نصب فونت Vazirmatn

### روش خودکار:
```bash
python install_fonts.py
```

### روش دستی:
```bash
# ایجاد پوشه فونت‌ها
mkdir -p fonts

# دانلود فونت‌های Vazirmatn
curl -L https://github.com/rastikerdar/vazirmatn/raw/main/fonts/ttf/Vazirmatn-Regular.ttf -o fonts/Vazirmatn-Regular.ttf
curl -L https://github.com/rastikerdar/vazirmatn/raw/main/fonts/ttf/Vazirmatn-Medium.ttf -o fonts/Vazirmatn-Medium.ttf
curl -L https://github.com/rastikerdar/vazirmatn/raw/main/fonts/ttf/Vazirmatn-Bold.ttf -o fonts/Vazirmatn-Bold.ttf
```

## 🐍 راه‌اندازی محیط مجازی Python

```bash
# ایجاد محیط مجازی
python3 -m venv venv

# فعال‌سازی محیط مجازی
source venv/bin/activate  # Linux/macOS
# یا
venv\Scripts\activate     # Windows

# نصب وابستگی‌ها
pip install -r requirements.txt
```

## 🚀 اجرای برنامه

### روش 1: اجرای مستقیم
```bash
python run.py
```

### روش 2: اجرای Streamlit
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### روش 3: اجرای API
```bash
python run_api.py
```

## 🌐 تنظیمات سرور

### 1. فایروال
```bash
# باز کردن پورت 8501 برای Streamlit
sudo ufw allow 8501

# باز کردن پورت 8000 برای API
sudo ufw allow 8000
```

### 2. Nginx (اختیاری)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Systemd Service (اختیاری)
```bash
# ایجاد فایل سرویس
sudo nano /etc/systemd/system/dubing.service
```

محتوای فایل:
```ini
[Unit]
Description=Auto Video Dubbing Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/dubing-2
Environment=PATH=/path/to/dubing-2/venv/bin
ExecStart=/path/to/dubing-2/venv/bin/python run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

فعال‌سازی سرویس:
```bash
sudo systemctl daemon-reload
sudo systemctl enable dubing
sudo systemctl start dubing
```

## 🔍 عیب‌یابی

### مشکل فونت Vazirmatn:
```bash
# بررسی وجود فونت‌های محلی
ls -la fonts/

# بررسی فونت‌های سیستم
fc-list | grep -i vazirmatn

# نصب مجدد فونت‌ها
python install_fonts.py
```

### مشکل FFmpeg:
```bash
# بررسی نصب FFmpeg
ffmpeg -version

# نصب مجدد FFmpeg
sudo apt install --reinstall ffmpeg  # Ubuntu/Debian
sudo yum reinstall ffmpeg            # CentOS/RHEL
```

### مشکل Rubberband:
```bash
# بررسی نصب Rubberband
rubberband --version

# نصب مجدد Rubberband
sudo apt install --reinstall rubberband-cli  # Ubuntu/Debian
sudo yum reinstall rubberband                # CentOS/RHEL
```

## 📁 ساختار فایل‌ها

```
dubing-2/
├── fonts/                    # فونت‌های محلی پروژه
│   ├── Vazirmatn-Regular.ttf
│   ├── Vazirmatn-Medium.ttf
│   └── Vazirmatn-Bold.ttf
├── dubbing_work/            # پوشه کار
├── temp/                    # فایل‌های موقت
├── app.py                   # برنامه اصلی Streamlit
├── api.py                   # API FastAPI
├── run.py                   # اسکریپت اجرا
├── install_fonts.py         # نصب‌کننده فونت
└── requirements.txt         # وابستگی‌های Python
```

## 🔐 تنظیمات امنیتی

### 1. متغیرهای محیطی
```bash
# ایجاد فایل .env
nano .env
```

محتوای فایل:
```env
GOOGLE_API_KEY=your_api_key_here
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### 2. محدود کردن دسترسی
```bash
# محدود کردن دسترسی به فایل‌های حساس
chmod 600 .env
chmod 700 dubbing_work/
```

## 📊 مانیتورینگ

### بررسی وضعیت سرویس:
```bash
# بررسی لاگ‌ها
sudo journalctl -u dubing -f

# بررسی استفاده از منابع
htop
```

### بررسی پورت‌ها:
```bash
# بررسی پورت‌های باز
netstat -tlnp | grep :8501
netstat -tlnp | grep :8000
```

## 🆘 پشتیبانی

در صورت بروز مشکل:

1. **بررسی لاگ‌ها**: `tail -f /var/log/syslog`
2. **بررسی وضعیت سرویس**: `systemctl status dubing`
3. **بررسی فونت‌ها**: `python -c "from dubbing_functions import DubbingApp; app = DubbingApp(); print(app._get_font_path('vazirmatn'))"`
4. **بررسی وابستگی‌ها**: `python run.py`

## ✅ چک‌لیست استقرار

- [ ] Python 3.8+ نصب شده
- [ ] FFmpeg نصب شده
- [ ] Rubberband نصب شده
- [ ] فونت‌های Vazirmatn در پوشه `fonts/` موجود است
- [ ] وابستگی‌های Python نصب شده
- [ ] متغیرهای محیطی تنظیم شده
- [ ] فایروال پیکربندی شده
- [ ] برنامه بدون خطا اجرا می‌شود
- [ ] دسترسی به وب‌سایت برقرار است

---

**نکته مهم**: این راهنما برای سرورهای Linux نوشته شده است. برای Windows Server، مراحل مشابه است اما دستورات متفاوت خواهد بود.
