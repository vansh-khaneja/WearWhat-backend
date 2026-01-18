from openai import OpenAI
from pydantic import BaseModel
from typing import List, Dict, Optional
from uuid import UUID
import random

from config import OPENAI_API_KEY
from repositories.wardrobe_tags_repository import WardrobeTagsRepository
from repositories.wardrobe_repository import WardrobeRepository
from services.image_combiner_service import ImageCombinerService

client = OpenAI(api_key=OPENAI_API_KEY)

class OutfitRecommendation(BaseModel):
    selected_categories: List[str]
    reasoning: str

class RecommendationService:
    @staticmethod
    def get_user_available_categories(user_id: UUID) -> List[str]:
        """Get flat list of all categories the user has in their wardrobe."""
        tags_data = WardrobeTagsRepository.get_by_user(user_id)
        if not tags_data or not tags_data.get('tags_by_category'):
            return []

        categories = []
        tags_by_category = tags_data['tags_by_category']

        # Flatten the tree: category_group -> category -> [item_ids]
        for category_group, categories_dict in tags_by_category.items():
            for category in categories_dict.keys():
                categories.append(category)

        return categories

    @staticmethod
    def get_recommendation(user_id: UUID, prompt: str) -> Dict:
        """
        Use OpenAI to decide which categories to pick based on the prompt,
        then return one random item from each selected category.
        """
        # Get user's available categories
        available_categories = RecommendationService.get_user_available_categories(user_id)

        if not available_categories:
            return {
                "success": False,
                "message": "No items in wardrobe yet",
                "items": []
            }

        # Ask OpenAI to select appropriate categories
        system_prompt = f"""You are a fashion assistant. The user has the following clothing categories in their wardrobe:
{', '.join(available_categories)}

Based on the user's request, select the most appropriate categories for an outfit.
Only select from the available categories listed above.
Select categories that would make a complete, appropriate outfit for the occasion."""

        response = client.responses.parse(
            model="gpt-4o-2024-08-06",
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            text_format=OutfitRecommendation,
        )

        recommendation = response.output_parsed
        selected_categories = recommendation.selected_categories

        # Filter to only include categories that actually exist
        valid_categories = [cat for cat in selected_categories if cat in available_categories]

        # Get the user's tags tree to find item IDs
        tags_data = WardrobeTagsRepository.get_by_user(user_id)
        tags_by_category = tags_data['tags_by_category']

        # For each selected category, get a random item
        result_items = []
        for category in valid_categories:
            # Find which category_group this category belongs to
            item_id = None
            for category_group, categories_dict in tags_by_category.items():
                if category in categories_dict:
                    item_ids = categories_dict[category]
                    if item_ids:
                        # Pick a random item from this category
                        item_id = random.choice(item_ids)
                        break

            if item_id:
                # Get the full item details
                item = WardrobeRepository.get_by_id(item_id)
                if item:
                    result_items.append({
                        "id": str(item["id"]),
                        "image_url": item["image_url"],
                        "categoryGroup": item["category_group"],
                        "category": item["category"],
                        "attributes": item["attributes"]
                    })

        # Combine all item images into a styled outfit layout
        combined_image_url = ImageCombinerService.combine_outfit_images(result_items)

        return {
            "success": True,
            "prompt": prompt,
            "reasoning": recommendation.reasoning,
            "selected_categories": valid_categories,
            "combined_image_url": combined_image_url,
            "items": result_items
        }
