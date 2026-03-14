import re
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from app.settings import settings


def extract_doc_id(url: str) -> str | None:
    match = re.search(r"/document/d/([a-zA-Z0-9_-]+)", url)
    if not match:
        return None
    return match.group(1)


def fetch_doc_content(doc_id: str) -> str:
    url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
    response = requests.get(url, timeout=10)

    if response.status_code == 404:
        raise ValueError("Document not found. Check if the URL is correct.")

    if response.status_code == 403:
        raise ValueError("Document is not accessible. Make sure it is shared publicly.")

    if response.status_code != 200:
        raise ValueError(f"Failed to fetch document. Status code: {response.status_code}")

    return response.text.strip()


def fetch_private_doc_content(doc_id: str) -> str:
    credentials = service_account.Credentials.from_service_account_file(
        settings.GOOGLE_SERVICE_ACCOUNT_JSON,
        scopes=["https://www.googleapis.com/auth/documents.readonly"]
    )
    service = build("docs", "v1", credentials=credentials)
    doc = service.documents().get(documentId=doc_id).execute()

    content = ""
    for element in doc.get("body").get("content"):
        if "paragraph" in element:
            for part in element["paragraph"]["elements"]:
                if "textRun" in part:
                    content += part["textRun"]["content"]

    return content.strip()


def extract_folder_id(url: str) -> str | None:
    match = re.search(r"/folders/([a-zA-Z0-9_-]+)", url)
    if not match:
        return None
    return match.group(1)


def get_drive_docs(folder_id: str) -> list[dict]:
    credentials = service_account.Credentials.from_service_account_file(
        settings.GOOGLE_SERVICE_ACCOUNT_JSON,
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    service = build("drive", "v3", credentials=credentials)

    results = service.files().list(
        q=f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.document' and trashed=false",
        fields="files(id, name)"
    ).execute()

    return results.get("files", [])
