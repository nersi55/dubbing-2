# 🎬 دوبله خودکار ویدیو

یک برنامه وب برای دوبله خودکار ویدیوهای یوتیوب با استفاده از هوش مصنوعی Google Gemini.

## ✨ ویژگی‌ها

- 📥 **دانلود از یوتیوب**: دانلود ویدیو با بالاترین کیفیت
- 🔐 **OAuth یوتیوب**: احراز هویت رسمی برای دسترسی بهتر
- 🎤 **استخراج صدا**: تبدیل گفتار به متن با Whisper
- 🌐 **ترجمه هوشمند**: ترجمه با Google Gemini AI
- 🎵 **تولید صدا**: تبدیل متن به صدا با 30+ گوینده حرفه‌ای
- 🎬 **ترکیب نهایی**: ایجاد ویدیو دوبله شده
- 🎛️ **تنظیمات پیشرفته**: کنترل کامل بر فرآیند

## 🔐 OAuth یوتیوب (جدید)

برای دسترسی بهتر به ویدیوهای یوتیوب، از OAuth استفاده کنید:

### راه‌اندازی OAuth
```bash
# راه‌اندازی خودکار
python setup_oauth.py

# یا راه‌اندازی دستی
# 1. فایل youtube_credentials.json را از Google Cloud Console دریافت کنید
# 2. در پوشه پروژه قرار دهید
# 3. API را اجرا کنید
```

### استفاده از OAuth
```bash
# دانلود با OAuth
curl -X POST "http://localhost:8000/download-youtube-oauth" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "YOUR_API_KEY",
    "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "target_language": "Persian (FA)",
    "voice": "Fenrir",
    "use_oauth": true
  }'
```

📚 **راهنمای کامل OAuth**: [YOUTUBE_OAUTH_GUIDE.md](YOUTUBE_OAUTH_GUIDE.md)

## 🚀 نصب و اجرا

### پیش‌نیازها

1. **Python 3.8+**
2. **FFmpeg** - برای پردازش ویدیو
3. **Rubberband** - برای تنظیم سرعت صدا
4. **Vazirmatn Font** - فونت فارسی برای زیرنویس‌ها
5. **کلید Google API** - از [Google AI Studio](https://aistudio.google.com/)

### نصب FFmpeg و Rubberband

#### Windows:
- FFmpeg: [دانلود از سایت رسمی](https://ffmpeg.org/download.html)
- Rubberband: [دانلود از GitHub](https://github.com/breakfastquay/rubberband)

#### macOS:
```bash
brew install ffmpeg rubberband
```

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install ffmpeg rubberband-cli
```

### نصب فونت Vazirmatn

فونت Vazirmatn برای نمایش صحیح متن فارسی در زیرنویس‌ها ضروری است.

#### روش خودکار (توصیه شده):
```bash
python install_fonts.py
```

#### روش دستی:

##### Windows:
1. دانلود فونت از [GitHub Vazirmatn](https://github.com/rastikerdar/vazirmatn/releases)
2. استخراج فایل‌های TTF از پوشه `fonts/ttf`
3. نصب فونت‌ها با کلیک راست → "Install"

##### macOS:
```bash
# دانلود و نصب خودکار
curl -L https://github.com/rastikerdar/vazirmatn/releases/latest/download/vazirmatn.zip -o vazirmatn.zip
unzip vazirmatn.zip
cp fonts/ttf/*.ttf ~/Library/Fonts/
rm -rf vazirmatn.zip fonts/
```

##### Ubuntu/Debian:
```bash
# نصب از پکیج رسمی
sudo apt install fonts-vazirmatn
```

### اجرای برنامه

1. **کلون کردن پروژه:**
```bash
git clone <repository-url>
cd dubing-2
```

2. **نصب خودکار (توصیه شده):**
```bash
# برای سرور
chmod +x install_server.sh
./install_server.sh

# یا برای سیستم محلی
python run.py
```

3. **اجرای دستی:**
```bash
# نصب وابستگی‌ها
pip install -r requirements.txt

# نصب فونت
python install_fonts.py

# اجرای برنامه
python run.py
```

4. **اجرای Streamlit:**
```bash
streamlit run app.py
```

5. **باز کردن مرورگر:**
   - آدرس: http://localhost:8501

## 🚀 استقرار روی سرور

برای استقرار روی سرور، از راهنمای کامل استفاده کنید:

```bash
# دانلود و اجرای اسکریپت نصب سرور
chmod +x install_server.sh
./install_server.sh
```

**راهنمای کامل استقرار سرور:** [SERVER_DEPLOYMENT.md](SERVER_DEPLOYMENT.md)

### ویژگی‌های استقرار سرور:
- ✅ **فونت‌های محلی**: فونت Vazirmatn در پوشه `fonts/` پروژه
- ✅ **نصب خودکار**: اسکریپت کامل نصب و پیکربندی
- ✅ **پشتیبانی چندپلتفرمه**: Ubuntu, CentOS, macOS
- ✅ **تست خودکار**: بررسی صحت نصب فونت‌ها
- ✅ **راهنمای کامل**: مستندات تفصیلی استقرار

## 📖 راهنمای استفاده

### مرحله 1: تنظیمات اولیه
- کلید Google API را وارد کنید
- روش آپلود ویدیو را انتخاب کنید (یوتیوب یا فایل محلی)
- زبان مقصد ترجمه را انتخاب کنید

### مرحله 2: آپلود ویدیو
- **یوتیوب**: لینک ویدیو را وارد کنید
- **فایل محلی**: فایل ویدیویی را آپلود کنید

### مرحله 3: استخراج متن
- **Whisper**: برای ویدیوهای بدون زیرنویس
- **زیرنویس یوتیوب**: برای ویدیوهای دارای زیرنویس

### مرحله 4: ترجمه
- متن استخراج شده به زبان انتخابی ترجمه می‌شود

### مرحله 5: تولید صدا
- گوینده مورد نظر را انتخاب کنید
- تنظیمات لحن صدا را تعریف کنید (اختیاری)

### مرحله 6: ایجاد ویدیو نهایی
- ویدیو دوبله شده ایجاد و آماده دانلود می‌شود

## ⚙️ تنظیمات پیشرفته

### گویندگان موجود:
- Fenrir, Achird, Zubenelgenubi, Vindemiatrix
- Sadachbia, Sadaltager, Sulafat, Laomedeia
- Achernar, Alnilam, Schedar, Gacrux
- و 20+ گوینده دیگر...

### زبان‌های پشتیبانی شده:
- فارسی (FA), انگلیسی (EN), آلمانی (DE)
- فرانسوی (FR), ایتالیایی (IT), اسپانیایی (ES)
- چینی (ZH), کره‌ای (KO), روسی (RU)
- عربی (AR), ژاپنی (JA), هندی (HI)

### تنظیمات فشرده‌سازی:
- ادغام چندین دیالوگ برای کاهش تعداد سگمنت‌ها
- بهبود کیفیت و سرعت پردازش

## 🔧 عیب‌یابی

### خطاهای رایج:

1. **خطای FFmpeg:**
   - مطمئن شوید FFmpeg نصب است
   - مسیر FFmpeg را به PATH اضافه کنید

2. **خطای Google API:**
   - کلید API معتبر وارد کنید
   - مطمئن شوید API فعال است

3. **خطای حافظه:**
   - برای ویدیوهای طولانی، زمان انتظار را افزایش دهید
   - فایل‌های موقت را پاک کنید

4. **خطای دانلود یوتیوب:**
   - لینک ویدیو را بررسی کنید
   - کوکی‌های مرورگر را پاک کنید

## 📁 ساختار پروژه

```
dubing/
├── app.py                 # رابط کاربری Streamlit
├── dubbing_functions.py   # توابع اصلی دوبله
├── run.py                # اسکریپت اجرا
├── requirements.txt      # وابستگی‌های Python
├── README.md            # راهنمای پروژه
└── dubbing_work/        # پوشه کار (خودکار ایجاد می‌شود)
    ├── input_video.mp4  # ویدیو ورودی
    ├── audio.wav        # صدا استخراج شده
    ├── audio.srt        # زیرنویس اصلی
    ├── audio_fa.srt     # زیرنویس ترجمه شده
    ├── final_dubbed_video.mp4  # ویدیو نهایی
    └── dubbed_segments/ # سگمنت‌های صوتی
```

## 🤝 مشارکت

برای مشارکت در پروژه:
1. Fork کنید
2. شاخه جدید ایجاد کنید
3. تغییرات را commit کنید
4. Pull request ارسال کنید

## 📄 مجوز

این پروژه تحت مجوز MIT منتشر شده است.

## 🙏 تشکر

- Google Gemini AI برای API ترجمه و تولید صدا
- OpenAI Whisper برای تشخیص گفتار
- Streamlit برای رابط کاربری
- FFmpeg برای پردازش ویدیو


دسنرسی به API
cd /Users/nersibayat/Desktop/Programing/VScode/dubing-2 && source venv/bin/activate && python run_api.py



آدرس‌های دسترسی:
صفحه وب: http://localhost:8580
API: http://127.0.0.1:8002
مستندات API: http://127.0.0.1:8002/docs



# بررسی وضعیت API
curl http://127.0.0.1:8002/health

# شروع پردازش ویدیو
curl -X POST "http://127.0.0.1:8002/process" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://youtube.com/watch?v=VIDEO_ID"}'





**نکته**: این برنامه برای استفاده آموزشی و شخصی طراحی شده است. لطفاً قوانین کپی‌رایت و استفاده منصفانه را رعایت کنید.
---