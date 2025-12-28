import gspread
from google.oauth2.service_account import Credentials
import os

class GoogleSheetsLogger:
    def __init__(self, credentials_path='Nersi76.json', spreadsheet_name='Video-2', sheet_name='YaShans'):
        """
        Initialize the Google Sheets logger.
        
        Args:
            credentials_path: Path to the Google Service Account JSON file.
            spreadsheet_name: Name of the spreadsheet.
            sheet_name: Name of the worksheet.
        """
        self.credentials_path = credentials_path
        self.spreadsheet_name = spreadsheet_name
        self.sheet_name = sheet_name
        self.client = None
        self.sheet = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Sheets API."""
        try:
            if not os.path.exists(self.credentials_path):
                print(f"❌ Credentials file not found: {self.credentials_path}")
                return

            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            creds = Credentials.from_service_account_file(self.credentials_path, scopes=scopes)
            self.client = gspread.authorize(creds)
            
            # Open the spreadsheet and sheet
            spreadsheet = self.client.open(self.spreadsheet_name)
            self.sheet = spreadsheet.worksheet(self.sheet_name)
            print(f"✅ Connected to Google Sheet: {self.spreadsheet_name} -> {self.sheet_name}")
        except Exception as e:
            print(f"❌ Error authenticating with Google Sheets: {e}")

    def log_upload(self, url):
        """
        Log the uploaded file URL to the first empty row in the first column.
        
        Args:
            url: The URL to log.
        """
        if not self.sheet:
            print("❌ Cannot log: Not connected to Google Sheets.")
            return False

        try:
            # Find the first empty row in the first column
            # We can get all values in the first column and see how many there are
            col_values = self.sheet.col_values(1)
            next_row = len(col_values) + 1
            
            # Update the cell
            self.sheet.update_cell(next_row, 1, url)
            print(f"✅ Logged URL to {self.sheet_name} at row {next_row}: {url}")
            return True
        except Exception as e:
            print(f"❌ Error logging to Google Sheets: {e}")
            return False

    def log_upload_triple(self, mp4_url, en_srt_url, fa_srt_url):
        """
        Log MP4, English SRT, and Persian SRT URLs to separate columns in the first empty row.
        
        Args:
            mp4_url: URL for the MP4 video file (Column A).
            en_srt_url: URL for the English subtitle file (Column B).
            fa_srt_url: URL for the Persian subtitle file (Column C).
        """
        if not self.sheet:
            print("❌ Cannot log: Not connected to Google Sheets.")
            return False

        try:
            # Find the first empty row based on Column A
            col_values = self.sheet.col_values(1)
            next_row = len(col_values) + 1
            
            # Prepare the row data
            row_data = [mp4_url or "", en_srt_url or "", fa_srt_url or ""]
            
            # Update the row (range is A{next_row}:C{next_row})
            cell_range = f"A{next_row}:C{next_row}"
            self.sheet.update(range_name=cell_range, values=[row_data])
            
            print(f"✅ Logged triple URLs to {self.sheet_name} at row {next_row}")
            return True
        except Exception as e:
            print(f"❌ Error logging triple URLs to Google Sheets: {e}")
            return False

if __name__ == "__main__":
    # Quick test
    logger = GoogleSheetsLogger()
    # logger.log_upload("https://example.com/test-upload.mp4")
