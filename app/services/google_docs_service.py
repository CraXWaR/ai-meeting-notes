import uuid

from app.helpers.google_docs_helper import extract_doc_id, fetch_doc_content
from app.services.database import supabase
from app.helpers.file_helpers import extract_date_from_filename
from app.models.google_docs_model import BulkImportRequest, BulkImportResult, BulkImportResponse


def import_google_docs(payload: BulkImportRequest) -> BulkImportResponse:
    results = []

    for item in payload.meetings:
        print(item)
        title = item.title
        url = str(item.google_doc_url)

        try:
            doc_id = extract_doc_id(url)
            if not doc_id:
                raise ValueError(f"Invalid Google Docs URL: {url}")

            existing = supabase.table("meetings").select("id").eq("external_id", doc_id).execute()
            if existing.data:
                raise ValueError(f"Meeting already exists: {title}")

            transcript = fetch_doc_content(doc_id)
            meeting_date = extract_date_from_filename(title)
            meeting_id = str(uuid.uuid4())

            supabase.table("meetings").insert({
                "id": meeting_id,
                "title": title,
                "meeting_date": str(meeting_date),
                "source": "google_docs",
                "source_url": url,
                "external_id": doc_id,
                "raw_transcript": transcript
            }).execute()

            results.append(BulkImportResult(
                title=title,
                success=True,
                meeting_id=meeting_id
            ))

        except Exception as e:
            results.append(BulkImportResult(
                title=title,
                success=False,
                error=str(e)
            ))

    succeeded = sum(1 for r in results if r.success)
    failed = len(results) - succeeded

    return BulkImportResponse(
        results=results,
        total=len(results),
        succeeded=succeeded,
        failed=failed
    )
