import gspread
from google.oauth2.service_account import Credentials

class GoogleSheetService:

    def __init__(self, sheet_name):
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        creds = Credentials.from_service_account_file(
            "credentials.json",
            scopes=scope
        )

        client = gspread.authorize(creds)
        self.sheet = client.open(sheet_name).sheet1

    def append_row(self, row):
        self.sheet.append_row(row)

    def get_all_values(self):
        return self.sheet.get_all_values()
