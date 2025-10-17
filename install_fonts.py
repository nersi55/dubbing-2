#!/usr/bin/env python3
"""
Vazirmatn Font Installer
نصب خودکار فونت Vazirmatn برای پروژه دوبله ویدیو
"""

import os
import sys
import platform
import subprocess
import urllib.request
import zipfile
import shutil
from pathlib import Path

class VazirmatnInstaller:
    def __init__(self):
        self.system = platform.system().lower()
        self.font_url = "https://github.com/rastikerdar/vazirmatn/releases/latest/download/vazirmatn.zip"
        self.temp_dir = Path("temp_fonts")
        self.fonts_installed = []
        
    def print_status(self, message, status="info"):
        """چاپ وضعیت نصب با رنگ‌بندی"""
        colors = {
            "info": "\033[94m",      # آبی
            "success": "\033[92m",   # سبز
            "warning": "\033[93m",   # زرد
            "error": "\033[91m",     # قرمز
            "reset": "\033[0m"       # بازنشانی
        }
        
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
        
        print(f"{colors.get(status, '')}{icons.get(status, '')} {message}{colors['reset']}")
    
    def download_fonts(self):
        """دانلود فونت‌های Vazirmatn"""
        try:
            self.print_status("در حال دانلود فونت Vazirmatn...", "info")
            
            # ایجاد پوشه موقت
            self.temp_dir.mkdir(exist_ok=True)
            
            # دانلود فایل
            zip_path = self.temp_dir / "vazirmatn.zip"
            urllib.request.urlretrieve(self.font_url, zip_path)
            
            self.print_status("دانلود کامل شد", "success")
            return zip_path
            
        except Exception as e:
            self.print_status(f"خطا در دانلود: {e}", "error")
            return None
    
    def extract_fonts(self, zip_path):
        """استخراج فونت‌ها از فایل ZIP"""
        try:
            self.print_status("در حال استخراج فونت‌ها...", "info")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
            
            # پیدا کردن فایل‌های TTF
            ttf_dir = self.temp_dir / "fonts" / "ttf"
            if ttf_dir.exists():
                ttf_files = list(ttf_dir.glob("*.ttf"))
                self.print_status(f"تعداد فونت‌های یافت شده: {len(ttf_files)}", "success")
                return ttf_files
            else:
                self.print_status("پوشه فونت‌ها یافت نشد", "error")
                return []
                
        except Exception as e:
            self.print_status(f"خطا در استخراج: {e}", "error")
            return []
    
    def get_font_directories(self):
        """دریافت مسیرهای نصب فونت بر اساس سیستم عامل"""
        if self.system == "windows":
            return [
                os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts"),
                os.path.expanduser("~/Fonts"),
                "C:/Windows/Fonts"
            ]
        elif self.system == "darwin":  # macOS
            return [
                os.path.expanduser("~/Library/Fonts"),
                "/Library/Fonts",
                "/System/Library/Fonts"
            ]
        else:  # Linux
            return [
                os.path.expanduser("~/.fonts"),
                os.path.expanduser("~/.local/share/fonts"),
                "/usr/share/fonts/truetype",
                "/usr/local/share/fonts"
            ]
    
    def install_fonts(self, ttf_files):
        """نصب فونت‌ها در سیستم و پوشه محلی پروژه"""
        # اولویت اول: نصب در پوشه محلی پروژه
        local_fonts_dir = os.path.join(os.path.dirname(__file__), "fonts")
        
        try:
            os.makedirs(local_fonts_dir, exist_ok=True)
            self.print_status(f"نصب فونت‌ها در پوشه محلی: {local_fonts_dir}", "info")
            
            local_installed = 0
            for ttf_file in ttf_files:
                try:
                    target_path = os.path.join(local_fonts_dir, ttf_file.name)
                    shutil.copy2(ttf_file, target_path)
                    self.fonts_installed.append(target_path)
                    local_installed += 1
                    self.print_status(f"نصب شد (محلی): {ttf_file.name}", "success")
                except Exception as e:
                    self.print_status(f"خطا در نصب محلی {ttf_file.name}: {e}", "error")
            
            if local_installed > 0:
                self.print_status("فونت‌ها با موفقیت در پوشه محلی نصب شدند", "success")
                return True
                
        except Exception as e:
            self.print_status(f"خطا در ایجاد پوشه محلی: {e}", "error")
        
        # اولویت دوم: نصب در سیستم (برای سازگاری)
        font_dirs = self.get_font_directories()
        
        # پیدا کردن اولین مسیر قابل نوشتن
        target_dir = None
        for font_dir in font_dirs:
            try:
                os.makedirs(font_dir, exist_ok=True)
                if os.access(font_dir, os.W_OK):
                    target_dir = font_dir
                    break
            except:
                continue
        
        if not target_dir:
            self.print_status("هیچ مسیر قابل نوشتن برای فونت‌ها یافت نشد", "error")
            return False
        
        self.print_status(f"نصب فونت‌ها در سیستم: {target_dir}", "info")
        
        installed_count = 0
        for ttf_file in ttf_files:
            try:
                target_path = os.path.join(target_dir, ttf_file.name)
                shutil.copy2(ttf_file, target_path)
                self.fonts_installed.append(target_path)
                installed_count += 1
                self.print_status(f"نصب شد (سیستم): {ttf_file.name}", "success")
            except Exception as e:
                self.print_status(f"خطا در نصب سیستم {ttf_file.name}: {e}", "error")
        
        return installed_count > 0
    
    def verify_installation(self):
        """بررسی نصب فونت‌ها"""
        self.print_status("بررسی نصب فونت‌ها...", "info")
        
        # اولویت اول: بررسی فونت‌های محلی پروژه
        local_fonts_dir = os.path.join(os.path.dirname(__file__), "fonts")
        if os.path.exists(local_fonts_dir):
            for font_file in os.listdir(local_fonts_dir):
                if "vazirmatn" in font_file.lower() and font_file.endswith(".ttf"):
                    self.print_status(f"فونت محلی یافت شد: {os.path.join(local_fonts_dir, font_file)}", "success")
                    return True
        
        # اولویت دوم: بررسی فونت‌های سیستم
        font_dirs = self.get_font_directories()
        vazirmatn_found = False
        
        for font_dir in font_dirs:
            if os.path.exists(font_dir):
                for font_file in os.listdir(font_dir):
                    if "vazirmatn" in font_file.lower() and font_file.endswith(".ttf"):
                        vazirmatn_found = True
                        self.print_status(f"فونت سیستم یافت شد: {os.path.join(font_dir, font_file)}", "success")
                        break
                if vazirmatn_found:
                    break
        
        if not vazirmatn_found:
            self.print_status("فونت Vazirmatn یافت نشد. ممکن است نیاز به راه‌اندازی مجدد سیستم باشد.", "warning")
        
        return vazirmatn_found
    
    def cleanup(self):
        """پاک‌سازی فایل‌های موقت"""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                self.print_status("فایل‌های موقت پاک شدند", "info")
        except Exception as e:
            self.print_status(f"خطا در پاک‌سازی: {e}", "warning")
    
    def install(self):
        """اجرای کامل فرآیند نصب"""
        self.print_status("شروع نصب فونت Vazirmatn", "info")
        self.print_status(f"سیستم عامل: {platform.system()} {platform.release()}", "info")
        
        # بررسی وجود قبلی فونت
        if self.verify_installation():
            self.print_status("فونت Vazirmatn قبلاً نصب شده است", "success")
            return True
        
        # دانلود فونت‌ها
        zip_path = self.download_fonts()
        if not zip_path:
            return False
        
        # استخراج فونت‌ها
        ttf_files = self.extract_fonts(zip_path)
        if not ttf_files:
            return False
        
        # نصب فونت‌ها
        if not self.install_fonts(ttf_files):
            return False
        
        # پاک‌سازی
        self.cleanup()
        
        # بررسی نهایی
        if self.verify_installation():
            self.print_status("نصب فونت Vazirmatn با موفقیت انجام شد!", "success")
            self.print_status(f"تعداد فونت‌های نصب شده: {len(self.fonts_installed)}", "success")
            return True
        else:
            self.print_status("نصب کامل نشد. لطفاً دستی نصب کنید.", "error")
            return False

def main():
    """تابع اصلی"""
    print("🎨 نصب‌کننده فونت Vazirmatn")
    print("=" * 50)
    
    installer = VazirmatnInstaller()
    success = installer.install()
    
    if success:
        print("\n🎉 نصب با موفقیت انجام شد!")
        print("حالا می‌توانید از برنامه دوبله ویدیو استفاده کنید.")
    else:
        print("\n❌ نصب با خطا مواجه شد.")
        print("لطفاً دستی فونت را نصب کنید یا با پشتیبانی تماس بگیرید.")
        sys.exit(1)

if __name__ == "__main__":
    main()
