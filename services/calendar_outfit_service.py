from uuid import UUID
from typing import Optional, List
from datetime import date
from repositories.calendar_outfit_repository import CalendarOutfitRepository

class CalendarOutfitService:
    @staticmethod
    def save_outfit(
        user_id: UUID,
        outfit_date: date,
        combined_image_url: str,
        prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        weather: Optional[str] = None,
        selected_categories: List[str] = None,
        items: List[dict] = None
    ) -> dict:
        """Save outfit to calendar. Auto-removes outfits older than 5 days."""
        if selected_categories is None:
            selected_categories = []
        if items is None:
            items = []

        return CalendarOutfitRepository.save(
            user_id=user_id,
            outfit_date=outfit_date,
            combined_image_url=combined_image_url,
            prompt=prompt,
            temperature=temperature,
            weather=weather,
            selected_categories=selected_categories,
            items=items
        )

    @staticmethod
    def get_all_outfits(user_id: UUID) -> List[dict]:
        """Get all calendar outfits for user."""
        return CalendarOutfitRepository.get_by_user(user_id)

    @staticmethod
    def get_outfit_by_date(user_id: UUID, outfit_date: date) -> Optional[dict]:
        """Get outfit for a specific date."""
        return CalendarOutfitRepository.get_by_date(user_id, outfit_date)

    @staticmethod
    def delete_outfit(user_id: UUID, outfit_date: date) -> bool:
        """Delete outfit for a specific date."""
        return CalendarOutfitRepository.delete(user_id, outfit_date)
