from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class SaveImageRequest(BaseModel):
    image_id: UUID
    note: Optional[str] = None

class UpdateNoteRequest(BaseModel):
    saved_image_id: UUID
    note: str

class SavedImageResponse(BaseModel):
    id: UUID
    user_id: UUID
    image_id: UUID
    note: Optional[str]
    saved_at: str
