#!/bin/bash
"""
اسکریپت تنظیم فایروال برای macOS
Firewall Setup Script for macOS
"""

echo "🔧 تنظیم فایروال برای API دوبله"
echo "================================="

# بررسی دسترسی root
if [ "$EUID" -ne 0 ]; then
    echo "❌ این اسکریپت نیاز به دسترسی root دارد"
    echo "💡 اجرا کنید: sudo ./setup_firewall.sh"
    exit 1
fi

# پورت API
PORT=8002

echo "🔓 باز کردن پورت $PORT در فایروال..."

# ایجاد قانون فایروال موقت
echo "pass in proto tcp from any to any port $PORT" > /tmp/pf_api_rule

# اعمال قانون
pfctl -f /tmp/pf_api_rule

if [ $? -eq 0 ]; then
    echo "✅ پورت $PORT با موفقیت باز شد"
    echo "🌐 API حالا از راه دور قابل دسترسی است"
    echo ""
    echo "📱 آدرس‌های دسترسی:"
    echo "   - محلی: http://127.0.0.1:$PORT"
    echo "   - شبکه: http://[IP_SERVER]:$PORT"
    echo ""
    echo "⚠️  توجه: این تنظیمات موقت است و بعد از ریست سیستم از بین می‌رود"
    echo "💡 برای تنظیمات دائمی، از System Preferences > Security & Privacy > Firewall استفاده کنید"
else
    echo "❌ خطا در باز کردن پورت"
    exit 1
fi

# پاک کردن فایل موقت
rm -f /tmp/pf_api_rule

echo ""
echo "🔍 برای تست دسترسی:"
echo "   python test_remote_access.py"
