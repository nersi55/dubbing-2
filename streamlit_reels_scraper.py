"""
رابط کاربری Streamlit برای استخراج لینک‌های Reels اینستاگرام
Streamlit UI for Instagram Reels Link Scraper
"""

import streamlit as st
import os
import csv
import io
import time
from pathlib import Path
from instagram_reels_scraper import (
    extract_username_from_url,
    scrape_instagram_reels
)

# تنظیمات صفحه
st.set_page_config(
    page_title="🎬 استخراج Reels اینستاگرام",
    page_icon="🎬",
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
    .reel-link {
        background-color: #fff;
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        padding: 0.75rem;
        margin: 0.5rem 0;
        word-break: break-all;
    }
    .stats-box {
        background-color: #f0f0f0;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin: 1rem 0;
        text-align: center;
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #E4405F;
    }
    .stat-label {
        font-size: 1rem;
        color: #666;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# هدر اصلی
st.markdown('<h1 class="main-header">🎬 استخراج Reels اینستاگرام</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">استخراج تمام لینک‌های Reels از صفحه اینستاگرام و ذخیره در فایل CSV</p>', unsafe_allow_html=True)

# بررسی وجود cookies
cookie_file = 'cookies_insta.txt'
has_cookies = os.path.exists(cookie_file)

if has_cookies:
    st.info(f"🍪 فایل احراز هویت ({cookie_file}) یافت شد. برای صفحات خصوصی استفاده خواهد شد.")
else:
    st.warning(f"⚠️ فایل احراز هویت ({cookie_file}) یافت نشد. فقط صفحات عمومی قابل دسترسی هستند.")

# بخش ورودی
st.markdown("### 📝 ورودی")
profile_url = st.text_input(
    "لینک صفحه اینستاگرام",
    placeholder="https://www.instagram.com/innertune.affirmations/",
    help="لینک کامل صفحه اینستاگرام را وارد کنید"
)

# تنظیمات پیشرفته
with st.expander("⚙️ تنظیمات پیشرفته"):
    headless_mode = st.checkbox(
        "اجرای مرورگر در حالت Headless (بدون نمایش)",
        value=False,
        help="در این حالت مرورگر نمایش داده نمی‌شود و سریع‌تر اجرا می‌شود"
    )
    max_scrolls = st.slider(
        "حداکثر تعداد اسکرول",
        min_value=20,
        max_value=200,
        value=100,
        help="تعداد اسکرول برای بارگذاری Reels بیشتر (برای صفحات با Reels زیاد، مقدار بالاتر انتخاب کنید)"
    )
    scroll_delay = st.slider(
        "تاخیر بین اسکرول‌ها (ثانیه)",
        min_value=1.0,
        max_value=5.0,
        value=2.0,
        step=0.5,
        help="تاخیر بین هر اسکرول برای جلوگیری از محدودیت اینستاگرام"
    )

# دکمه استخراج
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    extract_button = st.button(
        "🚀 شروع استخراج",
        type="primary",
        use_container_width=True
    )

# نمایش نتایج
if extract_button:
    if not profile_url:
        st.error("❌ لطفاً لینک صفحه اینستاگرام را وارد کنید.")
    elif 'instagram.com' not in profile_url:
        st.error("❌ لینک وارد شده معتبر نیست. لطفاً لینک اینستاگرام وارد کنید.")
    else:
        # استخراج نام کاربری
        username = extract_username_from_url(profile_url)
        
        if not username:
            st.error(f"❌ نتوانستیم نام کاربری را از URL استخراج کنیم: {profile_url}")
        else:
            st.info(f"👤 نام کاربری شناسایی شده: **{username}**")
            
            # نمایش پیشرفت
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # ایجاد placeholder برای نتایج
            results_container = st.container()
            
            try:
                status_text.info("🚀 در حال راه‌اندازی مرورگر...")
                progress_bar.progress(10)
                
                # اجرای استخراج با تنظیمات
                status_text.info("🔄 در حال استخراج لینک‌های Reels...")
                progress_bar.progress(30)
                
                csv_path = scrape_instagram_reels(
                    profile_url,
                    output_dir='.',
                    headless=headless_mode,
                    max_scrolls=max_scrolls,
                    scroll_delay=scroll_delay
                )
                
                if csv_path and os.path.exists(csv_path):
                    progress_bar.progress(100)
                    status_text.success("✅ استخراج با موفقیت انجام شد!")
                    
                    # خواندن فایل CSV
                    reel_links = []
                    with open(csv_path, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        next(reader)  # رد کردن هدر
                        reel_links = [row[0] for row in reader if row]
                    
                    # نمایش آمار
                    with results_container:
                        st.markdown("---")
                        st.markdown("### 📊 نتایج")
                        
                        # آمار
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown(f"""
                            <div class="stats-box">
                                <div class="stat-number">{len(reel_links)}</div>
                                <div class="stat-label">تعداد Reels</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"""
                            <div class="stats-box">
                                <div class="stat-number">{username}</div>
                                <div class="stat-label">نام کاربری</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col3:
                            file_size = os.path.getsize(csv_path) / 1024  # KB
                            st.markdown(f"""
                            <div class="stats-box">
                                <div class="stat-number">{file_size:.1f} KB</div>
                                <div class="stat-label">حجم فایل CSV</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # دانلود فایل CSV
                        st.markdown("### 📥 دانلود فایل CSV")
                        with open(csv_path, 'r', encoding='utf-8') as f:
                            csv_data = f.read()
                        
                        st.download_button(
                            label=f"💾 دانلود {os.path.basename(csv_path)}",
                            data=csv_data,
                            file_name=os.path.basename(csv_path),
                            mime="text/csv",
                            type="primary",
                            use_container_width=True
                        )
                        
                        # نمایش لیست لینک‌ها
                        st.markdown("### 🔗 لیست لینک‌های Reels")
                        
                        # جستجو در لیست
                        search_term = st.text_input(
                            "🔍 جستجو در لینک‌ها",
                            placeholder="جستجو...",
                            key="search_reels"
                        )
                        
                        # فیلتر کردن لینک‌ها
                        filtered_links = reel_links
                        if search_term:
                            filtered_links = [link for link in reel_links if search_term.lower() in link.lower()]
                            st.info(f"نمایش {len(filtered_links)} از {len(reel_links)} لینک")
                        
                        # نمایش لینک‌ها در یک جدول
                        if filtered_links:
                            # ایجاد DataFrame برای نمایش بهتر
                            import pandas as pd
                            df = pd.DataFrame({
                                'ردیف': range(1, len(filtered_links) + 1),
                                'لینک Reel': filtered_links
                            })
                            st.dataframe(df, use_container_width=True, hide_index=True)
                            
                            # نمایش لینک‌ها به صورت لیست
                            with st.expander("📋 نمایش به صورت لیست"):
                                for idx, link in enumerate(filtered_links, 1):
                                    st.markdown(f"""
                                    <div class="reel-link">
                                        <strong>{idx}.</strong> <a href="{link}" target="_blank">{link}</a>
                                    </div>
                                    """, unsafe_allow_html=True)
                        else:
                            st.warning("هیچ لینکی یافت نشد.")
                        
                        # نمایش مسیر فایل
                        st.info(f"📁 فایل CSV در مسیر زیر ذخیره شد:\n`{os.path.abspath(csv_path)}`")
                        
                else:
                    progress_bar.progress(0)
                    status_text.error("❌ استخراج ناموفق بود. لطفاً دوباره تلاش کنید.")
                    st.error("""
                    **مشکلات احتمالی:**
                    - صفحه خصوصی است و نیاز به احراز هویت دارد
                    - صفحه Reels خالی است
                    - مشکل در اتصال به اینستاگرام
                    - لینک وارد شده معتبر نیست
                    """)
                    
            except Exception as e:
                progress_bar.progress(0)
                status_text.error(f"❌ خطا: {str(e)}")
                st.error(f"خطای جزئیات:\n```\n{str(e)}\n```")
                import traceback
                with st.expander("جزئیات خطا"):
                    st.code(traceback.format_exc())

# راهنما
with st.expander("📖 راهنما"):
    st.markdown("""
    ### نحوه استفاده:
    
    1. **وارد کردن لینک**: لینک کامل صفحه اینستاگرام را وارد کنید
       - مثال: `https://www.instagram.com/innertune.affirmations/`
    
    2. **تنظیمات (اختیاری)**: می‌توانید تنظیمات پیشرفته را تغییر دهید
    
    3. **شروع استخراج**: روی دکمه "شروع استخراج" کلیک کنید
    
    4. **دانلود نتایج**: پس از اتمام، فایل CSV را دانلود کنید
    
    ### نکات مهم:
    
    - ⚠️ برای صفحات **خصوصی**، فایل `cookies_insta.txt` لازم است
    - ⏱️ استخراج ممکن است چند دقیقه طول بکشد (بسته به تعداد Reels)
    - 🔒 مرورگر به صورت خودکار باز و بسته می‌شود
    - 📊 تمام لینک‌های Reels در فایل CSV ذخیره می‌شوند
    
    ### فرمت فایل CSV:
    
    فایل CSV شامل یک ستون به نام `reel_url` است که شامل تمام لینک‌های Reels می‌باشد.
    
    ### مثال:
    ```csv
    reel_url
    https://www.instagram.com/reel/ABC123/
    https://www.instagram.com/reel/XYZ789/
    ```
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🎬 استخراج Reels اینستاگرام | ساخته شده با Streamlit و Selenium</p>
</div>
""", unsafe_allow_html=True)

