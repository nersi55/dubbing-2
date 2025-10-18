#!/bin/bash
# نصب فونت Vazirmatn در Linux
# Install Vazirmatn fonts on Linux

echo "🔤 نصب فونت Vazirmatn در Linux"
echo "================================="

# بررسی وجود wget یا curl
if command -v wget &> /dev/null; then
    DOWNLOAD_CMD="wget"
elif command -v curl &> /dev/null; then
    DOWNLOAD_CMD="curl -L"
else
    echo "❌ wget یا curl یافت نشد. لطفاً یکی از آن‌ها را نصب کنید."
    exit 1
fi

# ایجاد پوشه فونت
FONT_DIR="/usr/local/share/fonts/vazirmatn"
echo "📁 ایجاد پوشه فونت: $FONT_DIR"
sudo mkdir -p "$FONT_DIR"

# دانلود فونت‌های Vazirmatn
echo "⬇️ دانلود فونت‌های Vazirmatn..."

# فونت‌های مختلف Vazirmatn
FONTS=(
    "https://github.com/rastikerdar/vazirmatn/releases/download/v33.003/Vazirmatn-Regular.ttf"
    "https://github.com/rastikerdar/vazirmatn/releases/download/v33.003/Vazirmatn-Medium.ttf"
    "https://github.com/rastikerdar/vazirmatn/releases/download/v33.003/Vazirmatn-Bold.ttf"
    "https://github.com/rastikerdar/vazirmatn/releases/download/v33.003/Vazirmatn-ExtraBold.ttf"
    "https://github.com/rastikerdar/vazirmatn/releases/download/v33.003/Vazirmatn-Black.ttf"
)

for font_url in "${FONTS[@]}"; do
    font_name=$(basename "$font_url")
    echo "   دانلود $font_name..."
    $DOWNLOAD_CMD "$font_url" -o "/tmp/$font_name"
    
    if [ $? -eq 0 ]; then
        sudo mv "/tmp/$font_name" "$FONT_DIR/"
        echo "   ✅ $font_name نصب شد"
    else
        echo "   ❌ خطا در دانلود $font_name"
    fi
done

# تنظیم مجوزها
echo "🔐 تنظیم مجوزها..."
sudo chmod 644 "$FONT_DIR"/*.ttf

# به‌روزرسانی کش فونت
echo "🔄 به‌روزرسانی کش فونت..."
if command -v fc-cache &> /dev/null; then
    sudo fc-cache -fv
    echo "✅ کش فونت به‌روزرسانی شد"
else
    echo "⚠️ fc-cache یافت نشد. ممکن است نیاز به راه‌اندازی مجدد سیستم باشد."
fi

# بررسی نصب
echo "🔍 بررسی نصب فونت‌ها..."
if command -v fc-list &> /dev/null; then
    echo "فونت‌های Vazirmatn نصب شده:"
    fc-list | grep -i vazirmatn || echo "❌ فونت Vazirmatn یافت نشد"
else
    echo "⚠️ fc-list یافت نشد. نمی‌توان فونت‌ها را بررسی کرد."
fi

echo ""
echo "🎉 نصب فونت Vazirmatn کامل شد!"
echo "💡 برای استفاده از فونت، ممکن است نیاز به راه‌اندازی مجدد برنامه باشد."
echo ""
echo "🔧 برای تست فونت‌ها:"
echo "   python test_linux_font.py"
