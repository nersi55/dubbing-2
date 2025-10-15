#!/usr/bin/env python3
"""
تست API دوبله ویدیو
Video Dubbing API Test Script
"""

import requests
import time
import json
import os
from pathlib import Path

class VideoDubbingAPIClient:
    """کلاینت API دوبله ویدیو"""
    
    def __init__(self, base_url="http://localhost:8000", api_key=None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
    
    def health_check(self):
        """بررسی سلامت API"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return None
    
    def upload_video(self, video_path, **kwargs):
        """آپلود ویدیو"""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        if not self.api_key:
            raise ValueError("API key is required")
        
        with open(video_path, 'rb') as f:
            files = {'file': f}
            data = {
                'api_key': self.api_key,
                'target_language': kwargs.get('target_language', 'Persian (FA)'),
                'voice': kwargs.get('voice', 'Fenrir'),
                'speech_prompt': kwargs.get('speech_prompt', ''),
                'keep_original_audio': kwargs.get('keep_original_audio', False),
                'original_audio_volume': kwargs.get('original_audio_volume', 0.3),
                'enable_compression': kwargs.get('enable_compression', True),
                'merge_count': kwargs.get('merge_count', 5),
                'tts_model': kwargs.get('tts_model', 'gemini-2.5-flash-preview-tts'),
                'sleep_between_requests': kwargs.get('sleep_between_requests', 30)
            }
            
            response = self.session.post(f"{self.base_url}/upload-video", files=files, data=data)
            response.raise_for_status()
            return response.json()
    
    def download_youtube(self, youtube_url, **kwargs):
        """دانلود از یوتیوب"""
        if not self.api_key:
            raise ValueError("API key is required")
        
        data = {
            'api_key': self.api_key,
            'youtube_url': youtube_url,
            'target_language': kwargs.get('target_language', 'Persian (FA)'),
            'voice': kwargs.get('voice', 'Fenrir'),
            'speech_prompt': kwargs.get('speech_prompt', ''),
            'keep_original_audio': kwargs.get('keep_original_audio', False),
            'original_audio_volume': kwargs.get('original_audio_volume', 0.3),
            'enable_compression': kwargs.get('enable_compression', True),
            'merge_count': kwargs.get('merge_count', 5),
            'tts_model': kwargs.get('tts_model', 'gemini-2.5-flash-preview-tts'),
            'sleep_between_requests': kwargs.get('sleep_between_requests', 30),
            'extraction_method': kwargs.get('extraction_method', 'whisper')
        }
        
        response = self.session.post(f"{self.base_url}/download-youtube", json=data)
        response.raise_for_status()
        return response.json()
    
    def create_subtitles(self, **kwargs):
        """ایجاد زیرنویس"""
        if not self.api_key:
            raise ValueError("API key is required")
        
        data = {
            'api_key': self.api_key,
            'target_language': kwargs.get('target_language', 'Persian (FA)'),
            'subtitle_config': kwargs.get('subtitle_config'),
            'fixed_text_config': kwargs.get('fixed_text_config')
        }
        
        response = self.session.post(f"{self.base_url}/create-subtitles", json=data)
        response.raise_for_status()
        return response.json()
    
    def get_job_status(self, job_id):
        """دریافت وضعیت کار"""
        response = self.session.get(f"{self.base_url}/job-status/{job_id}")
        response.raise_for_status()
        return response.json()
    
    def download_result(self, job_id, output_path):
        """دانلود نتیجه"""
        response = self.session.get(f"{self.base_url}/download/{job_id}")
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        return True
    
    def list_jobs(self):
        """لیست کارها"""
        response = self.session.get(f"{self.base_url}/jobs")
        response.raise_for_status()
        return response.json()
    
    def cleanup(self):
        """پاکسازی فایل‌ها"""
        if not self.api_key:
            raise ValueError("API key is required")
        
        data = {'api_key': self.api_key}
        response = self.session.post(f"{self.base_url}/cleanup", data=data)
        response.raise_for_status()
        return response.json()
    
    def wait_for_completion(self, job_id, check_interval=10, max_wait_time=3600):
        """انتظار برای تکمیل کار"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            status = self.get_job_status(job_id)
            
            print(f"📊 Status: {status['status']} | Progress: {status['progress']}% | Step: {status['current_step']}")
            print(f"💬 Message: {status['message']}")
            
            if status['status'] == 'completed':
                print("✅ Job completed successfully!")
                return status
            elif status['status'] == 'failed':
                print(f"❌ Job failed: {status['message']}")
                return status
            
            time.sleep(check_interval)
        
        print("⏰ Timeout waiting for job completion")
        return None

def main():
    """تابع اصلی تست"""
    print("🎬 Video Dubbing API Test")
    print("=" * 50)
    
    # تنظیمات
    API_KEY = input("Enter your Google API key: ").strip()
    if not API_KEY:
        print("❌ API key is required!")
        return
    
    # ایجاد کلاینت
    client = VideoDubbingAPIClient(api_key=API_KEY)
    
    # بررسی سلامت API
    print("🔍 Checking API health...")
    health = client.health_check()
    if not health:
        print("❌ API is not accessible. Make sure the server is running.")
        return
    
    print(f"✅ API is healthy: {health}")
    
    # منوی تست
    while True:
        print("\n" + "=" * 50)
        print("Select test option:")
        print("1. Upload video file")
        print("2. Download from YouTube")
        print("3. Create subtitles")
        print("4. Check job status")
        print("5. List all jobs")
        print("6. Cleanup files")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        try:
            if choice == "1":
                # آپلود ویدیو
                video_path = input("Enter video file path: ").strip()
                if not os.path.exists(video_path):
                    print("❌ File not found!")
                    continue
                
                print("📤 Uploading video...")
                result = client.upload_video(video_path)
                print(f"✅ Upload successful! Job ID: {result['job_id']}")
                
                # انتظار برای تکمیل
                wait = input("Wait for completion? (y/n): ").strip().lower()
                if wait == 'y':
                    final_status = client.wait_for_completion(result['job_id'])
                    if final_status and final_status['status'] == 'completed':
                        output_path = f"output_{result['job_id']}.mp4"
                        print(f"📥 Downloading result to {output_path}...")
                        client.download_result(result['job_id'], output_path)
                        print(f"✅ Video saved as {output_path}")
            
            elif choice == "2":
                # دانلود از یوتیوب
                youtube_url = input("Enter YouTube URL: ").strip()
                if not youtube_url:
                    print("❌ URL is required!")
                    continue
                
                print("📥 Downloading from YouTube...")
                result = client.download_youtube(youtube_url)
                print(f"✅ Download started! Job ID: {result['job_id']}")
                
                # انتظار برای تکمیل
                wait = input("Wait for completion? (y/n): ").strip().lower()
                if wait == 'y':
                    final_status = client.wait_for_completion(result['job_id'])
                    if final_status and final_status['status'] == 'completed':
                        output_path = f"output_{result['job_id']}.mp4"
                        print(f"📥 Downloading result to {output_path}...")
                        client.download_result(result['job_id'], output_path)
                        print(f"✅ Video saved as {output_path}")
            
            elif choice == "3":
                # ایجاد زیرنویس
                print("📝 Creating subtitled video...")
                result = client.create_subtitles()
                print(f"✅ Subtitle creation started! Job ID: {result['job_id']}")
                
                # انتظار برای تکمیل
                wait = input("Wait for completion? (y/n): ").strip().lower()
                if wait == 'y':
                    final_status = client.wait_for_completion(result['job_id'])
                    if final_status and final_status['status'] == 'completed':
                        output_path = f"subtitled_{result['job_id']}.mp4"
                        print(f"📥 Downloading result to {output_path}...")
                        client.download_result(result['job_id'], output_path)
                        print(f"✅ Video saved as {output_path}")
            
            elif choice == "4":
                # بررسی وضعیت کار
                job_id = input("Enter job ID: ").strip()
                if not job_id:
                    print("❌ Job ID is required!")
                    continue
                
                status = client.get_job_status(job_id)
                print(f"📊 Job Status: {json.dumps(status, indent=2, ensure_ascii=False)}")
            
            elif choice == "5":
                # لیست کارها
                jobs = client.list_jobs()
                print(f"📋 Total jobs: {jobs['total']}")
                for job in jobs['jobs']:
                    print(f"  - {job['job_id']}: {job['status']} ({job['progress']}%)")
            
            elif choice == "6":
                # پاکسازی
                confirm = input("Are you sure you want to cleanup files? (y/n): ").strip().lower()
                if confirm == 'y':
                    result = client.cleanup()
                    print(f"✅ {result['message']}")
            
            elif choice == "7":
                # خروج
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice!")
        
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
