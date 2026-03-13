import re
import requests


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
