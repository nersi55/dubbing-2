import os
import boto3
import mimetypes
from botocore.config import Config

class S3Uploader:
    def __init__(self, access_key, secret_key, endpoint_url, region_name='us-west-1'):
        """
        Initialize the S3 client for Claw Cloud.
        """
        self.access_key = access_key
        self.secret_key = secret_key
        self.endpoint_url = endpoint_url
        self.region_name = region_name
        
        # Claw Cloud usually uses S3 compatible API
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            endpoint_url=self.endpoint_url,
            region_name=self.region_name,
            config=Config(signature_version='s3v4')
        )
        self.bucket_name = 'dubbing' # We will try to use 'dubbing' bucket or create it

    def ensure_bucket(self, bucket_name=None):
        """Check if bucket exists, if not create it."""
        b_name = bucket_name or self.bucket_name
        try:
            self.s3.head_bucket(Bucket=b_name)
            return True
        except:
            try:
                self.s3.create_bucket(Bucket=b_name)
                return True
            except Exception as e:
                print(f"❌ Error ensuring bucket: {e}")
                return False

    def test_connection(self):
        """
        درخواست لیست باکت‌ها برای تست اتصال اولیه
        """
        try:
            self.s3.list_buckets()
            return True, "اتصال به S3 برقرار شد."
        except Exception as e:
            return False, f"خطا در اتصال به S3: {str(e)}"

    def check_bucket(self, bucket_name):
        """
        بررسی وجود و دسترسی به باکت خاص
        """
        try:
            self.s3.head_bucket(Bucket=bucket_name)
            return True, f"باکت '{bucket_name}' در دسترس است."
        except Exception as e:
            return False, f"خطا در دسترسی به باکت '{bucket_name}': {str(e)}"

    def upload_file(self, file_path, bucket_name=None, object_name=None):
        """
        Upload a file to Claw Cloud Object Storage.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        b_name = bucket_name or self.bucket_name
        obj_name = object_name or os.path.basename(file_path)
        
        mime_type, _ = mimetypes.guess_type(file_path)
        content_type = mime_type or 'application/octet-stream'

        try:
            # Upload directly - if it fails due to bucket not existing, user will see error
            self.s3.upload_file(
                file_path, 
                b_name, 
                obj_name,
                ExtraArgs={'ContentType': content_type}
            )
            
            # Construct external URL
            external_base = "http://objectstorageapi.us-west-1.clawcloudrun.com"
            file_url = f"{external_base}/{b_name}/{obj_name}"
            
            return {
                'url': file_url,
                'bucket': b_name,
                'key': obj_name
            }
        except Exception as e:
            print(f"❌ Error uploading to S3: {e}")
            return None

    def upload_batch(self, file_paths, bucket_name=None):
        """
        Upload multiple files and return a dictionary of their URLs.
        """
        results = {}
        for path in file_paths:
            if not path or not os.path.exists(path):
                continue
            print(f"📡 Uploading {os.path.basename(path)} to Object Storage...")
            res = self.upload_file(path, bucket_name=bucket_name)
            if res and 'url' in res:
                results[os.path.basename(path)] = res['url']
                print(f"✅ Uploaded: {res['url']}")
            else:
                results[os.path.basename(path)] = None
                print(f"❌ Failed to upload {os.path.basename(path)}")
        return results

if __name__ == "__main__":
    # Test script usage with provided credentials
    ACCESS_KEY = "m9bth4qn"
    SECRET_KEY = "w46z8gspqb86m5l2"
    ENDPOINT = "http://objectstorageapi.us-west-1.clawcloudrun.com"
    
    uploader = S3Uploader(ACCESS_KEY, SECRET_KEY, ENDPOINT)
    # res = uploader.upload_file("test.mp4")
    # print(res)
