from fastapi import APIRouter, HTTPException
from app.models.meetings_model import MeetingResponse, MeetingDetailsResponse
from app.services.meeting_service import create_meeting, get_all_meetings, get_meeting_by_id

router = APIRouter(prefix="/meetings", tags=["Meetings"])


@router.post("/", response_model=list[MeetingResponse], status_code=201)
def post_meeting():
    return create_meeting()


@router.get("/", response_model=list[MeetingResponse])
def get_meetings():
    return get_all_meetings()


@router.get("/{meeting_id}", response_model=MeetingDetailsResponse)
def get_meeting(meeting_id: str):
    meeting = get_meeting_by_id(meeting_id)

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting
