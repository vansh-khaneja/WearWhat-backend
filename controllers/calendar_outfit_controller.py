from datetime import date
from uuid import UUID
from dependencies.auth import CurrentUser
from services.calendar_outfit_service import CalendarOutfitService
from models.calendar_outfit import SaveCalendarOutfitRequest

def save_calendar_outfit_controller(request: SaveCalendarOutfitRequest, user: CurrentUser):
    result = CalendarOutfitService.save_outfit(
        user_id=UUID(user.id),
        outfit_date=request.outfit_date,
        combined_image_url=request.combined_image_url,
        prompt=request.prompt,
        temperature=request.temperature,
        selected_categories=request.selected_categories,
        items=request.items
    )
    return {"success": True, "outfit": result}

def get_calendar_outfits_controller(user: CurrentUser):
    outfits = CalendarOutfitService.get_all_outfits(UUID(user.id))
    return {"success": True, "count": len(outfits), "outfits": outfits}

def get_calendar_outfit_by_date_controller(outfit_date: date, user: CurrentUser):
    outfit = CalendarOutfitService.get_outfit_by_date(UUID(user.id), outfit_date)
    if not outfit:
        return {"success": False, "message": "No outfit found for this date"}
    return {"success": True, "outfit": outfit}

def delete_calendar_outfit_controller(outfit_date: date, user: CurrentUser):
    deleted = CalendarOutfitService.delete_outfit(UUID(user.id), outfit_date)
    if not deleted:
        return {"success": False, "message": "No outfit found for this date"}
    return {"success": True, "message": "Outfit deleted"}
