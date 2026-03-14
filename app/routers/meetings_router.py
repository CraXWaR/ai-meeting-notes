from fastapi import APIRouter, HTTPException, UploadFile, File

from app.models.google_docs_model import BulkImportRequest, BulkImportResponse, DriveImportRequest, ImportStatus
from app.models.meetings_model import MeetingResponse, MeetingDetailsResponse
from app.services.meeting_service import create_meeting, get_all_meetings, get_meeting_by_id, create_meeting_from_file
from app.services.google_docs_service import import_google_docs, start_async_drive_import, imports

router = APIRouter(prefix="/meetings", tags=["Meetings"])


@router.post("/", response_model=list[MeetingResponse], status_code=201)
def post_meeting():
    return create_meeting()


@router.get("/", response_model=list[MeetingResponse])
def get_meetings():
    return get_all_meetings()


@router.post("/upload", response_model=MeetingResponse, status_code=201)
async def upload_meeting(file: UploadFile = File(...)):
    if not file.filename.endswith((".docx", ".pdf")):
        raise HTTPException(status_code=400, detail="Only .docx and .pdf files are supported")

    contents = await file.read()
    return create_meeting_from_file(contents, file.filename)


@router.post("/import/google-docs", response_model=BulkImportResponse, status_code=201)
def import_from_google_docs(payload: BulkImportRequest):
    return import_google_docs(payload)


@router.post("/import/google-drive", response_model=ImportStatus, status_code=201)
def import_from_google_drive(payload: DriveImportRequest):
    return start_async_drive_import(payload)


@router.get("/import/{import_id}", response_model=ImportStatus)
def get_import_status(import_id: str):
    print(f"Looking for: {import_id}")
    print(f"Available imports: {list(imports.keys())}")
    if import_id not in imports:
        raise HTTPException(status_code=404, detail="Import not found")

    data = imports[import_id]
    return ImportStatus(
        import_id=import_id,
        status=data["status"],
        results=data.get("results")
    )


@router.get("/{meeting_id}", response_model=MeetingDetailsResponse)
def get_meeting(meeting_id: str):
    meeting = get_meeting_by_id(meeting_id)

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting
