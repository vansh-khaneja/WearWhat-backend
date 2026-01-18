from pydantic import BaseModel
from typing import Dict, List
from uuid import UUID

class WardrobeTagsResponse(BaseModel):
    id: UUID
    user_id: UUID
    tags_by_category: Dict[str, Dict[str, List[str]]]
    created_at: str
    updated_at: str
