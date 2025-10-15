"""
تنظیمات پیش‌فرض برای برنامه دوبله خودکار ویدیو
Default configuration for Auto Video Dubbing application
"""

# تنظیمات عمومی
DEFAULT_CONFIG = {
    # تنظیمات ویدیو
    "video": {
        "max_duration_minutes": 60,  # حداکثر مدت ویدیو (دقیقه)
        "supported_formats": [".mp4", ".avi", ".mov", ".mkv"],
        "output_format": "mp4",
        "video_quality": "bestvideo+bestaudio/best"
    },
    
    # تنظیمات صدا
    "audio": {
        "sample_rate": 44100,
        "channels": 2,
        "bitrate": "192k",
        "format": "wav"
    },
    
    # تنظیمات Whisper
    "whisper": {
        "model": "base",  # tiny, base, small, medium, large
        "language": None,  # None for auto-detect
        "task": "transcribe"
    },
    
    # تنظیمات ترجمه
    "translation": {
        "models": [
            "gemini-2.5-flash",        # بهترین کیفیت
            "gemini-2.5-flash-lite",   # کیفیت خوب و سریع
            "gemini-flash-lite-latest" # پشتیبان
        ],
        "max_retries": 3,
        "retry_delay": 2,  # seconds
        "rate_limit_delay": 1,  # seconds between requests (کاهش یافته)
        "quality_mode": True  # فعال‌سازی حالت کیفیت بالا
    },
    
    # تنظیمات TTS
    "tts": {
        "models": [
            "gemini-2.5-flash-preview-tts",
            "gemini-2.5-pro-preview-tts"
        ],
        "voices": [
            "Fenrir", "Achird", "Zubenelgenubi", "Vindemiatrix", "Sadachbia",
            "Sadaltager", "Sulafat", "Laomedeia", "Achernar", "Alnilam",
            "Schedar", "Gacrux", "Pulcherrima", "Umbriel", "Algieba",
            "Despina", "Erinome", "Algenib", "Rasalthgeti", "Orus",
            "Aoede", "Callirrhoe", "Autonoe", "Enceladus", "Iapetus",
            "Zephyr", "Puck", "Charon", "Kore", "Leda"
        ],
        "default_voice": "Fenrir",
        "sleep_between_requests": 30,  # افزایش زمان انتظار برای رعایت محدودیت‌ها
        "max_retries": 5,  # افزایش تعداد تلاش‌ها
        "quota_limit_per_day": 15,  # محدودیت روزانه
        "quota_limit_per_minute": 3,  # محدودیت دقیقه‌ای
        "batch_size": 3,  # تعداد سگمنت‌ها در هر batch
        "batch_delay": 60  # تاخیر بین batch ها (ثانیه)
    },
    
    # تنظیمات فشرده‌سازی
    "compression": {
        "enabled": True,
        "default_merge_count": 5,  # افزایش فشرده‌سازی برای کاهش تعداد سگمنت‌ها
        "min_merge_count": 3,
        "max_merge_count": 15,
        "auto_compress": True  # فشرده‌سازی خودکار بر اساس تعداد سگمنت‌ها
    },
    
    # تنظیمات ویدیو نهایی
    "final_video": {
        "keep_original_audio": False,
        "original_audio_volume": 0.3,
        "audio_merge_method": "pydub"  # pydub, ffmpeg_concat, ffmpeg_filter
    },
    
    # تنظیمات رابط کاربری
    "ui": {
        "default_language": "Persian (FA)",
        "supported_languages": [
            "Persian (FA)", "English (EN)", "German (DE)", "French (FR)",
            "Italian (IT)", "Spanish (ES)", "Chinese (ZH)", "Korean (KO)",
            "Russian (RU)", "Arabic (AR)", "Japanese (JA)", "Hindi (HI)"
        ],
        "theme": "light",
        "page_title": "🎬 دوبله خودکار ویدیو",
        "page_icon": "🎬"
    },
    
    # تنظیمات فایل‌ها
    "files": {
        "work_directory": "dubbing_work",
        "segments_directory": "dubbing_work/dubbed_segments",
        "temp_directory": "temp",
        "cleanup_on_exit": True
    },
    
    # تنظیمات لاگ
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "dubbing.log"
    }
}

# تنظیمات ایمنی
SAFETY_SETTINGS = {
    "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
    "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE", 
    "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
    "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE"
}

# تنظیمات FFmpeg
FFMPEG_SETTINGS = {
    "video_codec": "copy",
    "audio_codec": "aac",
    "audio_sample_rate": 44100,
    "audio_channels": 2,
    "audio_bitrate": "192k"
}

# تنظیمات Rubberband
RUBBERBAND_SETTINGS = {
    "min_tempo": 0.5,
    "max_tempo": 2.5,
    "default_tempo": 1.0
}

def get_config():
    """دریافت تنظیمات پیش‌فرض"""
    return DEFAULT_CONFIG.copy()

def get_safety_settings():
    """دریافت تنظیمات ایمنی"""
    return SAFETY_SETTINGS.copy()

def get_ffmpeg_settings():
    """دریافت تنظیمات FFmpeg"""
    return FFMPEG_SETTINGS.copy()

def get_rubberband_settings():
    """دریافت تنظیمات Rubberband"""
    return RUBBERBAND_SETTINGS.copy()
