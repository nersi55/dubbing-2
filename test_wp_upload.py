import os
import sys
from wordpress_uploader import WordPressUploader

def test_connection():
    WP_URL = "https://cepmjgfj.us-west-1.clawcloudrun.com/"
    WP_USER = "admin"
    WP_PASS = "Fy)VLABpB6fyuXWK)Gtest"
    
    print(f"🔍 Testing connection to {WP_URL}...")
    try:
        uploader = WordPressUploader(WP_URL, WP_USER, WP_PASS)
        print("✅ Client initialized.")
        
        # Create a tiny test file
        test_file = "wp_test_upload.txt"
        with open(test_file, "w") as f:
            f.write("This is a test upload for WordPress XML-RPC integration.")
        
        print(f"📡 Attempting to upload {test_file}...")
        result = uploader.upload_file(os.path.abspath(test_file))
        
        if result and 'url' in result:
            print(f"🚀 Success! File uploaded to: {result['url']}")
            # Clean up
            os.remove(test_file)
            return True
        else:
            print("❌ Upload failed. No URL in response.")
            return False
            
    except Exception as e:
        print(f"❌ Connection/Upload test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
