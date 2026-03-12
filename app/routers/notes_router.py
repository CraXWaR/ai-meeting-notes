from fastapi import APIRouter, HTTPException
from app.services.notes_service import process_meeting, process_all_meetings, get_notes_by_meeting_id
from app.models.notes_model import NoteResponse
from app.validators.validate_id import validate_id

router = APIRouter(prefix="/meetings", tags=["Notes"])


@router.post("/{meeting_id}/process")
def process(meeting_id: str, llm: str = "groq"):
    validate_id(meeting_id)
    notes = process_meeting(meeting_id, llm)

    if notes is None:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return notes


@router.post("/process-all")
def process_all():
    return process_all_meetings()


@router.get("/{meeting_id}/notes", response_model=NoteResponse)
def get_notes(meeting_id: str):
    notes = get_notes_by_meeting_id(meeting_id)
    if notes is None:
        raise HTTPException(status_code=404, detail="Notes not found")
    return notes
