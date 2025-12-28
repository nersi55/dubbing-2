from sheets_logger import GoogleSheetsLogger
import time

def test_logging():
    print("🚀 Starting Google Sheets logging test...")
    logger = GoogleSheetsLogger()
    
    t = int(time.time())
    mp4 = f"https://site.com/video_{t}.mp4"
    en_srt = f"https://site.com/en_{t}.srt"
    fa_srt = f"https://site.com/fa_{t}.srt"
    
    print(f"📡 Attempting to log triple URLs for timestamp {t}...")
    success = logger.log_upload_triple(mp4, en_srt, fa_srt)
    
    if success:
        print("✅ Test PASSED: URL logged successfully.")
    else:
        print("❌ Test FAILED: Could not log URL.")

if __name__ == "__main__":
    test_logging()
