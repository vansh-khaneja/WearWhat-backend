from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

from config import QDRANT_URL, QDRANT_API_KEY


# Collection name for wardrobe embeddings
COLLECTION_NAME = "wardrobe_embeddings"

# CLIP embedding dimension (ViT-B/32)
EMBEDDING_DIM = 512


def get_qdrant_client() -> QdrantClient:
    """Get Qdrant client instance for Qdrant Cloud."""
    return QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY
    )


def init_collection():
    """Initialize Qdrant collection with proper indexing."""
    client = get_qdrant_client()

    collections = client.get_collections().collections
    collection_names = [c.name for c in collections]

    if COLLECTION_NAME not in collection_names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=EMBEDDING_DIM,
                distance=Distance.COSINE
            )
        )

        # Create payload indexes for efficient filtering
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="user_id",
            field_schema=models.PayloadSchemaType.KEYWORD
        )
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="category_group",
            field_schema=models.PayloadSchemaType.KEYWORD
        )
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="category",
            field_schema=models.PayloadSchemaType.KEYWORD
        )
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="color",
            field_schema=models.PayloadSchemaType.KEYWORD
        )
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="occasion",
            field_schema=models.PayloadSchemaType.KEYWORD
        )
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="season",
            field_schema=models.PayloadSchemaType.KEYWORD
        )

        print(f"Created Qdrant collection: {COLLECTION_NAME}")
    else:
        print(f"Qdrant collection {COLLECTION_NAME} already exists")


def store_embedding(
    item_id: str,
    user_id: str,
    embedding: List[float],
    category_group: str,
    category: str,
    attributes: dict,
    image_url: str
):
    """
    Store wardrobe item embedding in Qdrant.

    Args:
        item_id: Wardrobe item ID
        user_id: User ID
        embedding: CLIP image embedding (512-dim vector)
        category_group: e.g., "upperWear", "bottomWear"
        category: e.g., "T-Shirt", "Jeans"
        attributes: Dict with color, pattern, material, etc.
        image_url: Cloudinary image URL
    """
    client = get_qdrant_client()

    # Build payload with tags for filtering
    payload = {
        "item_id": item_id,
        "user_id": user_id,
        "category_group": category_group,
        "category": category,
        "image_url": image_url,
        "color": attributes.get("color", "Unknown"),
        "pattern": attributes.get("pattern", "Unknown"),
        "material": attributes.get("material", "Unknown"),
        "season": attributes.get("season", "All Season"),
        "occasion": attributes.get("occasion", "Casual"),
    }

    # Add any additional attributes
    for key, value in attributes.items():
        if key not in payload:
            payload[key] = value

    point = PointStruct(
        id=item_id,
        vector=embedding,
        payload=payload
    )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[point]
    )


def search_similar(
    user_id: str,
    query_embedding: List[float],
    category_group: Optional[str] = None,
    category: Optional[str] = None,
    color: Optional[str] = None,
    occasion: Optional[str] = None,
    season: Optional[str] = None,
    limit: int = 5
) -> List[dict]:
    """
    Search for similar wardrobe items using embedding similarity.

    Args:
        user_id: Filter by user
        query_embedding: CLIP embedding to search with
        category_group: Optional filter by category group
        category: Optional filter by category
        color: Optional filter by color
        occasion: Optional filter by occasion
        season: Optional filter by season
        limit: Number of results to return

    Returns:
        List of matching items with scores
    """
    print(f"  [QDRANT] search_similar called - user_id: {user_id}, category_group: {category_group}")
    client = get_qdrant_client()

    # Build filter conditions
    must_conditions = [
        FieldCondition(key="user_id", match=MatchValue(value=user_id))
    ]

    if category_group:
        must_conditions.append(
            FieldCondition(key="category_group", match=MatchValue(value=category_group))
        )

    if category:
        must_conditions.append(
            FieldCondition(key="category", match=MatchValue(value=category))
        )

    if color:
        must_conditions.append(
            FieldCondition(key="color", match=MatchValue(value=color))
        )

    if occasion:
        must_conditions.append(
            FieldCondition(key="occasion", match=MatchValue(value=occasion))
        )

    if season:
        must_conditions.append(
            FieldCondition(key="season", match=MatchValue(value=season))
        )

    search_filter = Filter(must=must_conditions)
    print(f"  [QDRANT] Filter conditions: {len(must_conditions)} conditions")

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        query_filter=search_filter,
        limit=limit
    )
    print(f"  [QDRANT] Results count: {len(results.points)}")

    return [
        {
            "item_id": hit.payload["item_id"],
            "image_url": hit.payload["image_url"],
            "category_group": hit.payload["category_group"],
            "category": hit.payload["category"],
            "color": hit.payload.get("color"),
            "occasion": hit.payload.get("occasion"),
            "season": hit.payload.get("season"),
            "score": hit.score
        }
        for hit in results.points
    ]


def search_by_text(
    user_id: str,
    text_embedding: List[float],
    category_group: Optional[str] = None,
    limit: int = 5
) -> List[dict]:
    """
    Search wardrobe items using text embedding (e.g., "blue formal shirt").

    Args:
        user_id: Filter by user
        text_embedding: CLIP text embedding
        category_group: Optional filter
        limit: Number of results

    Returns:
        List of matching items
    """
    return search_similar(
        user_id=user_id,
        query_embedding=text_embedding,
        category_group=category_group,
        limit=limit
    )


def delete_embedding(item_id: str):
    """Delete embedding when wardrobe item is deleted."""
    client = get_qdrant_client()

    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=models.PointIdsList(points=[item_id])
    )


def get_items_by_tag(
    user_id: str,
    category_group: Optional[str] = None,
    category: Optional[str] = None,
    color: Optional[str] = None,
    limit: int = 100
) -> List[dict]:
    """
    Get wardrobe items by tag filters (without similarity search).

    Args:
        user_id: Filter by user
        category_group: Optional filter
        category: Optional filter
        color: Optional filter
        limit: Max results

    Returns:
        List of items matching filters
    """
    client = get_qdrant_client()

    must_conditions = [
        FieldCondition(key="user_id", match=MatchValue(value=user_id))
    ]

    if category_group:
        must_conditions.append(
            FieldCondition(key="category_group", match=MatchValue(value=category_group))
        )

    if category:
        must_conditions.append(
            FieldCondition(key="category", match=MatchValue(value=category))
        )

    if color:
        must_conditions.append(
            FieldCondition(key="color", match=MatchValue(value=color))
        )

    results, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=Filter(must=must_conditions),
        limit=limit
    )

    return [
        {
            "item_id": point.payload["item_id"],
            "image_url": point.payload["image_url"],
            "category_group": point.payload["category_group"],
            "category": point.payload["category"],
            "color": point.payload.get("color"),
            "occasion": point.payload.get("occasion"),
            "season": point.payload.get("season"),
        }
        for point in results
    ]
