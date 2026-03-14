import uuid
from app.helpers.google_docs_helper import extract_doc_id, fetch_doc_content, fetch_private_doc_content, \
    extract_folder_id, get_drive_docs
from app.services.database import supabase
from app.helpers.file_helpers import extract_date_from_filename
from app.models.google_docs_model import BulkImportRequest, BulkImportResult, BulkImportResponse, DriveImportRequest, \
    ImportStatus
import threading


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

            try:
                transcript = fetch_doc_content(doc_id)
            except ValueError as e:
                if "403" in str(e) or "401" in str(e):
                    transcript = fetch_private_doc_content(doc_id)
                else:
                    raise

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


imports: dict = {}


def _run_import(import_id: str, payload: DriveImportRequest):
    imports[import_id]["status"] = "in_progress"
    url = str(payload.folder_url)
    folder_id = extract_folder_id(url)
    docs = get_drive_docs(folder_id)
    results = []

    for doc in docs:
        doc_id = doc["id"]
        title = doc["name"]
        try:
            existing = supabase.table("meetings").select("id").eq("external_id", doc_id).execute()
            if existing.data:
                raise ValueError(f"Meeting already exists: {title}")
            transcript = fetch_private_doc_content(doc_id)
            meeting_date = extract_date_from_filename(title)
            meeting_id = str(uuid.uuid4())
            supabase.table("meetings").insert({
                "id": meeting_id,
                "title": title,
                "meeting_date": str(meeting_date),
                "source": "google_drive",
                "source_url": f"https://docs.google.com/document/d/{doc_id}/edit",
                "external_id": doc_id,
                "raw_transcript": transcript
            }).execute()
            results.append(BulkImportResult(title=title, success=True, meeting_id=meeting_id))
            print(f"✅ Imported: {title}", flush=True)
        except Exception as e:
            results.append(BulkImportResult(title=title, success=False, error=str(e)))
            print(f"❌ Failed: {title} - {str(e)}", flush=True)

    succeeded = sum(1 for r in results if r.success)
    failed = len(results) - succeeded
    imports[import_id]["status"] = "completed"
    imports[import_id]["results"] = BulkImportResponse(
        results=results,
        total=len(results),
        succeeded=succeeded,
        failed=failed
    )


def start_async_drive_import(payload: DriveImportRequest) -> ImportStatus:
    import_id = str(uuid.uuid4())
    imports[import_id] = {"status": "pending", "results": None}
    thread = threading.Thread(target=_run_import, args=(import_id, payload))
    thread.start()
    return ImportStatus(import_id=import_id, status="pending")
