# حل مشکل OAuth 403: access_denied

## مشکل
```
Error 403: access_denied
Request details: access_type=offline scope=https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/youtube.force-ssl response_type=code redirect_uri=http://localhost:50937/ state=... flowName=GeneralOAuthFlow client_id=...
```

## علت
این خطا معمولاً به دلایل زیر رخ می‌دهد:
1. **OAuth consent screen تنظیم نشده**
2. **User type اشتباه انتخاب شده**
3. **Scopes مجاز نیستند**
4. **Redirect URI اشتباه است**
5. **Test users اضافه نشده**

## راه‌حل کامل

### مرحله 1: تنظیم OAuth Consent Screen

1. **به Google Cloud Console بروید:**
   - https://console.cloud.google.com/
   - پروژه `gen-lang-client-0683609810` را انتخاب کنید

2. **OAuth consent screen را تنظیم کنید:**
   - APIs & Services > OAuth consent screen
   - User Type: **External** را انتخاب کنید (نه Internal)
   - App name: `Video Dubbing App`
   - User support email: ایمیل خود را وارد کنید
   - Developer contact: ایمیل خود را وارد کنید

3. **Scopes را اضافه کنید:**
   - Scopes > Add or Remove Scopes
   - این scopes را اضافه کنید:
     - `https://www.googleapis.com/auth/youtube.readonly`
     - `https://www.googleapis.com/auth/youtube.force-ssl`
   - Update

4. **Test users اضافه کنید:**
   - Test users > Add users
   - ایمیل خود را اضافه کنید
   - Save

### مرحله 2: تنظیم Credentials

1. **Credentials را ویرایش کنید:**
   - APIs & Services > Credentials
   - OAuth 2.0 Client ID را انتخاب کنید
   - روی credential خود کلیک کنید

2. **Authorized redirect URIs را تنظیم کنید:**
   - Authorized redirect URIs:
     - `http://localhost:8080`
     - `http://localhost:50937`
     - `http://localhost`
   - Save

### مرحله 3: تست مجدد

1. **فایل credentials را به‌روزرسانی کنید:**
   ```bash
   # فایل جدید دانلود کنید
   # یا از فایل موجود استفاده کنید
   ```

2. **تست کنید:**
   ```bash
   python test_youtube_oauth.py
   ```

## راه‌حل سریع

اگر می‌خواهید سریع تست کنید:

### گزینه 1: استفاده از Internal User Type
1. OAuth consent screen > User Type > **Internal**
2. فقط کاربران داخل سازمان می‌توانند استفاده کنند
3. نیازی به Test users نیست

### گزینه 2: استفاده از Service Account
1. APIs & Services > Credentials > Create Credentials > Service Account
2. Service Account Key ایجاد کنید
3. از Service Account به جای OAuth استفاده کنید

## تست OAuth

```bash
# تست کامل
python test_youtube_oauth.py

# تست ساده
python youtube_oauth.py

# تست API
python -c "
from youtube_oauth import YouTubeOAuthManager
oauth = YouTubeOAuthManager('AIzaSyATk52Q35uG1Ups7q-kCatJEUjXAO2C--k')
print('احراز هویت:', oauth.authenticate())
"
```

## عیب‌یابی

### خطای "redirect_uri_mismatch"
- Authorized redirect URIs را بررسی کنید
- مطمئن شوید `http://localhost:8080` اضافه شده

### خطای "invalid_client"
- Client ID و Client Secret را بررسی کنید
- فایل credentials را دوباره دانلود کنید

### خطای "access_denied"
- OAuth consent screen را تنظیم کنید
- Test users اضافه کنید
- Scopes را مجاز کنید

## فایل‌های مهم

- `youtube_credentials.json` - فایل credentials
- `youtube_token.pickle` - توکن OAuth (خودکار ایجاد می‌شود)
- `fix_oauth_403.py` - اسکریپت حل مشکل

## نکات مهم

1. **امنیت**: فایل‌های credentials را در git commit نکنید
2. **تست**: همیشه در محیط تست اول تست کنید
3. **محدودیت‌ها**: YouTube API محدودیت‌های روزانه دارد
4. **پشتیبان‌گیری**: فایل‌های credentials را backup کنید

## پشتیبانی

در صورت بروز مشکل:
1. لاگ‌ها را بررسی کنید
2. Google Cloud Console را بررسی کنید
3. فایل‌های credentials را بررسی کنید
4. با تیم پشتیبانی تماس بگیرید
