#!/bin/bash
"""
اسکریپت نصب وابستگی‌های YouTube API
YouTube API Dependencies Installation Script
"""

echo "🚀 نصب وابستگی‌های YouTube API..."
echo "================================="

# بررسی Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 یافت نشد"
    exit 1
fi

echo "✅ Python3 یافت شد"

# نصب وابستگی‌های YouTube API
echo "📦 نصب وابستگی‌های YouTube API..."

pip install google-api-python-client>=2.100.0
if [ $? -eq 0 ]; then
    echo "✅ google-api-python-client نصب شد"
else
    echo "❌ خطا در نصب google-api-python-client"
    exit 1
fi

pip install google-auth-httplib2>=0.1.0
if [ $? -eq 0 ]; then
    echo "✅ google-auth-httplib2 نصب شد"
else
    echo "❌ خطا در نصب google-auth-httplib2"
    exit 1
fi

pip install google-auth-oauthlib>=1.0.0
if [ $? -eq 0 ]; then
    echo "✅ google-auth-oauthlib نصب شد"
else
    echo "❌ خطا در نصب google-auth-oauthlib"
    exit 1
fi

# تست نصب
echo "🧪 تست نصب..."
python3 -c "
try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    print('✅ تمام وابستگی‌ها نصب شدند')
except ImportError as e:
    print(f'❌ خطا در import: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 نصب با موفقیت انجام شد!"
    echo ""
    echo "📋 مراحل بعدی:"
    echo "1. تنظیم API Key: export YOUTUBE_API_KEY='your_key'"
    echo "2. یا کپی فایل credentials: cp youtube_credentials.json ."
    echo "3. تست: python test_youtube_api.py"
    echo ""
    echo "📚 راهنمای کامل: cat YOUTUBE_API_SETUP.md"
else
    echo "❌ خطا در تست نصب"
    exit 1
fi
