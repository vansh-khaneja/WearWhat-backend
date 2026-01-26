from typing import Optional
from pydantic import BaseModel


class RecommendationRequest(BaseModel):
    prompt: str
    lat: Optional[float] = None  # Latitude for weather
    lon: Optional[float] = None  # Longitude for weather
    city: Optional[str] = None   # Or city name as alternative
    date: Optional[str] = None   # Target date in YYYY-MM-DD format (defaults to today)
