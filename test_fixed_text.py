#!/usr/bin/env python3
"""
تست فیلتر متن ثابت
Test fixed text filter
"""

import os
import platform
from dubbing_functions import VideoDubbingApp

def test_fixed_text_filter():
    """تست فیلتر متن ثابت"""
    print("🔤 تست فیلتر متن ثابت")
    print(f"سیستم عامل: {platform.system()}")
    print("-" * 50)
    
    # ایجاد نمونه از کلاس
    try:
        app = VideoDubbingApp("dummy_key")
    except:
        # اگر API key نیاز باشد، یک کلاس ساده ایجاد کن
        class TestApp:
            def __init__(self):
                self.work_dir = "dubbing_work"
                os.makedirs(self.work_dir, exist_ok=True)
            
            def _get_font_path(self, font_name):
                import platform
                import os
                system = platform.system()
                
                font_paths = {
                    "vazirmatn": [
                        os.path.join(os.path.dirname(__file__), "fonts", "Vazirmatn-Regular.ttf"),
                        os.path.join(os.path.dirname(__file__), "fonts", "Vazirmatn-Medium.ttf"),
                        os.path.join(os.path.dirname(__file__), "fonts", "Vazirmatn-Bold.ttf"),
                        "/usr/share/fonts/truetype/vazirmatn/Vazirmatn-Regular.ttf",
                        "/usr/share/fonts/opentype/vazirmatn/Vazirmatn-Regular.ttf",
                        "/usr/local/share/fonts/Vazirmatn-Regular.ttf",
                    ]
                }
                
                if font_name in font_paths:
                    for path in font_paths[font_name]:
                        if os.path.exists(path):
                            if font_name.lower() == 'vazirmatn' and system == 'Linux':
                                return "Vazirmatn"
                            return path
                
                if system == 'Linux':
                    return "Vazirmatn"
                return ""
            
            def _normalize_persian_text(self, text):
                """نرمال‌سازی متن فارسی"""
                # تبدیل کاراکترهای عربی به فارسی
                arabic_to_persian = {
                    'ي': 'ی', 'ك': 'ک', 'ة': 'ه', 'أ': 'ا', 'إ': 'ا',
                    'آ': 'آ', 'ؤ': 'و', 'ئ': 'ی', 'ء': 'ء'
                }
                
                for arabic, persian in arabic_to_persian.items():
                    text = text.replace(arabic, persian)
                
                return text
            
            def _color_to_hex(self, color_name):
                """تبدیل نام رنگ به فرمت hex"""
                color_map = {
                    "white": "ffffff",
                    "yellow": "00ffff",
                    "red": "0000ff",
                    "green": "00ff00",
                    "blue": "ff0000",
                    "black": "000000",
                    "orange": "00a5ff",
                    "purple": "ff00ff",
                    "pink": "ffc0cb",
                    "gray": "808080"
                }
                return color_map.get(color_name.lower(), "ffffff")
            
            def _create_fixed_text_filter(self, config):
                """ایجاد فیلتر FFmpeg برای متن ثابت"""
                try:
                    import platform
                    system = platform.system()
                    
                    # متن و تنظیمات
                    text = config['text']
                    fontsize = config['fontsize']
                    color = config['color']
                    margin_bottom = config['margin_bottom']
                    font_name = config.get('font', 'Arial')
                    
                    # نرمال‌سازی متن فارسی
                    normalized_text = self._normalize_persian_text(text)
                    
                    # پیدا کردن فونت
                    font_path = self._get_font_path(font_name)
                    if font_path and font_name.lower() == 'vazirmatn':
                        print(f"✅ فونت متن ثابت: {font_name} (فونت سیستم)")
                        final_font = font_name
                    elif font_path:
                        print(f"✅ فونت متن ثابت: {font_name} → {font_path}")
                        final_font = font_path
                    else:
                        print(f"⚠️ فونت متن ثابت: {font_name} (فونت سیستم)")
                        final_font = font_name
                    
                    # تنظیم موقعیت متن
                    position = config.get('position', 'bottom_center')
                    if position == 'bottom_center':
                        x_pos = '(w-text_w)/2'
                        y_pos = f'h-text_h-{margin_bottom}'
                    else:
                        x_pos = '(w-text_w)/2'
                        y_pos = f'h-text_h-{margin_bottom}'
                    
                    # تنظیم رنگ
                    color_hex = self._color_to_hex(color)
                    r = color_hex[4:6]
                    g = color_hex[2:4]
                    b = color_hex[0:2]
                    drawtext_color = f"0x{r}{g}{b}"
                    
                    # تنظیم فونت برای drawtext
                    if system == 'Linux':
                        font_param = f"fontfile='{final_font}'" if final_font.endswith(('.ttf', '.otf')) else f"font='{final_font}'"
                    else:
                        font_param = f"fontfile='{final_font}'" if final_font.endswith(('.ttf', '.otf')) else f"font='{final_font}'"
                    
                    # ساخت فیلتر drawtext
                    filter_parts = [
                        f"drawtext=text='{normalized_text}'",
                        font_param,
                        f"fontsize={fontsize}",
                        f"fontcolor={drawtext_color}",
                        f"x={x_pos}",
                        f"y={y_pos}",
                        "enable='between(t,0,999999)'"
                    ]
                    
                    filter_text = ':'.join(filter_parts)
                    return filter_text
                    
                except Exception as e:
                    print(f"❌ خطا در ایجاد فیلتر: {str(e)}")
                    return ""
        
        app = TestApp()
    
    # تست تنظیمات مختلف
    test_configs = [
        {
            "text": "متن تست فارسی",
            "font": "vazirmatn",
            "fontsize": 24,
            "color": "white",
            "margin_bottom": 20,
            "position": "bottom_center"
        },
        {
            "text": "Test English Text",
            "font": "Arial",
            "fontsize": 20,
            "color": "yellow",
            "margin_bottom": 30,
            "position": "bottom_center"
        }
    ]
    
    for i, config in enumerate(test_configs, 1):
        print(f"\n🔤 تست {i}: {config['text']}")
        print(f"   فونت: {config['font']}")
        print(f"   اندازه: {config['fontsize']}")
        print(f"   رنگ: {config['color']}")
        
        filter_text = app._create_fixed_text_filter(config)
        print(f"   فیلتر: {filter_text}")
        
        if filter_text:
            print("   ✅ فیلتر ایجاد شد")
        else:
            print("   ❌ خطا در ایجاد فیلتر")

if __name__ == "__main__":
    test_fixed_text_filter()