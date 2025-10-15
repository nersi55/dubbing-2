# 🎬 API دوبله خودکار ویدیو - ققنوس شانس

## 📋 توضیحات
این API برای تبدیل ویدیوهای یوتیوب به فارسی با زیرنویس سفارشی طراحی شده است. تمام تنظیمات طبق درخواست شما به صورت پیش‌فرض تنظیم شده‌اند.

## 🚀 نصب و اجرا

### 1. نصب وابستگی‌ها
```bash
pip install -r requirements_api.txt
```

### 2. اجرای API
```bash
python run_api.py
```

یا

```bash
uvicorn api_simple:app --host 127.0.0.1 --port 8002 --reload
```

## 🔗 آدرس‌های دسترسی

- **API اصلی:** http://127.0.0.1:8002
- **مستندات Swagger:** http://127.0.0.1:8002/docs
- **مستندات ReDoc:** http://127.0.0.1:8002/redoc

## 📡 Endpoints

### 1. شروع پردازش ویدیو
```http
POST /process
Content-Type: application/json

{
  "url": "https://youtube.com/watch?v=VIDEO_ID"
}
```

**پاسخ:**
```json
{
  "task_id": "uuid-string",
  "status": "processing",
  "progress": 0,
  "message": "شروع پردازش...",
  "download_url": null,
  "error": null
}
```

### 2. بررسی وضعیت پردازش
```http
GET /status/{task_id}
```

**پاسخ:**
```json
{
  "task_id": "uuid-string",
  "status": "processing|completed|failed",
  "progress": 50,
  "message": "در حال ترجمه زیرنویس‌ها...",
  "download_url": "/download/uuid-string",
  "error": null
}
```

### 3. دانلود ویدیو
```http
GET /download/{task_id}
```

**پاسخ:** فایل ویدیو MP4

### 4. بررسی وضعیت API
```http
GET /health
```

**پاسخ:**
```json
{
  "status": "healthy",
  "google_ai_connected": true,
  "timestamp": 1234567890.123
}
```

### 5. لیست تمام task ها
```http
GET /tasks
```

### 6. حذف task
```http
DELETE /tasks/{task_id}
```

### 7. دریافت تنظیمات
```http
GET /config
```

## ⚙️ تنظیمات ثابت

### 🔑 کلید Google API
- **مقدار:** `AIzaSyBNYpugB8Ezrpmk-U7Yvp9ynClEJLCETMo`

### 📺 روش آپلود
- **نوع:** یوتیوب

### 🌐 زبان مقصد
- **زبان:** فارسی

### 📝 تنظیمات فشرده‌سازی
- **وضعیت:** غیرفعال

### 🔍 استخراج متن
- **روش:** Whisper

### 📝 نوع خروجی
- **نوع:** زیرنویس ترجمه شده

### 🎨 تنظیمات زیرنویس
- **فونت:** vazirmatn
- **اندازه:** 14px
- **رنگ:** سفید
- **زمینه:** سیاه
- **حاشیه:** 0px سیاه
- **موقعیت:** پایین وسط

### 📌 تنظیمات متن ثابت پایین
- **متن:** "ترجمه و زیرنویس ققنوس شانس"
- **فونت:** vazirmatn
- **اندازه:** 9px
- **رنگ:** زرد
- **موقعیت:** پایین وسط
- **شفافیت:** 1.0
- **ضخیم:** بله

## 🔄 مراحل پردازش

1. **📥 دانلود ویدیو:** ویدیو از یوتیوب دانلود می‌شود
2. **🔍 استخراج متن:** متن با Whisper استخراج می‌شود
3. **🌐 ترجمه:** زیرنویس‌ها به فارسی ترجمه می‌شوند
4. **🎬 ایجاد ویدیو:** ویدیو نهایی با زیرنویس سفارشی ایجاد می‌شود

## 📱 مثال استفاده

### Python
```python
import requests
import time

# شروع پردازش
response = requests.post("http://127.0.0.1:8002/process", json={
    "url": "https://youtube.com/watch?v=VIDEO_ID"
})
task = response.json()
task_id = task["task_id"]

# بررسی وضعیت
while True:
    status_response = requests.get(f"http://127.0.0.1:8002/status/{task_id}")
    status = status_response.json()
    
    if status["status"] == "completed":
        # دانلود ویدیو
        download_response = requests.get(f"http://127.0.0.1:8002/download/{task_id}")
        with open("output.mp4", "wb") as f:
            f.write(download_response.content)
        break
    elif status["status"] == "failed":
        print(f"خطا: {status['error']}")
        break
    
    print(f"پیشرفت: {status['progress']}% - {status['message']}")
    time.sleep(5)
```

### JavaScript
```javascript
// شروع پردازش
const response = await fetch('http://127.0.0.1:8001/process', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        url: 'https://youtube.com/watch?v=VIDEO_ID'
    })
});

const task = await response.json();
const taskId = task.task_id;

// بررسی وضعیت
const checkStatus = async () => {
    const statusResponse = await fetch(`http://127.0.0.1:8001/status/${taskId}`);
    const status = await statusResponse.json();
    
    if (status.status === 'completed') {
        // دانلود ویدیو
        window.open(`http://127.0.0.1:8001/download/${taskId}`);
    } else if (status.status === 'failed') {
        console.error('خطا:', status.error);
    } else {
        console.log(`پیشرفت: ${status.progress}% - ${status.message}`);
        setTimeout(checkStatus, 5000);
    }
};

checkStatus();
```

### cURL
```bash
# شروع پردازش
curl -X POST "http://127.0.0.1:8002/process" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://youtube.com/watch?v=VIDEO_ID"}'

# بررسی وضعیت
curl "http://127.0.0.1:8002/status/TASK_ID"

# دانلود ویدیو
curl "http://127.0.0.1:8002/download/TASK_ID" -o output.mp4
```

## ⚠️ نکات مهم

- **اینترنت:** اتصال اینترنت برای دانلود ویدیو و استفاده از API لازم است
- **مدت زمان:** پردازش ویدیوهای طولانی ممکن است چند دقیقه طول بکشد
- **کیفیت:** کیفیت خروجی بستگی به کیفیت ویدیو اصلی دارد
- **محدودیت API:** Google API محدودیت‌هایی دارد که باید رعایت شود
- **Background Processing:** پردازش در background انجام می‌شود
- **Task Management:** هر task یک ID منحصر به فرد دارد

## 🛠️ نیازمندی‌ها

- Python 3.8+
- FastAPI
- Uvicorn
- کتابخانه‌های Python (در `requirements_api.txt`)

## 📞 پشتیبانی

در صورت بروز مشکل، لطفاً با تیم ققنوس شانس تماس بگیرید.

---
**🎬 دوبله خودکار ویدیو API - ققنوس شانس**