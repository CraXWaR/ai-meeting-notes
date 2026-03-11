from fastapi import HTTPException
import uuid


def validate_id(meeting_id: str):
    try:
        uuid.UUID(meeting_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid meeting ID")
