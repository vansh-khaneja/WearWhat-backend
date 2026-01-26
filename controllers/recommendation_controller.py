from typing import Optional
from uuid import UUID
from dependencies.auth import CurrentUser
from services.recommendation_service import RecommendationService


def get_recommendation_controller(
    prompt: str,
    user: CurrentUser,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    city: Optional[str] = None,
    date: Optional[str] = None
):
    return RecommendationService.get_recommendation(
        user_id=UUID(user.id),
        prompt=prompt,
        lat=lat,
        lon=lon,
        city=city,
        date=date
    )