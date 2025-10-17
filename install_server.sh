#!/bin/bash

# اسکریپت نصب کامل برای سرور
# Complete Server Installation Script

echo "🚀 نصب کامل دوبله خودکار ویدیو روی سرور"
echo "=========================================="

# بررسی سیستم عامل
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo "❌ سیستم عامل پشتیبانی نمی‌شود"
    exit 1
fi

echo "🔍 سیستم عامل: $OS"

# بررسی Python
echo "🐍 بررسی Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 نصب نیست. لطفاً ابتدا Python3 را نصب کنید"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python $PYTHON_VERSION نصب است"

# بررسی pip
echo "📦 بررسی pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 نصب نیست. لطفاً ابتدا pip3 را نصب کنید"
    exit 1
fi
echo "✅ pip3 نصب است"

# نصب وابستگی‌های سیستم
echo "🔧 نصب وابستگی‌های سیستم..."

if [[ "$OS" == "linux" ]]; then
    # Ubuntu/Debian
    if command -v apt-get &> /dev/null; then
        echo "📦 نصب وابستگی‌ها با apt..."
        sudo apt update
        sudo apt install -y ffmpeg rubberband-cli git curl unzip
    # CentOS/RHEL
    elif command -v yum &> /dev/null; then
        echo "📦 نصب وابستگی‌ها با yum..."
        sudo yum install -y epel-release
        sudo yum install -y ffmpeg rubberband git curl unzip
    # Fedora
    elif command -v dnf &> /dev/null; then
        echo "📦 نصب وابستگی‌ها با dnf..."
        sudo dnf install -y ffmpeg rubberband git curl unzip
    else
        echo "❌ مدیر بسته‌ای یافت نشد"
        exit 1
    fi
elif [[ "$OS" == "macos" ]]; then
    if command -v brew &> /dev/null; then
        echo "📦 نصب وابستگی‌ها با Homebrew..."
        brew install ffmpeg rubberband git curl
    else
        echo "❌ Homebrew نصب نیست"
        exit 1
    fi
fi

# بررسی نصب وابستگی‌ها
echo "🔍 بررسی نصب وابستگی‌ها..."

if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg نصب است"
    ffmpeg -version | head -1
else
    echo "❌ FFmpeg نصب نیست"
    exit 1
fi

if command -v rubberband &> /dev/null; then
    echo "✅ Rubberband نصب است"
    rubberband --version
else
    echo "❌ Rubberband نصب نیست"
    exit 1
fi

# ایجاد محیط مجازی Python
echo "🐍 ایجاد محیط مجازی Python..."
if [[ -d "venv" ]]; then
    echo "⚠️  محیط مجازی قبلاً وجود دارد"
    read -p "آیا می‌خواهید آن را حذف و دوباره ایجاد کنید؟ (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
    fi
else
    python3 -m venv venv
fi

# فعال‌سازی محیط مجازی
echo "🔄 فعال‌سازی محیط مجازی..."
source venv/bin/activate

# به‌روزرسانی pip
echo "📦 به‌روزرسانی pip..."
pip install --upgrade pip

# نصب وابستگی‌های Python
echo "📦 نصب وابستگی‌های Python..."
pip install -r requirements.txt

# نصب فونت Vazirmatn
echo "🎨 نصب فونت Vazirmatn..."
if [[ -f "install_fonts.py" ]]; then
    python install_fonts.py
    if [[ $? -eq 0 ]]; then
        echo "✅ فونت Vazirmatn نصب شد"
    else
        echo "⚠️  خطا در نصب فونت. تلاش برای نصب دستی..."
        
        # نصب دستی فونت‌ها
        echo "📁 ایجاد پوشه فونت‌ها..."
        mkdir -p fonts
        
        echo "⬇️  دانلود فونت‌های Vazirmatn..."
        curl -L https://github.com/rastikerdar/vazirmatn/raw/main/fonts/ttf/Vazirmatn-Regular.ttf -o fonts/Vazirmatn-Regular.ttf
        curl -L https://github.com/rastikerdar/vazirmatn/raw/main/fonts/ttf/Vazirmatn-Medium.ttf -o fonts/Vazirmatn-Medium.ttf
        curl -L https://github.com/rastikerdar/vazirmatn/raw/main/fonts/ttf/Vazirmatn-Bold.ttf -o fonts/Vazirmatn-Bold.ttf
        
        echo "✅ فونت‌ها دانلود شدند"
    fi
else
    echo "⚠️  فایل install_fonts.py یافت نشد"
fi

# ایجاد پوشه‌های مورد نیاز
echo "📁 ایجاد پوشه‌های مورد نیاز..."
mkdir -p dubbing_work/dubbed_segments
mkdir -p temp

# تست نصب
echo "🧪 تست نصب..."
if [[ -f "test_font_installation.py" ]]; then
    python test_font_installation.py
    if [[ $? -eq 0 ]]; then
        echo "✅ تست نصب موفق"
    else
        echo "⚠️  تست نصب ناموفق - ممکن است مشکلی وجود داشته باشد"
    fi
fi

# تنظیم مجوزها
echo "🔐 تنظیم مجوزها..."
chmod +x run.py
chmod +x install_fonts.py
chmod +x test_font_installation.py

# خلاصه نصب
echo ""
echo "🎉 نصب کامل شد!"
echo "=================="
echo "📁 مسیر پروژه: $(pwd)"
echo "🐍 محیط مجازی: venv/"
echo "🎨 فونت‌ها: fonts/"
echo "📝 فایل‌های کار: dubbing_work/"
echo ""
echo "🚀 برای اجرای برنامه:"
echo "   source venv/bin/activate"
echo "   python run.py"
echo ""
echo "🌐 یا برای اجرای Streamlit:"
echo "   source venv/bin/activate"
echo "   streamlit run app.py --server.port 8501 --server.address 0.0.0.0"
echo ""
echo "🔧 برای تست فونت‌ها:"
echo "   source venv/bin/activate"
echo "   python test_font_installation.py"
echo ""
echo "📚 راهنمای کامل: SERVER_DEPLOYMENT.md"
