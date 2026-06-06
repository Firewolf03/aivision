import gspread
from google.oauth2.service_account import Credentials
from config import SHEET_NAME

class GoogleSheetService:

    def __init__(self):
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        creds = Credentials.from_service_account_file(
            "credentials.json",
            scopes=scope
        )

        client = gspread.authorize(creds)
        self.sheet = client.open(SHEET_NAME).sheet1

    def append_row(self, row):
        self.sheet.append_row(row)

    def get_all_rows(self):
        return self.sheet.get_all_values()
