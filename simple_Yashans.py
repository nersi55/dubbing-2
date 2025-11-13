"""
استخراج پست اینستاگرام - شامل تصویر/ویدیو و کپشن
Instagram Post Extractor - Extract Image/Video and Caption
"""

import streamlit as st
import os
import csv
import io
import time
from pathlib import Path

# تنظیمات صفحه
st.set_page_config(
    page_title="📸 استخراج پست اینستاگرام - یاشانس",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# استایل‌های سفارشی
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #E4405F;
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
    .caption-box {
        background-color: #fff;
        border: 2px solid #E4405F;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin: 1rem 0;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    .media-info {
        background-color: #f0f0f0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# هدر اصلی
st.markdown('<h1 class="main-header">📸 استخراج پست اینستاگرام</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">استخراج تصویر/ویدیو و کپشن از پست‌های اینستاگرام - یاشانس</p>', unsafe_allow_html=True)

# تنظیمات API (می‌توانید از متغیر محیطی استفاده کنید)
API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyBNYpugB8Ezrpmk-U7Yvp9ynClEJLCETMo")

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

# تابع برای خواندن URL ها از CSV
def read_instagram_urls_from_csv(uploaded_file) -> list:
    """خواندن لینک‌های اینستاگرام از فایل CSV"""
    urls = []
    try:
        # خواندن فایل
        content = uploaded_file.read().decode('utf-8')
        csv_file = io.StringIO(content)
        
        # تلاش برای خواندن به عنوان CSV با header
        try:
            reader = csv.DictReader(csv_file)
            fieldnames = [fn.strip().lower() for fn in (reader.fieldnames or [])]
            candidate_cols = ['url', 'instagram_url', 'link', 'instagram_link']
            selected = None
            for c in candidate_cols:
                if c in fieldnames:
                    selected = c
                    break
            
            if selected:
                for row in reader:
                    val = row.get(selected) or row.get(selected.capitalize()) or row.get(selected.upper())
                    if val and val.strip() and 'instagram.com' in val:
                        urls.append(val.strip())
                return urls
        except Exception:
            csv_file.seek(0)
            pass
        
        # Fallback: خواندن خط به خط
        csv_file.seek(0)
        for line in csv_file:
            line = line.strip()
            if line and 'instagram.com' in line:
                urls.append(line)
        
        return urls
    except Exception as e:
        st.error(f"❌ خطا در خواندن فایل CSV: {str(e)}")
        return []

# تب‌ها برای انتخاب روش ورودی
tab1, tab2 = st.tabs(["🔗 لینک تکی", "📄 فایل CSV (دسته‌ای)"])

with tab1:
    # فرم ورودی تکی
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    st.markdown("### 🔗 لینک پست اینستاگرام")
    instagram_url = st.text_input(
        "لینک پست",
        placeholder="https://www.instagram.com/p/... یا https://www.instagram.com/reel/...",
        help="لینک کامل پست اینستاگرام (پست عکس، ویدیو یا ریل) را اینجا وارد کنید",
        label_visibility="collapsed",
        key="single_url"
    )

    col1, col2 = st.columns(2)

    with col1:
        extract_only = st.button("📋 فقط استخراج اطلاعات", type="primary", use_container_width=True, key="extract_single")

    with col2:
        download_and_extract = st.button("📥 دانلود + استخراج", type="secondary", use_container_width=True, key="download_single")

    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    # فرم ورودی CSV
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    st.markdown("### 📄 آپلود فایل CSV")
    st.markdown("""
    **فرمت CSV:**
    - یک ستون با نام `url` یا `instagram_url` یا `link` 
    - یا هر سطر یک لینک اینستاگرام باشد
    - مثال:
    ```csv
    url
    https://www.instagram.com/p/ABC123/
    https://www.instagram.com/reel/XYZ789/
    ```
    """)
    
    uploaded_file = st.file_uploader(
        "فایل CSV را انتخاب کنید",
        type=['csv'],
        help="فایل CSV حاوی لینک‌های اینستاگرام را آپلود کنید",
        key="csv_uploader"
    )
    
    if uploaded_file is not None:
        # ذخیره فایل در session state
        st.session_state['uploaded_csv'] = uploaded_file
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 فقط استخراج اطلاعات (دسته‌ای)", type="primary", use_container_width=True, key="extract_batch"):
                st.session_state['batch_mode'] = 'extract'
                st.rerun()
        with col2:
            if st.button("📥 دانلود + استخراج (دسته‌ای)", type="secondary", use_container_width=True, key="download_batch"):
                st.session_state['batch_mode'] = 'download'
                st.rerun()
        
        # اگر batch mode تنظیم شده، پردازش را شروع کن
        if 'batch_mode' in st.session_state:
            batch_mode = st.session_state['batch_mode']
            uploaded_file = st.session_state.get('uploaded_csv')
            
            if uploaded_file is not None:
                # خواندن URL ها از CSV
                urls = read_instagram_urls_from_csv(uploaded_file)
                
                if not urls:
                    st.error("❌ هیچ لینک معتبری در فایل CSV یافت نشد")
                else:
                    st.success(f"✅ {len(urls)} لینک از فایل CSV خوانده شد")
                    
                    # نمایش پیش‌نمایش
                    with st.expander(f"📋 نمایش {min(5, len(urls))} لینک اول"):
                        for i, url in enumerate(urls[:5], 1):
                            st.text(f"{i}. {url}")
                        if len(urls) > 5:
                            st.text(f"... و {len(urls) - 5} لینک دیگر")
                    
                    # تعیین نوع پردازش
                    process_type = "استخراج" if batch_mode == 'extract' else "دانلود + استخراج"
                    
                    # شروع پردازش
                    if st.button(f"🚀 شروع پردازش دسته‌ای ({process_type})", type="primary", key="start_batch"):
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        results = []
                        
                        for idx, url in enumerate(urls, 1):
                            status_text.text(f"📥 پردازش {idx}/{len(urls)}: {url[:50]}...")
                            progress_bar.progress(idx / len(urls))
                            
                            try:
                                if batch_mode == 'extract':
                                    # فقط استخراج اطلاعات
                                    post_info = dubbing_app.extract_instagram_post(url)
                                else:
                                    # دانلود + استخراج
                                    post_info = dubbing_app.download_instagram_media(url, download_media=True)
                                
                                if 'error' in post_info:
                                    results.append({
                                        'url': url,
                                        'status': '❌ خطا',
                                        'message': post_info.get('error', 'خطای نامشخص'),
                                        'downloaded': False
                                    })
                                else:
                                    media_type = post_info.get('media_type', 'unknown')
                                    downloaded = post_info.get('downloaded', False)
                                    caption_file = post_info.get('caption_file', '')
                                    
                                    status = '✅ موفق' if downloaded else '⚠️ بدون دانلود'
                                    results.append({
                                        'url': url,
                                        'status': status,
                                        'media_type': media_type,
                                        'downloaded': downloaded,
                                        'downloaded_file': post_info.get('downloaded_file', ''),
                                        'caption_file': caption_file,
                                        'caption': post_info.get('caption', '')[:100] + '...' if len(post_info.get('caption', '')) > 100 else post_info.get('caption', '')
                                    })
                            except Exception as e:
                                results.append({
                                    'url': url,
                                    'status': '❌ خطا',
                                    'message': str(e)[:100],
                                    'downloaded': False
                                })
                            
                            # تاخیر کوتاه بین پردازش‌ها
                            if idx < len(urls):
                                time.sleep(1)
                        
                        # نمایش نتایج
                        progress_bar.progress(1.0)
                        status_text.text("✅ پردازش کامل شد!")
                        
                        st.markdown("### 📊 نتایج پردازش")
                        
                        # آمار
                        successful = sum(1 for r in results if r.get('status') == '✅ موفق')
                        failed = sum(1 for r in results if '❌' in r.get('status', ''))
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("✅ موفق", successful)
                        with col2:
                            st.metric("❌ ناموفق", failed)
                        with col3:
                            st.metric("📊 کل", len(urls))
                        
                        # جدول نتایج
                        st.markdown("### 📋 جزئیات نتایج")
                        for i, result in enumerate(results, 1):
                            with st.expander(f"{i}. {result['url'][:60]}... - {result['status']}"):
                                st.json(result)
                        
                        # دانلود نتایج به صورت CSV
                        if results:
                            output_csv = io.StringIO()
                            fieldnames = ['url', 'status', 'media_type', 'downloaded', 'downloaded_file', 'caption_file']
                            writer = csv.DictWriter(output_csv, fieldnames=fieldnames)
                            writer.writeheader()
                            for r in results:
                                writer.writerow({k: r.get(k, '') for k in fieldnames})
                            
                            st.download_button(
                                label="📥 دانلود نتایج به صورت CSV",
                                data=output_csv.getvalue(),
                                file_name=f"instagram_batch_results_{int(time.time())}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
    
    st.markdown('</div>', unsafe_allow_html=True)

# نمایش اطلاعات کوکی
if os.path.exists('cookies.txt'):
    st.info("🍪 فایل cookies.txt یافت شد - برای محتوای خصوصی استفاده می‌شود")
else:
    st.warning("⚠️ فایل cookies.txt یافت نشد - برای محتوای خصوصی ممکن است نیاز باشد")

# پردازش درخواست تکی
if extract_only or download_and_extract:
    if not instagram_url or not instagram_url.strip():
        st.error("❌ لطفاً لینک پست اینستاگرام را وارد کنید")
    else:
        url = instagram_url.strip()
        
        # بررسی صحت URL
        if 'instagram.com' not in url:
            st.error("❌ لینک وارد شده معتبر نیست. لطفاً لینک اینستاگرام را وارد کنید.")
        else:
            if extract_only:
                # فقط استخراج اطلاعات
                with st.spinner("📡 در حال استخراج اطلاعات از اینستاگرام..."):
                    post_info = dubbing_app.extract_instagram_post(url)
            else:
                # دانلود + استخراج
                with st.spinner("📥 در حال دانلود و استخراج اطلاعات..."):
                    post_info = dubbing_app.download_instagram_media(url, download_media=True)
            
            # نمایش نتایج
            if 'error' in post_info:
                st.error(f"❌ خطا: {post_info['error']}")
            else:
                st.success("✅ اطلاعات با موفقیت استخراج شد!")
                
                # نمایش اطلاعات پست
                st.markdown("### 📊 اطلاعات پست")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**👤 کاربر:** {post_info.get('uploader', 'نامشخص')}")
                    st.markdown(f"**🆔 شناسه:** {post_info.get('uploader_id', 'نامشخص')}")
                    media_type = post_info.get('media_type', 'unknown')
                    if media_type == 'video':
                        st.markdown("**📹 نوع محتوا:** 🎥 ویدیو")
                    elif media_type == 'image':
                        st.markdown("**📹 نوع محتوا:** 🖼️ تصویر")
                    else:
                        st.markdown(f"**📹 نوع محتوا:** {media_type}")
                
                with col2:
                    if post_info.get('view_count'):
                        st.markdown(f"**👁️ بازدید:** {post_info.get('view_count', 0):,}")
                    if post_info.get('like_count'):
                        st.markdown(f"**❤️ لایک:** {post_info.get('like_count', 0):,}")
                    if post_info.get('duration'):
                        duration_sec = post_info.get('duration', 0)
                        minutes = int(duration_sec // 60)
                        seconds = int(duration_sec % 60)
                        st.markdown(f"**⏱️ مدت زمان:** {minutes}:{seconds:02d}")
                
                # نمایش عنوان
                if post_info.get('title'):
                    st.markdown("### 📝 عنوان")
                    st.markdown(f"**{post_info.get('title')}**")
                
                # نمایش کپشن
                caption = post_info.get('caption', '')
                if caption:
                    st.markdown("### 💬 کپشن")
                    st.markdown(f'<div class="caption-box">{caption}</div>', unsafe_allow_html=True)
                    
                    # دکمه کپی کپشن
                    st.code(caption, language=None)
                else:
                    st.info("ℹ️ کپشنی برای این پست یافت نشد")
                
                # نمایش اطلاعات رسانه
                st.markdown("### 🎬 اطلاعات رسانه")
                
                if post_info.get('media_type') == 'video':
                    if post_info.get('width') and post_info.get('height'):
                        st.markdown(f"**📐 ابعاد:** {post_info.get('width')} × {post_info.get('height')}")
                    if post_info.get('video_url'):
                        st.markdown("**🔗 لینک ویدیو:**")
                        st.code(post_info.get('video_url', '')[:200] + '...' if len(post_info.get('video_url', '')) > 200 else post_info.get('video_url', ''))
                else:
                    if post_info.get('image_url'):
                        st.markdown("**🔗 لینک تصویر:**")
                        st.code(post_info.get('image_url', '')[:200] + '...' if len(post_info.get('image_url', '')) > 200 else post_info.get('image_url', ''))
                
                # نمایش thumbnail
                if post_info.get('thumbnail'):
                    st.markdown("### 🖼️ تصویر بندانگشتی")
                    try:
                        st.image(post_info.get('thumbnail'), use_container_width=True)
                    except:
                        st.markdown(f"**🔗 لینک:** {post_info.get('thumbnail')}")
                
                # نمایش فایل دانلود شده
                if post_info.get('downloaded'):
                    if post_info.get('downloaded_file'):
                        file_path = Path(post_info.get('downloaded_file'))
                        if file_path.exists():
                            st.markdown("### 📁 فایل دانلود شده")
                            st.success(f"✅ فایل با موفقیت دانلود شد: `{file_path.name}`")
                            
                            file_size = file_path.stat().st_size / (1024 * 1024)  # MB
                            st.info(f"📊 حجم فایل: {file_size:.2f} MB")
                            
                            # نمایش ویدیو یا تصویر
                            if post_info.get('media_type') == 'video':
                                st.video(str(file_path))
                            else:
                                st.image(str(file_path), use_container_width=True)
                            
                            # دکمه دانلود
                            with open(file_path, 'rb') as f:
                                file_data = f.read()
                                file_extension = file_path.suffix
                                st.download_button(
                                    label=f"⬇️ دانلود {file_path.name}",
                                    data=file_data,
                                    file_name=file_path.name,
                                    mime=f"{'video' if post_info.get('media_type') == 'video' else 'image'}/{file_extension[1:]}",
                                    use_container_width=True
                                )
                        else:
                            st.warning("⚠️ فایل دانلود شده یافت نشد")
                elif download_and_extract:
                    st.warning("⚠️ دانلود فایل انجام نشد")


# راهنما
with st.expander("ℹ️ راهنما"):
    st.markdown("""
    ### نحوه استفاده:
    
    1. **فقط استخراج اطلاعات**: لینک پست را وارد کنید و روی "فقط استخراج اطلاعات" کلیک کنید.
       - کپشن پست نمایش داده می‌شود
       - اطلاعات پست (کاربر، لایک، بازدید و...) نمایش داده می‌شود
       - فایل دانلود نمی‌شود
    
    2. **دانلود + استخراج**: لینک پست را وارد کنید و روی "دانلود + استخراج" کلیک کنید.
       - تمام اطلاعات استخراج می‌شود
       - فایل تصویر یا ویدیو دانلود می‌شود
       - می‌توانید فایل را دانلود کنید
    
    ### انواع پست‌های پشتیبانی شده:
    - 📸 پست عکس (`/p/...`)
    - 🎥 پست ویدیو (`/p/...`)
    - 🎬 ریل (`/reel/...`)
    - 📺 IGTV (`/tv/...`)
    
    ### پردازش دسته‌ای (CSV):
    1. فایل CSV را آماده کنید با یک ستون `url` یا `instagram_url`
    2. فایل را آپلود کنید
    3. روی "شروع پردازش دسته‌ای" کلیک کنید
    4. برنامه همه لینک‌ها را یکی یکی پردازش می‌کند
    5. نتایج را می‌توانید به صورت CSV دانلود کنید
    
    ### نکات مهم:
    - برای پست‌های خصوصی، فایل `cookies.txt` لازم است
    - مطمئن شوید `yt-dlp` به‌روز است: `pip install -U yt-dlp`
    - برخی پست‌ها ممکن است به دلیل محدودیت‌های اینستاگرام قابل دسترسی نباشند
    - در پردازش دسته‌ای، بین هر پردازش 1 ثانیه تاخیر وجود دارد
    """)

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; padding: 2rem;">'
    '📸 استخراج پست اینستاگرام - یاشانس | ساخته شده با ❤️'
    '</div>',
    unsafe_allow_html=True
)

