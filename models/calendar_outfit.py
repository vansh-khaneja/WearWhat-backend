from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import date

class SaveCalendarOutfitRequest(BaseModel):
    outfit_date: date
    combined_image_url: str
    prompt: Optional[str] = None
    temperature: Optional[float] = None
    weather: Optional[str] = None
    selected_categories: List[str] = []
    items: List[dict] = []

class CalendarOutfitResponse(BaseModel):
    id: UUID
    user_id: UUID
    outfit_date: date
    combined_image_url: str
    prompt: Optional[str]
    temperature: Optional[float]
    weather: Optional[str]
    selected_categories: List[str]
    items: List[dict]
    created_at: str
