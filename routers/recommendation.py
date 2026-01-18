from fastapi import APIRouter, Depends
from dependencies.auth import get_current_user, CurrentUser
from models.recommendation import RecommendationRequest
from controllers.recommendation_controller import get_recommendation_controller

router = APIRouter(
    prefix="/recommendation",
    tags=["Recommendation"]
)

@router.post("")
def get_recommendation(request: RecommendationRequest, user: CurrentUser = Depends(get_current_user)):
    return get_recommendation_controller(request.prompt, user)
