from uuid import UUID
from dependencies.auth import CurrentUser
from services.recommendation_service import RecommendationService

def get_recommendation_controller(prompt: str, user: CurrentUser):
    return RecommendationService.get_recommendation(UUID(user.id), prompt)