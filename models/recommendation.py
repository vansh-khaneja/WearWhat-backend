from pydantic import BaseModel

class RecommendationRequest(BaseModel):
    prompt: str
