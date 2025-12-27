#!/usr/bin/env python3
"""
تست اتصال به Azure OpenAI
Test Azure OpenAI Connection
"""

import requests
import json

# تنظیمات Azure OpenAI
AZURE_ENDPOINT = "https://nersi-mjop93nv-eastus2.openai.azure.com"
AZURE_API_KEY = ""
AZURE_MODEL = "grok-4-fast-reasoning"

def test_azure_connection():
    """تست اتصال به Azure OpenAI"""
    try:
        # ساخت URL کامل
        url = f"{AZURE_ENDPOINT.rstrip('/')}/openai/v1/chat/completions"
        
        headers = {
            'Content-Type': 'application/json',
            'api-key': AZURE_API_KEY
        }
        
        # درخواست تست ساده
        data = {
            'model': AZURE_MODEL,
            'messages': [
                {'role': 'user', 'content': 'Hello, this is a test message. Please respond with "Connection successful!"'}
            ],
            'max_tokens': 50
        }
        
        print(f"🔍 در حال تست اتصال به Azure OpenAI...")
        print(f"   Endpoint: {url}")
        print(f"   Model: {AZURE_MODEL}")
        print()
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ اتصال موفقیت‌آمیز بود!")
            print(f"   Status Code: {response.status_code}")
            
            if 'choices' in result and len(result['choices']) > 0:
                message = result['choices'][0]['message']['content']
                print(f"   پاسخ مدل: {message}")
            
            print()
            print("📊 اطلاعات کامل پاسخ:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return True
        else:
            print(f"❌ خطای HTTP {response.status_code}")
            print(f"   پاسخ: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ خطا در اتصال: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_azure_connection()
    exit(0 if success else 1)
