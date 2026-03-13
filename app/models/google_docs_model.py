from pydantic import BaseModel, HttpUrl
from typing import Optional


class GoogleDocItem(BaseModel):
    title: str
    google_doc_url: HttpUrl


class BulkImportRequest(BaseModel):
    meetings: list[GoogleDocItem]


class BulkImportResult(BaseModel):
    title: str
    success: bool
    meeting_id: Optional[str] = None
    error: Optional[str] = None


class BulkImportResponse(BaseModel):
    results: list[BulkImportResult]
    total: int
    succeeded: int
    failed: int
