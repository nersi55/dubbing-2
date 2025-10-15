"""
صفحه ساده دوبله خودکار ویدیو - فقط آدرس YouTube
Simple Auto Video Dubbing Page - YouTube URL Only
"""

import streamlit as st
import os
import tempfile
import subprocess
import random
import string
from pathlib import Path
from dubbing_functions import VideoDubbingApp

# تنظیمات صفحه
st.set_page_config(
    page_title="🎬 دوبله خودکار ویدیو - ققنوس شانس",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# استایل‌های سفارشی
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
        font-size: 2.5rem;
        font-weight: bold;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 3rem;
        font-size: 1.2rem;
    }
    .input-container {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin: 2rem 0;
        border: 2px solid #e9ecef;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .footer {
        text-align: center;
        color: #666;
        margin-top: 3rem;
        padding: 2rem;
        background-color: #f8f9fa;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# هدر اصلی
st.markdown('<h1 class="main-header">🎬 دوبله خودکار ویدیو</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">تبدیل ویدیوهای یوتیوب به فارسی با زیرنویس سفارشی - ققنوس شانس</p>', unsafe_allow_html=True)

# تنظیمات ثابت (مخفی)
API_KEY = "AIzaSyBNYpugB8Ezrpmk-U7Yvp9ynClEJLCETMo"
TARGET_LANGUAGE = "Persian (FA)"
VOICE = "Fenrir"
ENABLE_COMPRESSION = False  # فشرده‌سازی غیرفعال
EXTRACTION_METHOD = "Whisper"
OUTPUT_TYPE = "زیرنویس ترجمه شده"

# تنظیمات زیرنویس ثابت
SUBTITLE_CONFIG = {
    "font": "vazirmatn",
    "fontsize": 14,
    "color": "white",
    "background_color": "black",
    "outline_color": "black",
    "outline_width": 0,
    "position": "bottom_center",
    "margin_v": 20,
    "shadow": 0,
    "shadow_color": "black",
    "bold": False,
    "italic": False
}

# تنظیمات متن ثابت پایین
FIXED_TEXT_CONFIG = {
    "enabled": True,
    "text": "ترجمه و زیرنویس ققنوس شانس",
    "font": "vazirmatn",
    "fontsize": 9,
    "color": "yellow",
    "background_color": "none",
    "position": "bottom_center",
    "margin_bottom": 10,
    "opacity": 1.0,
    "bold": True,
    "italic": False
}

# ایجاد instance از کلاس دوبله
try:
    dubbing_app = VideoDubbingApp(API_KEY)
    st.success("✅ اتصال به Google AI برقرار شد")
except Exception as e:
    st.error(f"❌ خطا در اتصال به Google AI: {str(e)}")
    st.stop()

# فرم ورودی
st.markdown('<div class="input-container">', unsafe_allow_html=True)
st.markdown("### 🔗 لینک ویدیو یوتیوب")
youtube_url = st.text_input(
    "آدرس ویدیو یوتیوب را اینجا وارد کنید:",
    placeholder="https://youtube.com/watch?v=...",
    help="لینک کامل ویدیو یوتیوب را اینجا وارد کنید",
    label_visibility="collapsed"
)

# نمایش تنظیمات ثابت
with st.expander("⚙️ تنظیمات ثابت (غیرقابل تغییر)"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🔑 کلید Google API:** `AIzaSyBNYpugB8Ezrpmk-U7Yvp9ynClEJLCETMo`")
        st.markdown("**📺 روش آپلود:** یوتیوب")
        st.markdown("**🌐 زبان مقصد:** فارسی")
        st.markdown("**📝 فشرده‌سازی:** غیرفعال")
        st.markdown("**🔍 استخراج متن:** Whisper")
    
    with col2:
        st.markdown("**📝 نوع خروجی:** زیرنویس ترجمه شده")
        st.markdown("**🎨 فونت زیرنویس:** vazirmatn")
        st.markdown("**📏 اندازه:** 14px")
        st.markdown("**🎨 رنگ:** سفید")
        st.markdown("**🖤 زمینه:** سیاه")
        st.markdown("**📌 حاشیه:** 0px سیاه")

st.markdown("**📌 متن ثابت پایین:**")
st.markdown("- **متن:** ترجمه و زیرنویس ققنوس شانس")
st.markdown("- **فونت:** vazirmatn | **اندازه:** 9px | **رنگ:** زرد")
st.markdown("- **موقعیت:** پایین وسط | **شفافیت:** 1.0 | **ضخیم:** بله")

st.markdown('</div>', unsafe_allow_html=True)

# دکمه شروع پردازش
if st.button("🚀 شروع پردازش ویدیو", type="primary", use_container_width=True):
    if not youtube_url:
        st.error("❌ لطفاً لینک ویدیو یوتیوب را وارد کنید")
    else:
        # مرحله 1: دانلود ویدیو
        with st.spinner("📥 در حال دانلود ویدیو از یوتیوب..."):
            success = dubbing_app.download_youtube_video(youtube_url)
            if not success:
                st.error("❌ خطا در دانلود ویدیو")
                st.stop()
        
        st.success("✅ ویدیو با موفقیت دانلود شد")
        
        # مرحله 2: استخراج متن با Whisper
        with st.spinner("🔍 در حال استخراج متن با Whisper..."):
            success = dubbing_app.extract_audio_with_whisper()
            if not success:
                st.error("❌ خطا در استخراج متن")
                st.stop()
        
        st.success("✅ متن با موفقیت استخراج شد")
        
        # مرحله 3: ترجمه (فشرده‌سازی غیرفعال)
        with st.spinner("🌐 در حال ترجمه زیرنویس‌ها به فارسی..."):
            success = dubbing_app.translate_subtitles(TARGET_LANGUAGE)
            if not success:
                st.error("❌ خطا در ترجمه")
                st.stop()
        
        st.success("✅ زیرنویس‌ها به فارسی ترجمه شدند")
        
        # مرحله 4: ایجاد ویدیو با زیرنویس
        with st.spinner("🎬 در حال ایجاد ویدیو با زیرنویس سفارشی..."):
            # ایجاد نام فایل رندم
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            random_filename = f"dubbed_video_{random_suffix}.mp4"
            
            # تغییر نام فایل خروجی در کلاس
            original_create_method = dubbing_app.create_subtitled_video
            def create_with_random_name(subtitle_config=None, fixed_text_config=None):
                result = original_create_method(subtitle_config, fixed_text_config)
                if result and os.path.exists(result):
                    # تغییر نام فایل
                    new_path = dubbing_app.work_dir / random_filename
                    os.rename(result, str(new_path))
                    return str(new_path)
                return result
            
            # جایگزینی موقت متد
            dubbing_app.create_subtitled_video = create_with_random_name
            
            output_path = dubbing_app.create_subtitled_video(
                subtitle_config=SUBTITLE_CONFIG,
                fixed_text_config=FIXED_TEXT_CONFIG
            )
            
            # بازگردانی متد اصلی
            dubbing_app.create_subtitled_video = original_create_method
            
            if output_path and os.path.exists(output_path):
                st.success("🎉 ویدیو با زیرنویس سفارشی با موفقیت ایجاد شد!")
                
                # نمایش اطلاعات فایل
                file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
                st.info(f"📁 نام فایل: {os.path.basename(output_path)}")
                st.info(f"📊 حجم فایل: {file_size:.2f} MB")
                
                # دکمه دانلود
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="📥 دانلود ویدیو با زیرنویس",
                        data=file.read(),
                        file_name=os.path.basename(output_path),
                        mime="video/mp4",
                        type="primary",
                        use_container_width=True
                    )
            else:
                st.error("❌ خطا در ایجاد ویدیو با زیرنویس")

# اطلاعات اضافی
st.markdown("""
<div class="info-box">
<h4>ℹ️ راهنمای استفاده:</h4>
<ol>
<li><strong>لینک یوتیوب:</strong> آدرس کامل ویدیو یوتیوب را وارد کنید</li>
<li><strong>پردازش خودکار:</strong> تمام مراحل به صورت خودکار انجام می‌شود</li>
<li><strong>تنظیمات ثابت:</strong> تمام تنظیمات طبق درخواست شما تنظیم شده است</li>
<li><strong>دانلود:</strong> پس از اتمام پردازش، ویدیو را دانلود کنید</li>
</ol>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
<p>🎬 دوبله خودکار ویدیو - ققنوس شانس</p>
<p>ساخته شده با Streamlit و Google AI</p>
</div>
""", unsafe_allow_html=True)
