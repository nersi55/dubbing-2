#!/bin/bash

# اسکریپت نصب وابستگی‌های سیستم برای دوبله خودکار ویدیو
# System dependencies installation script for Auto Video Dubbing

echo "🎬 دوبله خودکار ویدیو - نصب وابستگی‌ها"
echo "========================================"

# تشخیص سیستم عامل
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
else
    echo "❌ سیستم عامل پشتیبانی نمی‌شود"
    exit 1
fi

echo "🔍 سیستم عامل تشخیص داده شد: $OS"

# نصب FFmpeg
echo "📦 نصب FFmpeg..."
if [[ "$OS" == "linux" ]]; then
    if command -v apt-get &> /dev/null; then
        sudo apt update
        sudo apt install -y ffmpeg
    elif command -v yum &> /dev/null; then
        sudo yum install -y ffmpeg
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y ffmpeg
    else
        echo "❌ مدیر بسته‌ای یافت نشد. لطفاً FFmpeg را دستی نصب کنید"
    fi
elif [[ "$OS" == "macos" ]]; then
    if command -v brew &> /dev/null; then
        brew install ffmpeg
    else
        echo "❌ Homebrew نصب نیست. لطفاً ابتدا Homebrew را نصب کنید"
        echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
elif [[ "$OS" == "windows" ]]; then
    echo "⚠️  برای Windows، لطفاً FFmpeg را از https://ffmpeg.org/download.html دانلود کنید"
    echo "   و آن را به PATH اضافه کنید"
fi

# نصب Rubberband
echo "📦 نصب Rubberband..."
if [[ "$OS" == "linux" ]]; then
    if command -v apt-get &> /dev/null; then
        sudo apt install -y rubberband-cli
    elif command -v yum &> /dev/null; then
        sudo yum install -y rubberband
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y rubberband
    else
        echo "❌ مدیر بسته‌ای یافت نشد. لطفاً Rubberband را دستی نصب کنید"
    fi
elif [[ "$OS" == "macos" ]]; then
    if command -v brew &> /dev/null; then
        brew install rubberband
    else
        echo "❌ Homebrew نصب نیست"
    fi
elif [[ "$OS" == "windows" ]]; then
    echo "⚠️  برای Windows، لطفاً Rubberband را از https://breakfastquay.com/rubberband/ دانلود کنید"
fi

# بررسی نصب
echo "🔍 بررسی نصب..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg نصب است"
    ffmpeg -version | head -1
else
    echo "❌ FFmpeg نصب نیست"
fi

if command -v rubberband &> /dev/null; then
    echo "✅ Rubberband نصب است"
    rubberband --version
else
    echo "❌ Rubberband نصب نیست"
fi

# نصب وابستگی‌های Python
echo "🐍 نصب وابستگی‌های Python..."
if command -v python3 &> /dev/null; then
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt
    echo "✅ وابستگی‌های Python نصب شدند"
else
    echo "❌ Python3 نصب نیست"
fi

# نصب فونت Vazirmatn
echo "🎨 نصب فونت Vazirmatn..."
if command -v python3 &> /dev/null; then
    if [[ -f "install_fonts.py" ]]; then
        python3 install_fonts.py
        if [[ $? -eq 0 ]]; then
            echo "✅ فونت Vazirmatn نصب شد"
        else
            echo "⚠️  خطا در نصب فونت. لطفاً دستی نصب کنید"
        fi
    else
        echo "⚠️  فایل install_fonts.py یافت نشد"
    fi
else
    echo "❌ Python3 نصب نیست - نمی‌توان فونت را نصب کرد"
fi

echo ""
echo "🎉 نصب کامل شد!"
echo "🚀 برای اجرای برنامه: python run.py"
echo "🌐 یا: streamlit run app.py"
