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
     
     st.markdown("---")
     
     # مرحله صفر - انتخاب نوع فرآیند
     st.markdown("## 🎯 مرحله صفر - انتخاب نوع فرآیند")
     
     # انتخاب نوع فرآیند
     process_type = st.radio(
         "نحوه انجام کار را انتخاب کنید:",
         ["🚀 فرآیند خودکار (تنظیمات پیش‌فرض)", "⚙️ فرآیند دستی (تنظیمات خاص)"],
         help="فرآیند خودکار: فقط لینک ویدیو وارد کنید و تمام مراحل با تنظیمات پیش‌فرض انجام می‌شود\nفرآیند دستی: تمام مراحل را خودتان کنترل کنید"
     )
     
     st.markdown("---")
     
     # فرآیند خودکار
     if process_type == "🚀 فرآیند خودکار (تنظیمات پیش‌فرض)":
         st.markdown("### 🚀 فرآیند خودکار")
         st.markdown("فقط لینک ویدیو یا یوتیوب را وارد کنید و تمام مراحل به صورت خودکار انجام می‌شود!")
         
         col_auto1, col_auto2 = st.columns([3, 1])
         
         with col_auto1:
             auto_video_url = st.text_input(
                 "🔗 لینک ویدیو یا یوتیوب", 
                 placeholder="https://www.youtube.com/watch?v=... یا https://example.com/video.mp4",
                 help="لینک یوتیوب یا لینک مستقیم ویدیو را وارد کنید",
                 key="auto_video_url"
             )
         
         with col_auto2:
             st.markdown("<br>", unsafe_allow_html=True)  # فاصله
             auto_create_button = st.button("🎬 ایجاد خودکار", type="primary", use_container_width=True, key="auto_create_btn")
         
         if auto_create_button and auto_video_url:
             if not auto_video_url.strip():
                 st.error("❌ لطفاً لینک ویدیو یا یوتیوب را وارد کنید")
             else:
                 with st.spinner("🔄 در حال ایجاد ویدیو خودکار... این فرآیند ممکن است چند دقیقه طول بکشد"):
                     try:
                         output_path = dubbing_app.create_automatic_video(auto_video_url)
                         
                         if output_path and os.path.exists(output_path):
                             st.success("✅ ویدیو خودکار با موفقیت ایجاد شد!")
                             
                             # نمایش اطلاعات فایل
                             file_size = os.path.getsize(output_path) / (1024 * 1024)
                             st.info(f"📊 **اطلاعات فایل:**\n- مسیر: `{output_path}`\n- حجم: {file_size:.2f} MB")
                             
                             # نمایش ویدیو
                             st.video(output_path)
                             
                             # دکمه دانلود
                             with open(output_path, "rb") as file:
                                 st.download_button(
                                     label="📥 دانلود ویدیو",
                                     data=file.read(),
                                     file_name="automatic_video.mp4",
                                     mime="video/mp4"
                                 )
                         else:
                             st.error("❌ خطا در ایجاد ویدیو خودکار")
                             
                     except Exception as e:
                         st.error(f"❌ خطا در فرآیند خودکار: {str(e)}")
     
     # فرآیند دستی
     else:
         st.markdown("### ⚙️ فرآیند دستی")
         st.markdown("تمام مراحل را خودتان کنترل کنید و تنظیمات دلخواه اعمال کنید.")
         
         st.markdown("---")
         
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
                         success = dubbing_app.download_youtube_video(youtube_url)
                         if success:
                             st.success("✅ ویدیو با موفقیت دانلود شد!")
                         else:
                             st.error("❌ خطا در دانلود ویدیو")
                 else:
                     st.error("❌ لطفاً لینک یوتیوب را وارد کنید")
         
         else:  # فایل محلی
             uploaded_file = st.file_uploader(
                 "📁 انتخاب فایل ویدیو",
                 type=['mp4', 'avi', 'mov', 'mkv', 'wmv'],
                 help="فایل ویدیو خود را آپلود کنید"
             )
             
             if uploaded_file is not None:
                 # ذخیره فایل آپلود شده
                 with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                     tmp_file.write(uploaded_file.getvalue())
                     temp_path = tmp_file.name
                 
                 # کپی فایل به پوشه کار
                 import shutil
                 work_dir = Path("dubbing_work")
                 work_dir.mkdir(exist_ok=True)
                 final_path = work_dir / "input_video.mp4"
                 shutil.copy2(temp_path, final_path)
                 os.unlink(temp_path)  # حذف فایل موقت
                 
                 st.success(f"✅ فایل با موفقیت آپلود شد: {final_path}")
                 
                 # نمایش ویدیو
                 st.video(str(final_path))
         
         st.markdown("---")
         
         # مرحله 2: استخراج صدا و ترجمه
         st.markdown('<h2 class="step-header">🎤 مرحله 2: استخراج صدا و ترجمه</h2>', unsafe_allow_html=True)
         
         col1, col2 = st.columns(2)
         
         with col1:
             if st.button("🎵 استخراج صدا", type="primary"):
                 with st.spinner("در حال استخراج صدا..."):
                     success = dubbing_app.extract_audio_with_whisper()
                     if success:
                         st.success("✅ صدا با موفقیت استخراج شد!")
                     else:
                         st.error("❌ خطا در استخراج صدا")
         
         with col2:
             if st.button("🌐 ترجمه زیرنویس", type="primary"):
                 with st.spinner("در حال ترجمه..."):
                     success = dubbing_app.translate_subtitles(target_language)
                     if success:
                         st.success("✅ ترجمه با موفقیت انجام شد!")
                     else:
                         st.error("❌ خطا در ترجمه")
         
         # نمایش فایل‌های SRT
         st.markdown("### 📄 فایل‌های زیرنویس")
         col_srt1, col_srt2 = st.columns(2)
         
         with col_srt1:
             if os.path.exists("dubbing_work/audio.srt"):
                 st.success("✅ فایل زیرنویس اصلی (انگلیسی)")
                 with open("dubbing_work/audio.srt", "r", encoding="utf-8") as f:
                     st.text_area("محتوای فایل انگلیسی", f.read(), height=200)
         
         with col_srt2:
             if os.path.exists("dubbing_work/audio_fa.srt"):
                 st.success("✅ فایل زیرنویس ترجمه شده")
                 with open("dubbing_work/audio_fa.srt", "r", encoding="utf-8") as f:
                     st.text_area("محتوای فایل فارسی", f.read(), height=200)
         
         # دکمه‌های پاکسازی و بازیابی
         st.markdown("### 🧹 مدیریت فایل‌های SRT")
         col_clean1, col_clean2 = st.columns(2)
         
         with col_clean1:
             if st.button("🧹 پاکسازی فایل‌های SRT"):
                 dubbing_app.clean_existing_srt_files()
                 st.success("✅ فایل‌های SRT پاکسازی شدند")
                 st.rerun()
         
         with col_clean2:
             if st.button("🔄 بازیابی فایل‌های SRT"):
                 dubbing_app._restore_srt_files()
                 st.success("✅ فایل‌های SRT بازیابی شدند")
                 st.rerun()
         
         st.markdown("---")
         
         # مرحله 3: تولید صدا
         st.markdown('<h2 class="step-header">🎙️ مرحله 3: تولید صدا</h2>', unsafe_allow_html=True)
         
         if st.button("🎵 تولید صدا", type="primary"):
             with st.spinner("در حال تولید صدا..."):
                 success = dubbing_app.generate_audio(voice, speech_prompt, enable_compression, merge_count)
                 if success:
                     st.success("✅ صدا با موفقیت تولید شد!")
                 else:
                     st.error("❌ خطا در تولید صدا")
         
         st.markdown("---")
         
         # مرحله 4: ایجاد ویدیو نهایی
         st.markdown('<h2 class="step-header">🎬 مرحله 4: ایجاد ویدیو نهایی</h2>', unsafe_allow_html=True)
         
         if st.button("🎬 ایجاد ویدیو نهایی", type="primary"):
             with st.spinner("در حال ایجاد ویدیو نهایی..."):
                 success = dubbing_app.create_final_video(keep_original_audio, original_audio_volume if keep_original_audio else 0.0)
                 if success:
                     st.success("✅ ویدیو نهایی با موفقیت ایجاد شد!")
                     
                     # نمایش ویدیو
                     output_path = "dubbing_work/final_video.mp4"
                     if os.path.exists(output_path):
                         st.video(output_path)
                         
                         # دکمه دانلود
                         with open(output_path, "rb") as file:
                             st.download_button(
                                 label="📥 دانلود ویدیو نهایی",
                                 data=file.read(),
                                 file_name="final_video.mp4",
                                 mime="video/mp4"
                             )
                 else:
                     st.error("❌ خطا در ایجاد ویدیو نهایی")
         
         st.markdown("---")
         
         # مرحله 5: ایجاد ویدیو با زیرنویس سفارشی
         st.markdown('<h2 class="step-header">📝 مرحله 5: ایجاد ویدیو با زیرنویس سفارشی</h2>', unsafe_allow_html=True)
         
         st.markdown("### 🎨 تنظیمات زیرنویس")
         
         col_sub1, col_sub2 = st.columns(2)
         
         with col_sub1:
             st.markdown("**📝 تنظیمات متن:**")
             font_name = st.selectbox("فونت", ["Arial", "Times New Roman", "Courier New", "Verdana", "Tahoma", "Georgia", "Impact"], index=0)
             font_size = st.slider("اندازه فونت", 12, 48, 24)
             text_color = st.selectbox("رنگ متن", ["white", "yellow", "red", "green", "blue", "black", "orange", "purple", "pink", "cyan"], index=0)
             background_color = st.selectbox("رنگ زمینه", ["none", "black", "white", "red", "green", "blue", "yellow"], index=0)
         
         with col_sub2:
             st.markdown("**🎨 تنظیمات ظاهری:**")
             outline_color = st.selectbox("رنگ حاشیه", ["black", "white", "red", "green", "blue", "yellow"], index=0)
             outline_width = st.slider("ضخامت حاشیه", 0, 5, 2)
             position = st.selectbox("موقعیت", ["bottom_center", "bottom_left", "bottom_right", "top_center", "top_left", "top_right"], index=0, format_func=lambda x: {"bottom_center": "پایین وسط", "bottom_left": "پایین چپ", "bottom_right": "پایین راست", "top_center": "بالا وسط", "top_left": "بالا چپ", "top_right": "بالا راست"}[x])
             margin_v = st.slider("فاصله از لبه", 10, 100, 20)
         
         # تنظیمات اضافی
         col_sub3, col_sub4 = st.columns(2)
         with col_sub3:
             shadow = st.checkbox("سایه")
             if shadow:
                 shadow_color = st.selectbox("رنگ سایه", ["black", "white", "red", "green", "blue", "yellow"], index=0)
             else:
                 shadow_color = "black"
         with col_sub4:
             bold = st.checkbox("ضخیم")
             italic = st.checkbox("مایل")
         
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
                 
                 # ایجاد پیش‌نمایش HTML با پشتیبانی کامل از رنگ‌ها
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
                         'none': 'transparent'
                     }
                     return color_map.get(color_name, '#000000')
                 
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
                 output_path = dubbing_app.create_subtitled_video(
                     subtitle_config=subtitle_config,
                     fixed_text_config=fixed_text_config
                 )
                 
                 if output_path and os.path.exists(output_path):
                     st.success("✅ ویدیو با زیرنویس سفارشی با موفقیت ایجاد شد!")
                     
                     # نمایش اطلاعات فایل
                     file_size = os.path.getsize(output_path) / (1024 * 1024)
                     st.info(f"📊 **اطلاعات فایل:**\n- مسیر: `{output_path}`\n- حجم: {file_size:.2f} MB")
                     
                     # نمایش ویدیو
                     st.video(output_path)
                     
                     # دکمه دانلود
                     with open(output_path, "rb") as file:
                         st.download_button(
                             label="📥 دانلود ویدیو سفارشی",
                             data=file.read(),
                             file_name="custom_subtitled_video.mp4",
                             mime="video/mp4"
                         )
                 else:
                     st.error("❌ خطا در ایجاد ویدیو با زیرنویس سفارشی")

# محتوای اصلی
if api_key:
    # ایجاد instance از کلاس دوبله
    try:
        dubbing_app = VideoDubbingApp(api_key)
        st.success("✅ اتصال به Google AI برقرار شد")
    except Exception as e:
        st.error(f"❌ خطا در اتصال به Google AI: {str(e)}")
        st.stop()

# تمام مراحل در بخش فرآیند دستی قرار دارند

# پاکسازی و بازیابی
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🧹 پاکسازی فایل‌های موقت", type="secondary"):
        dubbing_app.clean_previous_files()
        st.success("✅ فایل‌های موقت پاک شدند")
        st.rerun()

with col2:
    if st.button("🔄 بازیابی فایل‌های SRT", type="secondary"):
        if dubbing_app._restore_srt_files():
            st.success("✅ فایل‌های SRT از پشتیبان بازیابی شدند")
            st.rerun()
        else:
            st.error("❌ هیچ فایل پشتیبان معتبری یافت نشد")

with col3:
    if st.button("🧽 پاکسازی فایل‌های SRT", type="secondary"):
        if dubbing_app.clean_existing_srt_files():
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
                    
                    # ایجاد پیش‌نمایش HTML با پشتیبانی کامل از رنگ‌ها
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
                            'none': 'transparent'
                        }
                        return color_map.get(color_name, '#000000')
                    
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
                    output_path = dubbing_app.create_subtitled_video(
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
                    "default": "• فونت: Arial 24px\n• رنگ: سفید\n• حاشیه: سیاه 2px",
                    "modern": "• فونت: Arial 28px\n• رنگ: زرد\n• حاشیه: سیاه 3px",
                    "minimal": "• فونت: Arial 20px\n• رنگ: سفید\n• حاشیه: سیاه 1px",
                    "elegant": "• فونت: Georgia 26px\n• رنگ: طلایی\n• سایه: سیاه",
                    "bold": "• فونت: Impact 30px\n• رنگ: قرمز\n• حاشیه: سفید 4px",
                    "colorful": "• فونت: Verdana 24px\n• رنگ: آبی\n• حاشیه: سبز 2px",
                    "persian": "• فونت: Vazirmatn 24px\n• رنگ: سفید\n• زمینه: سیاه\n• حاشیه: سفید 1px",
                    "classic": "• فونت: Times New Roman 22px\n• رنگ: سیاه\n• زمینه: سفید\n• بدون حاشیه"
                }
                st.markdown(style_descriptions[subtitle_style])
            
            # تنظیمات استایل‌های آماده
            style_configs = {
                "default": {"font": "Arial", "fontsize": 24, "color": "white", "outline_color": "black", "outline_width": 2},
                "modern": {"font": "Arial", "fontsize": 28, "color": "yellow", "outline_color": "black", "outline_width": 3},
                "minimal": {"font": "Arial", "fontsize": 20, "color": "white", "outline_color": "black", "outline_width": 1},
                "elegant": {"font": "Georgia", "fontsize": 26, "color": "gold", "outline_color": "black", "outline_width": 1, "shadow": 1},
                "bold": {"font": "Impact", "fontsize": 30, "color": "red", "outline_color": "white", "outline_width": 4, "bold": True},
                "colorful": {"font": "Verdana", "fontsize": 24, "color": "blue", "outline_color": "green", "outline_width": 2},
                "persian": {"font": "vazirmatn", "fontsize": 24, "color": "white", "background_color": "black", "outline_color": "white", "outline_width": 1},
                "classic": {"font": "Times New Roman", "fontsize": 22, "color": "black", "background_color": "white", "outline_color": "black", "outline_width": 0}
            }
            
            if st.button("📝 ایجاد ویدیو با استایل آماده", type="primary"):
                with st.spinner("در حال ایجاد ویدیو با زیرنویس..."):
                    output_path = dubbing_app.create_subtitled_video(subtitle_config=style_configs[subtitle_style])
                    
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

# پاکسازی و بازیابی
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🧹 پاکسازی فایل‌های موقت", type="secondary"):
        dubbing_app.clean_previous_files()
        st.success("✅ فایل‌های موقت پاک شدند")
        st.rerun()

with col2:
    if st.button("🔄 بازیابی فایل‌های SRT", type="secondary"):
        if dubbing_app._restore_srt_files():
            st.success("✅ فایل‌های SRT از پشتیبان بازیابی شدند")
            st.rerun()
        else:
            st.error("❌ هیچ فایل پشتیبان معتبری یافت نشد")

with col3:
    if st.button("🧽 پاکسازی فایل‌های SRT", type="secondary"):
        if dubbing_app.clean_existing_srt_files():
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
