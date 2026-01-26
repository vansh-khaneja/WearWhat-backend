from typing import Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from dependencies.auth import get_current_user, CurrentUser
from models.recommendation import RecommendationRequest
from controllers.recommendation_controller import get_recommendation_controller
from services.qdrant_service import search_similar, search_by_text, get_items_by_tag, get_qdrant_client, COLLECTION_NAME
from services.clip_service import get_text_embedding
from services.styling_service import StylingService


router = APIRouter(
    prefix="/recommendation",
    tags=["Recommendation"]
)


@router.post("")
def get_recommendation(request: RecommendationRequest, user: CurrentUser = Depends(get_current_user)):
    return get_recommendation_controller(
        prompt=request.prompt,
        user=user,
        lat=request.lat,
        lon=request.lon,
        city=request.city,
        date=request.date
    )


# Vector search models
class TextSearchRequest(BaseModel):
    query: str
    category_group: Optional[str] = None
    limit: int = 5


class SimilarItemRequest(BaseModel):
    item_id: str
    category_group: Optional[str] = None
    color: Optional[str] = None
    occasion: Optional[str] = None
    season: Optional[str] = None
    limit: int = 5


class StyleOutfitRequest(BaseModel):
    item_id: str


@router.post("/search")
def search_by_text_prompt(
    request: TextSearchRequest,
    user: CurrentUser = Depends(get_current_user)
):
    """
    Search wardrobe items using natural language.
    Example queries:
    - "blue formal shirt"
    - "casual summer dress"
    - "black leather jacket"
    """
    text_embedding = get_text_embedding(request.query)

    results = search_by_text(
        user_id=str(user.id),
        text_embedding=text_embedding,
        category_group=request.category_group,
        limit=request.limit
    )

    return {
        "success": True,
        "query": request.query,
        "count": len(results),
        "items": results
    }


@router.get("/filter")
def search_by_filters(
    user: CurrentUser = Depends(get_current_user),
    category_group: Optional[str] = Query(None, description="e.g., upperWear, bottomWear"),
    category: Optional[str] = Query(None, description="e.g., T-Shirt, Jeans"),
    color: Optional[str] = Query(None, description="e.g., Blue, Red"),
    limit: int = Query(20, le=100)
):
    """
    Get wardrobe items by tag filters.
    """
    results = get_items_by_tag(
        user_id=str(user.id),
        category_group=category_group,
        category=category,
        color=color,
        limit=limit
    )

    return {
        "success": True,
        "count": len(results),
        "items": results
    }


@router.post("/similar")
def find_similar_items(
    request: SimilarItemRequest,
    user: CurrentUser = Depends(get_current_user)
):
    """
    Find similar items to a given wardrobe item.
    Useful for outfit recommendations.
    """
    client = get_qdrant_client()

    points = client.retrieve(
        collection_name=COLLECTION_NAME,
        ids=[request.item_id],
        with_vectors=True
    )

    if not points:
        return {"success": False, "message": "Item not found"}

    source_embedding = points[0].vector

    results = search_similar(
        user_id=str(user.id),
        query_embedding=source_embedding,
        category_group=request.category_group,
        color=request.color,
        occasion=request.occasion,
        season=request.season,
        limit=request.limit + 1
    )

    # Exclude the source item from results
    results = [r for r in results if r["item_id"] != request.item_id][:request.limit]

    return {
        "success": True,
        "source_item_id": request.item_id,
        "count": len(results),
        "items": results
    }


@router.post("/style")
def style_outfit(
    request: StyleOutfitRequest,
    user: CurrentUser = Depends(get_current_user)
):
    """
    Generate a styled outfit based on a single wardrobe item.
    Pass an item_id and get back:
    - Best matching items from other category groups (bottomWear, footwear, accessories, etc.)
    - Combined outfit image uploaded to Cloudinary

    Example: Pass a shirt ID → Get matching pants, shoes, accessories + combined image
    """
    return StylingService.get_styled_outfit(
        user_id=str(user.id),
        item_id=request.item_id
    )


@router.get("/debug/qdrant-items")
def debug_qdrant_items(user_id: Optional[str] = Query(None)):
    """
    Debug endpoint: List all items in Qdrant.
    Pass user_id as query param to filter by user, or leave empty for all.
    """
    client = get_qdrant_client()

    from qdrant_client.http.models import Filter, FieldCondition, MatchValue

    scroll_filter = None
    if user_id:
        scroll_filter = Filter(
            must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
        )

    results, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=scroll_filter,
        limit=100,
        with_payload=True,
        with_vectors=False
    )

    items_by_category = {}
    for point in results:
        cat_group = point.payload.get("category_group", "unknown")
        if cat_group not in items_by_category:
            items_by_category[cat_group] = []
        items_by_category[cat_group].append({
            "id": point.id,
            "item_id": point.payload.get("item_id"),
            "user_id": point.payload.get("user_id"),
            "category": point.payload.get("category"),
            "color": point.payload.get("color"),
            "image_url": point.payload.get("image_url")
        })

    return {
        "success": True,
        "filter_user_id": user_id,
        "total_items_in_qdrant": len(results),
        "items_by_category_group": items_by_category
    }
