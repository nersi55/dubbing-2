@echo off
REM اسکریپت نصب وابستگی‌های سیستم برای دوبله خودکار ویدیو (Windows)
REM System dependencies installation script for Auto Video Dubbing (Windows)

echo 🎬 دوبله خودکار ویدیو - نصب وابستگی‌ها
echo ========================================

REM بررسی Python
echo 🔍 بررسی Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python نصب نیست. لطفاً از https://python.org دانلود کنید
    pause
    exit /b 1
)
echo ✅ Python نصب است

REM بررسی pip
echo 🔍 بررسی pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip نصب نیست
    pause
    exit /b 1
)
echo ✅ pip نصب است

REM نصب وابستگی‌های Python
echo 🐍 نصب وابستگی‌های Python...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ خطا در نصب وابستگی‌های Python
    pause
    exit /b 1
)
echo ✅ وابستگی‌های Python نصب شدند

REM بررسی FFmpeg
echo 🔍 بررسی FFmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ FFmpeg نصب نیست
    echo 📥 لطفاً FFmpeg را از https://ffmpeg.org/download.html دانلود کنید
    echo    و آن را به PATH اضافه کنید
    echo.
    echo راهنمای اضافه کردن به PATH:
    echo 1. فایل ffmpeg.exe را در پوشه‌ای قرار دهید (مثل C:\ffmpeg\bin)
    echo 2. به System Properties ^> Environment Variables بروید
    echo 3. در System Variables، PATH را انتخاب کنید
    echo 4. Edit ^> New و مسیر ffmpeg را اضافه کنید
    echo 5. OK کنید و Command Prompt را restart کنید
    pause
    exit /b 1
)
echo ✅ FFmpeg نصب است

REM بررسی Rubberband
echo 🔍 بررسی Rubberband...
rubberband --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Rubberband نصب نیست
    echo 📥 لطفاً Rubberband را از https://breakfastquay.com/rubberband/ دانلود کنید
    echo    و آن را به PATH اضافه کنید
    pause
    exit /b 1
)
echo ✅ Rubberband نصب است

REM نصب فونت Vazirmatn
echo 🎨 نصب فونت Vazirmatn...
if exist "install_fonts.py" (
    python install_fonts.py
    if %errorlevel% equ 0 (
        echo ✅ فونت Vazirmatn نصب شد
    ) else (
        echo ⚠️  خطا در نصب فونت. لطفاً دستی نصب کنید
    )
) else (
    echo ⚠️  فایل install_fonts.py یافت نشد
)

echo.
echo 🎉 نصب کامل شد!
echo 🚀 برای اجرای برنامه: python run.py
echo 🌐 یا: streamlit run app.py
echo.
pause
