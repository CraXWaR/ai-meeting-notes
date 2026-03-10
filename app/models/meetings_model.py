from pydantic import BaseModel
from typing import Optional
from datetime import date


class MeetingResponse(BaseModel):
    id: str
    title: str
    meeting_date: date
    source: Optional[str] = None
    has_notes: bool


class MeetingDetailsResponse(BaseModel):
    id: str
    title: str
    meeting_date: date
    source: Optional[str] = None
    raw_transcript: str
    notes: Optional[str] = None