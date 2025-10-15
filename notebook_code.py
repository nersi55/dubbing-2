# Auto-extracted from the original notebook. You may refine this file to better structure functions.
# The original notebook's code is kept as-is below, separated by cell comments.

# --- Cell 1 ---

#@title نصب کتابخانه‌ها
import base64

encoded_text = "Q3JlYXRlIGJ5IDogYWlnb2xkZW4="
decoded_text = base64.b64decode(encoded_text.encode()).decode()
print(decoded_text)
print("="*20)

print("📦 Installing Python libraries...")

# [removed_magic] !pip install google-genai yt-dlp pysrt pydub youtube-transcript-api git+https://github.com/yaranbarzi/stable-ts.git

print("\n🔧 Installing system tools...")

# [removed_magic] !sudo apt-get update -y
# [removed_magic] !sudo apt-get install -y ffmpeg rubberband-cli

print("\n✅ All dependencies installed successfully!")

# --- Cell 2 ---

#@title آپلود ویدیو از یوتیوب یا حافظه داخلی
#@markdown ### `در صورتی که دانلود از یوتیوب ناموفق بود کوکی های مرورگر را قبل از اجرا پاک کنید`
# [removed_magic] from google.colab import files
from IPython.display import display
import ipywidgets as widgets
import yt_dlp
import os
import shutil
import glob

# پاکسازی فایل‌های قبلی
for file in glob.glob('input_video*'):
    os.remove(file)
    print(f"فایل ویدیوی قبلی {file} حذف شد.")
if os.path.exists('audio.wav'):
    os.remove('audio.wav')
    print("فایل صوتی قبلی حذف شد.")
if os.path.exists('audio.srt'):
    os.remove('audio.srt')
    print("فایل زیرنویس قبلی حذف شد.")
if os.path.exists('dubbing_project'):
    shutil.rmtree('dubbing_project')
    print("پوشه پروژه دوبله قبلی حذف شد.")

upload_method = "یوتیوب" #@param ["یوتیوب", "حافظه داخلی"]
#@markdown ---
#@markdown #### اگر «یوتیوب» را انتخاب کردید، لینک را اینجا وارد کنید:
YT_Link = "https://youtube.com/shorts/CVtRmmFrSL0?si=4VGwYzRntFbeFVKd" #@param {type:"string"}
os.environ['YT_Link'] = YT_Link

def process_youtube(url):
    if url.strip():
        for file in glob.glob('temp_video*'):
            if os.path.exists(file):
                os.remove(file)

        # دانلود ویدیو با بالاترین کیفیت
        format_option = 'bestvideo+bestaudio/best'
        temp_filename = 'temp_video.%(ext)s'
        video_opts = {
            'format': format_option,
            'outtmpl': temp_filename,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'no_warnings': False,
            'quiet': False
        }

        try:
            with yt_dlp.YoutubeDL(video_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)

            print(f"فایل دانلود شده: {downloaded_file}")

            if os.path.exists(downloaded_file):
                _, file_extension = os.path.splitext(downloaded_file)
                final_filename = 'input_video' + file_extension
                os.rename(downloaded_file, final_filename)
                print(f"نام فایل به {final_filename} تغییر یافت")

                if file_extension.lower() != '.mp4':
                    os.system(f'ffmpeg -i "{final_filename}" -c copy input_video.mp4 -y')
                    if os.path.exists('input_video.mp4'):
                        os.remove(final_filename)
                        print("فایل به فرمت MP4 تبدیل شد")

                os.system('ffmpeg -i input_video.mp4 -vn audio.wav -y')
                print("صدا از ویدیو استخراج شد.")
                return True
            else:
                print("فایل دانلود شده یافت نشد.")
                return False
        except Exception as e:
            print(f"خطا در دانلود: {str(e)}")
            return False
    return False

if upload_method == "یوتیوب" and YT_Link.strip():
    print("در حال دانلود ویدیو با بالاترین کیفیت...")
    success = process_youtube(YT_Link)
    if success:
        print("ویدیو با موفقیت دانلود شد.")
    else:
        print("دانلود ناموفق بود.")
elif upload_method == "حافظه داخلی":
    print("لطفاً ویدیوی خود را آپلود کنید:")
    uploaded = files.upload()
    video_file = next(iter(uploaded.keys()))
    os.rename(video_file, 'input_video.mp4')
    os.system(f'ffmpeg -i "input_video.mp4" -vn audio.wav -y')
    print("ویدیو آپلود و فایل صوتی استخراج شد.")

if os.path.exists('input_video.mp4'):
    print("\nعملیات آپلود و آماده‌سازی ویدیو با موفقیت انجام شد!")
else:
    print("\nخطا: فایل ویدیویی 'input_video.mp4' ایجاد نشد. لطفاً لینک یا فایل خود را بررسی کنید.")

# --- Cell 3 ---

#@title ورود و پیکربندی کلید
import google.generativeai as genai
import os

#@markdown ---
#@markdown ### **کلید دسترسی جمینای خود را اینجا وارد کنید**
#@markdown این کلید برای تمام بخش‌های نوتبوک (ترجمه و تولید صدا) استفاده خواهد شد.
GOOGLE_API_KEY = "AIzaSyCaybkGZbMN0SwLrLCtp864MqHhYU2VUhw" #@param {type:"string"}

if not GOOGLE_API_KEY or "YOUR_API_KEY" in GOOGLE_API_KEY:
    print(" هشدار: لطفاً کلید API معتبر خود را وارد کرده و سپس سلول را اجرا کنید.")
else:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)

        os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY
        print(" کلید API با موفقیت برای استفاده در کل نوتبوک پیکربندی شد.")
    except Exception as e:
        print(f" خطا در پیکربندی کلید API: {e}")

# --- Cell 4 ---


#@title استخراج متن از فایل صوتی
# [removed_magic] from google.colab import files
import os
import pysrt
import subprocess
import re
import json
from youtube_transcript_api import YouTubeTranscriptApi

extraction_method = "Whisper" #@param ["Whisper", "آپلود زیرنویس", "Transcript"]
transcript_language = "Auto-detect" #@param ["Auto-detect", "English (EN)", "Persian (FA)", "German (DE)", "French (FR)", "Italian (IT)", "Spanish (ES)", "Chinese (ZH)", "Korean (KO)", "Russian (RU)", "Arabic (AR)", "Japanese (JA)", "Hindi (HI)"]

if extraction_method == "Whisper":
    if os.path.exists('audio.wav'):
# [removed_magic]         !whisper "audio.wav" --model large --output_dir ./ --output_format srt
        os.rename("audio.srt", "audio.srt")  # اطمینان از نام فایل صحیح
    else:
        print("لطفاً ابتدا یک فایل صوتی آپلود کنید.")

elif extraction_method == "Transcript":
    # بررسی وجود فایل و شرایط لازم
    if not os.path.exists('input_video.mp4'):
        print("فایل ویدیویی یافت نشد! لطفاً ابتدا یک ویدیو از یوتیوب دانلود کنید.")
    else:
        # دریافت لینک یوتیوب از متغیر محیطی
        youtube_url = os.environ.get('YT_Link', '')

        if not youtube_url:
            print("لینک یوتیوب یافت نشد! لطفاً در سلول آپلود، یک لینک معتبر وارد کنید.")
        else:
            print(f"در حال استخراج زیرنویس از ویدیوی یوتیوب با لینک: {youtube_url}")

            # استخراج شناسه ویدیوی یوتیوب
            video_id = None
            patterns = [
                r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})',
                r'(?:youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})'
            ]

            for pattern in patterns:
                match = re.search(pattern, youtube_url)
                if match:
                    video_id = match.group(1)
                    break

            if not video_id:
                if 'shorts/' in youtube_url:
                    shorts_id = youtube_url.split('shorts/')[1].split('?')[0].split('&')[0]
                    if len(shorts_id) == 11:
                        video_id = shorts_id
                elif 'youtu.be/' in youtube_url:
                    video_id = youtube_url.split('youtu.be/')[1].split('?')[0].split('&')[0]
                elif 'v=' in youtube_url:
                    video_id = youtube_url.split('v=')[1].split('&')[0].split('?')[0]

            if video_id and len(video_id) == 11:
                print(f"شناسه ویدیو: {video_id}")
            else:
                print(f"نتوانستیم شناسه ویدیو را از لینک {youtube_url} استخراج کنیم.")
                print("لطفاً مطمئن شوید لینک به شکل درستی وارد شده است.")
                exit()

            # نگاشت زبان‌ها به کدهای استاندارد (هماهنگ با سلول ترجمه)
            language_map = {
                "Auto-detect": None,
                "English (EN)": "en",
                "Persian (FA)": "fa",
                "German (DE)": "de",
                "French (FR)": "fr",
                "Italian (IT)": "it",
                "Spanish (ES)": "es",
                "Chinese (ZH)": "zh",
                "Korean (KO)": "ko",
                "Russian (RU)": "ru",
                "Arabic (AR)": "ar",
                "Japanese (JA)": "ja",
                "Hindi (HI)": "hi"
            }
            selected_language = language_map.get(transcript_language)

            # دریافت زیرنویس با YouTube Transcript API
            try:
                print(f"در حال دریافت زیرنویس برای ویدیو با شناسه: {video_id}")

                # دریافت لیست زیرنویس‌ها
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

                # چاپ لیست زیرنویس‌های موجود
                print("\nزیرنویس‌های موجود برای این ویدیو:")
                print("----------------------------------------")
                manual_transcripts = []
                generated_transcripts = []
                translatable_transcripts = []

                for transcript in transcript_list:
                    if not transcript.is_generated and not transcript.is_translatable:
                        manual_transcripts.append(f"{transcript.language} ({transcript.language_code}) - Manual")
                    elif transcript.is_generated:
                        generated_transcripts.append(f"{transcript.language} ({transcript.language_code}) - Auto-generated")
                    if transcript.is_translatable:
                        translatable_transcripts.append(f"{transcript.language} ({transcript.language_code}) - Translatable")

                if manual_transcripts:
                    print("زیرنویس‌های دستی (Manually Created):")
                    for t in manual_transcripts:
                        print(f"  - {t}")
                else:
                    print("زیرنویس‌های دستی: هیچ‌کدام")

                if generated_transcripts:
                    print("زیرنویس‌های خودکار (Generated):")
                    for t in generated_transcripts:
                        print(f"  - {t}")
                else:
                    print("زیرنویس‌های خودکار: هیچ‌کدام")

                if translatable_transcripts:
                    print("زیرنویس‌های قابل ترجمه (Translatable):")
                    for t in translatable_transcripts:
                        print(f"  - {t}")
                print("----------------------------------------\n")

                # انتخاب زیرنویس
                if selected_language:  # زبان خاص انتخاب شده
                    transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=[selected_language])
                    print(f"زیرنویس به زبان {transcript_language} دریافت شد.")
                else:  # Auto-detect
                    transcript_data = None
                    selected_lang_code = None

                    # پیدا کردن اولین زیرنویس موجود (دستی یا خودکار)
                    for transcript in transcript_list:
                        if transcript.is_generated:
                            print(f"زیرنویس خودکار به زبان {transcript.language} انتخاب شد.")
                            selected_lang_code = transcript.language_code
                            transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=[transcript.language_code])
                            break
                        elif not transcript.is_translatable:
                            print(f"زیرنویس دستی به زبان {transcript.language} انتخاب شد.")
                            selected_lang_code = transcript.language_code
                            transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=[transcript.language_code])
                            break

                    # اگه هیچ زیرنویسی نبود، ترجمه به انگلیسی
                    if not transcript_data:
                        for transcript in transcript_list:
                            if transcript.is_translatable:
                                print(f"استفاده از زیرنویس ترجمه‌شده به انگلیسی از {transcript.language}")
                                transcript_data = transcript.translate('en').fetch()
                                selected_lang_code = 'en'
                                break

                if transcript_data:
                    print("زیرنویس با موفقیت دریافت شد!")

                    # محاسبه مدت زمان ویدیو
                    result = subprocess.run([
                        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                        '-of', 'default=noprint_wrappers=1:nokey=1',
                        'input_video.mp4'
                    ], capture_output=True, text=True)

                    video_duration = float(result.stdout.strip())
                    print(f"مدت زمان ویدیو: {video_duration} ثانیه")

                    # پردازش زیرنویس‌ها
                    processed_data = []
                    for entry in transcript_data:
                        processed_data.append({
                            'start': entry['start'],
                            'duration': entry.get('duration', 0),
                            'text': entry['text']
                        })

                    # مرتب‌سازی بر اساس زمان شروع
                    processed_data.sort(key=lambda x: x['start'])

                    print(f"تعداد زیرنویس‌های اولیه: {len(processed_data)}")

                    # گام 1: رفع تداخل‌های اولیه زمانی بین زیرنویس‌ها
                    cleaned_data = []
                    if processed_data:
                        cleaned_data.append(processed_data[0])
                        for i in range(1, len(processed_data)):
                            current = processed_data[i]
                            previous = cleaned_data[-1]
                            prev_end = previous['start'] + previous['duration']

                            if current['start'] < prev_end:
                                if current['start'] + current['duration'] <= prev_end:
                                    print(f"زیرنویس {i+1} کاملاً با زیرنویس قبلی همپوشانی دارد و ادغام می‌شود")
                                    previous['text'] += " " + current['text']
                                else:
                                    overlap = prev_end - current['start']
                                    new_duration = current['duration'] - overlap

                                    if new_duration > 0.3:
                                        current['start'] = prev_end
                                        current['duration'] = new_duration
                                        cleaned_data.append(current)
                                        print(f"تداخل زمانی اولیه در زیرنویس {i+1} اصلاح شد")
                                    else:
                                        previous['text'] += " " + current['text']
                                        previous['duration'] = max(previous['duration'],
                                                                 (current['start'] + current['duration']) - previous['start'])
                                        print(f"زیرنویس {i+1} به دلیل تداخل زمانی با زیرنویس قبلی ادغام شد")
                            else:
                                cleaned_data.append(current)

                    processed_data = cleaned_data
                    print(f"تعداد زیرنویس‌ها پس از رفع تداخل‌های اولیه: {len(processed_data)}")

                    # گام 2: بررسی شروع دیرهنگام و پایان فراتر از حد
                    first_start_time = processed_data[0]['start'] if processed_data else 0
                    has_early_gap = first_start_time > 0.5
                    early_gap_under_3s = first_start_time < 3.0

                    last_entry = processed_data[-1] if processed_data else {'start': 0, 'duration': 0}
                    last_end_time = last_entry['start'] + last_entry['duration']
                    late_overflow = last_end_time > (video_duration - 0.5)

                    # گام 3: تعیین استراتژی برای مدیریت زمان‌بندی
                    if late_overflow and has_early_gap and early_gap_under_3s:
                        print(f"زیرنویس‌ها به صورت هوشمند به عقب کشیده می‌شوند...")
                        available_space = video_duration - 0.5
                        required_space = last_end_time

                        if required_space > available_space:
                            scale_factor = available_space / required_space
                            print(f"ضریب مقیاس زمانی: {scale_factor:.4f}")
                            for entry in processed_data:
                                entry['start'] = entry['start'] * scale_factor
                                entry['duration'] = entry['duration'] * scale_factor
                        else:
                            time_shift = -first_start_time
                            print(f"انتقال زمانی: {time_shift:.2f} ثانیه")
                            for entry in processed_data:
                                entry['start'] += time_shift
                    elif late_overflow:
                        print("فقط سرریز انتهایی داریم - حذف یا کوتاه کردن زیرنویس‌های انتهایی...")

                    # گام 4: نهایی‌سازی زیرنویس‌ها
                    valid_entries = []
                    for i, entry in enumerate(processed_data):
                        start_time = entry['start']
                        duration = entry['duration']
                        end_time = start_time + duration

                        if start_time < 0:
                            duration += start_time
                            start_time = 0
                            entry['start'] = start_time
                            entry['duration'] = duration

                        if end_time > (video_duration - 0.5):
                            if start_time < (video_duration - 0.5):
                                duration = (video_duration - 0.5) - start_time
                                entry['duration'] = duration
                                valid_entries.append(entry)
                                print(f"زیرنویس شماره {i+1} کوتاه شد (پایان: {end_time:.2f} -> {video_duration - 0.5:.2f})")
                            else:
                                print(f"زیرنویس شماره {i+1} به دلیل خارج بودن از محدوده زمانی ویدیو حذف شد")
                                continue
                        else:
                            valid_entries.append(entry)

                    # گام 5: بررسی مجدد تداخل‌های زمانی
                    if len(valid_entries) > 1:
                        final_entries = [valid_entries[0]]
                        for i in range(1, len(valid_entries)):
                            current = valid_entries[i]
                            previous = final_entries[-1]
                            prev_end = previous['start'] + previous['duration']

                            if current['start'] < prev_end:
                                new_duration = (current['start'] + current['duration']) - prev_end
                                if new_duration > 0.3:
                                    current['start'] = prev_end
                                    current['duration'] = new_duration
                                    final_entries.append(current)
                                    print(f"تداخل زمانی نهایی در زیرنویس {i+1} اصلاح شد")
                                else:
                                    previous['text'] += " " + current['text']
                                    previous['duration'] = (current['start'] + current['duration']) - previous['start']
                                    print(f"زیرنویس {i+1} به دلیل تداخل زمانی نهایی با زیرنویس قبلی ادغام شد")
                            else:
                                final_entries.append(current)
                        valid_entries = final_entries

                    # گام 6: تبدیل به فرمت SRT
                    srt_content = []
                    for i, entry in enumerate(valid_entries):
                        start_time = entry['start']
                        duration = entry['duration']
                        end_time = start_time + duration

                        start_str = '{:02d}:{:02d}:{:02d},{:03d}'.format(
                            int(start_time // 3600),
                            int((start_time % 3600) // 60),
                            int(start_time % 60),
                            int((start_time % 1) * 1000)
                        )
                        end_str = '{:02d}:{:02d}:{:02d},{:03d}'.format(
                            int(end_time // 3600),
                            int((end_time % 3600) // 60),
                            int(end_time % 60),
                            int((end_time % 1) * 1000)
                        )
                        srt_content.append(f"{i+1}\n{start_str} --> {end_str}\n{entry['text']}\n")

                    # ذخیره به فایل SRT
                    with open('audio.srt', 'w', encoding='utf-8') as f:
                        f.write('\n'.join(srt_content))

                    print(f"زیرنویس با موفقیت از یوتیوب استخراج شد و در فایل audio.srt ذخیره شد.")
                    print(f"تعداد زیرنویس‌های نهایی: {len(valid_entries)} (از {len(transcript_data)} زیرنویس اصلی)")
                else:
                    print("متأسفانه هیچ زیرنویسی برای این ویدیو یافت نشد!")

            except Exception as e:
                print(f"خطا در استخراج زیرنویس: {str(e)}")
                print("اگر این ویدیو زیرنویس دارد، مطمئن شوید لینک به درستی وارد شده است.")
                print("مثال لینک‌های قابل قبول: https://www.youtube.com/watch?v=VIDEO_ID یا https://www.youtube.com/shorts/VIDEO_ID")

else:  # آپلود زیرنویس
    print("لطفاً فایل زیرنویس خود را با فرمت .srt آپلود کنید:")
    uploaded = files.upload()
    subtitle_file = next(iter(uploaded.keys()))
    os.rename(subtitle_file, 'audio.srt')

# --- Cell 5 ---
#@title فشرده‌سازی دیالوگ‌ها (اختیاری)
import re
import os

#@markdown ---
#@markdown ### **تنظیمات فشرده‌سازی**
#@markdown با فعال کردن این گزینه، دیالوگ‌ها با هم ادغام می‌شوند.
fashordeh_sazi_dialogue = True #@param {type:"boolean"}

#@markdown تعداد دیالوگ برای ادغام در هر گروه (مثلا عدد ۳ یعنی هر ۳ دیالوگ یکی شوند)
merge_n = 2 #@param {type:"slider", min:2, max:30, step:1}


def compress_srt_dialogues(srt_content_string, merge_count=3):
    """
    محتوای یک فایل SRT را به عنوان ورودی می‌گیرد، دیالوگ‌ها را ادغام می‌کند
    و محتوای SRT جدید و فشرده‌شده را برمی‌گرداند.
    """
    def _parse_srt(srt_content):
        subtitle_blocks = srt_content.strip().split('\n\n')
        subtitles = []
        for block in subtitle_blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 2:
                try:
                    time_line_index = -1
                    for i, line in enumerate(lines):
                        if '-->' in line:
                            time_line_index = i
                            break
                    if time_line_index != -1:
                        time_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})', lines[time_line_index])
                        start_time, end_time = time_match.groups()
                        text = '\n'.join(lines[time_line_index+1:])
                        subtitles.append({'start': start_time, 'end': end_time, 'text': text})
                except Exception:
                    continue
        return subtitles

    def _merge_subtitles(subtitles, n):
        merged_subs = []
        new_index = 1
        for i in range(0, len(subtitles), n):
            chunk = subtitles[i:i+n]
            if not chunk: continue
            start_time = chunk[0]['start']
            end_time = chunk[-1]['end']
            combined_text = ' '.join([sub['text'].replace('\n', ' ') for sub in chunk])
            merged_subs.append({'index': new_index, 'start': start_time, 'end': end_time, 'text': combined_text})
            new_index += 1
        return merged_subs

    def _format_srt(subtitles):
        srt_output = []
        for sub in subtitles:
            srt_output.append(str(sub['index']))
            srt_output.append(f"{sub['start']} --> {sub['end']}")
            srt_output.append(sub['text'])
            srt_output.append('')
        return '\n'.join(srt_output)

    original_subtitles = _parse_srt(srt_content_string)
    if not original_subtitles:
        print("هشدار: هیچ دیالوگ معتبری در زیرنویس برای فشرده‌سازی یافت نشد.")
        return srt_content_string

    merged_list = _merge_subtitles(original_subtitles, merge_count)
    new_srt_content = _format_srt(merged_list)

    print(f"فشرده‌سازی {merge_count} تایی انجام شد: {len(original_subtitles)} دیالوگ به {len(merged_list)} دیالوگ تبدیل شد.")
    return new_srt_content

# --- اجرای فشرده‌سازی ---
if fashordeh_sazi_dialogue:
    subtitle_path = 'audio.srt'
    if os.path.exists(subtitle_path):
        print(f"✔️ گزینه فشرده‌سازی فعال است. در حال پردازش فایل '{subtitle_path}' با گروه‌های {merge_n} تایی...")
        with open(subtitle_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        # استفاده از مقدار اسلایدر در فراخوانی تابع
        compressed_content = compress_srt_dialogues(original_content, merge_count=merge_n)

        with open(subtitle_path, 'w', encoding='utf-8') as f:
            f.write(compressed_content)
        print("فایل زیرنویس با موفقیت فشرده و جایگزین شد.")
    else:
        print(f"⚠️ هشدار: فایل زیرنویس '{subtitle_path}' یافت نشد. مرحله فشرده‌سازی نادیده گرفته شد.")
else:
    print("❌ گزینه فشرده‌سازی غیرفعال است. از زیرنویس اصلی استفاده می‌شود.")

# --- Cell 6 ---

#@title ترجمه زیرنویس
#@markdown زبان مبدا بصورت خودکار انتخاب میشود و زبان مقصد را دستی انتخاب کنید

import pysrt
import google.generativeai as genai
from tqdm.notebook import tqdm
import time
# [removed_magic] from google.colab import files
import os
import subprocess
import json

# بررسی اینکه آیا کلید API در سلول قبل تنظیم شده است یا نه
if 'GOOGLE_API_KEY' not in os.environ or not os.environ['GOOGLE_API_KEY']:
     print("❌ خطا: کلید API تنظیم نشده است. لطفاً ابتدا سلول قبلی (ورود کلید API) را اجرا کنید.")
else:
    #@markdown ---
    translation_method = "هوش مصنوعی" #@param ["هوش مصنوعی", "آپلود زیرنویس بصورت دستی"]
    #@markdown زبان مبدا
    source_language = "Auto-detect" #@param ["Auto-detect", "English (EN)", "Persian (FA)", "German (DE)", "French (FR)", "Italian (IT)", "Spanish (ES)", "Chinese (ZH)", "Korean (KO)", "Russian (RU)", "Arabic (AR)", "Japanese (JA)", "Hindi (HI)"]
    #@markdown زبان مقصد
    target_language = "Persian (FA)" #@param ["Persian (FA)", "English (EN)", "German (DE)", "French (FR)", "Italian (IT)", "Spanish (ES)", "Chinese (ZH)", "Korean (KO)", "Russian (RU)", "Arabic (AR)", "Japanese (JA)", "Hindi (HI)"]

    if translation_method == "هوش مصنوعی":
        filename = '/content/audio.srt'
        output_filename = '/content/audio_translated.srt'

        # تعریف لیست مدل‌ها با اولویت مد نظر شما
        translation_models = [
            "gemini-flash-lite-latest",
            "gemini-2.5-flash-lite",
            "gemini-2.5-flash"
        ]

        def clean_srt_response(response_text):
            """پاکسازی پاسخ Gemini از توضیحات اضافی و حفظ ساختار SRT"""
            try:
                lines = response_text.split('\n')
                cleaned_lines = []
                in_srt_content = False
                subtitle_count = 0
                found_first_subtitle = False
                
                for i, line in enumerate(lines):
                    line = line.strip()
                    
                    # اگر خط خالی است، آن را حفظ کن
                    if not line:
                        if in_srt_content:
                            cleaned_lines.append(line)
                        continue
                    
                    # بررسی اینکه آیا این خط شروع یک زیرنویس است (شماره)
                    if line.isdigit() and not found_first_subtitle:
                        # بررسی اینکه آیا این اولین زیرنویس است (شماره 1)
                        if line == "1":
                            found_first_subtitle = True
                            in_srt_content = True
                            subtitle_count += 1
                            cleaned_lines.append(line)
                            continue
                        else:
                            # اگر شماره 1 نیست، نادیده بگیر
                            continue
                    elif line.isdigit() and found_first_subtitle:
                        # زیرنویس‌های بعدی
                        in_srt_content = True
                        subtitle_count += 1
                        cleaned_lines.append(line)
                        continue
                    
                    # اگر در محتوای SRT هستیم، خط را پردازش کن
                    if in_srt_content:
                        # اگر خط زمان‌بندی است، آن را حفظ کن
                        if '-->' in line:
                            cleaned_lines.append(line)
                            continue
                        
                        # اگر خط متن است، بررسی کن که آیا شامل هر دو زبان است
                        if not line.isdigit() and '-->' not in line:
                            # بررسی اینکه آیا خط شامل متن انگلیسی و فارسی است
                            cleaned_line = extract_persian_text(line)
                            if cleaned_line:
                                cleaned_lines.append(cleaned_line)
                            continue
                        
                        # در غیر این صورت، خط را حفظ کن
                        cleaned_lines.append(line)
                        continue
                    
                    # اگر هنوز در محتوای SRT نیستیم، بررسی کن که آیا این خط توضیح اضافی است
                    explanation_keywords = [
                        'متن کامل فایل SRT', 'ترجمه فارسی', 'فایل SRT', 'زیرنویس', 'ترجمه',
                        'به همین دلیل', 'درک کامل', 'موضوع و مفهوم', 'عملاً غیرممکن', 'متنی بی‌معنی',
                        'انتظارات شما', 'اگر متن اصلی', 'لطفاً زبان', 'در صورت امکان', 'در حال حاضر',
                        'قادر به ارائه', 'بر اساس فرض', 'SRT File', 'Translation', 'subtitle',
                        'translate', 'file', 'content', 'text', 'because', 'unable', 'impossible',
                        'cannot', 'please', 'if you have', 'currently', 'based on', 'در خط', 'به نظر می‌رسد',
                        'تحریف شده', 'احتمالاً', 'باشد', 'است', 'I\'ve', 'Wow', 'amount', 'money'
                    ]
                    
                    # اگر خط حاوی کلمات توضیحی است، آن را نادیده بگیر
                    if any(keyword in line for keyword in explanation_keywords):
                        continue
                    
                    # اگر خط کوتاه است و احتمالاً توضیح است، نادیده بگیر
                    if len(line) < 20 and not line[0].isdigit() and '-->' not in line:
                        continue
                    
                    # در غیر این صورت، خط را حفظ کن
                    cleaned_lines.append(line)
                
                # اگر هیچ زیرنویسی پیدا نشد، کل متن را برگردان
                if subtitle_count == 0:
                    print("⚠️ هیچ زیرنویسی در پاسخ یافت نشد، کل متن برگردانده می‌شود")
                    return response_text
                
                cleaned_text = '\n'.join(cleaned_lines)
                print(f"✅ {subtitle_count} زیرنویس از پاسخ پاکسازی شد")
                return cleaned_text
                
            except Exception as e:
                print(f"❌ خطا در پاکسازی پاسخ: {str(e)}")
                return response_text

        def extract_persian_text(line):
            """استخراج متن فارسی از خطی که شامل هر دو زبان است و حفظ اعداد"""
            try:
                # تقسیم خط به کلمات
                words = line.split()
                result_words = []
                
                for word in words:
                    # بررسی اینکه آیا کلمه فارسی است یا نه
                    if is_persian_word(word):
                        result_words.append(word)
                    # اگر کلمه شامل عدد است، آن را حفظ کن
                    elif contains_number(word):
                        result_words.append(word)
                    # اگر کلمه فقط عدد است، آن را حفظ کن
                    elif word.isdigit():
                        result_words.append(word)
                    # اگر کلمه شامل عدد و حروف است (مثل "18th", "2.5", "5G")
                    elif any(c.isdigit() for c in word):
                        result_words.append(word)
                
                # اگر کلمه فارسی یا عدد پیدا شد، آن‌ها را برگردان
                if result_words:
                    return ' '.join(result_words)
                
                # اگر هیچ کلمه فارسی یا عدد پیدا نشد، کل خط را برگردان
                return line
                
            except Exception as e:
                print(f"❌ خطا در استخراج متن فارسی: {str(e)}")
                return line

        def is_persian_word(word):
            """بررسی اینکه آیا کلمه فارسی است یا نه"""
            try:
                # حذف علائم نگارشی
                clean_word = ''.join(c for c in word if c.isalnum())
                
                if not clean_word:
                    return False
                
                # بررسی وجود کاراکترهای فارسی
                persian_chars = 'ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی'
                has_persian = any(c in persian_chars for c in clean_word)
                
                # بررسی عدم وجود کاراکترهای انگلیسی
                english_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
                has_english = any(c in english_chars for c in clean_word)
                
                # اگر کاراکتر فارسی دارد و کاراکتر انگلیسی ندارد، فارسی است
                return has_persian and not has_english
                
            except Exception as e:
                return False
        
        def contains_number(word):
            """بررسی اینکه آیا کلمه شامل عدد است یا نه"""
            try:
                # بررسی وجود کاراکترهای عددی
                return any(c.isdigit() for c in word)
            except Exception as e:
                return False

        def translate_entire_srt_with_fallback(srt_text):
            """
            ترجمه کل فایل SRT در یک درخواست با استفاده از مدل‌های مختلف
            """
            for model_name in translation_models:
                try:
                    model = genai.GenerativeModel(
                        model_name,
                        safety_settings={
                            genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                            genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
                            genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                            genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                        }
                    )

                    # --- پرامپت بهینه شده برای ترجمه کامل فایل ---
                    if target_language == "Persian (FA)":
                        prompt = f"""متن کامل فایل SRT زیر را که شامل زیرنویس‌های یک ویدیو به زبان انگلیسی است، به دقت مطالعه کن تا کاملاً متوجه موضوع و مفهوم کلی آن شوی.
پس از درک کامل محتوا، هر خط از متن زیرنویس (بخش انگلیسی) را به فارسی بسیار روان، طبیعی و قابل فهم برای مخاطب عمومی ترجمه کن. ترجمه نباید حالت ماشینی داشته باشد و باید شبیه متنی باشد که یک فارسی‌زبان بومی می‌نوشت. پیام اصلی هر خط را بدون هیچ گونه ابهام یا دشواری در درک منتقل کن.
نکات بسیار مهم:
حفظ ساختار SRT: لطفاً ساختار زمانی فایل SRT را دقیقاً حفظ کن. یعنی هر خط ترجمه فارسی باید دقیقاً مقابل خط اصلی انگلیسی و با همان شماره و زمان‌بندی قرار گیرد. فقط متن انگلیسی را ترجمه کن و اعداد و زمان‌بندی را بدون تغییر کپی کن.
حفظ اعداد در متن ترجمه: هر عدد یا رقمی که در متن انگلیسی زیرنویس وجود دارد (مثلاً "Gemma 3N", "version 2.5", "100 meters", "5G connectivity")، باید دقیقاً و بدون تغییر در ترجمه فارسی نیز آورده شود. اعداد را ترجمه یا حذف نکن.

فایل SRT:
{srt_text}

ترجمه فارسی:"""
                    else:
                        language_map = {"English (EN)": "English", "German (DE)": "German", "French (FR)": "French", "Italian (IT)": "Italian", "Spanish (ES)": "Spanish", "Chinese (ZH)": "Chinese", "Korean (KO)": "Korean", "Russian (RU)": "Russian", "Arabic (AR)": "Arabic", "Japanese (JA)": "Japanese", "Hindi (HI)": "Hindi"}
                        target_lang_name = language_map.get(target_language, "English")
                        prompt = f"""You are an expert subtitle translator. Please carefully read the complete SRT file below which contains subtitles for a video in English, and understand the overall topic and context.
After fully understanding the content, translate each line of subtitle text (English part) to {target_lang_name} in a very fluent, natural and understandable way for general audience. The translation should not sound machine-like and should be like text written by a native speaker. Convey the main message of each line without any ambiguity or difficulty in understanding.
Very important note: Please preserve the exact timing structure of the SRT file. Each translated line should be exactly opposite the original English line with the same number and timing. Only translate the English text and copy the numbers and timing without any changes.

SRT File:
{srt_text}

{target_lang_name} Translation:"""
                    # --- پایان پرامپت ---

                    print(f"🔄 ارسال کل فایل SRT به مدل {model_name} برای ترجمه...")
                    response = model.generate_content(prompt)
                    time.sleep(3)  # Rate limiting
                    
                    # پاکسازی پاسخ از خطوط اضافی
                    cleaned_response = clean_srt_response(response.text.strip())
                    return cleaned_response

                except Exception as e:
                    print(f"⚠️ مدل {model_name} با خطا مواجه شد: {str(e)}. در حال تلاش با مدل بعدی...")
                    time.sleep(5) # A short pause before trying the next model

            # اگر تمام مدل‌ها شکست خوردند، متن اصلی را برگردان تا کار متوقف نشود
            print(f"❌ تمام مدل‌های ترجمه برای فایل SRT ناموفق بودند. متن اصلی جایگزین شد.")
            return srt_text

        try:
            # خواندن کل محتوای فایل SRT
            with open(filename, 'r', encoding='utf-8') as f:
                srt_content = f.read()
            
            print(f"🔄 شروع ترجمه کامل فایل SRT...")
            # ترجمه کل فایل SRT در یک درخواست
            translated_content = translate_entire_srt_with_fallback(srt_content)
            
            # ذخیره فایل ترجمه شده
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(translated_content)
            
            os.rename(output_filename, 'audio_fa.srt')
            print(f"\n✅ ترجمه کامل فایل SRT از {source_language} به {target_language} با موفقیت به پایان رسید!")

        except Exception as e:
            print(f"خطا در خواندن یا ترجمه فایل زیرنویس: {str(e)}")

    else:  # آپلود زیرنویس بصورت دستی
        print("لطفاً فایل زیرنویس ترجمه شده خود را با فرمت .srt آپلود کنید:")
        uploaded = files.upload()
        subtitle_file = next(iter(uploaded.keys()))
        os.rename(subtitle_file, 'audio_fa.srt')

    if os.path.exists('audio_fa.srt'):
        print("\n✅ فایل زیرنویس ترجمه شده 'audio_fa.srt' آماده است.")
    else:
        print("\n❌ خطا: فایل زیرنویس ترجمه شده 'audio_fa.srt' ایجاد نشد.")

# --- Cell 7 ---

#@title ساخت سگمنت‌های صوتی
import google.genai as genai
from google.genai import types
import pysrt
import os
import subprocess
import traceback
from pydub import AudioSegment
import time
import shutil
import mimetypes
import struct

#@markdown ---
#@markdown ### **تنظیمات زمان استراحت**
#@markdown برای جلوگیری از خطا، می‌توانید زمان انتظار بین درخواست‌ها را افزایش دهید.

#@markdown زمان استراحت بین هر درخواست موفق (ثانیه):
sleep_between_requests = 9 #@param {type:"slider", min:3, max:20, step:1}

#@markdown زمان استراحت پایه بین تلاش‌های مجدد پس از خطا (ثانیه):
sleep_between_retries = 9 #@param {type:"slider", min:5, max:30, step:1}

#@markdown ---
#@markdown ### **پرامپت برای تعیین لحن صدا**
#@markdown در اینجا می‌توانید لحن صدا را مشخص کنید (مثلا: با لحنی آرام و شمرده صحبت کن)
speech_prompt = "" #@param {type:"string"}

#@markdown ---
#@markdown ### **تنظیمات تولید صدا با مدل‌های اختصاصی TTS**
#@markdown نسخه فلش رایگان میباشد
tts_model_name = "gemini-2.5-flash-preview-tts" #@param ["gemini-2.5-flash-preview-tts", "gemini-2.5-pro-preview-tts"]

#@markdown ---
#@markdown ### **انتخاب گوینده**
#@markdown لیست کامل گویندگان حرفه‌ای Gemini:
speaker_voice = "Fenrir" #@param ["Achird", "Zubenelgenubi", "Vindemiatrix", "Sadachbia", "Sadaltager", "Sulafat", "Laomedeia", "Achernar", "Alnilam", "Schedar", "Gacrux", "Pulcherrima", "Umbriel", "Algieba", "Despina", "Erinome", "Algenib", "Rasalthgeti", "Orus", "Aoede", "Callirrhoe", "Autonoe", "Enceladus", "Iapetus", "Zephyr", "Puck", "Charon", "Kore", "Fenrir", "Leda"]


os.makedirs('dubbing_project/dubbed_segments', exist_ok=True)


def parse_audio_mime_type(mime_type: str) -> dict:
    parts = mime_type.split(";")
    details = {'bits_per_sample': 16, 'rate': 24000}
    for param in parts:
        param = param.strip()
        if param.lower().startswith("rate="):
            details['rate'] = int(param.split("=", 1)[1])
        elif param.startswith("audio/L"):
            details['bits_per_sample'] = int(param.split("L", 1)[1])
    return details

def convert_to_wav(audio_data: bytes, mime_type: str) -> bytes:
    parameters = parse_audio_mime_type(mime_type)
    bits_per_sample = parameters["bits_per_sample"]
    sample_rate = parameters["rate"]
    num_channels = 1
    data_size = len(audio_data)
    bytes_per_sample = bits_per_sample // 8
    block_align = num_channels * bytes_per_sample
    byte_rate = sample_rate * block_align
    chunk_size = 36 + data_size
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF", chunk_size, b"WAVE", b"fmt ", 16, 1,
        num_channels, sample_rate, byte_rate, block_align,
        bits_per_sample, b"data", data_size
    )
    return header + audio_data



def generate_gemini_tts_segment(client, text, prompt, voice, model, output_path, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            if prompt and prompt.strip():
                final_text = f"{prompt.strip()}: \"{text}\""
            else:
                final_text = text

            contents = [types.Content(role="user", parts=[types.Part.from_text(text=final_text)])]
            generate_content_config = types.GenerateContentConfig(
                response_modalities=["audio"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)
                    )
                ),
            )
            stream = client.models.generate_content_stream(
                model=model, contents=contents, config=generate_content_config,
            )

            audio_data_buffer = b""
            mime_type = ""
            for chunk in stream:
                if chunk.candidates and chunk.candidates[0].content and chunk.candidates[0].content.parts:
                    part = chunk.candidates[0].content.parts[0]
                    if part.inline_data:
                        audio_data_buffer += part.inline_data.data
                        mime_type = part.inline_data.mime_type

            if audio_data_buffer and mime_type:
                final_wav_data = convert_to_wav(audio_data_buffer, mime_type)
                with open(output_path, 'wb') as f:
                    f.write(final_wav_data)
                return output_path
            else:
                raise Exception("هیچ داده صوتی از API دریافت نشد.")

        except Exception as e:
            print(f"❌ خطا در تولید صدای Gemini (تلاش {attempt}/{max_retries}): {str(e)}")
            if attempt < max_retries:

                wait_time = sleep_between_retries * attempt
                print(f"⏳ انتظار برای {wait_time} ثانیه قبل از تلاش مجدد...")
                time.sleep(wait_time)
            else:
                print(f"💔 تولید صدا برای قطعه '{text[:50]}...' ناموفق بود.")
                return None
    return None


def run_dubbing_process():
    if 'GOOGLE_API_KEY' not in globals() or not GOOGLE_API_KEY:
        print("❌ کلید API جمینای در سلول قبلی وارد نشده است. لطفاً ابتدا سلول ترجمه را اجرا کنید.")
        return

    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        print("✅ کلاینت Gemini با موفقیت ایجاد شد.")
    except Exception as e:
        print(f"❌ خطا در ایجاد کلاینت Gemini: {e}. لطفاً کلید API خود را بررسی کنید.")
        return

    try:
        subs = pysrt.open('/content/audio_fa.srt', encoding='utf-8')
    except Exception as e:
        print(f"❌ خطا در خواندن فایل زیرنویس 'audio_fa.srt': {str(e)}")
        return

    print(f"🚀 شروع تولید {len(subs)} سگمنت صوتی با مدل {tts_model_name} و صدای {speaker_voice}...")
    if speech_prompt and speech_prompt.strip():
        print(f"🗣️ با استفاده از پرامپت لحن: '{speech_prompt}'")
    print("="*50)

    for i, sub in enumerate(subs):
        print(f"🎧 پردازش سگمنت {i+1}/{len(subs)}...")
        temp_audio_path = f"dubbing_project/dubbed_segments/temp_{i+1}.wav"
        final_segment_path = f"dubbing_project/dubbed_segments/dub_{i+1}.wav"

        generated_path = generate_gemini_tts_segment(client, sub.text, speech_prompt, speaker_voice, tts_model_name, temp_audio_path)


        if i < len(subs) - 1:
            print(f"⏱️ استراحت برای {sleep_between_requests} ثانیه...")
            time.sleep(sleep_between_requests)

        if not generated_path or not os.path.exists(generated_path):
            print(f"⚠️ تولید صدای Gemini برای سگمنت {i+1} ناموفق بود. یک فایل سکوت ایجاد می‌شود.")
            start_ms = sub.start.hours * 3600000 + sub.start.minutes * 60000 + sub.start.seconds * 1000 + sub.start.milliseconds
            end_ms = sub.end.hours * 3600000 + sub.end.minutes * 60000 + sub.end.seconds * 1000 + sub.end.milliseconds
            target_duration_ms = end_ms - start_ms
            silent_audio = AudioSegment.silent(duration=max(int(target_duration_ms), 100))
            silent_audio.export(final_segment_path, format="wav")
            continue

        try:
            start_ms = sub.start.hours * 3600000 + sub.start.minutes * 60000 + sub.start.seconds * 1000 + sub.start.milliseconds
            end_ms = sub.end.hours * 3600000 + sub.end.minutes * 60000 + sub.end.seconds * 1000 + sub.end.milliseconds
            target_duration = (end_ms - start_ms) / 1000.0
            if target_duration <= 0: target_duration = 0.5

            sound = AudioSegment.from_file(generated_path)
            original_duration = len(sound) / 1000.0

            if original_duration == 0:
                raise ValueError("فایل صوتی تولید شده خالی است.")

            speed_factor = original_duration / target_duration
            speed_factor = max(0.5, min(speed_factor, 2.5))

            print(f"   - زمان هدف: {target_duration:.2f}s | زمان اصلی: {original_duration:.2f}s | ضریب سرعت: {speed_factor:.2f}")

            subprocess.run([
                'ffmpeg', '-i', generated_path,
                '-filter:a', f'rubberband=tempo={speed_factor}',
                '-y', final_segment_path
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            print(f"   ✅ سگمنت {i+1} با موفقیت ساخته و زمان‌بندی شد.")

        except Exception as e:
            print(f"   ❌ خطا در زمان‌بندی سگمنت {i+1}: {e}")
            shutil.copy(generated_path, final_segment_path)
        #finally:
            #if os.path.exists(generated_path):
                #os.remove(generated_path)

    print("="*50)
    print("🎉 تمام سگمنت‌های صوتی با Gemini TTS با موفقیت ساخته شدند!")


run_dubbing_process()

# --- Cell 8 ---

#@title شروع عملیات نهایی
import subprocess
import pysrt
import os
from datetime import timedelta
import json
from pydub import AudioSegment
import tempfile
import glob
import shutil
from IPython.display import display, HTML

video_files = glob.glob('input_video.*')
if not os.path.exists('input_video.mp4') and video_files:
    input_video = video_files[0]
else:
    input_video = 'input_video.mp4'

#@markdown ---
#@markdown ### **تنظیمات صدای اصلی**
#@markdown آیا می‌خواهید صدای اصلی ویدیو حفظ شود؟
keep_original_audio = False #@param {type:"boolean"}
#@markdown میزان صدای اصلی ویدیو (فقط در صورت فعال بودن گزینه بالا)
original_audio_volume = 0.8 #@param {type:"slider", min:0, max:1, step:0.005}

#@markdown ---
#@markdown ### **روش ترکیب صدا**

audio_merge_method = "pydub" #@param ["pydub", "ffmpeg filter_complex", "ffmpeg concat"]


if not os.path.exists(input_video):
    print(f"❌ خطا: فایل ویدیویی {input_video} یافت نشد!")
else:
    print(f"✔️ فایل ویدیو یافت شد: {input_video}")

if not os.path.exists('/content/audio_fa.srt'):
    print("❌ خطا: فایل زیرنویس 'audio_fa.srt' یافت نشد!")
else:
    print("✔️ فایل زیرنویس یافت شد")

segment_dir = "dubbing_project/dubbed_segments"
if not os.path.exists(segment_dir):
    print("❌ خطا: پوشه سگمنت‌های صوتی یافت نشد!")
    os.makedirs(segment_dir, exist_ok=True)
else:
    segments = [f for f in os.listdir(segment_dir) if f.startswith("dub_") and f.endswith(".wav")]
    print(f"✔️ {len(segments)} سگمنت صوتی یافت شد")

# --- خواندن فایل زیرنویس با بررسی فرمت‌های مختلف ---
try:
    subs = pysrt.open('/content/audio_fa.srt', encoding='utf-8')
    print("✔️ فایل زیرنویس با موفقیت خوانده شد (utf-8)")
except Exception:
    try:
        subs = pysrt.open('/content/audio_fa.srt', encoding='latin-1')
        print("✔️ فایل زیرنویس با موفقیت خوانده شد (latin-1)")
    except Exception:
        try:
            print("⚠️ در حال تلاش برای تبدیل فرمت زیرنویس به UTF-8...")
            subprocess.run(['iconv', '-f', 'ISO-8859-1', '-t', 'UTF-8', '/content/audio_fa.srt', '-o', '/content/audio_fa_utf8.srt'], check=True)
            subs = pysrt.open('/content/audio_fa_utf8.srt')
            print("✔️ فایل زیرنویس با تبدیل به UTF-8 خوانده شد")
        except Exception as e:
            print(f"❌ خطا در خواندن فایل زیرنویس حتی پس از تبدیل فرمت: {str(e)}")


# --- تعیین نام فایل خروجی ---
try:
    voice_code = speaker_voice.split("(")[1].split(")")[0] if "(" in speaker_voice else "FA"
    output_filename = f'final_dubbed_video_{voice_code}.mp4'
    if os.path.exists(output_filename):
        os.remove(output_filename)
        print(f"✔️ فایل خروجی قبلی '{output_filename}' حذف شد")
except NameError:
    print("⚠️ متغیر 'speaker_voice' تعریف نشده است. لطفاً سلول ساخت صدا را اجرا کنید.")
    output_filename = 'final_dubbed_video.mp4'


# --- شروع فرآیند ترکیب صدا ---
temp_dir = None
try:
    temp_dir = tempfile.mkdtemp()

    # روش 1: استفاده از فایل concat
    if audio_merge_method == "ffmpeg concat":
        print("⚙️ در حال استفاده از روش ffmpeg concat...")

        segment_info_file = os.path.join(temp_dir, "segments.txt")
        original_audio_path = os.path.join(temp_dir, "original_audio.wav")
        subprocess.run(['ffmpeg', '-i', input_video, '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2', '-y', original_audio_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        modified_original_audio = os.path.join(temp_dir, "original_audio_modified.wav")
        volume = original_audio_volume if keep_original_audio else 0.0
        subprocess.run(['ffmpeg', '-i', original_audio_path, '-filter:a', f'volume={volume}', '-y', modified_original_audio], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with open(segment_info_file, 'w') as f:
            for i, sub in enumerate(subs):
                start_time_ms = (sub.start.hours * 3600 + sub.start.minutes * 60 + sub.start.seconds) * 1000 + sub.start.milliseconds
                start_time_sec = start_time_ms / 1000.0
                segment_path = f"dubbing_project/dubbed_segments/dub_{i+1}.wav"
                if os.path.exists(segment_path):
                    f.write(f"file '{os.path.abspath(segment_path)}'\n")
        merged_audio = os.path.join(temp_dir, "merged_audio.wav")
        dubbing_audio = os.path.join(temp_dir, "dubbing_audio.wav")
        subprocess.run(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', segment_info_file, '-c', 'copy', '-y', dubbing_audio], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['ffmpeg', '-i', modified_original_audio, '-i', dubbing_audio, '-filter_complex', '[0:a][1:a]amix=inputs=2:duration=longest', '-y', merged_audio], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['ffmpeg', '-i', input_video, '-i', merged_audio, '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v', '-map', '1:a', '-y', output_filename], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"🎉 ویدیو با موفقیت با روش concat ساخته شد: {output_filename}")
# [removed_magic]         from google.colab import files
        files.download(output_filename)


    # روش 2: استفاده از filter_complex
    elif audio_merge_method == "ffmpeg filter_complex":
        print("⚙️ در حال استفاده از روش ffmpeg filter_complex...")

        if keep_original_audio:
            filter_complex = f"[0:a]volume={original_audio_volume}[original_audio];"
        else:
            filter_complex = "[0:a]volume=0[original_audio];"
        valid_segments = []
        input_files_list = ['-i', input_video]
        for i, sub in enumerate(subs):
            segment_path = f"dubbing_project/dubbed_segments/dub_{i+1}.wav"
            if os.path.exists(segment_path):
                try:
                    start_time_ms = (sub.start.hours * 3600 + sub.start.minutes * 60 + sub.start.seconds) * 1000 + sub.start.milliseconds
                    if start_time_ms < 0: start_time_ms = 0
                    filter_complex += f"[{i+1}:a]adelay={start_time_ms}|{start_time_ms}[a{i+1}];"
                    valid_segments.append(i+1)
                    input_files_list.append('-i')
                    input_files_list.append(segment_path)
                except Exception as e:
                    print(f"⚠️ رد کردن سگمنت {i+1} به دلیل مشکل: {str(e)}")
        if valid_segments:
            merge_command = "[original_audio]"
            for i in valid_segments:
                merge_command += f"[a{i}]"
            merge_command += f"amix=inputs={len(valid_segments) + 1}:normalize=0[aout]"
            filter_complex += merge_command
            command = ['ffmpeg', '-y'] + input_files_list + ['-filter_complex', filter_complex, '-map', '0:v', '-map', '[aout]', '-c:v', 'copy', '-c:a', 'aac', output_filename]
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ خطای ffmpeg (filter_complex):")
                print(result.stderr)
                raise Exception("فایل خروجی با filter_complex ساخته نشد!")
            else:
                print(f"🎉 ویدیو با موفقیت با روش filter_complex ساخته شد: {output_filename}")
# [removed_magic]                 from google.colab import files
                files.download(output_filename)
        else:
            raise Exception("هیچ سگمنت صوتی معتبری یافت نشد!")

    # روش 3: استفاده از pydub
    elif audio_merge_method == "pydub":
        print("⚙️ در حال استفاده از روش pydub...")
        original_audio_path = os.path.join(temp_dir, "original_audio.wav")
        subprocess.run([
            'ffmpeg', '-i', input_video, '-vn',
            '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2',
            '-y', original_audio_path
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        original_audio = AudioSegment.from_file(original_audio_path)
        if keep_original_audio:
            volume_reduction = - (60 * (1 - original_audio_volume))
            original_audio = original_audio + volume_reduction
        else:
            original_audio = AudioSegment.silent(duration=len(original_audio))

        final_audio = original_audio
        for i, sub in enumerate(subs):
            segment_path = f"dubbing_project/dubbed_segments/dub_{i+1}.wav"
            if os.path.exists(segment_path):
                try:
                    segment_audio = AudioSegment.from_file(segment_path)
                    start_time_ms = (sub.start.hours * 3600 + sub.start.minutes * 60 + sub.start.seconds) * 1000 + sub.start.milliseconds
                    if start_time_ms < 0: start_time_ms = 0
                    final_audio = final_audio.overlay(segment_audio, position=start_time_ms)
                except Exception as e:
                    print(f"⚠️ خطا در اضافه کردن سگمنت {i+1}: {str(e)}")

        merged_audio_path = os.path.join(temp_dir, "merged_audio.wav")
        final_audio.export(merged_audio_path, format="wav")

        subprocess.run([
            'ffmpeg', '-i', input_video, '-i', merged_audio_path,
            '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v', '-map', '1:a',
            '-y', output_filename
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print(f"\n🎉 ویدیو با موفقیت با روش pydub ساخته شد: {output_filename}")


        image_url = 'https://huggingface.co/Toolsai/dubtest/resolve/main/newgolden.png'
        youtube_channel_url = 'https://youtube.com/@aigolden'
        html_code = f'''
        <div style="text-align: center; border: 2px solid #e0e0e0; padding: 15px; border-radius: 12px; background-color: #f9f9f9; max-width: 350px; margin: auto;">
            <a href="{youtube_channel_url}" target="_blank" title="رفتن به کانال یوتیوب AIGOLDEN">
                <img src="{image_url}" alt="AIGOLDEN YouTube Channel" style="max-width: 100%; height: auto; border-radius: 8px;">
            </a>
            <p style="font-size: 16px; font-family: 'Vazir', sans-serif; margin-top: 15px; color: #333;">
                برای مشاهده آموزش‌های بیشتر، ما را در یوتیوب دنبال کنید.
            </p>
            <a href="{youtube_channel_url}" target="_blank" style="text-decoration: none; display: inline-block; background-color: #FF0000; color: white; padding: 10px 20px; border-radius: 8px; font-weight: bold; font-family: 'Vazir', sans-serif; margin-top: 10px;">
                🚀 دنبال کردن در یوتیوب
            </a>
        </div>
        '''
        display(HTML(html_code))


        print("\n📥 در حال آماده‌سازی فایل برای دانلود...")
# [removed_magic]         from google.colab import files
        files.download(output_filename)

except Exception as e:
    print(f"❌ یک خطای کلی در فرآیند ترکیب نهایی رخ داد: {str(e)}")
    # Fallback logic for pydub if other methods fail
    if audio_merge_method != 'pydub':
        print("⚠️ خطایی در روش انتخابی رخ داد، در حال امتحان روش pydub...")

finally:
    if temp_dir and os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        print("🧹 فایل‌های موقت پاک شدند.")

# --- Cell 9 ---

#@title دانلود فایل صوتی کامل دوبله (با سرعت عادی)
import os
import glob
from pydub import AudioSegment
# [removed_magic] from google.colab import files
import re

segments_folder = "dubbing_project/dubbed_segments"
output_audio_filename = "final_normal_speed_dub.mp3"

print(f"⚙️ در حال جستجو برای فایل‌های صوتی در پوشه: {segments_folder}")


temp_files = glob.glob(os.path.join(segments_folder, "temp_*.wav"))

if not temp_files:
    print("❌ هیچ فایل صوتی با سرعت عادی یافت نشد.")
    print("💡 لطفاً ابتدا سلول ۶ (ساخت سگمنت‌های صوتی) را اجرا کنید و مطمئن شوید که خط مربوط به حذف فایل‌های موقت را کامنت کرده‌اید.")
else:
    # مرتب‌سازی عددی فایل‌ها برای اطمینان از ترتیب صحیح (مثلا temp_1, temp_2, ..., temp_10)
    temp_files.sort(key=lambda f: int(re.search(r'temp_(\d+)', f).group(1)))

    print(f"✔️ {len(temp_files)} فایل صوتی با سرعت عادی پیدا شد. در حال ادغام...")

    # ادغام فایل‌ها با استفاده از pydub
    combined_audio = AudioSegment.empty()
    for file_path in temp_files:
        try:
            segment = AudioSegment.from_file(file_path)
            combined_audio += segment
        except Exception as e:
            print(f"⚠️ خطا در خواندن فایل {os.path.basename(file_path)}: {e}")

    # ذخیره فایل نهایی با فرمت MP3 برای حجم کمتر
    try:
        combined_audio.export(output_audio_filename, format="mp3", bitrate="192k")
        print(f"\n🎉 فایل صوتی کامل با نام '{output_audio_filename}' با موفقیت ایجاد شد.")
        print("📥 در حال آماده‌سازی برای دانلود...")
        files.download(output_audio_filename)
    except Exception as e:
        print(f"❌ خطا در ذخیره فایل نهایی: {e}")

# --- Cell 10 ---
#@title پاکسازی فایل‌های جلسه قبلی
# [removed_magic] !rm -rf /content/*

