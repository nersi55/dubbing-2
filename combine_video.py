#!/usr/bin/env python3
"""
برنامه ترکیب ویدیوها - Video Merger
این برنامه چند ویدیو را به صورت متوالی به هم می‌چسباند
"""

import subprocess
import os
import sys
from pathlib import Path
from typing import List, Optional, Set, Tuple
import tempfile
import shutil
import random
import datetime
import json

def get_video_duration(video_path: str) -> float:
    """
    دریافت مدت زمان ویدیو به ثانیه
    
    Args:
        video_path: مسیر فایل ویدیو
    
    Returns:
        مدت زمان به ثانیه، 0 اگر خطا داشت
    """
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format',
            video_path
        ], capture_output=True, text=True, check=True)
        
        import json
        video_info = json.loads(result.stdout)
        return float(video_info['format']['duration'])
    except Exception:
        return 0.0

def format_time(seconds: float) -> str:
    """تبدیل ثانیه به فرمت MM:SS"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def parse_duration(duration_str: str) -> Optional[float]:
    """
    تبدیل مدت زمان از فرمت‌های مختلف به ثانیه
    
    فرمت‌های پشتیبانی شده:
    - "37" یا "37s" = 37 ثانیه
    - "1:33" = 1 دقیقه و 33 ثانیه
    - "0:37" = 37 ثانیه
    """
    duration_str = duration_str.strip().lower()
    
    # اگر فقط عدد است، به عنوان ثانیه در نظر بگیر
    if duration_str.replace('.', '').replace('s', '').isdigit():
        if 's' in duration_str:
            return float(duration_str.replace('s', ''))
        return float(duration_str)
    
    # اگر به فرمت m:s است
    if ':' in duration_str:
        parts = duration_str.split(':')
        if len(parts) == 2:
            minutes = float(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
    
    return None

def trim_video_to_duration(input_path: str, output_path: str, max_duration: float) -> bool:
    """
    برش ویدیو به مدت زمان مشخص
    
    Args:
        input_path: مسیر ویدیوی ورودی
        output_path: مسیر ویدیوی خروجی
        max_duration: حداکثر مدت زمان (ثانیه)
    """
    try:
        # تلاش با کپی کردن کدک‌ها (سریع‌تر)
        subprocess.run([
            'ffmpeg',
            '-i', input_path,
            '-t', str(max_duration),
            '-c', 'copy',
            '-avoid_negative_ts', 'make_zero',
            '-y',
            output_path
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        # اگر با copy نشد، با بازکدگذاری تلاش کن
        try:
            subprocess.run([
                'ffmpeg',
                '-i', input_path,
                '-t', str(max_duration),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'fast',
                '-crf', '23',
                '-y',
                output_path
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            return False

def find_video_file(filename: str, search_folders: List[str] = None) -> Optional[str]:
    """
    پیدا کردن فایل ویدیو در دایرکتوری‌های مختلف
    
    Args:
        filename: نام فایل
        search_folders: لیست فولدرهای جستجو (پیش‌فرض: دایرکتوری جاری و video)
    
    Returns:
        مسیر کامل فایل یا None اگر پیدا نشد
    """
    if search_folders is None:
        search_folders = [".", "video"]
    
    for folder in search_folders:
        full_path = Path(folder) / filename
        if full_path.exists():
            return str(full_path.absolute())
    
    return None

def get_combination_key(video_paths: List[str]) -> str:
    """
    تولید کلید یکتای یک ترکیب بر اساس نام فایل‌ها
    
    Args:
        video_paths: لیست مسیرهای ویدیو
    
    Returns:
        رشته کلید (مثلاً "1.mp4,2.mp4")
    """
    filenames = [os.path.basename(path) for path in sorted(video_paths)]
    return ",".join(filenames)

def load_used_combinations(history_file: str = "video/combinations_history.json") -> Set[str]:
    """
    بارگذاری لیست ترکیب‌های استفاده شده
    
    Args:
        history_file: مسیر فایل تاریخچه
    
    Returns:
        مجموعه کلیدهای ترکیب‌های استفاده شده
    """
    history_path = Path(history_file)
    if not history_path.exists():
        return set()
    
    try:
        with open(history_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return set(data.get('combinations', []))
    except Exception:
        return set()

def save_combination(combination_key: str, history_file: str = "video/combinations_history.json") -> None:
    """
    ذخیره یک ترکیب جدید در تاریخچه
    
    Args:
        combination_key: کلید ترکیب
        history_file: مسیر فایل تاریخچه
    """
    history_path = Path(history_file)
    history_path.parent.mkdir(parents=True, exist_ok=True)
    
    # بارگذاری ترکیب‌های موجود
    used_combinations = load_used_combinations(history_file)
    
    # اضافه کردن ترکیب جدید
    used_combinations.add(combination_key)
    
    # ذخیره
    try:
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump({
                'combinations': sorted(list(used_combinations)),
                'last_updated': datetime.datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ خطا در ذخیره تاریخچه: {e}")

def is_combination_used(combination_key: str, history_file: str = "video/combinations_history.json") -> bool:
    """
    بررسی اینکه آیا یک ترکیب قبلاً استفاده شده یا نه
    
    Args:
        combination_key: کلید ترکیب
        history_file: مسیر فایل تاریخچه
    
    Returns:
        True اگر قبلاً استفاده شده
    """
    used_combinations = load_used_combinations(history_file)
    return combination_key in used_combinations

def select_random_videos(target_duration: float, video_paths: List[str], 
                         min_videos: int = 2, max_videos: int = 3, 
                         tolerance: float = 30.0,
                         exclude_used: bool = True) -> Optional[List[str]]:
    """
    انتخاب رندوم ویدیوها که مجموع مدت زمانشان نزدیک به target_duration باشد
    
    Args:
        target_duration: مدت زمان هدف (ثانیه)
        video_paths: لیست تمام ویدیوهای موجود
        min_videos: حداقل تعداد ویدیو
        max_videos: حداکثر تعداد ویدیو
        tolerance: تفاوت مجاز از مدت زمان هدف (ثانیه)
        exclude_used: آیا ترکیب‌های استفاده شده را رد کند
    
    Returns:
        لیست ویدیوهای انتخاب شده یا None اگر هیچ ترکیب جدیدی پیدا نشد
    """
    if not video_paths:
        return None
    
    # بارگذاری ترکیب‌های استفاده شده
    used_combinations = set()
    if exclude_used:
        used_combinations = load_used_combinations()
    
    # دریافت مدت زمان هر ویدیو
    video_durations = []
    for video_path in video_paths:
        duration = get_video_duration(video_path)
        if duration > 0:
            video_durations.append((video_path, duration))
    
    if not video_durations:
        return None
    
    # تلاش برای پیدا کردن ترکیب مناسب
    best_combination = None
    best_diff = float('inf')
    best_over_target = None  # بهترین ترکیبی که بیشتر از target است
    
    # چندین تلاش برای پیدا کردن ترکیب خوب و جدید
    max_attempts = 200  # افزایش تلاش‌ها برای پیدا کردن ترکیب جدید
    for attempt in range(max_attempts):
        # انتخاب تعداد ویدیو به صورت رندوم
        num_videos = random.randint(min_videos, max_videos)
        
        # بررسی اینکه آیا تعداد کافی ویدیو داریم
        if num_videos > len(video_durations):
            num_videos = len(video_durations)
        
        # انتخاب رندوم ویدیوها
        selected = random.sample(video_durations, num_videos)
        selected_paths = [path for path, _ in selected]
        
        # بررسی تکراری بودن
        combination_key = get_combination_key(selected_paths)
        if exclude_used and combination_key in used_combinations:
            continue  # این ترکیب قبلاً استفاده شده، بعدی را امتحان کن
        
        total_duration = sum(duration for _, duration in selected)
        diff = abs(total_duration - target_duration)
        
        # اگر دقیقاً در محدوده tolerance باشد، عالی است
        if diff <= tolerance:
            return selected_paths
        
        # اگر بیشتر از target باشد و در محدوده tolerance+10 باشد، خیلی خوب است
        if total_duration >= target_duration and (total_duration - target_duration) <= (tolerance + 10):
            if best_over_target is None or (total_duration - target_duration) < (sum(get_video_duration(p) for p in best_over_target) - target_duration):
                best_over_target = selected_paths
        
        # اگر بهترین ترکیب تا حالا بود، ذخیره کن
        if diff < best_diff:
            best_diff = diff
            best_combination = selected_paths
    
    # اولویت با ترکیبی که بیشتر از target است (می‌توانیم برش بدهم)
    if best_over_target:
        combination_key = get_combination_key(best_over_target)
        if not exclude_used or combination_key not in used_combinations:
            return best_over_target
    
    # اگر ترکیب عالی پیدا نشد، بهترین را برگردان (اگر جدید باشد)
    if best_combination:
        combination_key = get_combination_key(best_combination)
        if not exclude_used or combination_key not in used_combinations:
            # اگر مجموع کمتر از target است، سعی کن یک ویدیوی دیگر اضافه کنی
            current_total = sum(get_video_duration(p) for p in best_combination)
            if current_total < target_duration:
                remaining_duration = target_duration - current_total
                # پیدا کردن ویدیوی مناسب برای اضافه کردن
                available = [v for v, d in video_durations 
                            if v not in best_combination and 
                            (v, d) not in [(p, get_video_duration(p)) for p in best_combination]]
                if available:
                    # انتخاب ویدیویی که می‌تواند gap را پر کند
                    for video_path, duration in available:
                        if duration >= remaining_duration:
                            extended = best_combination + [video_path]
                            extended_key = get_combination_key(extended)
                            if not exclude_used or extended_key not in used_combinations:
                                return extended
                    # اگر هیچ ویدیویی مناسب نبود، یک ویدیوی رندوم اضافه کن
                    if available:
                        extended = best_combination + [random.choice(available)[0]]
                        extended_key = get_combination_key(extended)
                        if not exclude_used or extended_key not in used_combinations:
                            return extended
            return best_combination
    
    # در نهایت، چند تا رندوم برگردان (فقط اگر جدید باشد)
    for attempt in range(50):
        num_videos = random.randint(min_videos, min(max_videos + 1, len(video_durations)))
        if num_videos > len(video_durations):
            num_videos = len(video_durations)
        
        selected = random.sample(video_durations, num_videos)
        selected_paths = [path for path, _ in selected]
        
        combination_key = get_combination_key(selected_paths)
        if not exclude_used or combination_key not in used_combinations:
            return selected_paths
    
    # اگر هیچ ترکیب جدیدی پیدا نشد
    return None

def get_videos_from_folder(folder_path: str = "video", exclude_output_files: bool = True) -> Optional[List[str]]:
    """
    دریافت همه فایل‌های ویدیویی از یک فولدر
    
    Args:
        folder_path: مسیر فولدر
    
    Returns:
        لیست مسیرهای فایل‌های ویدیویی یا None اگر فولدر وجود نداشت
    """
    video_folder = Path(folder_path)
    
    if not video_folder.exists() or not video_folder.is_dir():
        return None
    
    # فرمت‌های ویدیویی متداول
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v', '.webm']
    
    # پیدا کردن همه فایل‌های ویدیویی
    video_files = []
    for ext in video_extensions:
        video_files.extend(list(video_folder.glob(f'*{ext}')))
        video_files.extend(list(video_folder.glob(f'*{ext.upper()}')))
    
    if not video_files:
        return None
    
    # حذف فایل‌های خروجی احتمالی
    if exclude_output_files:
        output_keywords = ['output', 'combined', 'final', 'merged', 'result']
        video_files = [
            v for v in video_files 
            if not any(keyword in v.name.lower() for keyword in output_keywords)
        ]
    
    if not video_files:
        return None
    
    # مرتب‌سازی بر اساس نام فایل (برای ترتیب منطقی)
    video_files = sorted(video_files, key=lambda x: x.name)
    
    # تبدیل به رشته
    return [str(v) for v in video_files]

def combine_videos(video_paths: List[str], output_path: str, max_duration: Optional[float] = None) -> bool:
    """
    ترکیب چند ویدیو به صورت متوالی
    
    Args:
        video_paths: لیست مسیرهای فایل‌های ویدیویی
        output_path: مسیر فایل خروجی
        max_duration: حداکثر مدت زمان ویدیو نهایی به ثانیه (اختیاری)
    
    Returns:
        True اگر موفقیت‌آمیز بود، False در غیر این صورت
    """
    # بررسی وجود فایل‌ها و پیدا کردن مسیر صحیح
    resolved_paths = []
    for video_path in video_paths:
        if os.path.exists(video_path):
            resolved_paths.append(video_path)
        else:
            # جستجو در فولدر video
            found_path = find_video_file(os.path.basename(video_path))
            if found_path:
                print(f"💡 فایل '{os.path.basename(video_path)}' در فولدر 'video' پیدا شد")
                resolved_paths.append(found_path)
            else:
                print(f"❌ فایل یافت نشد: {video_path}")
                print(f"   💡 جستجو در: ./, video/")
                return False
    
    video_paths = resolved_paths
    
    # ایجاد فایل لیست برای concat
    concat_file = Path("video_list.txt")
    
    try:
        # نوشتن لیست ویدیوها در فایل
        with open(concat_file, 'w', encoding='utf-8') as f:
            for video_path in video_paths:
                # تبدیل به مسیر مطلق و escape کردن برای ffmpeg
                abs_path = os.path.abspath(video_path)
                # استفاده از مسیر نسبی برای جلوگیری از مشکلات کاراکترهای خاص
                f.write(f"file '{abs_path}'\n")
        
        print("📝 فایل لیست ایجاد شد")
        print(f"📁 تعداد ویدیوها: {len(video_paths)}")
        
        # ترکیب ویدیوها با ffmpeg
        print("🎬 در حال ترکیب ویدیوها...")
        
        subprocess.run([
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-c', 'copy',  # کپی کردن کدک‌ها بدون بازکدگذاری (سریع‌تر)
            '-y',  # رونویسی خودکار فایل خروجی
            output_path
        ], check=True, capture_output=False)
        
        # اگر max_duration مشخص شده، ویدیو را برش بده
        temp_dir = None
        if max_duration is not None:
            current_duration = get_video_duration(output_path)
            
            if current_duration > max_duration:
                print(f"\n✂️ مدت زمان فعلی: {format_time(current_duration)}")
                print(f"✂️ برش به مدت زمان: {format_time(max_duration)}")
                
                # استفاده از فایل موقت برای برش
                temp_dir = Path(tempfile.mkdtemp())
                temp_output = str(temp_dir / "temp_combined.mp4")
                
                if trim_video_to_duration(output_path, temp_output, max_duration):
                    # جایگزین کردن فایل اصلی با فایل برش خورده
                    os.remove(output_path)  # حذف فایل اصلی
                    shutil.move(temp_output, output_path)
                    print(f"✅ ویدیو به مدت زمان {format_time(max_duration)} برش داده شد")
                else:
                    print("⚠️ خطا در برش ویدیو، فایل اصلی حفظ می‌شود")
                    if os.path.exists(temp_output):
                        os.remove(temp_output)
            else:
                minutes = int(current_duration // 60)
                seconds = int(current_duration % 60)
                print(f"\n⏱️ مدت زمان فعلی: {minutes} دقیقه و {seconds} ثانیه ({format_time(current_duration)})")
                print(f"💡 مدت زمان درخواستی: {format_time(max_duration)}")
                diff = max_duration - current_duration
                print(f"⚠️ ویدیو {format_time(diff)} کوتاه‌تر از مدت زمان درخواستی است")
                print(f"💡 برای رسیدن به مدت زمان دقیق، ویدیوهای بیشتری انتخاب کنید")
        
        # پاک کردن فایل موقت
        if temp_dir and temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
        
        print(f"✅ ویدیوها با موفقیت ترکیب شدند!")
        print(f"📁 فایل خروجی: {output_path}")
        
        # نمایش اطلاعات فایل خروجی
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
            print(f"📊 حجم فایل: {file_size:.2f} MB")
            
            # دریافت مدت زمان ویدیو نهایی
            final_duration = get_video_duration(output_path)
            if final_duration > 0:
                minutes = int(final_duration // 60)
                seconds = int(final_duration % 60)
                print(f"⏱️ مدت زمان نهایی: {minutes} دقیقه و {seconds} ثانیه ({format_time(final_duration)})")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ خطا در ترکیب ویدیوها: {e}")
        print("💡 شاید ویدیوها کدک‌های متفاوتی داشته باشند. در حال تلاش با بازکدگذاری...")
        
        # تلاش مجدد با بازکدگذاری
        try:
            subprocess.run([
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(concat_file),
                '-c:v', 'libx264',  # بازکدگذاری ویدیو
                '-c:a', 'aac',      # بازکدگذاری صدا
                '-preset', 'medium',  # سرعت/کیفیت
                '-crf', '23',       # کیفیت (18-28، کمتر = بهتر)
                '-y',
                output_path
            ], check=True, capture_output=False)
            
            print(f"✅ ویدیوها با بازکدگذاری ترکیب شدند!")
            print(f"📁 فایل خروجی: {output_path}")
            return True
            
        except subprocess.CalledProcessError as e2:
            print(f"❌ خطا در ترکیب با بازکدگذاری: {e2}")
            return False
            
    except Exception as e:
        print(f"❌ خطای غیرمنتظره: {e}")
        return False
        
    finally:
        # پاک کردن فایل موقت
        if concat_file.exists():
            concat_file.unlink()
            print("🧹 فایل موقت پاک شد")


def main():
    """تابع اصلی"""
    print("=" * 60)
    print("🎬 برنامه ترکیب ویدیوها")
    print("=" * 60)
    print()
    
    video_paths = []
    output_path = None
    max_duration = None
    
    # اول بررسی کن که آیا فولدر video وجود دارد یا نه
    videos_from_folder = get_videos_from_folder("video")
    
    random_mode = False
    
    if len(sys.argv) > 1:
        args = sys.argv[1:]
        
        # بررسی حالت رندوم
        if '--random' in args or '-r' in args:
            random_mode = True
            random_flag = '--random' if '--random' in args else '-r'
            args.remove(random_flag)
            print("🎲 حالت رندوم فعال شد")
        
        # بررسی آرگومان --duration
        if '--duration' in args or '-d' in args:
            duration_flag = '--duration' if '--duration' in args else '-d'
            duration_idx = args.index(duration_flag)
            
            if duration_idx + 1 < len(args):
                duration_str = args[duration_idx + 1]
                max_duration = parse_duration(duration_str)
                if max_duration is None:
                    print(f"⚠️ مدت زمان '{duration_str}' نامعتبر است، نادیده گرفته می‌شود")
                    max_duration = None
                else:
                    print(f"⏱️ مدت زمان نهایی: {format_time(max_duration)}")
                
                # حذف --duration و مقدار آن از لیست
                args.pop(duration_idx)  # حذف --duration
                args.pop(duration_idx)  # حذف مقدار duration
        
        # اگر حالت رندوم فعال است
        if random_mode:
            if not videos_from_folder:
                print("❌ فولدر 'video' یافت نشد!")
                print("💡 لطفاً فایل‌های ویدیو را در فولدر 'video' قرار دهید")
                return
            
            if max_duration is None:
                print("❌ در حالت رندوم باید مدت زمان را با -d یا --duration مشخص کنید")
                print("💡 مثال: python combine_video.py -r -d 240 output.mp4")
                return
            
            # بارگذاری ترکیب‌های استفاده شده برای نمایش
            used_combinations = load_used_combinations()
            if used_combinations:
                print(f"📝 {len(used_combinations)} ترکیب قبلاً استفاده شده است")
            
            # انتخاب رندوم ویدیوها
            print(f"🔍 جستجو در {len(videos_from_folder)} ویدیو...")
            # استفاده از tolerance کمتر برای انتخاب دقیق‌تر
            selected_videos = select_random_videos(
                max_duration, 
                videos_from_folder,
                min_videos=2,
                max_videos=4,  # افزایش max_videos برای امکان اضافه کردن ویدیوی بیشتر
                tolerance=15.0,  # کاهش tolerance برای انتخاب دقیق‌تر
                exclude_used=True
            )
            
            if not selected_videos:
                print("❌ نتوانستم ترکیب جدیدی پیدا کنم!")
                print("💡 همه ترکیب‌های ممکن قبلاً استفاده شده‌اند")
                print(f"💡 تعداد ترکیب‌های استفاده شده: {len(used_combinations)}")
                return
            
            video_paths = selected_videos
            print(f"\n🎲 انتخاب شده {len(video_paths)} ویدیو به صورت رندوم:")
            total_selected_duration = 0
            for i, vpath in enumerate(video_paths, 1):
                dur = get_video_duration(vpath)
                total_selected_duration += dur
                print(f"   {i}. {os.path.basename(vpath)} ({format_time(dur)})")
            print(f"   📊 مجموع: {format_time(total_selected_duration)}")
            
            # اگر مجموع کمتر از مدت زمان درخواستی است، سعی کن ویدیوی دیگری اضافه کنی
            if total_selected_duration < max_duration:
                remaining = max_duration - total_selected_duration
                print(f"\n💡 مجموع {format_time(total_selected_duration)} کمتر از مدت زمان درخواستی ({format_time(max_duration)}) است")
                print(f"🔍 جستجو برای اضافه کردن ویدیوی دیگری...")
                
                # پیدا کردن ویدیوهای مناسب که قبلاً استفاده نشده‌اند
                available = [(v, get_video_duration(v)) for v in videos_from_folder 
                            if v not in video_paths]
                available = [v for v, d in available if d > 0]
                
                if available:
                    # تلاش برای پیدا کردن ویدیویی که می‌تواند gap را پر کند
                    best_addition = None
                    best_addition_diff = float('inf')
                    
                    for video_path in available:
                        duration = get_video_duration(video_path)
                        new_total = total_selected_duration + duration
                        diff = abs(new_total - max_duration)
                        
                        # اگر با این ویدیو به target برسیم یا از آن بیشتر شویم، عالی است
                        if new_total >= max_duration and diff < best_addition_diff:
                            best_addition = video_path
                            best_addition_diff = diff
                            if diff <= 10:  # اگر خیلی نزدیک است، همین را بردار
                                break
                    
                    if best_addition:
                        video_paths.append(best_addition)
                        new_dur = get_video_duration(best_addition)
                        total_selected_duration += new_dur
                        print(f"   ➕ اضافه شد: {os.path.basename(best_addition)} ({format_time(new_dur)})")
                        print(f"   📊 مجموع جدید: {format_time(total_selected_duration)}")
                    else:
                        # اگر هیچ ویدیوی مناسبی پیدا نشد، یک ویدیوی رندوم اضافه کن
                        added = random.choice(available)
                        new_dur = get_video_duration(added)
                        video_paths.append(added)
                        total_selected_duration += new_dur
                        print(f"   ➕ اضافه شد (رندوم): {os.path.basename(added)} ({format_time(new_dur)})")
                        print(f"   📊 مجموع جدید: {format_time(total_selected_duration)}")
                else:
                    print(f"   ⚠️ هیچ ویدیوی دیگری برای اضافه کردن یافت نشد")
            
            # اگر خروجی مشخص نشده، یک نام رندوم تولید کن
            if args:
                output_path = args[-1]
            else:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"video/random_combined_{timestamp}.mp4"
                print(f"📁 فایل خروجی: {output_path}")
        
        # حالت عادی (غیر رندوم)
        elif len(args) > 0:
            # اگر فقط یک آرگومان داشت، آن خروجی است (نه ورودی)
            if len(args) == 1:
                print("❌ لطفاً حداقل یک فایل ویدیو و نام خروجی را وارد کنید")
                print("💡 مثال: python combine_video.py video1.mp4 video2.mp4 output.mp4")
                print("💡 یا با مدت زمان: python combine_video.py video1.mp4 video2.mp4 output.mp4 --duration 37")
                print("💡 یا حالت رندوم: python combine_video.py -r -d 240 output.mp4")
                return
            
            # آخرین آرگومان خروجی است
            output_path = args[-1]
            video_paths = args[:-1]  # همه بجز آخر
        else:
            # اگر هیچ آرگومانی نداشت (فقط فلگ‌ها)
            if random_mode:
                print("❌ در حالت رندوم باید مدت زمان را مشخص کنید")
                return
    elif videos_from_folder:
        # استفاده از فایل‌های فولدر video
        video_paths = videos_from_folder
        print(f"📁 پیدا کردن {len(video_paths)} ویدیو در فولدر 'video':")
        for i, vpath in enumerate(video_paths, 1):
            print(f"   {i}. {os.path.basename(vpath)}")
        print()
        output_path = input("📁 نام فایل خروجی (مثال: combined_video.mp4): ").strip()
        if not output_path:
            output_path = "combined_video.mp4"
        
        # پرسیدن مدت زمان نهایی
        duration_input = input("\n⏱️ مدت زمان نهایی ویدیو (ثانیه یا MM:SS، خالی برای بدون محدودیت): ").strip()
        if duration_input:
            max_duration = parse_duration(duration_input)
            if max_duration is None:
                print(f"⚠️ مدت زمان '{duration_input}' نامعتبر است، بدون محدودیت ادامه می‌دهیم")
                max_duration = None
            else:
                print(f"✅ مدت زمان نهایی: {format_time(max_duration)}")
    else:
        # حالت تعاملی
        print("📁 لطفاً مسیر فایل‌های ویدیویی را وارد کنید:")
        print("   (برای پایان، یک خط خالی وارد کنید)")
        print()
        
        while True:
            path = input(f"ویدیو #{len(video_paths) + 1}: ").strip()
            if not path:
                break
            video_paths.append(path)
        
        if not video_paths:
            print("❌ هیچ ویدیویی وارد نشد!")
            return
        
        output_path = input("\n📁 نام فایل خروجی (مثال: combined_video.mp4): ").strip()
        if not output_path:
            output_path = "combined_video.mp4"
        
        # پرسیدن مدت زمان نهایی
        duration_input = input("\n⏱️ مدت زمان نهایی ویدیو (ثانیه یا MM:SS، خالی برای بدون محدودیت): ").strip()
        if duration_input:
            max_duration = parse_duration(duration_input)
            if max_duration is None:
                print(f"⚠️ مدت زمان '{duration_input}' نامعتبر است، بدون محدودیت ادامه می‌دهیم")
                max_duration = None
            else:
                print(f"✅ مدت زمان نهایی: {format_time(max_duration)}")
    
    if not video_paths:
        print("❌ هیچ ویدیویی مشخص نشد!")
        print("\n💡 نحوه استفاده:")
        print("   python combine_video.py video1.mp4 video2.mp4 output.mp4")
        print("   python combine_video.py video1.mp4 video2.mp4 output.mp4 --duration 37")
        print("   python combine_video.py video1.mp4 video2.mp4 output.mp4 -d 43")
        print("   python combine_video.py -r -d 240 output.mp4  (حالت رندوم)")
        print("   python combine_video.py --random --duration 240 output.mp4")
        print("   python combine_video.py  (خودکار از فولدر 'video')")
        print("\n   فرمت‌های مدت زمان: 37, 37s, 0:37, 1:33, 240 (4 دقیقه)")
        return
    
    # بررسی وجود ffmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ ffmpeg نصب نشده است!")
        print("💡 لطفاً ffmpeg را نصب کنید:")
        print("   macOS: brew install ffmpeg")
        print("   Ubuntu/Debian: sudo apt install ffmpeg")
        print("   Windows: https://ffmpeg.org/download.html")
        return
    
    # ترکیب ویدیوها
    print()
    if max_duration:
        print(f"⏱️ محدودیت مدت زمان: {format_time(max_duration)}")
    success = combine_videos(video_paths, output_path, max_duration)
    
    if success:
        # ذخیره ترکیب در تاریخچه (اگر از فولدر video استفاده شده باشد)
        # بررسی اینکه آیا همه ویدیوها از فولدر video هستند
        all_from_video_folder = all(
            os.path.dirname(os.path.abspath(path)) == os.path.abspath("video") or 
            "video/" in os.path.abspath(path)
            for path in video_paths
        )
        
        if random_mode or (videos_from_folder and all_from_video_folder):
            combination_key = get_combination_key(video_paths)
            save_combination(combination_key)
            print(f"💾 ترکیب ذخیره شد: {combination_key}")
        
        print("\n🎉 کار تمام شد!")
    else:
        print("\n❌ خطا در ترکیب ویدیوها")
        sys.exit(1)


if __name__ == "__main__":
    main()