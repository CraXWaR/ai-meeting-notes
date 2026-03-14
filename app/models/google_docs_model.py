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


class DriveImportRequest(BaseModel):
    folder_url: HttpUrl


class ImportStatus(BaseModel):
    import_id: str
    status: str
    results: Optional[BulkImportResponse] = None
