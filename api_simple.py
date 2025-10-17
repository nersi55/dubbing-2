"""
API ساده دوبله خودکار ویدیو - فقط آدرس YouTube
Simple Auto Video Dubbing API - YouTube URL Only
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import os
import tempfile
import subprocess
import random
import string
import uuid
from pathlib import Path
from dubbing_functions import VideoDubbingApp
from typing import Optional
import asyncio
import threading
import time

# تنظیمات API
app = FastAPI(
    title="🎬 دوبله خودکار ویدیو API - ققنوس شانس",
    description="API برای تبدیل ویدیوهای یوتیوب به فارسی با زیرنویس سفارشی",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تنظیمات ثابت
API_KEY = "AIzaSyBNYpugB8Ezrpmk-U7Yvp9ynClEJLCETMo"
TARGET_LANGUAGE = "Persian (FA)"
VOICE = "Fenrir"
ENABLE_COMPRESSION = False
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

# مدل‌های Pydantic
class YouTubeRequest(BaseModel):
    url: HttpUrl
    description: str = "آدرس ویدیو یوتیوب برای دوبله و زیرنویس"

class ProcessingStatus(BaseModel):
    task_id: str
    status: str  # "processing", "completed", "failed"
    progress: int  # 0-100
    message: str
    download_url: Optional[str] = None
    error: Optional[str] = None

# ذخیره وضعیت پردازش
processing_tasks = {}

# ایجاد instance از کلاس دوبله
try:
    dubbing_app = VideoDubbingApp(API_KEY)
    print("✅ اتصال به Google AI برقرار شد")
except Exception as e:
    print(f"❌ خطا در اتصال به Google AI: {str(e)}")
    dubbing_app = None

def generate_random_filename():
    """تولید نام فایل رندم"""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"dubbed_video_{random_suffix}.mp4"

def process_video_task(task_id: str, youtube_url: str):
    """پردازش ویدیو در background"""
    try:
        processing_tasks[task_id]["status"] = "processing"
        processing_tasks[task_id]["progress"] = 10
        processing_tasks[task_id]["message"] = "در حال دانلود ویدیو..."
        
        # مرحله 1: دانلود ویدیو
        success = dubbing_app.download_youtube_video(str(youtube_url))
        if not success:
            raise Exception("خطا در دانلود ویدیو")
        
        processing_tasks[task_id]["progress"] = 30
        processing_tasks[task_id]["message"] = "در حال استخراج متن..."
        
        # مرحله 2: استخراج متن با Whisper
        success = dubbing_app.extract_audio_with_whisper()
        if not success:
            raise Exception("خطا در استخراج متن")
        
        processing_tasks[task_id]["progress"] = 50
        processing_tasks[task_id]["message"] = "در حال ترجمه زیرنویس‌ها..."
        
        # مرحله 3: ترجمه
        success = dubbing_app.translate_subtitles(TARGET_LANGUAGE)
        if not success:
            raise Exception("خطا در ترجمه")
        
        processing_tasks[task_id]["progress"] = 70
        processing_tasks[task_id]["message"] = "در حال ایجاد ویدیو با زیرنویس..."
        
        # مرحله 4: ایجاد ویدیو با زیرنویس
        random_filename = generate_random_filename()
        
        # تغییر نام فایل خروجی
        original_create_method = dubbing_app.create_subtitled_video
        def create_with_random_name(subtitle_config=None, fixed_text_config=None):
            result = original_create_method(subtitle_config, fixed_text_config)
            if result and os.path.exists(result):
                new_path = dubbing_app.work_dir / random_filename
                os.rename(result, str(new_path))
                return str(new_path)
            return result
        
        dubbing_app.create_subtitled_video = create_with_random_name
        
        output_path = dubbing_app.create_subtitled_video(
            subtitle_config=SUBTITLE_CONFIG,
            fixed_text_config=FIXED_TEXT_CONFIG
        )
        
        dubbing_app.create_subtitled_video = original_create_method
        
        if output_path and os.path.exists(output_path):
            processing_tasks[task_id]["status"] = "completed"
            processing_tasks[task_id]["progress"] = 100
            processing_tasks[task_id]["message"] = "ویدیو با موفقیت ایجاد شد"
            processing_tasks[task_id]["download_url"] = f"/download/{task_id}"
        else:
            raise Exception("خطا در ایجاد ویدیو")
            
    except Exception as e:
        processing_tasks[task_id]["status"] = "failed"
        processing_tasks[task_id]["error"] = str(e)
        processing_tasks[task_id]["message"] = f"خطا: {str(e)}"

@app.get("/", response_class=JSONResponse)
async def root():
    """صفحه اصلی API"""
    return {
        "message": "🎬 دوبله خودکار ویدیو API - ققنوس شانس",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "start_processing": "POST /process",
            "check_status": "GET /status/{task_id}",
            "download": "GET /download/{task_id}",
            "health": "GET /health"
        }
    }

@app.get("/health")
async def health_check():
    """بررسی وضعیت API"""
    return {
        "status": "healthy",
        "google_ai_connected": dubbing_app is not None,
        "timestamp": time.time()
    }

@app.post("/process", response_model=ProcessingStatus)
async def start_processing(request: YouTubeRequest, background_tasks: BackgroundTasks):
    """شروع پردازش ویدیو"""
    if not dubbing_app:
        raise HTTPException(status_code=500, detail="Google AI API در دسترس نیست")
    
    # ایجاد task ID منحصر به فرد
    task_id = str(uuid.uuid4())
    
    # مقداردهی اولیه وضعیت
    processing_tasks[task_id] = {
        "task_id": task_id,
        "status": "processing",
        "progress": 0,
        "message": "شروع پردازش...",
        "download_url": None,
        "error": None
    }
    
    # شروع پردازش در background
    background_tasks.add_task(process_video_task, task_id, request.url)
    
    return ProcessingStatus(**processing_tasks[task_id])

@app.get("/status/{task_id}", response_model=ProcessingStatus)
async def get_status(task_id: str):
    """بررسی وضعیت پردازش"""
    if task_id not in processing_tasks:
        raise HTTPException(status_code=404, detail="Task یافت نشد")
    
    return ProcessingStatus(**processing_tasks[task_id])

@app.get("/download/{task_id}")
async def download_video(task_id: str):
    """دانلود ویدیو پردازش شده"""
    if task_id not in processing_tasks:
        raise HTTPException(status_code=404, detail="Task یافت نشد")
    
    task = processing_tasks[task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="ویدیو هنوز آماده نیست")
    
    # پیدا کردن فایل ویدیو
    work_dir = dubbing_app.work_dir
    video_files = list(work_dir.glob("dubbed_video_*.mp4"))
    
    if not video_files:
        raise HTTPException(status_code=404, detail="فایل ویدیو یافت نشد")
    
    # جدیدترین فایل
    latest_video = max(video_files, key=os.path.getctime)
    
    return FileResponse(
        path=str(latest_video),
        filename=latest_video.name,
        media_type="video/mp4"
    )

@app.get("/tasks")
async def list_tasks():
    """لیست تمام task ها"""
    return {
        "tasks": list(processing_tasks.values()),
        "total": len(processing_tasks)
    }

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """حذف task"""
    if task_id not in processing_tasks:
        raise HTTPException(status_code=404, detail="Task یافت نشد")
    
    del processing_tasks[task_id]
    return {"message": "Task حذف شد"}

@app.get("/config")
async def get_config():
    """دریافت تنظیمات API"""
    return {
        "subtitle_config": SUBTITLE_CONFIG,
        "fixed_text_config": FIXED_TEXT_CONFIG,
        "target_language": TARGET_LANGUAGE,
        "voice": VOICE,
        "compression_enabled": ENABLE_COMPRESSION,
        "extraction_method": EXTRACTION_METHOD,
        "output_type": OUTPUT_TYPE
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 در حال اجرای API دوبله خودکار ویدیو...")
    print("📱 API در آدرس: http://127.0.0.1:8002")
    print("📚 مستندات: http://127.0.0.1:8002/docs")
    print("⏹️  برای توقف: Ctrl+C")
    print("-" * 50)
    
    uvicorn.run(
        "api_simple:app",
        # host="127.0.0.1",
        host="0.0.0.0",
        port=8003,
        reload=False,
        log_level="info"
    )
