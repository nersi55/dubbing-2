"""
دوبله خودکار ویدیو - رابط کاربری Streamlit
Auto Video Dubbing - Streamlit Web Interface
"""

import streamlit as st
import os
import tempfile
import subprocess
from pathlib import Path
from dubbing_functions import VideoDubbingApp
from config import get_config, get_safety_settings

# تنظیمات صفحه
st.set_page_config(
    page_title="🎬 دوبله خودکار ویدیو",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# استایل‌های سفارشی
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .step-header {
        color: #ff6b6b;
        margin-top: 2rem;
        margin-bottom: 1rem;
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
</style>
""", unsafe_allow_html=True)

# هدر اصلی
st.markdown('<h1 class="main-header">🎬 دوبله خودکار ویدیو</h1>', unsafe_allow_html=True)
st.markdown("### تبدیل ویدیوهای یوتیوب به زبان‌های مختلف با هوش مصنوعی")

# نوار کناری برای تنظیمات
with st.sidebar:
    st.header("⚙️ تنظیمات")
    
    # کلید API
    api_key = st.text_input(
        "🔑 کلید Google API",
        type="password",
        help="کلید API خود را از Google AI Studio دریافت کنید"
    )
    
    if not api_key:
        st.error("لطفاً کلید API را وارد کنید")
        st.stop()
    
    st.markdown("---")
    
    # تنظیمات عمومی
    st.subheader("🎛️ تنظیمات عمومی")
    
    # روش آپلود
    upload_method = st.radio(
        "روش آپلود ویدیو",
        ["یوتیوب", "فایل محلی"],
        help="انتخاب کنید که ویدیو را از یوتیوب دانلود کنید یا فایل محلی آپلود کنید"
    )
    
    # تنظیمات ترجمه
    st.subheader("🌐 تنظیمات ترجمه")
    target_language = st.selectbox(
        "زبان مقصد",
        ["Persian (FA)", "English (EN)", "German (DE)", "French (FR)", 
         "Italian (IT)", "Spanish (ES)", "Chinese (ZH)", "Korean (KO)", 
         "Russian (RU)", "Arabic (AR)", "Japanese (JA)", "Hindi (HI)"],
        index=0
    )
    
    # تنظیمات صدا
    st.subheader("🎤 تنظیمات صدا")
    voice = st.selectbox(
        "گوینده",
        ["Fenrir", "Achird", "Zubenelgenubi", "Vindemiatrix", "Sadachbia", 
         "Sadaltager", "Sulafat", "Laomedeia", "Achernar", "Alnilam", 
         "Schedar", "Gacrux", "Pulcherrima", "Umbriel", "Algieba", 
         "Despina", "Erinome", "Algenib", "Rasalthgeti", "Orus", 
         "Aoede", "Callirrhoe", "Autonoe", "Enceladus", "Iapetus", 
         "Zephyr", "Puck", "Charon", "Kore", "Leda"],
        index=0
    )
    
    speech_prompt = st.text_area(
        "پرامپت لحن صدا (اختیاری)",
        placeholder="مثال: با لحنی آرام و شمرده صحبت کن",
        help="در صورت تمایل، لحن خاصی برای گوینده تعریف کنید"
    )
    
    # تنظیمات فشرده‌سازی
    st.subheader("📝 تنظیمات فشرده‌سازی")
    enable_compression = st.checkbox("فعال‌سازی فشرده‌سازی دیالوگ‌ها", value=True, 
                                   help="برای کاهش تعداد سگمنت‌ها و رعایت محدودیت‌های API")
    merge_count = st.slider("تعداد دیالوگ برای ادغام", min_value=3, max_value=15, value=5,
                           help="تعداد بالاتر = سگمنت‌های کمتر = مصرف کمتر API")
    
    # نمایش اطلاعات فشرده‌سازی
    if enable_compression:
        st.info(f"📊 با فشرده‌سازی {merge_count} تایی، تعداد سگمنت‌ها کاهش می‌یابد و محدودیت‌های API بهتر رعایت می‌شود.")
    
    # تنظیمات ویدیو نهایی
    st.subheader("🎥 تنظیمات ویدیو نهایی")
    keep_original_audio = st.checkbox("حفظ صدای اصلی ویدیو", value=False)
    if keep_original_audio:
        original_audio_volume = st.slider("حجم صدای اصلی", min_value=0.0, max_value=1.0, value=0.3, step=0.1)

# محتوای اصلی
if api_key:
    # ایجاد instance از کلاس دوبله
    try:
        dubbing_app = VideoDubbingApp(api_key)
        st.session_state['dubbing_app'] = dubbing_app
        st.success("✅ اتصال به Google AI برقرار شد")
    except Exception as e:
        st.error(f"❌ خطا در اتصال به Google AI: {str(e)}")
        st.stop()

# مرحله 1: آپلود ویدیو
st.markdown('<h2 class="step-header">📥 مرحله 1: آپلود ویدیو</h2>', unsafe_allow_html=True)

if upload_method == "یوتیوب":
    youtube_url = st.text_input(
        "🔗 لینک ویدیو یوتیوب",
        placeholder="https://youtube.com/watch?v=...",
        help="لینک کامل ویدیو یوتیوب را اینجا وارد کنید"
    )
    
    if st.button("📥 دانلود ویدیو", type="primary"):
        if youtube_url:
            with st.spinner("در حال دانلود ویدیو..."):
                success = st.session_state['dubbing_app'].download_youtube_video(youtube_url)
                if success:
                    st.success("✅ ویدیو با موفقیت دانلود شد")
                    st.session_state['video_downloaded'] = True
                else:
                    st.error("❌ خطا در دانلود ویدیو")
        else:
            st.warning("لطفاً لینک ویدیو را وارد کنید")

else:  # فایل محلی
    uploaded_file = st.file_uploader(
        "📁 انتخاب فایل ویدیو",
        type=['mp4', 'avi', 'mov', 'mkv'],
        help="فایل ویدیویی خود را آپلود کنید"
    )
    
    if uploaded_file is not None:
        # ذخیره فایل آپلود شده
        video_path = st.session_state['dubbing_app'].work_dir / 'input_video.mp4'
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # استخراج صدا
        with st.spinner("در حال استخراج صدا..."):
            subprocess.run([
                'ffmpeg', '-i', str(video_path), '-vn', 
                str(st.session_state['dubbing_app'].work_dir / 'audio.wav'), '-y'
            ], check=True, capture_output=True)
        
        st.success("✅ فایل ویدیو آپلود و صدا استخراج شد")
        st.session_state['video_downloaded'] = True

# مرحله 2: استخراج متن
if st.session_state.get('video_downloaded', False):
    st.markdown('<h2 class="step-header">📝 مرحله 2: استخراج متن</h2>', unsafe_allow_html=True)
    
    extraction_method = st.radio(
        "روش استخراج متن",
        ["Whisper (توصیه می‌شود)", "زیرنویس یوتیوب"],
        help="Whisper برای ویدیوهای بدون زیرنویس، زیرنویس یوتیوب برای ویدیوهای دارای زیرنویس"
    )
    
    if st.button("🔍 استخراج متن", type="primary"):
        with st.spinner("در حال استخراج متن..."):
            if extraction_method == "Whisper (توصیه می‌شود)":
                success = st.session_state['dubbing_app'].extract_audio_with_whisper()
            else:  # زیرنویس یوتیوب
                if upload_method == "یوتیوب" and youtube_url:
                    success = st.session_state['dubbing_app'].extract_transcript_from_youtube(youtube_url)
                else:
                    st.error("برای استفاده از زیرنویس یوتیوب، باید ویدیو را از یوتیوب دانلود کنید")
                    success = False
            
            if success:
                st.success("✅ متن با موفقیت استخراج شد")
                st.session_state['text_extracted'] = True
            else:
                st.error("❌ خطا در استخراج متن")

# مرحله 3: فشرده‌سازی (اختیاری)
if st.session_state.get('text_extracted', False) and enable_compression:
    st.markdown('<h2 class="step-header">📦 مرحله 3: فشرده‌سازی دیالوگ‌ها</h2>', unsafe_allow_html=True)
    
    if st.button("📦 فشرده‌سازی دیالوگ‌ها", type="primary"):
        with st.spinner("در حال فشرده‌سازی..."):
            success = st.session_state['dubbing_app'].compress_srt_dialogues(merge_count)
            if success:
                st.success(f"✅ دیالوگ‌ها با گروه‌های {merge_count} تایی فشرده شدند")
            else:
                st.error("❌ خطا در فشرده‌سازی")

# مرحله 4: ترجمه
if st.session_state.get('text_extracted', False):
    st.markdown('<h2 class="step-header">🌐 مرحله 4: ترجمه</h2>', unsafe_allow_html=True)
    
    if st.button("🌐 ترجمه زیرنویس‌ها", type="primary"):
        with st.spinner("در حال ترجمه..."):
            success = st.session_state['dubbing_app'].translate_subtitles(target_language)
            if success:
                st.success(f"✅ زیرنویس‌ها به {target_language} ترجمه شدند")
                st.session_state['translated'] = True
            else:
                st.error("❌ خطا در ترجمه")

# مرحله 5: تولید صدا
if st.session_state.get('translated', False):
    st.markdown('<h2 class="step-header">🎤 مرحله 5: تولید صدا</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        sleep_time = st.slider("زمان انتظار بین درخواست‌ها (ثانیه)", min_value=10, max_value=60, value=30, 
                              help="برای رعایت محدودیت‌های API رایگان، حداقل 30 ثانیه توصیه می‌شود")
    with col2:
        tts_model = st.selectbox("مدل TTS", ["gemini-2.5-flash-preview-tts", "gemini-2.5-pro-preview-tts"], index=0)
    
    # هشدار محدودیت API
    st.warning("""
    ⚠️ **محدودیت API رایگان**: 
    - حداکثر 15 درخواست در روز
    - حداکثر 3 درخواست در دقیقه
    - برای ویدیوهای طولانی، فشرده‌سازی خودکار فعال می‌شود
    """)
    
    if st.button("🎤 تولید صدا", type="primary"):
        with st.spinner("در حال تولید صدا... این فرآیند ممکن است چند دقیقه طول بکشد"):
            success = st.session_state['dubbing_app'].create_audio_segments(
                voice=voice, 
                model=tts_model, 
                speech_prompt=speech_prompt,
                sleep_between_requests=sleep_time
            )
            if success:
                st.success("✅ تمام سگمنت‌های صوتی تولید شدند")
                st.session_state['audio_generated'] = True
            else:
                st.error("❌ خطا در تولید صدا")

# مرحله 6: انتخاب نوع خروجی
if st.session_state.get('translated', False) and 'dubbing_app' in st.session_state:
    st.markdown('<h2 class="step-header">🎬 مرحله 6: انتخاب نوع خروجی</h2>', unsafe_allow_html=True)
    
    # انتخاب نوع خروجی
    output_type = st.radio(
        "نوع خروجی مورد نظر خود را انتخاب کنید:",
        ["دوبله صدا", "زیرنویس ترجمه شده"],
        help="دوبله صدا: صدای ترجمه شده به ویدیو اضافه می‌شود | زیرنویس: متن ترجمه شده به صورت زیرنویس نمایش داده می‌شود"
    )
    
    st.session_state.output_type = output_type
    
    if output_type == "دوبله صدا":
        st.markdown("### 🎤 تنظیمات دوبله صدا")
        
        if st.session_state.get('audio_generated', False):
            if st.button("🎤 ایجاد ویدیو دوبله شده", type="primary"):
                with st.spinner("در حال ایجاد ویدیو دوبله شده..."):
                    output_path = st.session_state['dubbing_app'].create_final_video(
                        keep_original_audio=keep_original_audio,
                        original_audio_volume=original_audio_volume if keep_original_audio else 0.8
                    )
                    
                    if output_path and os.path.exists(output_path):
                        st.success("✅ ویدیو دوبله شده با موفقیت ایجاد شد!")
                        
                        # نمایش اطلاعات فایل
                        file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
                        st.info(f"📁 نام فایل: {os.path.basename(output_path)}")
                        st.info(f"📊 حجم فایل: {file_size:.2f} MB")
                        
                        # دکمه دانلود
                        with open(output_path, "rb") as file:
                            st.download_button(
                                label="📥 دانلود ویدیو دوبله شده",
                                data=file.read(),
                                file_name=os.path.basename(output_path),
                                mime="video/mp4",
                                type="primary"
                            )
                    else:
                        st.error("❌ خطا در ایجاد ویدیو دوبله شده")
        else:
            st.warning("⚠️ ابتدا باید سگمنت‌های صوتی را ایجاد کنید.")
    
    elif output_type == "زیرنویس ترجمه شده":
        st.markdown("### 📝 تنظیمات زیرنویس")
        
        # تب‌های تنظیمات
        tab1, tab2 = st.tabs(["🎨 تنظیمات پیشرفته", "⚡ استایل‌های آماده"])
        
        with tab1:
            st.markdown("#### تنظیمات سفارشی زیرنویس")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📝 تنظیمات فونت:**")
                font_name = st.selectbox(
                    "نام فونت:",
                    ["Arial", "Times New Roman", "Courier New", "Verdana", "Tahoma", "Georgia", "Impact", "vazirmatn", "Tahoma"],
                    index=0
                )
                
                font_size = st.slider("اندازه فونت:", min_value=12, max_value=48, value=24, step=2)
                
                bold = st.checkbox("ضخیم (Bold)", value=False)
                italic = st.checkbox("مایل (Italic)", value=False)
            
            with col2:
                st.markdown("**🎨 تنظیمات رنگ:**")
                text_color = st.selectbox(
                    "رنگ متن:",
                    ["white", "yellow", "red", "green", "blue", "orange", "purple", "pink", "cyan", "lime", "magenta", "silver", "gold", "black"],
                    index=0
                )
                
                background_color = st.selectbox(
                    "رنگ زمینه:",
                    ["none", "black", "white", "red", "blue", "green", "yellow", "purple", "orange", "gray"],
                    index=0,
                    help="رنگ پس‌زمینه زیرنویس (none = بدون زمینه)"
                )
                
                outline_color = st.selectbox(
                    "رنگ حاشیه:",
                    ["black", "white", "red", "blue", "green", "yellow", "purple"],
                    index=0
                )
                
                outline_width = st.slider("ضخامت حاشیه:", min_value=0, max_value=8, value=2, step=1)
            
            col3, col4 = st.columns(2)
            
            with col3:
                st.markdown("**📍 موقعیت و فاصله:**")
                position = st.selectbox(
                    "موقعیت زیرنویس:",
                    ["bottom_center", "bottom_left", "bottom_right", "top_center", "top_left", "top_right", "middle_center", "middle_left", "middle_right"],
                    format_func=lambda x: {
                        "bottom_center": "پایین وسط",
                        "bottom_left": "پایین چپ",
                        "bottom_right": "پایین راست",
                        "top_center": "بالا وسط",
                        "top_left": "بالا چپ",
                        "top_right": "بالا راست",
                        "middle_center": "وسط صفحه",
                        "middle_left": "وسط چپ",
                        "middle_right": "وسط راست"
                    }[x]
                )
                
                margin_v = st.slider("فاصله از لبه (پیکسل):", min_value=0, max_value=100, value=20, step=5)
            
            with col4:
                st.markdown("**✨ افکت‌های اضافی:**")
                shadow = st.checkbox("سایه", value=False)
                
                if shadow:
                    shadow_color = st.selectbox(
                        "رنگ سایه:",
                        ["black", "white", "red", "blue", "green"],
                        index=0
                    )
                else:
                    shadow_color = "black"
            
            # پیش‌نمایش تنظیمات
            st.markdown("#### 🔍 پیش‌نمایش تنظیمات:")
            preview_text = f"**فونت:** {font_name} | **اندازه:** {font_size}px | **رنگ:** {text_color}"
            if background_color != "none":
                preview_text += f" | **زمینه:** {background_color}"
            preview_text += f" | **حاشیه:** {outline_width}px {outline_color}"
            if bold:
                preview_text += " | **ضخیم**"
            if italic:
                preview_text += " | **مایل**"
            if shadow:
                preview_text += f" | **سایه {shadow_color}**"
            
            st.info(preview_text)
            
            # تنظیمات متن ثابت
            st.markdown("#### 📌 تنظیمات متن ثابت پایین")
            fixed_text_enabled = st.checkbox("فعال کردن متن ثابت", value=False, help="متن ثابت در پایین ویدیو نمایش داده می‌شود")
            
            if fixed_text_enabled:
                col5, col6 = st.columns(2)
                
                with col5:
                    st.markdown("**📝 تنظیمات متن:**")
                    fixed_text = st.text_input("متن ثابت", placeholder="متن شما اینجا نمایش داده می‌شود...", help="این متن در تمام مدت ویدیو در پایین نمایش داده می‌شود")
                    fixed_font = st.selectbox("فونت متن ثابت", ["Arial", "Times New Roman", "Courier New", "Verdana", "Tahoma", "vazirmatn", "Georgia", "Impact"], index=5)
                    fixed_fontsize = st.slider("اندازه فونت متن ثابت", 8, 36, 20)
                    fixed_color = st.selectbox("رنگ متن ثابت", ["yellow", "white", "red", "green", "blue", "black", "orange", "purple", "pink", "cyan"], index=0)
                
                with col6:
                    st.markdown("**🎨 تنظیمات ظاهری:**")
                    fixed_bg_color = st.selectbox("رنگ زمینه متن ثابت", ["black", "none", "white", "red", "green", "blue", "yellow"], index=0)
                    fixed_position = st.selectbox("موقعیت متن ثابت", ["bottom_center", "bottom_left", "bottom_right"], index=0, format_func=lambda x: {"bottom_center": "پایین وسط", "bottom_left": "پایین چپ", "bottom_right": "پایین راست"}[x])
                    fixed_margin = st.slider("فاصله از پایین", 5, 50, 10)
                    fixed_opacity = st.slider("شفافیت", 0.1, 1.0, 0.8)
                
                # تنظیمات اضافی متن ثابت
                col7, col8 = st.columns(2)
                with col7:
                    fixed_bold = st.checkbox("ضخیم (متن ثابت)", value=True)
                with col8:
                    fixed_italic = st.checkbox("مایل (متن ثابت)", value=False)
                
                # پیش‌نمایش واقعی متن ثابت
                if fixed_text:
                    st.markdown("**🔍 پیش‌نمایش متن ثابت:**")
                    
                    # تابع تبدیل نام رنگ به کد HTML
                    def get_html_color(color_name):
                        color_map = {
                            'black': '#000000',
                            'white': '#ffffff',
                            'red': '#ff0000',
                            'green': '#00ff00',
                            'blue': '#0000ff',
                            'yellow': '#ffff00',
                            'orange': '#ffa500',
                            'purple': '#800080',
                            'pink': '#ffc0cb',
                            'cyan': '#00ffff',
                            'lime': '#00ff00',
                            'magenta': '#ff00ff',
                            'silver': '#c0c0c0',
                            'gold': '#ffd700',
                            'gray': '#808080',
                            'none': 'transparent'
                        }
                        return color_map.get(color_name, '#000000')
                    
                    # ایجاد پیش‌نمایش HTML با رنگ‌های صحیح
                    bg_color = get_html_color(fixed_bg_color)
                    text_color = get_html_color(fixed_color)
                    
                    preview_html = f"""
                    <div style="
                        background-color: {bg_color};
                        color: {text_color};
                        font-family: {fixed_font};
                        font-size: {fixed_fontsize}px;
                        font-weight: {'bold' if fixed_bold else 'normal'};
                        font-style: {'italic' if fixed_italic else 'normal'};
                        text-align: center;
                        padding: 10px;
                        border: 2px dashed #ccc;
                        border-radius: 5px;
                        margin: 10px 0;
                        opacity: {fixed_opacity};
                        min-height: 40px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    ">
                        {fixed_text}
                    </div>
                    """
                    
                    st.markdown(preview_html, unsafe_allow_html=True)
                    
                    # نمایش تنظیمات
                    preview_settings = f"**تنظیمات:** فونت {fixed_font} | اندازه {fixed_fontsize}px | رنگ {fixed_color}"
                    if fixed_bg_color != "none":
                        preview_settings += f" | زمینه {fixed_bg_color}"
                    preview_settings += f" | موقعیت {fixed_position} | شفافیت {fixed_opacity}"
                    if fixed_bold:
                        preview_settings += " | ضخیم"
                    if fixed_italic:
                        preview_settings += " | مایل"
                    st.caption(preview_settings)
                
                fixed_text_config = {
                    "enabled": True,
                    "text": fixed_text,
                    "font": fixed_font,
                    "fontsize": fixed_fontsize,
                    "color": fixed_color,
                    "background_color": fixed_bg_color,
                    "position": fixed_position,
                    "margin_bottom": fixed_margin,
                    "opacity": fixed_opacity,
                    "bold": fixed_bold,
                    "italic": fixed_italic
                }
            else:
                fixed_text_config = {"enabled": False}
            
            # ایجاد تنظیمات
            subtitle_config = {
                "font": font_name,
                "fontsize": font_size,
                "color": text_color,
                "background_color": background_color,
                "outline_color": outline_color,
                "outline_width": outline_width,
                "position": position,
                "margin_v": margin_v,
                "shadow": 1 if shadow else 0,
                "shadow_color": shadow_color,
                "bold": bold,
                "italic": italic
            }
            
            if st.button("📝 ایجاد ویدیو با تنظیمات سفارشی", type="primary"):
                with st.spinner("در حال ایجاد ویدیو با زیرنویس سفارشی..."):
                    try:
                        output_path = st.session_state['dubbing_app'].create_subtitled_video(
                            subtitle_config=subtitle_config,
                            fixed_text_config=fixed_text_config
                        )
                        
                        if output_path and os.path.exists(output_path):
                            st.success("✅ ویدیو با زیرنویس سفارشی با موفقیت ایجاد شد!")
                            
                            # نمایش اطلاعات فایل
                            file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
                            st.info(f"📁 نام فایل: {os.path.basename(output_path)}")
                            st.info(f"📊 حجم فایل: {file_size:.2f} MB")
                            
                            # دکمه دانلود
                            with open(output_path, "rb") as file:
                                st.download_button(
                                    label="📥 دانلود ویدیو با زیرنویس سفارشی",
                                    data=file.read(),
                                    file_name=os.path.basename(output_path),
                                    mime="video/mp4",
                                    type="primary"
                                )
                        else:
                            st.error("❌ خطا در ایجاد ویدیو با زیرنویس سفارشی")
                    except Exception as e:
                        st.error(f"❌ خطا در ایجاد ویدیو با زیرنویس سفارشی: {str(e)}")
                        st.error("لطفاً دوباره تلاش کنید یا تنظیمات را تغییر دهید.")
        
        with tab2:
            st.markdown("#### استایل‌های آماده")
            
            col1, col2 = st.columns(2)
            with col1:
                subtitle_style = st.selectbox(
                    "استایل زیرنویس:",
                    ["default", "modern", "minimal", "elegant", "bold", "colorful", "persian", "classic"],
                    format_func=lambda x: {
                        "default": "پیش‌فرض (سفید با حاشیه سیاه)",
                        "modern": "مدرن (زرد با حاشیه ضخیم)",
                        "minimal": "مینیمال (ساده و کوچک)",
                        "elegant": "زیبا (طلایی با سایه)",
                        "bold": "قوی (قرمز ضخیم)",
                        "colorful": "رنگی (آبی با حاشیه سبز)",
                        "persian": "فارسی (فونت Vazirmatn، سفید روی زمینه سیاه)",
                        "classic": "کلاسیک (سیاه روی زمینه سفید)"
                    }[x]
                )
            
            with col2:
                st.markdown("**پیش‌نمایش استایل‌ها:**")
                style_descriptions = {
                    "default": "• فونت: Vazirmatn 24px\n• رنگ: سفید\n• حاشیه: سیاه 2px",
                    "modern": "• فونت: Vazirmatn 28px\n• رنگ: زرد\n• حاشیه: سیاه 3px",
                    "minimal": "• فونت: Vazirmatn 20px\n• رنگ: سفید\n• حاشیه: سیاه 1px",
                    "elegant": "• فونت: Vazirmatn 26px\n• رنگ: طلایی\n• سایه: سیاه",
                    "bold": "• فونت: Vazirmatn 30px\n• رنگ: قرمز\n• حاشیه: سفید 4px",
                    "colorful": "• فونت: Vazirmatn 24px\n• رنگ: آبی\n• حاشیه: سبز 2px",
                    "persian": "• فونت: Vazirmatn 24px\n• رنگ: سفید\n• زمینه: سیاه\n• حاشیه: سفید 1px",
                    "classic": "• فونت: Vazirmatn 22px\n• رنگ: سیاه\n• زمینه: سفید\n• بدون حاشیه"
                }
                st.markdown(style_descriptions[subtitle_style])
            
            # تنظیمات استایل‌های آماده - استفاده از فونت‌های فارسی
            style_configs = {
                "default": {"font": "vazirmatn", "fontsize": 24, "color": "white", "outline_color": "black", "outline_width": 2},
                "modern": {"font": "vazirmatn", "fontsize": 28, "color": "yellow", "outline_color": "black", "outline_width": 3},
                "minimal": {"font": "vazirmatn", "fontsize": 20, "color": "white", "outline_color": "black", "outline_width": 1},
                "elegant": {"font": "vazirmatn", "fontsize": 26, "color": "gold", "outline_color": "black", "outline_width": 1, "shadow": 1},
                "bold": {"font": "vazirmatn", "fontsize": 30, "color": "red", "outline_color": "white", "outline_width": 4, "bold": True},
                "colorful": {"font": "vazirmatn", "fontsize": 24, "color": "blue", "outline_color": "green", "outline_width": 2},
                "persian": {"font": "vazirmatn", "fontsize": 24, "color": "white", "background_color": "black", "outline_color": "white", "outline_width": 1},
                "classic": {"font": "vazirmatn", "fontsize": 22, "color": "black", "background_color": "white", "outline_color": "black", "outline_width": 0}
            }
            
            if st.button("📝 ایجاد ویدیو با استایل آماده", type="primary"):
                with st.spinner("در حال ایجاد ویدیو با زیرنویس..."):
                    try:
                        output_path = st.session_state['dubbing_app'].create_subtitled_video(subtitle_config=style_configs[subtitle_style])
                        
                        if output_path and os.path.exists(output_path):
                            st.success("✅ ویدیو با زیرنویس با موفقیت ایجاد شد!")
                            
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
                                    type="primary"
                                )
                        else:
                            st.error("❌ خطا در ایجاد ویدیو با زیرنویس")
                    except Exception as e:
                        st.error(f"❌ خطا در ایجاد ویدیو با زیرنویس: {str(e)}")
                        st.error("لطفاً دوباره تلاش کنید یا استایل دیگری انتخاب کنید.")

# پاکسازی و بازیابی
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🧹 پاکسازی فایل‌های موقت", type="secondary"):
        st.session_state['dubbing_app'].clean_previous_files()
        st.success("✅ فایل‌های موقت پاک شدند")
        st.rerun()

with col2:
    if st.button("🔄 بازیابی فایل‌های SRT", type="secondary"):
        if st.session_state['dubbing_app']._restore_srt_files():
            st.success("✅ فایل‌های SRT از پشتیبان بازیابی شدند")
            st.rerun()
        else:
            st.error("❌ هیچ فایل پشتیبان معتبری یافت نشد")

with col3:
    if st.button("🧽 پاکسازی فایل‌های SRT", type="secondary"):
        if st.session_state['dubbing_app'].clean_existing_srt_files():
            st.success("✅ فایل‌های SRT پاکسازی شدند")
            st.rerun()
        else:
            st.error("❌ خطا در پاکسازی فایل‌های SRT")

# اطلاعات اضافی
with st.expander("ℹ️ راهنمای استفاده"):
    st.markdown("""
    ### نحوه استفاده:
    1. **کلید API**: کلید Google API خود را از [Google AI Studio](https://aistudio.google.com/) دریافت کنید
    2. **آپلود ویدیو**: لینک یوتیوب وارد کنید یا فایل محلی آپلود کنید
    3. **استخراج متن**: از Whisper برای ویدیوهای بدون زیرنویس استفاده کنید
    4. **ترجمه**: زبان مقصد را انتخاب کنید
    5. **تولید صدا**: گوینده و تنظیمات صدا را انتخاب کنید
    6. **دانلود**: ویدیو نهایی را دانلود کنید
    
    ### نکات مهم:
    - فرآیند تولید صدا ممکن است چند دقیقه طول بکشد
    - برای ویدیوهای طولانی، زمان انتظار بین درخواست‌ها را افزایش دهید
    - در صورت خطا، دکمه پاکسازی را فشار دهید و دوباره شروع کنید
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    <p>🎬 دوبله خودکار ویدیو - ساخته شده با Streamlit و Google AI</p>
</div>
""", unsafe_allow_html=True)
