"""
صفحه پیشرفته دوبله خودکار ویدیو - با تنظیمات قابل تغییر
Advanced Auto Video Dubbing Page - With Customizable Settings
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
    page_title="🎬 دوبله خودکار ویدیو (پیشرفته) - ققنوس شانس",
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
st.markdown('<h1 class="main-header">🎬 دوبله خودکار ویدیو (پیشرفته)</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">تبدیل ویدیوهای یوتیوب به فارسی با زیرنویس سفارشی - ققنوس شانس</p>', unsafe_allow_html=True)

# تنظیمات ثابت (مخفی)
API_KEY = "AIzaSyBNYpugB8Ezrpmk-U7Yvp9ynClEJLCETMo"
TARGET_LANGUAGE = "Persian (FA)"
VOICE = "Fenrir"
ENABLE_COMPRESSION = False  # فشرده‌سازی غیرفعال
EXTRACTION_METHOD = "Whisper"
OUTPUT_TYPE = "زیرنویس ترجمه شده"

# مقادیر پیش‌فرض تنظیمات
DEFAULT_SUBTITLE_FONT = "vazirmatn"
DEFAULT_SUBTITLE_FONTSIZE = 14
DEFAULT_SUBTITLE_COLOR = "black"
DEFAULT_SUBTITLE_BG_COLOR = "none"
DEFAULT_SUBTITLE_OUTLINE_COLOR = "white"
DEFAULT_SUBTITLE_OUTLINE_WIDTH = 1
DEFAULT_SUBTITLE_POSITION = "bottom_center"
DEFAULT_SUBTITLE_MARGIN_V = 40
DEFAULT_SUBTITLE_SHADOW = 0
DEFAULT_SUBTITLE_SHADOW_COLOR = "black"
DEFAULT_SUBTITLE_BOLD = True
DEFAULT_SUBTITLE_ITALIC = False

DEFAULT_FIXED_TEXT = "ترجمه و زیرنویس ققنوس شانس"
DEFAULT_FIXED_FONT = "vazirmatn"
DEFAULT_FIXED_FONTSIZE = 9
DEFAULT_FIXED_COLOR = "yellow"
DEFAULT_FIXED_BG_COLOR = "none"
DEFAULT_FIXED_POSITION = "bottom_center"
DEFAULT_FIXED_MARGIN_BOTTOM = 10
DEFAULT_FIXED_OPACITY = 1.0
DEFAULT_FIXED_BOLD = False
DEFAULT_FIXED_ITALIC = False
DEFAULT_FIXED_ENABLED = True

# تابع برای ایجاد تنظیمات زیرنویس
def get_subtitle_config(
    font=None, fontsize=None, color=None, background_color=None,
    outline_color=None, outline_width=None, position=None, margin_v=None,
    shadow=None, shadow_color=None, bold=None, italic=None
):
    """ایجاد تنظیمات زیرنویس با مقادیر سفارشی"""
    return {
        "font": font or DEFAULT_SUBTITLE_FONT,
        "fontsize": fontsize or DEFAULT_SUBTITLE_FONTSIZE,
        "color": color or DEFAULT_SUBTITLE_COLOR,
        "background_color": background_color or DEFAULT_SUBTITLE_BG_COLOR,
        "outline_color": outline_color or DEFAULT_SUBTITLE_OUTLINE_COLOR,
        "outline_width": outline_width or DEFAULT_SUBTITLE_OUTLINE_WIDTH,
        "position": position or DEFAULT_SUBTITLE_POSITION,
        "margin_v": margin_v or DEFAULT_SUBTITLE_MARGIN_V,
        "shadow": shadow if shadow is not None else DEFAULT_SUBTITLE_SHADOW,
        "shadow_color": shadow_color or DEFAULT_SUBTITLE_SHADOW_COLOR,
        "bold": bold if bold is not None else DEFAULT_SUBTITLE_BOLD,
        "italic": italic if italic is not None else DEFAULT_SUBTITLE_ITALIC
    }

# تابع برای ایجاد تنظیمات متن ثابت
def get_fixed_text_config(
    text=None, font=None, fontsize=None, color=None,
    background_color=None, position=None, margin_bottom=None,
    opacity=None, bold=None, italic=None, enabled=None
):
    """ایجاد تنظیمات متن ثابت با مقادیر سفارشی"""
    return {
        "enabled": enabled if enabled is not None else DEFAULT_FIXED_ENABLED,
        "text": text or DEFAULT_FIXED_TEXT,
        "font": font or DEFAULT_FIXED_FONT,
        "fontsize": fontsize or DEFAULT_FIXED_FONTSIZE,
        "color": color or DEFAULT_FIXED_COLOR,
        "background_color": background_color or DEFAULT_FIXED_BG_COLOR,
        "position": position or DEFAULT_FIXED_POSITION,
        "margin_bottom": margin_bottom or DEFAULT_FIXED_MARGIN_BOTTOM,
        "opacity": opacity if opacity is not None else DEFAULT_FIXED_OPACITY,
        "bold": bold if bold is not None else DEFAULT_FIXED_BOLD,
        "italic": italic if italic is not None else DEFAULT_FIXED_ITALIC
    }

# تابع برای ایجاد instance از کلاس دوبله
@st.cache_resource
def get_dubbing_app(gemini_key, azure_endpoint=None, azure_api_key=None, azure_model="grok-4-fast-reasoning"):
    """ایجاد instance از کلاس دوبله با cache"""
    try:
        from dubbing_functions import VideoDubbingApp
        return VideoDubbingApp(gemini_key, azure_endpoint=azure_endpoint, 
                              azure_api_key=azure_api_key, azure_model=azure_model)
    except Exception as e:
        st.error(f"❌ خطا در اتصال به هوش مصنوعی: {str(e)}")
        return None



# بررسی اتصال (با تنظیمات پیش‌فرض Gemini)
dubbing_app = get_dubbing_app(API_KEY)
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


# تنظیمات قابل تغییر
with st.expander("⚙️ تنظیمات قابل تغییر", expanded=False):
    st.markdown("### 🤖 تنظیمات ترجمه (Translation Provider)")
    
    # انتخاب Translation Provider
    translation_provider = st.radio(
        "انتخاب سرویس ترجمه:",
        ["Gemini (Google AI)", "Azure OpenAI"],
        index=0,
        key="translation_provider"
    )
    
    # تنظیمات Azure OpenAI
    if translation_provider == "Azure OpenAI":
        st.markdown("#### ⚙️ تنظیمات Azure OpenAI")
        
        col_azure1, col_azure2 = st.columns(2)
        
        with col_azure1:
            azure_endpoint = st.text_input(
                "Azure Endpoint:",
                value="", # Removed hardcoded value
                placeholder="https://your-resource.openai.azure.com",
                key="azure_endpoint"
            )
            
            azure_model = st.text_input(
                "Model Name:",
                value="grok-4-fast-reasoning",
                placeholder="grok-4-fast-reasoning",
                key="azure_model"
            )
        
        with col_azure2:
            azure_api_key = st.text_input(
                "Azure API Key:",
                value="",
                type="password",
                placeholder="Enter your Azure API key",
                key="azure_api_key"
            )
            
            # دکمه تست اتصال
            if st.button("🔍 Test Azure Connection", key="test_azure_btn"):
                with st.spinner("در حال تست اتصال..."):
                    test_app = get_dubbing_app(
                        API_KEY, 
                        azure_endpoint=azure_endpoint,
                        azure_api_key=azure_api_key,
                        azure_model=azure_model
                    )
                    if test_app:
                        result = test_app.test_azure_connection()
                        if result['success']:
                            st.success(f"✅ {result['message']}")
                        else:
                            st.error(f"❌ {result['message']}")
    
    st.markdown("---")
    st.markdown("### 📝 تنظیمات زیرنویس")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # مقداردهی اولیه session state
        if 'subtitle_font' not in st.session_state:
            st.session_state.subtitle_font = DEFAULT_SUBTITLE_FONT
        if 'subtitle_fontsize' not in st.session_state:
            st.session_state.subtitle_fontsize = DEFAULT_SUBTITLE_FONTSIZE
        if 'subtitle_color' not in st.session_state:
            st.session_state.subtitle_color = DEFAULT_SUBTITLE_COLOR
        if 'subtitle_bg_color' not in st.session_state:
            st.session_state.subtitle_bg_color = DEFAULT_SUBTITLE_BG_COLOR
        if 'subtitle_outline_color' not in st.session_state:
            st.session_state.subtitle_outline_color = DEFAULT_SUBTITLE_OUTLINE_COLOR
        if 'subtitle_outline_width' not in st.session_state:
            st.session_state.subtitle_outline_width = DEFAULT_SUBTITLE_OUTLINE_WIDTH
        
        subtitle_font = st.selectbox(
            "فونت زیرنویس:",
            ["vazirmatn", "Arial", "Arial Black", "Times New Roman", "Courier New", "Helvetica"],
            index=0 if DEFAULT_SUBTITLE_FONT == "vazirmatn" else 1,
            key="subtitle_font_select"
        )
        st.session_state.subtitle_font = subtitle_font
        
        subtitle_fontsize = st.number_input(
            "اندازه فونت (px):",
            min_value=8,
            max_value=100,
            value=DEFAULT_SUBTITLE_FONTSIZE,
            key="subtitle_fontsize_input"
        )
        st.session_state.subtitle_fontsize = subtitle_fontsize
        
        subtitle_color = st.selectbox(
            "رنگ متن:",
            ["black", "white", "yellow", "red", "blue", "green", "cyan", "magenta"],
            index=["black", "white", "yellow", "red", "blue", "green", "cyan", "magenta"].index(DEFAULT_SUBTITLE_COLOR) if DEFAULT_SUBTITLE_COLOR in ["black", "white", "yellow", "red", "blue", "green", "cyan", "magenta"] else 0,
            key="subtitle_color_select"
        )
        st.session_state.subtitle_color = subtitle_color
        
        subtitle_bg_color = st.selectbox(
            "رنگ پس‌زمینه:",
            ["none", "black", "white", "yellow", "red", "blue"],
            index=["none", "black", "white", "yellow", "red", "blue"].index(DEFAULT_SUBTITLE_BG_COLOR) if DEFAULT_SUBTITLE_BG_COLOR in ["none", "black", "white", "yellow", "red", "blue"] else 0,
            key="subtitle_bg_color_select"
        )
        st.session_state.subtitle_bg_color = subtitle_bg_color
        
        subtitle_outline_color = st.selectbox(
            "رنگ حاشیه:",
            ["white", "black", "yellow", "red", "blue", "green"],
            index=["white", "black", "yellow", "red", "blue", "green"].index(DEFAULT_SUBTITLE_OUTLINE_COLOR) if DEFAULT_SUBTITLE_OUTLINE_COLOR in ["white", "black", "yellow", "red", "blue", "green"] else 0,
            key="subtitle_outline_color_select"
        )
        st.session_state.subtitle_outline_color = subtitle_outline_color
        
        subtitle_outline_width = st.number_input(
            "ضخامت حاشیه (px):",
            min_value=0,
            max_value=10,
            value=DEFAULT_SUBTITLE_OUTLINE_WIDTH,
            key="subtitle_outline_width_input"
        )
        st.session_state.subtitle_outline_width = subtitle_outline_width
    
    with col2:
        if 'subtitle_position' not in st.session_state:
            st.session_state.subtitle_position = DEFAULT_SUBTITLE_POSITION
        if 'subtitle_margin_v' not in st.session_state:
            st.session_state.subtitle_margin_v = DEFAULT_SUBTITLE_MARGIN_V
        if 'subtitle_shadow' not in st.session_state:
            st.session_state.subtitle_shadow = DEFAULT_SUBTITLE_SHADOW
        if 'subtitle_shadow_color' not in st.session_state:
            st.session_state.subtitle_shadow_color = DEFAULT_SUBTITLE_SHADOW_COLOR
        if 'subtitle_bold' not in st.session_state:
            st.session_state.subtitle_bold = DEFAULT_SUBTITLE_BOLD
        if 'subtitle_italic' not in st.session_state:
            st.session_state.subtitle_italic = DEFAULT_SUBTITLE_ITALIC
        
        subtitle_position = st.selectbox(
            "موقعیت:",
            ["bottom_center", "bottom_left", "bottom_right", "top_center", "top_left", "top_right"],
            index=["bottom_center", "bottom_left", "bottom_right", "top_center", "top_left", "top_right"].index(DEFAULT_SUBTITLE_POSITION) if DEFAULT_SUBTITLE_POSITION in ["bottom_center", "bottom_left", "bottom_right", "top_center", "top_left", "top_right"] else 0,
            key="subtitle_position_select"
        )
        st.session_state.subtitle_position = subtitle_position
        
        subtitle_margin_v = st.number_input(
            "فاصله عمودی (px):",
            min_value=0,
            max_value=200,
            value=DEFAULT_SUBTITLE_MARGIN_V,
            key="subtitle_margin_v_input"
        )
        st.session_state.subtitle_margin_v = subtitle_margin_v
        
        subtitle_shadow = st.checkbox(
            "فعال کردن سایه:",
            value=DEFAULT_SUBTITLE_SHADOW > 0,
            key="subtitle_shadow_checkbox"
        )
        st.session_state.subtitle_shadow = 1 if subtitle_shadow else 0
        
        subtitle_shadow_color = st.selectbox(
            "رنگ سایه:",
            ["black", "white", "gray", "red", "blue"],
            index=0,
            key="subtitle_shadow_color_select"
        )
        st.session_state.subtitle_shadow_color = subtitle_shadow_color
        
        subtitle_bold = st.checkbox(
            "متن ضخیم (Bold):",
            value=DEFAULT_SUBTITLE_BOLD,
            key="subtitle_bold_checkbox"
        )
        st.session_state.subtitle_bold = subtitle_bold
        
        subtitle_italic = st.checkbox(
            "متن کج (Italic):",
            value=DEFAULT_SUBTITLE_ITALIC,
            key="subtitle_italic_checkbox"
        )
        st.session_state.subtitle_italic = subtitle_italic

    st.markdown("---")
    st.markdown("### 📌 تنظیمات متن ثابت پایین ویدیو")
    
    col3, col4 = st.columns(2)
    
    with col3:
        if 'fixed_text_enabled' not in st.session_state:
            st.session_state.fixed_text_enabled = DEFAULT_FIXED_ENABLED
        if 'fixed_text' not in st.session_state:
            st.session_state.fixed_text = DEFAULT_FIXED_TEXT
        if 'fixed_font' not in st.session_state:
            st.session_state.fixed_font = DEFAULT_FIXED_FONT
        if 'fixed_fontsize' not in st.session_state:
            st.session_state.fixed_fontsize = DEFAULT_FIXED_FONTSIZE
        if 'fixed_color' not in st.session_state:
            st.session_state.fixed_color = DEFAULT_FIXED_COLOR
        if 'fixed_bg_color' not in st.session_state:
            st.session_state.fixed_bg_color = DEFAULT_FIXED_BG_COLOR
        
        fixed_text_enabled = st.checkbox(
            "فعال کردن متن ثابت:",
            value=DEFAULT_FIXED_ENABLED,
            key="fixed_text_enabled_checkbox"
        )
        st.session_state.fixed_text_enabled = fixed_text_enabled
        
        fixed_text = st.text_input(
            "متن ثابت:",
            value=DEFAULT_FIXED_TEXT,
            placeholder="متن خود را اینجا وارد کنید...",
            key="fixed_text_input"
        )
        st.session_state.fixed_text = fixed_text if fixed_text.strip() else DEFAULT_FIXED_TEXT
        
        fixed_font = st.selectbox(
            "فونت متن ثابت:",
            ["vazirmatn", "Arial", "Arial Black", "Times New Roman", "Courier New", "Helvetica"],
            index=0 if DEFAULT_FIXED_FONT == "vazirmatn" else 1,
            key="fixed_font_select"
        )
        st.session_state.fixed_font = fixed_font
        
        fixed_fontsize = st.number_input(
            "اندازه فونت متن ثابت (px):",
            min_value=8,
            max_value=50,
            value=DEFAULT_FIXED_FONTSIZE,
            key="fixed_fontsize_input"
        )
        st.session_state.fixed_fontsize = fixed_fontsize
        
        fixed_color = st.selectbox(
            "رنگ متن ثابت:",
            ["yellow", "black", "white", "red", "blue", "green", "cyan", "magenta"],
            index=0,
            key="fixed_color_select"
        )
        st.session_state.fixed_color = fixed_color
        
        fixed_bg_color = st.selectbox(
            "رنگ پس‌زمینه متن ثابت:",
            ["none", "black", "white", "yellow", "red", "blue"],
            index=0,
            key="fixed_bg_color_select"
        )
        st.session_state.fixed_bg_color = fixed_bg_color
    
    with col4:
        if 'fixed_position' not in st.session_state:
            st.session_state.fixed_position = DEFAULT_FIXED_POSITION
        if 'fixed_margin_bottom' not in st.session_state:
            st.session_state.fixed_margin_bottom = DEFAULT_FIXED_MARGIN_BOTTOM
        if 'fixed_opacity' not in st.session_state:
            st.session_state.fixed_opacity = DEFAULT_FIXED_OPACITY
        if 'fixed_bold' not in st.session_state:
            st.session_state.fixed_bold = DEFAULT_FIXED_BOLD
        if 'fixed_italic' not in st.session_state:
            st.session_state.fixed_italic = DEFAULT_FIXED_ITALIC
        
        fixed_position = st.selectbox(
            "موقعیت متن ثابت:",
            ["bottom_center", "bottom_left", "bottom_right", "top_center", "top_left", "top_right"],
            index=0,
            key="fixed_position_select"
        )
        st.session_state.fixed_position = fixed_position
        
        fixed_margin_bottom = st.number_input(
            "فاصله از پایین (px):",
            min_value=0,
            max_value=200,
            value=DEFAULT_FIXED_MARGIN_BOTTOM,
            key="fixed_margin_bottom_input"
        )
        st.session_state.fixed_margin_bottom = fixed_margin_bottom
        
        fixed_opacity = st.slider(
            "شفافیت متن ثابت:",
            min_value=0.0,
            max_value=1.0,
            value=DEFAULT_FIXED_OPACITY,
            step=0.1,
            key="fixed_opacity_slider"
        )
        st.session_state.fixed_opacity = fixed_opacity
        
        fixed_bold = st.checkbox(
            "متن ثابت ضخیم (Bold):",
            value=DEFAULT_FIXED_BOLD,
            key="fixed_bold_checkbox"
        )
        st.session_state.fixed_bold = fixed_bold

# نمایش تنظیمات ثابت
with st.expander("ℹ️ تنظیمات سیستم (غیرقابل تغییر)"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🔑 کلید Google API:** `AIzaSyBNYpugB8Ezrpmk-U7Yvp9ynClEJLCETMo`")
        st.markdown("**📺 روش آپلود:** یوتیوب / اینستاگرام")
        st.markdown("**🌐 زبان مقصد:** فارسی")
        st.markdown("**📝 فشرده‌سازی:** غیرفعال")
        st.markdown("**🔍 استخراج متن:** Whisper")
    
    with col2:
        st.markdown("**📝 نوع خروجی:** زیرنویس ترجمه شده")

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
        # بررسی اینکه آیا باید از Azure استفاده کنیم
        provider_name = "Gemini"
        if 'translation_provider' in st.session_state and st.session_state.translation_provider == "Azure OpenAI":
            provider_name = "Azure"
            # حفظ session_id فعلی قبل از بازسازی
            current_sid = dubbing_app.session_id
            # ایجاد dubbing app با تنظیمات Azure
            if 'azure_endpoint' in st.session_state and 'azure_api_key' in st.session_state:
                dubbing_app = get_dubbing_app(
                    API_KEY,
                    azure_endpoint=st.session_state.azure_endpoint,
                    azure_api_key=st.session_state.azure_api_key,
                    azure_model=st.session_state.get('azure_model', 'grok-4-fast-reasoning')
                )
                # بازیابی session_id
                if current_sid:
                    dubbing_app.set_session_id(current_sid)
        
        spinner_text = f"🌐 ترجمه زیرنویس با {provider_name}..."
        with st.spinner(spinner_text):
            if not dubbing_app.translate_subtitles(TARGET_LANGUAGE, provider=provider_name):
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

            # استفاده از تنظیمات سفارشی کاربر
            subtitle_config = get_subtitle_config(
                font=st.session_state.subtitle_font,
                fontsize=st.session_state.subtitle_fontsize,
                color=st.session_state.subtitle_color,
                background_color=st.session_state.subtitle_bg_color,
                outline_color=st.session_state.subtitle_outline_color,
                outline_width=st.session_state.subtitle_outline_width,
                position=st.session_state.subtitle_position,
                margin_v=st.session_state.subtitle_margin_v,
                shadow=st.session_state.subtitle_shadow,
                shadow_color=st.session_state.subtitle_shadow_color,
                bold=st.session_state.subtitle_bold,
                italic=st.session_state.subtitle_italic
            )
            
            fixed_text_config = get_fixed_text_config(
                text=st.session_state.fixed_text,
                font=st.session_state.fixed_font,
                fontsize=st.session_state.fixed_fontsize,
                color=st.session_state.fixed_color,
                background_color=st.session_state.fixed_bg_color,
                position=st.session_state.fixed_position,
                margin_bottom=st.session_state.fixed_margin_bottom,
                opacity=st.session_state.fixed_opacity,
                bold=st.session_state.fixed_bold,
                italic=st.session_state.fixed_italic,
                enabled=st.session_state.fixed_text_enabled
            )
            
            out = dubbing_app.create_subtitled_video(
                subtitle_config=subtitle_config,
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
<li><strong>تنظیمات سفارشی:</strong> می‌توانید تمام تنظیمات زیرنویس و متن ثابت را تغییر دهید</li>
<li><strong>پردازش خودکار:</strong> تمام مراحل به صورت خودکار انجام می‌شود</li>
<li><strong>دانلود:</strong> پس از اتمام پردازش، ویدیو را دانلود کنید</li>
</ol>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
<p>🎬 دوبله خودکار ویدیو (پیشرفته) - ققنوس شانس</p>
<p>ساخته شده با Streamlit و Google AI</p>
</div>
""", unsafe_allow_html=True)



















