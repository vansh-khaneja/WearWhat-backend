from typing import List, Dict, Optional

from repositories.wardrobe_repository import WardrobeRepository
from services.qdrant_service import get_qdrant_client, COLLECTION_NAME, search_similar
from services.image_combiner_service import ImageCombinerService


# Define which category groups to match for each source category group
CATEGORY_GROUP_MATCHES = {
    "upperWear": ["bottomWear", "footwear", "accessories", "outerWear"],
    "bottomWear": ["upperWear", "footwear", "accessories", "outerWear"],
    "outerWear": ["upperWear", "bottomWear", "footwear", "accessories"],
    "footwear": ["upperWear", "bottomWear", "accessories", "outerWear"],
    "accessories": ["upperWear", "bottomWear", "footwear", "outerWear"],
}


class StylingService:

    @staticmethod
    def get_styled_outfit(user_id: str, item_id: str) -> Dict:
        """
        Given a wardrobe item, find the best matching items from other categories
        and combine them into a styled outfit image.

        Args:
            user_id: User ID
            item_id: Source wardrobe item ID

        Returns:
            Dict with combined outfit image URL and matched items
        """
        print(f"\n{'='*50}")
        print(f"[DEBUG] get_styled_outfit called")
        print(f"[DEBUG] user_id: {user_id}")
        print(f"[DEBUG] item_id: {item_id}")

        # Get source item details from database
        source_item = WardrobeRepository.get_by_id(item_id)
        print(f"[DEBUG] source_item from DB: {source_item}")

        if not source_item:
            print("[DEBUG] ERROR: Item not found in database")
            return {"success": False, "message": "Item not found"}

        # Verify item belongs to user
        if str(source_item["user_id"]) != user_id:
            print(f"[DEBUG] ERROR: Unauthorized - item user_id: {source_item['user_id']}, request user_id: {user_id}")
            return {"success": False, "message": "Unauthorized"}

        # Get source item embedding from Qdrant
        client = get_qdrant_client()
        print(f"[DEBUG] Retrieving embedding from Qdrant for item_id: {item_id}")
        points = client.retrieve(
            collection_name=COLLECTION_NAME,
            ids=[item_id],
            with_vectors=True
        )
        print(f"[DEBUG] Points retrieved from Qdrant: {len(points) if points else 0}")

        if not points:
            print("[DEBUG] ERROR: No embedding found in Qdrant")
            return {"success": False, "message": "Item embedding not found. Please re-upload the item."}

        source_embedding = points[0].vector
        source_category_group = source_item["category_group"]
        print(f"[DEBUG] Source category_group: {source_category_group}")
        print(f"[DEBUG] Embedding length: {len(source_embedding)}")

        # Get category groups to match
        categories_to_match = CATEGORY_GROUP_MATCHES.get(source_category_group, [])
        print(f"[DEBUG] Categories to match: {categories_to_match}")

        # Find best matching item from each category group
        matched_items = []

        # Add source item first
        matched_items.append({
            "id": str(source_item["id"]),
            "image_url": source_item["image_url"],
            "categoryGroup": source_item["category_group"],
            "category": source_item["category"],
            "attributes": source_item["attributes"],
            "is_source": True,
            "match_score": 1.0
        })

        for category_group in categories_to_match:
            print(f"\n[DEBUG] Searching for category_group: {category_group}")
            # Search for best matching item in this category group
            results = search_similar(
                user_id=user_id,
                query_embedding=source_embedding,
                category_group=category_group,
                limit=1
            )
            print(f"[DEBUG] Results for {category_group}: {results}")

            if results:
                best_match = results[0]
                # Get full item details from database
                item = WardrobeRepository.get_by_id(best_match["item_id"])
                print(f"[DEBUG] Best match item from DB: {item}")
                if item:
                    matched_items.append({
                        "id": str(item["id"]),
                        "image_url": item["image_url"],
                        "categoryGroup": item["category_group"],
                        "category": item["category"],
                        "attributes": item["attributes"],
                        "is_source": False,
                        "match_score": best_match.get("score", 0)
                    })
            else:
                print(f"[DEBUG] No items found for category_group: {category_group}")

        # Combine all matched item images
        print(f"\n[DEBUG] Total matched items: {len(matched_items)}")
        print(f"[DEBUG] Matched items summary: {[{'id': m['id'], 'categoryGroup': m['categoryGroup']} for m in matched_items]}")

        combined_image_url = ImageCombinerService.combine_outfit_images(matched_items)
        print(f"[DEBUG] Combined image URL: {combined_image_url}")
        print(f"{'='*50}\n")

        return {
            "success": True,
            "source_item": {
                "id": str(source_item["id"]),
                "image_url": source_item["image_url"],
                "categoryGroup": source_item["category_group"],
                "category": source_item["category"]
            },
            "combined_image_url": combined_image_url,
            "matched_items": matched_items,
            "total_items": len(matched_items)
        }

    @staticmethod
    def get_styled_outfit_with_options(
        user_id: str,
        item_id: str,
        include_categories: Optional[List[str]] = None,
        limit_per_category: int = 1
    ) -> Dict:
        """
        Get styled outfit with more options per category.

        Args:
            user_id: User ID
            item_id: Source wardrobe item ID
            include_categories: Optional list of category groups to include
            limit_per_category: Number of options to return per category

        Returns:
            Dict with multiple options per category (no combined image)
        """
        # Get source item details
        source_item = WardrobeRepository.get_by_id(item_id)

        if not source_item:
            return {"success": False, "message": "Item not found"}

        if str(source_item["user_id"]) != user_id:
            return {"success": False, "message": "Unauthorized"}

        # Get source embedding
        client = get_qdrant_client()
        points = client.retrieve(
            collection_name=COLLECTION_NAME,
            ids=[item_id],
            with_vectors=True
        )

        if not points:
            return {"success": False, "message": "Item embedding not found"}

        source_embedding = points[0].vector
        source_category_group = source_item["category_group"]

        # Determine which categories to match
        if include_categories:
            categories_to_match = include_categories
        else:
            categories_to_match = CATEGORY_GROUP_MATCHES.get(source_category_group, [])

        # Find matching items for each category
        matches_by_category = {}

        for category_group in categories_to_match:
            results = search_similar(
                user_id=user_id,
                query_embedding=source_embedding,
                category_group=category_group,
                limit=limit_per_category
            )

            category_matches = []
            for result in results:
                item = WardrobeRepository.get_by_id(result["item_id"])
                if item:
                    category_matches.append({
                        "id": str(item["id"]),
                        "image_url": item["image_url"],
                        "categoryGroup": item["category_group"],
                        "category": item["category"],
                        "attributes": item["attributes"],
                        "match_score": result.get("score", 0)
                    })

            if category_matches:
                matches_by_category[category_group] = category_matches

        return {
            "success": True,
            "source_item": {
                "id": str(source_item["id"]),
                "image_url": source_item["image_url"],
                "categoryGroup": source_item["category_group"],
                "category": source_item["category"],
                "attributes": source_item["attributes"]
            },
            "matches_by_category": matches_by_category
        }
