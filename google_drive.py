from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
from config import DRIVE_FOLDER_ID

def get_drive_service():
    scope = ["https://www.googleapis.com/auth/drive"]

    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=scope
    )

    return build("drive", "v3", credentials=creds)


def upload_image(file_path):
    service = get_drive_service()

    file_metadata = {
        "name": file_path.split("/")[-1],
        "parents": [DRIVE_FOLDER_ID]
    }

    media = MediaFileUpload(file_path, mimetype="image/jpeg")

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, webViewLink"
    ).execute()

    return file["webViewLink"]
