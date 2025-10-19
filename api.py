"""
دوبله خودکار ویدیو - API سرویس
Auto Video Dubbing - API Service
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
import tempfile
import uuid
import asyncio
from pathlib import Path
import json
import logging
from datetime import datetime

from dubbing_functions import VideoDubbingApp
from config import get_config, get_safety_settings

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ایجاد FastAPI app
app = FastAPI(
    title="🎬 Video Dubbing API",
    description="API سرویس دوبله خودکار ویدیو - Auto Video Dubbing Service API",
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

# مدل‌های Pydantic
class VideoUploadRequest(BaseModel):
    """درخواست آپلود ویدیو"""
    api_key: str = Field(..., description="کلید Google API")
    target_language: str = Field(default="Persian (FA)", description="زبان مقصد")
    voice: str = Field(default="Fenrir", description="گوینده")
    speech_prompt: Optional[str] = Field(default="", description="پرامپت لحن صدا")
    keep_original_audio: bool = Field(default=False, description="حفظ صدای اصلی")
    original_audio_volume: float = Field(default=0.3, description="حجم صدای اصلی")
    enable_compression: bool = Field(default=True, description="فعال‌سازی فشرده‌سازی")
    merge_count: int = Field(default=5, description="تعداد دیالوگ برای ادغام")
    tts_model: str = Field(default="gemini-2.5-flash-preview-tts", description="مدل TTS")
    sleep_between_requests: int = Field(default=30, description="زمان انتظار بین درخواست‌ها")

class YouTubeDownloadRequest(BaseModel):
    """درخواست دانلود از یوتیوب"""
    api_key: str = Field(..., description="کلید Google API")
    youtube_url: str = Field(..., description="لینک ویدیو یوتیوب")
    target_language: str = Field(default="Persian (FA)", description="زبان مقصد")
    voice: str = Field(default="Fenrir", description="گوینده")
    speech_prompt: Optional[str] = Field(default="", description="پرامپت لحن صدا")
    keep_original_audio: bool = Field(default=False, description="حفظ صدای اصلی")
    original_audio_volume: float = Field(default=0.3, description="حجم صدای اصلی")
    enable_compression: bool = Field(default=True, description="فعال‌سازی فشرده‌سازی")
    merge_count: int = Field(default=5, description="تعداد دیالوگ برای ادغام")
    tts_model: str = Field(default="gemini-2.5-flash-preview-tts", description="مدل TTS")
    sleep_between_requests: int = Field(default=30, description="زمان انتظار بین درخواست‌ها")
    extraction_method: str = Field(default="whisper", description="روش استخراج متن (whisper/youtube)")

class SubtitleRequest(BaseModel):
    """درخواست ایجاد زیرنویس"""
    api_key: str = Field(..., description="کلید Google API")
    target_language: str = Field(default="Persian (FA)", description="زبان مقصد")
    subtitle_config: Optional[Dict[str, Any]] = Field(default=None, description="تنظیمات زیرنویس")
    fixed_text_config: Optional[Dict[str, Any]] = Field(default=None, description="تنظیمات متن ثابت")

class ProcessStatus(BaseModel):
    """وضعیت پردازش"""
    job_id: str
    status: str  # pending, processing, completed, failed
    progress: int  # 0-100
    current_step: str
    message: str
    created_at: datetime
    updated_at: datetime
    result: Optional[Dict[str, Any]] = None

# ذخیره‌سازی وضعیت‌های پردازش
processing_jobs: Dict[str, ProcessStatus] = {}

# ذخیره‌سازی instance های دوبله
dubbing_instances: Dict[str, VideoDubbingApp] = {}

def get_dubbing_app(api_key: str, youtube_api_key: str = None) -> VideoDubbingApp:
    """دریافت یا ایجاد instance دوبله"""
    if api_key not in dubbing_instances:
        dubbing_instances[api_key] = VideoDubbingApp(api_key, youtube_api_key)
    return dubbing_instances[api_key]

def create_job_status(job_id: str, status: str, current_step: str, message: str) -> ProcessStatus:
    """ایجاد وضعیت کار"""
    now = datetime.now()
    return ProcessStatus(
        job_id=job_id,
        status=status,
        progress=0,
        current_step=current_step,
        message=message,
        created_at=now,
        updated_at=now
    )

def update_job_status(job_id: str, status: str = None, progress: int = None, 
                     current_step: str = None, message: str = None, result: Dict = None):
    """به‌روزرسانی وضعیت کار"""
    if job_id in processing_jobs:
        job = processing_jobs[job_id]
        if status is not None:
            job.status = status
        if progress is not None:
            job.progress = progress
        if current_step is not None:
            job.current_step = current_step
        if message is not None:
            job.message = message
        if result is not None:
            job.result = result
        job.updated_at = datetime.now()

async def process_video_workflow(job_id: str, dubbing_app: VideoDubbingApp, 
                                video_path: str, request_data: Dict[str, Any]):
    """پردازش کامل ویدیو"""
    try:
        # مرحله 1: استخراج صدا
        update_job_status(job_id, "processing", 10, "extracting_audio", "استخراج صدا از ویدیو...")
        audio_path = dubbing_app.work_dir / 'audio.wav'
        if not audio_path.exists():
            raise Exception("فایل صوتی یافت نشد")
        
        # مرحله 2: استخراج متن
        update_job_status(job_id, "processing", 20, "extracting_text", "استخراج متن از صدا...")
        success = dubbing_app.extract_audio_with_whisper()
        if not success:
            raise Exception("خطا در استخراج متن")
        
        # مرحله 3: فشرده‌سازی (اختیاری)
        if request_data.get('enable_compression', True):
            update_job_status(job_id, "processing", 30, "compressing", "فشرده‌سازی دیالوگ‌ها...")
            merge_count = request_data.get('merge_count', 5)
            dubbing_app.compress_srt_dialogues(merge_count)
        
        # مرحله 4: ترجمه
        update_job_status(job_id, "processing", 40, "translating", "ترجمه زیرنویس‌ها...")
        target_language = request_data.get('target_language', 'Persian (FA)')
        success = dubbing_app.translate_subtitles(target_language)
        if not success:
            raise Exception("خطا در ترجمه")
        
        # مرحله 5: تولید صدا
        update_job_status(job_id, "processing", 60, "generating_audio", "تولید سگمنت‌های صوتی...")
        voice = request_data.get('voice', 'Fenrir')
        tts_model = request_data.get('tts_model', 'gemini-2.5-flash-preview-tts')
        speech_prompt = request_data.get('speech_prompt', '')
        sleep_time = request_data.get('sleep_between_requests', 30)
        
        success = dubbing_app.create_audio_segments(
            voice=voice,
            model=tts_model,
            speech_prompt=speech_prompt,
            sleep_between_requests=sleep_time
        )
        if not success:
            raise Exception("خطا در تولید صدا")
        
        # مرحله 6: ایجاد ویدیو نهایی
        update_job_status(job_id, "processing", 80, "creating_video", "ایجاد ویدیو نهایی...")
        keep_original_audio = request_data.get('keep_original_audio', False)
        original_audio_volume = request_data.get('original_audio_volume', 0.3)
        
        output_path = dubbing_app.create_final_video(
            keep_original_audio=keep_original_audio,
            original_audio_volume=original_audio_volume
        )
        
        if not output_path or not os.path.exists(output_path):
            raise Exception("خطا در ایجاد ویدیو نهایی")
        
        # تکمیل کار
        update_job_status(
            job_id, 
            "completed", 
            100, 
            "completed", 
            "ویدیو با موفقیت دوبله شد",
            {
                "output_path": output_path,
                "file_name": os.path.basename(output_path),
                "file_size": os.path.getsize(output_path),
                "video_duration": "N/A"  # می‌توانید از ffprobe استفاده کنید
            }
        )
        
    except Exception as e:
        logger.error(f"خطا در پردازش ویدیو {job_id}: {str(e)}")
        update_job_status(job_id, "failed", 0, "failed", f"خطا: {str(e)}")

# Endpoints اصلی

@app.get("/")
async def root():
    """صفحه اصلی API"""
    return {
        "message": "🎬 Video Dubbing API",
        "version": "1.0.0",
        "description": "API سرویس دوبله خودکار ویدیو",
        "docs": "/docs",
        "endpoints": {
            "upload_video": "POST /upload-video",
            "download_youtube": "POST /download-youtube", 
            "create_subtitles": "POST /create-subtitles",
            "job_status": "GET /job-status/{job_id}",
            "download_result": "GET /download/{job_id}",
            "list_jobs": "GET /jobs",
            "cleanup": "POST /cleanup"
        }
    }

@app.post("/upload-video")
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    api_key: str = Form(...),
    target_language: str = Form(default="Persian (FA)"),
    voice: str = Form(default="Fenrir"),
    speech_prompt: str = Form(default=""),
    keep_original_audio: bool = Form(default=False),
    original_audio_volume: float = Form(default=0.3),
    enable_compression: bool = Form(default=True),
    merge_count: int = Form(default=5),
    tts_model: str = Form(default="gemini-2.5-flash-preview-tts"),
    sleep_between_requests: int = Form(default=30)
):
    """آپلود ویدیو و شروع پردازش"""
    try:
        # ایجاد job ID
        job_id = str(uuid.uuid4())
        
        # ایجاد instance دوبله
        dubbing_app = get_dubbing_app(api_key)
        
        # ذخیره فایل ویدیو
        video_path = dubbing_app.work_dir / f'input_video_{job_id}.mp4'
        with open(video_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # استخراج صدا
        audio_path = dubbing_app.work_dir / 'audio.wav'
        import subprocess
        subprocess.run([
            'ffmpeg', '-i', str(video_path), '-vn', 
            str(audio_path), '-y'
        ], check=True, capture_output=True)
        
        # ایجاد وضعیت کار
        processing_jobs[job_id] = create_job_status(
            job_id, "pending", "uploaded", "ویدیو آپلود شد، در انتظار پردازش..."
        )
        
        # شروع پردازش در پس‌زمینه
        request_data = {
            'target_language': target_language,
            'voice': voice,
            'speech_prompt': speech_prompt,
            'keep_original_audio': keep_original_audio,
            'original_audio_volume': original_audio_volume,
            'enable_compression': enable_compression,
            'merge_count': merge_count,
            'tts_model': tts_model,
            'sleep_between_requests': sleep_between_requests
        }
        
        background_tasks.add_task(process_video_workflow, job_id, dubbing_app, str(video_path), request_data)
        
        return {
            "job_id": job_id,
            "status": "uploaded",
            "message": "ویدیو با موفقیت آپلود شد و پردازش شروع شد",
            "check_status_url": f"/job-status/{job_id}",
            "download_url": f"/download/{job_id}"
        }
        
    except Exception as e:
        logger.error(f"خطا در آپلود ویدیو: {str(e)}")
        raise HTTPException(status_code=500, detail=f"خطا در آپلود ویدیو: {str(e)}")

@app.post("/download-youtube")
async def download_youtube_video(
    background_tasks: BackgroundTasks,
    request: YouTubeDownloadRequest
):
    """دانلود ویدیو از یوتیوب و شروع پردازش"""
    try:
        # ایجاد job ID
        job_id = str(uuid.uuid4())
        
        # ایجاد instance دوبله
        dubbing_app = get_dubbing_app(request.api_key)
        
        # ایجاد وضعیت کار
        processing_jobs[job_id] = create_job_status(
            job_id, "pending", "downloading", "در حال دانلود ویدیو از یوتیوب..."
        )
        
        # شروع پردازش در پس‌زمینه
        request_data = request.dict()
        background_tasks.add_task(process_youtube_workflow, job_id, dubbing_app, request_data)
        
        return {
            "job_id": job_id,
            "status": "downloading",
            "message": "دانلود ویدیو از یوتیوب شروع شد",
            "check_status_url": f"/job-status/{job_id}",
            "download_url": f"/download/{job_id}"
        }
        
    except Exception as e:
        logger.error(f"خطا در دانلود ویدیو: {str(e)}")
        raise HTTPException(status_code=500, detail=f"خطا در دانلود ویدیو: {str(e)}")

async def process_youtube_workflow(job_id: str, dubbing_app: VideoDubbingApp, request_data: Dict[str, Any]):
    """پردازش ویدیو یوتیوب"""
    try:
        # مرحله 1: دانلود ویدیو
        update_job_status(job_id, "processing", 10, "downloading", "دانلود ویدیو از یوتیوب...")
        youtube_url = request_data['youtube_url']
        success = dubbing_app.download_youtube_video(youtube_url)
        if not success:
            raise Exception("خطا در دانلود ویدیو از یوتیوب")
        
        # مرحله 2: استخراج متن
        update_job_status(job_id, "processing", 20, "extracting_text", "استخراج متن...")
        extraction_method = request_data.get('extraction_method', 'whisper')
        
        if extraction_method == 'youtube':
            success = dubbing_app.extract_transcript_from_youtube(youtube_url)
        else:
            success = dubbing_app.extract_audio_with_whisper()
        
        if not success:
            raise Exception("خطا در استخراج متن")
        
        # ادامه پردازش مشابه ویدیو آپلود شده
        await process_video_workflow(job_id, dubbing_app, str(dubbing_app.work_dir / 'input_video.mp4'), request_data)
        
    except Exception as e:
        logger.error(f"خطا در پردازش ویدیو یوتیوب {job_id}: {str(e)}")
        update_job_status(job_id, "failed", 0, "failed", f"خطا: {str(e)}")

@app.post("/create-subtitles")
async def create_subtitled_video(
    background_tasks: BackgroundTasks,
    request: SubtitleRequest
):
    """ایجاد ویدیو با زیرنویس"""
    try:
        # ایجاد job ID
        job_id = str(uuid.uuid4())
        
        # ایجاد instance دوبله
        dubbing_app = get_dubbing_app(request.api_key)
        
        # بررسی وجود فایل‌های لازم
        video_path = dubbing_app.work_dir / 'input_video.mp4'
        srt_path = dubbing_app.work_dir / 'audio_fa.srt'
        
        if not video_path.exists():
            raise HTTPException(status_code=400, detail="فایل ویدیو یافت نشد. ابتدا ویدیو را آپلود یا دانلود کنید.")
        
        if not srt_path.exists():
            raise HTTPException(status_code=400, detail="فایل زیرنویس یافت نشد. ابتدا ویدیو را پردازش کنید.")
        
        # ایجاد وضعیت کار
        processing_jobs[job_id] = create_job_status(
            job_id, "pending", "creating_subtitles", "ایجاد ویدیو با زیرنویس..."
        )
        
        # شروع پردازش در پس‌زمینه
        background_tasks.add_task(process_subtitle_workflow, job_id, dubbing_app, request.dict())
        
        return {
            "job_id": job_id,
            "status": "creating_subtitles",
            "message": "ایجاد ویدیو با زیرنویس شروع شد",
            "check_status_url": f"/job-status/{job_id}",
            "download_url": f"/download/{job_id}"
        }
        
    except Exception as e:
        logger.error(f"خطا در ایجاد زیرنویس: {str(e)}")
        raise HTTPException(status_code=500, detail=f"خطا در ایجاد زیرنویس: {str(e)}")

async def process_subtitle_workflow(job_id: str, dubbing_app: VideoDubbingApp, request_data: Dict[str, Any]):
    """پردازش زیرنویس"""
    try:
        update_job_status(job_id, "processing", 50, "creating_subtitles", "ایجاد ویدیو با زیرنویس...")
        
        subtitle_config = request_data.get('subtitle_config')
        fixed_text_config = request_data.get('fixed_text_config')
        
        output_path = dubbing_app.create_subtitled_video(
            subtitle_config=subtitle_config,
            fixed_text_config=fixed_text_config
        )
        
        if not output_path or not os.path.exists(output_path):
            raise Exception("خطا در ایجاد ویدیو با زیرنویس")
        
        update_job_status(
            job_id, 
            "completed", 
            100, 
            "completed", 
            "ویدیو با زیرنویس با موفقیت ایجاد شد",
            {
                "output_path": output_path,
                "file_name": os.path.basename(output_path),
                "file_size": os.path.getsize(output_path)
            }
        )
        
    except Exception as e:
        logger.error(f"خطا در پردازش زیرنویس {job_id}: {str(e)}")
        update_job_status(job_id, "failed", 0, "failed", f"خطا: {str(e)}")

@app.get("/job-status/{job_id}")
async def get_job_status(job_id: str):
    """دریافت وضعیت کار"""
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="کار یافت نشد")
    
    job = processing_jobs[job_id]
    return {
        "job_id": job.job_id,
        "status": job.status,
        "progress": job.progress,
        "current_step": job.current_step,
        "message": job.message,
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat(),
        "result": job.result
    }

@app.get("/download/{job_id}")
async def download_result(job_id: str):
    """دانلود نتیجه کار"""
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="کار یافت نشد")
    
    job = processing_jobs[job_id]
    
    if job.status != "completed":
        raise HTTPException(status_code=400, detail="کار هنوز تکمیل نشده است")
    
    if not job.result or 'output_path' not in job.result:
        raise HTTPException(status_code=404, detail="فایل نتیجه یافت نشد")
    
    output_path = job.result['output_path']
    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="فایل نتیجه وجود ندارد")
    
    return FileResponse(
        path=output_path,
        filename=job.result.get('file_name', 'output.mp4'),
        media_type='video/mp4'
    )

@app.get("/jobs")
async def list_jobs():
    """لیست تمام کارها"""
    return {
        "jobs": [
            {
                "job_id": job.job_id,
                "status": job.status,
                "progress": job.progress,
                "current_step": job.current_step,
                "created_at": job.created_at.isoformat(),
                "updated_at": job.updated_at.isoformat()
            }
            for job in processing_jobs.values()
        ],
        "total": len(processing_jobs)
    }

@app.post("/cleanup")
async def cleanup_files(api_key: str = Form(...)):
    """پاکسازی فایل‌های موقت"""
    try:
        dubbing_app = get_dubbing_app(api_key)
        dubbing_app.clean_previous_files()
        
        return {
            "message": "فایل‌های موقت پاکسازی شدند",
            "status": "success"
        }
    except Exception as e:
        logger.error(f"خطا در پاکسازی: {str(e)}")
        raise HTTPException(status_code=500, detail=f"خطا در پاکسازی: {str(e)}")

@app.get("/health")
async def health_check():
    """بررسی سلامت سرویس"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_jobs": len([job for job in processing_jobs.values() if job.status == "processing"])
    }

# اجرای سرور
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
