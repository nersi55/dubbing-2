"""
صفحه پیشرفته دوبله خودکار ویدیو - با تنظیمات آپلود در Object Storage
Advanced Auto Video Dubbing Page - With Object Storage Upload
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
from s3_uploader import S3Uploader
from sheets_logger import GoogleSheetsLogger
import google.generativeai as genai

# تنظیمات صفحه
st.set_page_config(
    page_title="🎬 دوبله و آپلود به Storage - ققنوس شانس",
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
st.markdown('<h1 class="main-header">🎬 دوبله و آپلود به Object Storage</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">تبدیل ویدیوها و آپلود خودکار به فضای ذخیره‌سازی ابری - ققنوس شانس</p>', unsafe_allow_html=True)

# تنظیمات ثابت
API_KEY = "AIzaSyBNYpugB8Ezrpmk-U7Yvp9ynClEJLCETMo"
TARGET_LANGUAGE = "Persian (FA)"

# تنظیمات Object Storage (Claw Cloud)
S3_ACCESS_KEY = "m9bth4qn"
S3_SECRET_KEY = "w46z8gspqb86m5l2"
S3_ENDPOINT_INTERNAL = "http://object-storage.objectstorage-system.svc.cluster.local"
S3_ENDPOINT_EXTERNAL = "http://objectstorageapi.us-west-1.clawcloudrun.com"
S3_REGION = "us-west-1"

# مقادیر پیش‌فرض تنظیمات زیرنویس
DEFAULT_SUBTITLE_FONT = "vazirmatn"
DEFAULT_SUBTITLE_FONTSIZE = 14
DEFAULT_SUBTITLE_COLOR = "black"
DEFAULT_SUBTITLE_BG_COLOR = "none"
DEFAULT_SUBTITLE_OUTLINE_COLOR = "white"
DEFAULT_SUBTITLE_OUTLINE_WIDTH = 1
DEFAULT_SUBTITLE_POSITION = "bottom_center"
DEFAULT_SUBTITLE_MARGIN_V = 40

# مقادیر پیش‌فرض متن ثابت (واترمارک)
DEFAULT_FIXED_ENABLED = False
DEFAULT_FIXED_TEXT = "ققنوس شانس"
DEFAULT_FIXED_FONT = "vazirmatn"
DEFAULT_FIXED_FONTSIZE = 16
DEFAULT_FIXED_COLOR = "white"
DEFAULT_FIXED_BG_COLOR = "black"
DEFAULT_FIXED_POSITION = "top_right"
DEFAULT_FIXED_MARGIN_BOTTOM = 20
DEFAULT_FIXED_OPACITY = 0.7
DEFAULT_FIXED_BOLD = True
DEFAULT_FIXED_ITALIC = False

# تابع کمکی برای ایجاد دیکشنری تنظیمات زیرنویس
def create_subtitle_config(font=None, fontsize=None, color=None, bg_color=None, 
                           outline_color=None, outline_width=None, position=None, margin_v=None):
    return {
        "font": font or DEFAULT_SUBTITLE_FONT,
        "fontsize": fontsize or DEFAULT_SUBTITLE_FONTSIZE,
        "color": color or DEFAULT_SUBTITLE_COLOR,
        "background_color": bg_color or DEFAULT_SUBTITLE_BG_COLOR,
        "outline_color": outline_color or DEFAULT_SUBTITLE_OUTLINE_COLOR,
        "outline_width": outline_width or DEFAULT_SUBTITLE_OUTLINE_WIDTH,
        "position": position or DEFAULT_SUBTITLE_POSITION,
        "margin_v": margin_v or DEFAULT_SUBTITLE_MARGIN_V
    }

# تابع کمکی برای ایجاد دیکشنری تنظیمات متن ثابت
def create_fixed_text_config(enabled=None, text=None, font=None, fontsize=None, color=None, 
                             background_color=None, position=None, margin_bottom=None, 
                             opacity=None, bold=None, italic=None):
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

# تابع برای ایجاد و مدیریت instance از کلاس دوبله در session state
def init_dubbing_app():
    """ایجاد یا بروزرسانی instance از کلاس دوبله در session_state"""
    gemini_key = st.session_state.get('gemini_api_key', API_KEY)
    azure_endpoint = st.session_state.get('azure_endpoint')
    azure_api_key = st.session_state.get('azure_api_key')
    azure_model = st.session_state.get('azure_model', "grok-4-fast-reasoning")
    
    if 'dubbing_instance' not in st.session_state:
        try:
            from dubbing_functions import VideoDubbingApp
            st.session_state.dubbing_instance = VideoDubbingApp(
                gemini_key, 
                azure_endpoint=azure_endpoint, 
                azure_api_key=azure_api_key, 
                azure_model=azure_model
            )
        except Exception as e:
            st.error(f"❌ خطا در ایجاد سرویس: {str(e)}")
            return None
    else:
        # بروزرسانی تنظیمات در صورت تغییر
        instance = st.session_state.dubbing_instance
        instance.api_key = gemini_key
        instance.azure_endpoint = azure_endpoint
        instance.azure_api_key = azure_api_key
        instance.azure_model = azure_model
        # اگر کلاینت گوگل نیاز به ریست دارد
        if hasattr(instance, 'client') and instance.api_key != gemini_key:
            from google import genai
            instance.client = genai.Client(api_key=gemini_key)
            
    return st.session_state.dubbing_instance

# مقداردهی اولیه
dubbing_app = init_dubbing_app()
if dubbing_app is None:
    st.stop()

# فرم ورودی
st.markdown('<div class="input-container">', unsafe_allow_html=True)
st.markdown("### 🔗 لینک ویدیو یا فایل CSV")
youtube_url = st.text_input(
    "آدرس ویدیو (یوتیوب یا اینستاگرام):",
    placeholder="https://youtube.com/watch?v=... یا https://www.instagram.com/reel/...",
)

csv_file = st.file_uploader("یا فایل CSV شامل لیست لینک‌ها را آپلود کنید", type=["csv"])

# تنظیمات قابل تغییر
with st.expander("⚙️ تنظیمات هوش مصنوعی (API Keys)", expanded=True):
    st.markdown("### 🤖 انتخاب سرویس ترجمه")
    
    col_api1, col_api2 = st.columns(2)
    
    with col_api1:
        gemini_key_input = st.text_input(
            "Gemini API Key:",
            value=st.session_state.get('gemini_api_key', API_KEY),
            type="password",
            help="اگر کلید فعلی مسدود شده است، کلید جدید را اینجا وارد کنید"
        )
        if gemini_key_input != st.session_state.get('gemini_api_key', API_KEY):
            st.session_state.gemini_api_key = gemini_key_input
            st.rerun()

    translation_provider = st.radio(
        "سرویس ترجمه:",
        ["Gemini (Google AI)", "Azure OpenAI"],
        index=0,
        key="translation_provider"
    )
    
    if translation_provider == "Azure OpenAI":
        col_az1, col_az2 = st.columns(2)
        with col_az1:
            azure_endpoint = st.text_input("Azure Endpoint:", value=st.session_state.get('azure_endpoint', ""))
            azure_model = st.text_input("Model Name:", value=st.session_state.get('azure_model', "grok-4-fast-reasoning"))
        with col_az2:
            azure_api_key = st.text_input("Azure API Key:", value=st.session_state.get('azure_api_key', ""), type="password")
            
        if st.button("🔍 تست اتصال Azure"):
            if azure_endpoint and azure_api_key:
                st.session_state.azure_endpoint = azure_endpoint
                st.session_state.azure_api_key = azure_api_key
                st.session_state.azure_model = azure_model
                app = init_dubbing_app()
                res = app.test_azure_connection()
                if res['success']: st.success("✅ اتصال برقرار شد")
                else: st.error(f"❌ خطا: {res['message']}")
            else:
                st.warning("⚠️ لطفا ابتدا اطلاعات Azure را وارد کنید")

    st.markdown("---")
    st.markdown("### 📝 تنظیمات زیرنویس")
    
    col_sub1, col_sub2 = st.columns(2)
    with col_sub1:
        subtitle_font = st.selectbox(
            "فونت زیرنویس:",
            ["vazirmatn", "vazir", "Arial", "Tahoma"],
            index=0
        )
        subtitle_fontsize = st.number_input("اندازه فونت:", min_value=10, max_value=50, value=DEFAULT_SUBTITLE_FONTSIZE)
        subtitle_color = st.selectbox("رنگ متن:", ["white", "black", "yellow", "red", "green"], index=1) # Default black
    
    with col_sub2:
        subtitle_bg = st.selectbox("رنگ پس‌زمینه:", ["none", "black", "white", "blue"], index=0)
        subtitle_pos = st.selectbox("موقعیت:", ["bottom_center", "top_center", "center"], index=0)
        subtitle_margin = st.number_input("حاشیه عمودی:", min_value=0, max_value=200, value=DEFAULT_SUBTITLE_MARGIN_V)

    st.markdown("---")
    st.markdown("### 🏷️ تنظیمات متن ثابت (واترمارک)")
    fixed_enabled = st.checkbox("فعال‌سازی متن ثابت", value=DEFAULT_FIXED_ENABLED)
    if fixed_enabled:
        col_fix1, col_fix2 = st.columns(2)
        with col_fix1:
            fixed_text = st.text_input("متن:", value=DEFAULT_FIXED_TEXT)
            fixed_font = st.selectbox("فونت متن ثابت:", ["vazirmatn", "Arial"], index=0)
            fixed_size = st.number_input("اندازه فونت ثابت:", value=DEFAULT_FIXED_FONTSIZE)
        with col_fix2:
            fixed_pos = st.selectbox("موقعیت ثابت:", ["top_right", "top_left", "bottom_right", "bottom_left"], index=0)
            fixed_color = st.selectbox("رنگ ثابت:", ["white", "yellow", "cyan"], index=0)
            fixed_opacity = st.slider("شفافیت:", 0.0, 1.0, DEFAULT_FIXED_OPACITY)
    else:
        fixed_text = DEFAULT_FIXED_TEXT
        fixed_font = DEFAULT_FIXED_FONT
        fixed_size = DEFAULT_FIXED_FONTSIZE
        fixed_pos = DEFAULT_FIXED_POSITION
        fixed_color = DEFAULT_FIXED_COLOR
        fixed_opacity = DEFAULT_FIXED_OPACITY

# تنظیمات آپلود
with st.expander("🌐 تنظیمات Object Storage", expanded=False):
    use_internal = st.checkbox("استفاده از شبکه داخلی (Internal Endpoint)", value=False)
    endpoint = S3_ENDPOINT_INTERNAL if use_internal else S3_ENDPOINT_EXTERNAL
    st.info(f"Endpoint فعلی: {endpoint}")
    bucket_name = st.text_input("نام Bucket:", value="m9bth4qn-test1")
    
    col_s3_test1, col_s3_test2 = st.columns(2)
    with col_s3_test1:
        if st.button("🔍 تست اتصال S3"):
            test_uploader = S3Uploader(S3_ACCESS_KEY, S3_SECRET_KEY, endpoint, S3_REGION)
            success, msg = test_uploader.test_connection()
            if success: st.success(f"✅ {msg}")
            else: st.error(f"❌ {msg}")
            
    with col_s3_test2:
        if st.button("📁 تست دسترسی باکت"):
            test_uploader = S3Uploader(S3_ACCESS_KEY, S3_SECRET_KEY, endpoint, S3_REGION)
            success, msg = test_uploader.check_bucket(bucket_name)
            if success: st.success(f"✅ {msg}")
            else: st.error(f"❌ {msg}")

st.markdown('</div>', unsafe_allow_html=True)

# دکمه شروع پردازش
if st.button("🚀 شروع پردازش و آپلود", type="primary", use_container_width=True):
    urls = []
    if csv_file is not None:
        try:
            text_io = io.StringIO(csv_file.getvalue().decode("utf-8"))
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
                    if u: urls.append(u)
            else:
                text_io.seek(0)
                for line in text_io:
                    line = line.strip()
                    if line.startswith("http"): urls.append(line)
        except Exception as e:
            st.error(f"❌ خطا در خواندن CSV: {e}")
            st.stop()
    elif youtube_url:
        urls = [youtube_url]

    if not urls:
        st.error("❌ لطفاً یک لینک یا فایل CSV معتبر وارد کنید")
        st.stop()

    # ایجاد S3 Uploader
    s3_uploader = S3Uploader(S3_ACCESS_KEY, S3_SECRET_KEY, endpoint, S3_REGION)
    
    results = []
    total = len(urls)
    progress = st.progress(0)

    for idx, url in enumerate(urls, start=1):
        st.write(f"[{idx}/{total}] پردازش: {url}")
        progress.progress(min(int(idx / total * 100), 100))

        # 1) دانلود
        if 'instagram.com' in url:
            with st.spinner("📥 دانلود از اینستاگرام..."):
                if not dubbing_app.download_instagram_video(url):
                    results.append((url, "download_failed"))
                    continue
        else:
            with st.spinner("📥 دانلود از یوتیوب..."):
                if not dubbing_app.download_youtube_video(url):
                    results.append((url, "download_failed"))
                    continue

        # 2) استخراج متن
        with st.spinner("🔍 استخراج متن..."):
            if not dubbing_app.extract_audio_with_whisper():
                results.append((url, "transcript_failed"))
                continue

        # 3) ترجمه
        provider_name = "Gemini"
        if translation_provider == "Azure OpenAI":
            provider_name = "Azure"
            # بروزرسانی تنظیمات در اینستنس فعلی
            dubbing_app.azure_endpoint = st.session_state.get('azure_endpoint')
            dubbing_app.azure_api_key = st.session_state.get('azure_api_key')
            dubbing_app.azure_model = st.session_state.get('azure_model')

        with st.spinner(f"🌐 ترجمه زیرنویس با {provider_name}..."):
            # ارسال صریح پارامترها به متد ترجمه
            if not dubbing_app.translate_subtitles(TARGET_LANGUAGE, provider=provider_name):
                results.append((url, "translate_failed"))
                continue

        # 4) ایجاد ویدیو
        with st.spinner("🎬 ساخت ویدیو..."):
            subtitle_config = create_subtitle_config(
                font=subtitle_font,
                fontsize=subtitle_fontsize,
                color=subtitle_color,
                bg_color=subtitle_bg,
                position=subtitle_pos,
                margin_v=subtitle_margin
            )
            
            fixed_text_config = create_fixed_text_config(
                enabled=fixed_enabled,
                text=fixed_text,
                font=fixed_font,
                fontsize=fixed_size,
                position=fixed_pos,
                color=fixed_color,
                opacity=fixed_opacity
            )

            # بررسی وجود و محتوای فایل زیرنویس قبل از استفاده
            srt_fa = dubbing_app._srt_fa_path()
            if not srt_fa.exists() or srt_fa.stat().st_size < 10:
                st.error("❌ فایل زیرنویس ترجمه شده معتبر نیست یا خالی است.")
                results.append((url, "subtitle_invalid"))
                continue

            out = dubbing_app.create_subtitled_video(
                subtitle_config=subtitle_config,
                fixed_text_config=fixed_text_config
            )
            if not out or not os.path.exists(out):
                results.append((url, "video_failed"))
                continue

        # 5) آپلود به Object Storage
        with st.spinner("📡 آپلود به Object Storage..."):
            s3_res = s3_uploader.upload_file(out, bucket_name=bucket_name)
            if s3_res:
                st.success(f"✅ آپلود موفق: {s3_res['url']}")
                st.markdown(f"🔗 [لینک ویدیو]({s3_res['url']})")
                
                # آپلود فایل‌های SRT و ثبت در گوگل شیت
                with st.spinner("📝 در حال ثبت در گوگل شیت و آپلود زیرنویس‌ها..."):
                    fa_srt_path = dubbing_app._srt_fa_path()
                    en_srt_path = dubbing_app._srt_en_path()
                    
                    fa_srt_url = ""
                    en_srt_url = ""
                    
                    if fa_srt_path.exists():
                        fa_res = s3_uploader.upload_file(str(fa_srt_path), bucket_name=bucket_name)
                        if fa_res:
                            fa_srt_url = fa_res['url']
                    
                    if en_srt_path.exists():
                        en_res = s3_uploader.upload_file(str(en_srt_path), bucket_name=bucket_name)
                        if en_res:
                            en_srt_url = en_res['url']
                    
                    # ثبت در گوگل شیت
                    try:
                        logger = GoogleSheetsLogger()
                        mp4_url = s3_res['url']
                        logger.log_upload_triple(mp4_url, fa_srt_url, en_srt_url)
                        st.success("✅ لینک‌های هردو زیرنویس و ویدیو در گوگل شیت ثبت شد")
                    except Exception as e:
                        st.warning(f"⚠️ خطا در ثبت گوگل شیت: {e}")
                
                results.append((url, f"ok:{s3_res['url']}"))
            else:
                st.error("❌ خطا در آپلود به Storage")
                results.append((url, "upload_failed"))

    ok = sum(1 for _, r in results if str(r).startswith("ok"))
    st.info(f"پایان عملیات: {ok}/{len(results)} فایل با موفقیت آپلود شد.")

# Footer
st.markdown('<div class="footer"><p>🎬 سیستم دوبله و آپلود خودکار ققنوس شانس</p></div>', unsafe_allow_html=True)
