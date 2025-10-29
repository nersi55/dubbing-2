"""
صفحه ساده دوبله خودکار ویدیو - فقط آدرس YouTube
Simple Auto Video Dubbing Page - YouTube URL Only
"""

import streamlit as st
import os
import io
import csv
import tempfile
import subprocess
import random
import string
from pathlib import Path

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
    "color": "black",
    "background_color": "none",
    "outline_color": "white",
    "outline_width": 1,
    "position": "bottom_center",
    "margin_v": 40,
    "shadow": 0,
    "shadow_color": "black",
    "bold": True,
    "italic": False
}

# مقدار پیش‌فرض متن ثابت
DEFAULT_FIXED_TEXT = "ترجمه و زیرنویس ققنوس شانس"

# تنظیمات متن ثابت پایین (متن از ورودی کاربر استفاده می‌شود)
def get_fixed_text_config(custom_text=None):
    """ایجاد تنظیمات متن ثابت با متن سفارشی"""
    text = custom_text if custom_text else DEFAULT_FIXED_TEXT
    return {
        "enabled": True,
        "text": text,
        "font": "vazirmatn",
        "fontsize": 9,  # کاهش اندازه فونت طبق درخواست
        "color": "yellow",
        "background_color": "none",
        "position": "bottom_center",
        "margin_bottom": 10,
        "opacity": 1.0,
        "bold": False,  # غیرفعال کردن bold برای جلوگیری از مشکل
        "italic": False
    }

# تابع برای ایجاد instance از کلاس دوبله
@st.cache_resource
def get_dubbing_app():
    """ایجاد instance از کلاس دوبله با cache"""
    try:
        from dubbing_functions import VideoDubbingApp
        return VideoDubbingApp(API_KEY)
    except Exception as e:
        st.error(f"❌ خطا در اتصال به Google AI: {str(e)}")
        return None

# بررسی اتصال
dubbing_app = get_dubbing_app()
if dubbing_app is None:
    st.stop()
else:
    st.success("✅ اتصال به Google AI برقرار شد")

# فرم ورودی
st.markdown('<div class="input-container">', unsafe_allow_html=True)
st.markdown("### 🔗 لینک ویدیو یوتیوب، اینستاگرام یا فایل CSV فهرست لینک‌ها")
youtube_url = st.text_input(
    "آدرس ویدیو (یوتیوب یا اینستاگرام) را اینجا وارد کنید:",
    placeholder="https://youtube.com/watch?v=... یا https://www.instagram.com/reel/...",
    help="لینک کامل ویدیو یوتیوب یا اینستاگرام را اینجا وارد کنید",
    label_visibility="collapsed"
)

# ورودی جایگزین: آپلود CSV حاوی لیست لینک‌ها
csv_file = st.file_uploader("یا فایل CSV شامل لیست لینک‌های یوتیوب/اینستاگرام را آپلود کنید", type=["csv"])

# نمایش تنظیمات ثابت
with st.expander("⚙️ تنظیمات ثابت (غیرقابل تغییر)"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🔑 کلید Google API:** `AIzaSyBNYpugB8Ezrpmk-U7Yvp9ynClEJLCETMo`")
        st.markdown("**📺 روش آپلود:** یوتیوب / اینستاگرام")
        st.markdown("**🌐 زبان مقصد:** فارسی")
        st.markdown("**📝 فشرده‌سازی:** غیرفعال")
        st.markdown("**🔍 استخراج متن:** Whisper")
    
    with col2:
        st.markdown("**📝 نوع خروجی:** زیرنویس ترجمه شده")
        st.markdown("**🎨 فونت زیرنویس:** vazirmatn")
        st.markdown("**📏 اندازه:** 14px")
        st.markdown("**🎨 رنگ:** مشکی")
        st.markdown("**🖤 زمینه:** شفاف")
        st.markdown("**📌 حاشیه:** 1px سفید")

st.markdown("**📌 متن ثابت پایین ویدیو:**")

# ورودی متن سفارشی - استفاده از session state برای ذخیره مقدار
if 'custom_fixed_text' not in st.session_state:
    st.session_state.custom_fixed_text = DEFAULT_FIXED_TEXT

custom_text = st.text_input(
    "متن ثابت نمایش داده شده در پایین ویدیو:",
    value=st.session_state.custom_fixed_text,
    placeholder="متن خود را اینجا وارد کنید...",
    help="این متن در پایین ویدیو نمایش داده می‌شود",
    key="fixed_text_input"
)

# به‌روزرسانی session state
st.session_state.custom_fixed_text = custom_text if custom_text.strip() else DEFAULT_FIXED_TEXT

st.markdown(f"- **متن فعلی:** {st.session_state.custom_fixed_text}")
st.markdown("- **فونت:** vazirmatn | **اندازه:** 9px | **رنگ:** زرد")
st.markdown("- **موقعیت:** پایین وسط | **شفافیت:** 1.0 | **ضخیم:** بله")

st.markdown('</div>', unsafe_allow_html=True)

"""
پردازش: از یک URL یا CSV چند URL
"""
# دکمه شروع پردازش
if st.button("🚀 شروع پردازش", type="primary", use_container_width=True):
    urls = []
    if csv_file is not None:
        try:
            text_io = io.StringIO(csv_file.getvalue().decode("utf-8"))
            # تلاش برای خواندن با هدر
            reader = csv.DictReader(text_io)
            selected = None
            if reader.fieldnames:
                fields = [f.strip().lower() for f in reader.fieldnames]
                for c in ["youtube_short_url", "url", "youtube_url"]:
                    if c in fields:
                        selected = c
                        break
            if selected:
                for row in reader:
                    u = (row.get(selected) or "").strip()
                    if u:
                        urls.append(u)
            else:
                # بدون هدر: هر خط یک URL
                text_io.seek(0)
                for line in text_io:
                    line = line.strip()
                    if line.startswith("http"):
                        urls.append(line)
        except Exception as e:
            st.error(f"❌ خطا در خواندن CSV: {e}")
            st.stop()
    elif youtube_url:
        urls = [youtube_url]

    if not urls:
        st.error("❌ لطفاً یک لینک یا فایل CSV معتبر وارد/آپلود کنید")
        st.stop()

    results = []
    total = len(urls)
    progress = st.progress(0)

    for idx, url in enumerate(urls, start=1):
        st.write(f"[{idx}/{total}] پردازش: {url}")
        progress.progress(min(int(idx / total * 100), 100))

        # 1) دانلود - تشخیص نوع URL
        if 'instagram.com' in url:
            with st.spinner("📥 دانلود ویدیو از اینستاگرام..."):
                if not dubbing_app.download_instagram_video(url):
                    results.append((url, "download_failed"))
                    continue
                # استخراج ID اینستاگرام برای نام‌گذاری
                try:
                    insta_id = dubbing_app._extract_instagram_id(url)
                    if insta_id:
                        dubbing_app.set_session_id(insta_id[:11])
                except Exception:
                    pass
        else:
            with st.spinner("📥 دانلود ویدیو از یوتیوب..."):
                if not dubbing_app.download_youtube_video(url):
                    results.append((url, "download_failed"))
                    continue

        # 2) استخراج متن
        with st.spinner("🔍 استخراج متن..."):
            if not dubbing_app.extract_audio_with_whisper():
                results.append((url, "transcript_failed"))
                continue

        # 3) ترجمه
        with st.spinner("🌐 ترجمه زیرنویس..."):
            if not dubbing_app.translate_subtitles(TARGET_LANGUAGE):
                results.append((url, "translate_failed"))
                continue

        # 4) ایجاد ویدیو با زیرنویس
        with st.spinner("🎬 ساخت ویدیو با زیرنویس..."):
            # اگر session_id قبلاً تنظیم نشده بود، تلاش برای استخراج
            if not dubbing_app.session_id:
                try:
                    if 'instagram.com' in url:
                        vid = dubbing_app._extract_instagram_id(url)
                    else:
                        vid = dubbing_app._extract_video_id(url)
                    if vid:
                        dubbing_app.set_session_id(vid[:11] if vid else None)
                except Exception:
                    pass

            # استفاده از متن سفارشی کاربر
            fixed_text_config = get_fixed_text_config(st.session_state.custom_fixed_text)
            
            out = dubbing_app.create_subtitled_video(
                subtitle_config=SUBTITLE_CONFIG,
                fixed_text_config=fixed_text_config
            )
            if not out or not os.path.exists(out):
                results.append((url, "video_failed"))
                continue

            file_size = os.path.getsize(out) / (1024 * 1024)
            st.success(f"✅ آماده: {os.path.basename(out)} | {file_size:.2f} MB")
            with open(out, "rb") as file:
                st.download_button(
                    label=f"دانلود {os.path.basename(out)}",
                    data=file.read(),
                    file_name=os.path.basename(out),
                    mime="video/mp4",
                    key=f"dl_{idx}",
                    use_container_width=True
                )
            results.append((url, f"ok:{os.path.basename(out)}"))

    ok = sum(1 for _, r in results if str(r).startswith("ok"))
    st.info(f"نتیجه نهایی: {ok}/{len(results)} موفق")

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
