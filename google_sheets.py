import streamlit as st
import json
import gspread
from google.oauth2.service_account import Credentials

class GoogleSheetService:

    def __init__(self):

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        # read from Streamlit Secrets
        creds_dict = json.loads(st.secrets["google_credentials"])

        creds = Credentials.from_service_account_info(
            creds_dict,
            scopes=scope
        )

        client = gspread.authorize(creds)

        self.sheet = client.open("YOUR_SHEET_NAME").sheet1

    def append_row(self, row):
        self.sheet.append_row(row)
