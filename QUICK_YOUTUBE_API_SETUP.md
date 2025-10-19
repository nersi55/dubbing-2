# راهنمای سریع تنظیم YouTube API

## 🚀 شروع سریع

### 1. نصب وابستگی‌ها
```bash
# در virtual environment
source venv/bin/activate
pip install requests google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 2. تنظیم OAuth2 (پیشنهادی)
```bash
# کپی فایل credentials
cp youtube_credentials.json .

# تست
python test_youtube_simple.py
```

### 3. تنظیم API Key (اختیاری)
```bash
# تنظیم متغیر محیطی
export YOUTUBE_API_KEY="YOUR_API_KEY"

# تست
python test_youtube_simple.py
```

## ✅ تست موفق

اگر پیام زیر را می‌بینید، تنظیمات درست است:
```
🎉 حداقل یک روش کار می‌کند!
```

## 🔧 استفاده در کد

```python
from dubbing_functions import VideoDubbingApp

# با YouTube API
app = VideoDubbingApp(
    api_key="YOUR_GOOGLE_AI_KEY",
    youtube_api_key="YOUR_YOUTUBE_API_KEY"  # اختیاری
)

# اعتبارسنجی ویدیو
is_valid = app.validate_youtube_video("https://youtube.com/watch?v=VIDEO_ID")
```

## 📚 راهنمای کامل

برای راهنمای کامل، فایل `YOUTUBE_API_SETUP.md` را مطالعه کنید.

## 🆘 عیب‌یابی

### مشکل: OAuth2 کار نمی‌کند
```bash
# حذف token قدیمی
rm youtube_token.pickle

# تست دوباره
python test_youtube_simple.py
```

### مشکل: API Key کار نمی‌کند
```bash
# بررسی API Key
echo $YOUTUBE_API_KEY

# تست API Key
curl "https://www.googleapis.com/youtube/v3/videos?part=snippet&id=dQw4w9WgXcQ&key=YOUR_API_KEY"
```
