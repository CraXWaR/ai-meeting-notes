import os
import uuid
from fastapi import HTTPException
from app.helpers.file_helpers import read_docx, extract_date_from_filename, read_pdf
from app.models.meetings_model import MeetingResponse, MeetingDetailsResponse
from app.services.database import supabase
import tempfile


def create_meeting():
    base_data_path = os.path.join(os.path.dirname(__file__), "..", "..", "data")
    inserted = []
    for sub_folder in os.listdir(base_data_path):
        folder_path = os.path.join(base_data_path, sub_folder)
        if not os.path.isdir(folder_path):
            continue
        for file in os.listdir(folder_path):
            if not file.endswith(".docx"):
                continue
            title = os.path.splitext(file)[0]
            existing = supabase.table("meetings").select("id").eq("title", title).execute()
            if existing.data:
                print(f"Skipping (already exists): {title}")
                continue
            transcript = read_docx(os.path.join(folder_path, file))
            meeting_id = str(uuid.uuid4())
            supabase.table("meetings").insert({
                "id": meeting_id,
                "title": title,
                "meeting_date": str(extract_date_from_filename(file)),
                "source": sub_folder,
                "raw_transcript": transcript
            }).execute()
            inserted.append({
                "id": meeting_id,
                "title": title,
                "meeting_date": extract_date_from_filename(file),
                "source": sub_folder,
                "has_notes": False
            })
            print("Inserted:", title)
    return inserted


def get_all_meetings() -> list[MeetingResponse]:
    meetings = supabase.table("meetings").select("id, title, meeting_date, source").execute()
    existing_notes = supabase.table("notes").select("meeting_id").execute()
    notes_ids = {note["meeting_id"] for note in existing_notes.data}

    return [
        MeetingResponse(**meeting, has_notes=meeting["id"] in notes_ids)
        for meeting in meetings.data
    ]


def get_meeting_by_id(meeting_id: str) -> MeetingDetailsResponse | None:
    meeting = supabase.table("meetings").select("*").eq("id", meeting_id).execute()

    if not meeting.data:
        return None

    return MeetingDetailsResponse(
        **meeting.data[0],
        notes="no notes"
    )


def create_meeting_from_file(contents: bytes, filename: str) -> MeetingResponse:
    title = os.path.splitext(filename)[0]

    existing = supabase.table("meetings").select("id").eq("title", title).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail=f"Meeting already exists: {title}")

    if filename.endswith(".pdf"):
        transcript = read_pdf(contents)
        tmp_path = None
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name
        transcript = read_docx(tmp_path)

    try:
        meeting_date = extract_date_from_filename(filename)
        meeting_id = str(uuid.uuid4())

        supabase.table("meetings").insert({
            "id": meeting_id,
            "title": title,
            "meeting_date": str(meeting_date),
            "source": "upload",
            "raw_transcript": transcript
        }).execute()

        return MeetingResponse(
            id=meeting_id,
            title=title,
            meeting_date=meeting_date,
            source="upload",
            has_notes=False
        )
    finally:
        if tmp_path:
            os.unlink(tmp_path)
