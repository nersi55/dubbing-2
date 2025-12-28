import os
import mimetypes
from wordpress_xmlrpc import Client, WordPressMedia
from wordpress_xmlrpc.methods import media

class WordPressUploader:
    def __init__(self, url, username, password):
        """
        Initialize the WordPress XML-RPC client.
        
        Args:
            url: The base URL of the WordPress site.
            username: WordPress admin username.
            password: WordPress admin password (or application password).
        """
        if not url.endswith('/xmlrpc.php'):
            if url.endswith('/'):
                url = url + 'xmlrpc.php'
            else:
                url = url + '/xmlrpc.php'
        
        self.url = url
        self.username = username
        self.password = password
        try:
            from wordpress_xmlrpc import Client
            self.client = Client(self.url, self.username, self.password)
        except Exception as e:
            print(f"❌ Error initializing WP Client: {e}")
            raise

    def upload_file(self, file_path):
        """
        Upload a file to the WordPress Media Library.
        
        Args:
            file_path: Absolute path to the file to upload.
            
        Returns:
            dict: Media information including 'id', 'file', 'url', 'type'.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        filename = os.path.basename(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # Prepare media data
        data = {
            'name': filename,
            'type': mime_type or 'application/octet-stream',
        }

        # Read file data
        with open(file_path, 'rb') as f:
            data['bits'] = f.read()

        # Upload to WordPress
        try:
            response = self.client.call(media.UploadFile(data))
            return response
        except Exception as e:
            print(f"❌ Error uploading to WordPress: {e}")
            return None

    def upload_batch(self, file_paths):
        """
        Upload multiple files and return a dictionary of their URLs.
        
        Args:
            file_paths: List of absolute paths to files.
            
        Returns:
            dict: Mapping of basename to uploaded URL.
        """
        results = {}
        for path in file_paths:
            if not path:
                continue
            print(f"📡 Uploading {os.path.basename(path)} to WordPress...")
            res = self.upload_file(path)
            if res and 'url' in res:
                results[os.path.basename(path)] = res['url']
                print(f"✅ Uploaded: {res['url']}")
            else:
                results[os.path.basename(path)] = None
                print(f"❌ Failed to upload {os.path.basename(path)}")
        return results

if __name__ == "__main__":
    # Test script usage
    WP_URL = "https://cepmjgfj.us-west-1.clawcloudrun.com/"
    WP_USER = "admin"
    WP_PASS = "Fy)VLABpB6fyuXWK)Gtest"
    
    uploader = WordPressUploader(WP_URL, WP_USER, WP_PASS)
    # Example test: uploader.upload_file("test.txt")
