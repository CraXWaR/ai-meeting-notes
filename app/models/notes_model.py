from pydantic import BaseModel
from typing import Optional


class ActionItem(BaseModel):
    text: str
    owner: Optional[str] = None
    due_date: Optional[str] = None


class NextStep(BaseModel):
    text: str
    owner: Optional[str] = None


class NoteResponse(BaseModel):
    id: str
    meeting_id: str
    summary: str
    action_items: list[ActionItem]
    decisions: list[str]
    key_takeaways: list[str]
    topics: list[str]
    next_steps: list[NextStep]
