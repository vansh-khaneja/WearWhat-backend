from fastapi import APIRouter, Depends
from datetime import date
from dependencies.auth import get_current_user, CurrentUser
from models.calendar_outfit import SaveCalendarOutfitRequest
from controllers.calendar_outfit_controller import (
    save_calendar_outfit_controller,
    get_calendar_outfits_controller,
    get_calendar_outfit_by_date_controller,
    delete_calendar_outfit_controller
)

router = APIRouter(
    prefix="/calendar-outfits",
    tags=["Calendar Outfits"]
)

@router.post("")
def save_calendar_outfit(request: SaveCalendarOutfitRequest, user: CurrentUser = Depends(get_current_user)):
    return save_calendar_outfit_controller(request, user)

@router.get("")
def get_calendar_outfits(user: CurrentUser = Depends(get_current_user)):
    return get_calendar_outfits_controller(user)

@router.get("/{outfit_date}")
def get_calendar_outfit_by_date(outfit_date: date, user: CurrentUser = Depends(get_current_user)):
    return get_calendar_outfit_by_date_controller(outfit_date, user)

@router.delete("/{outfit_date}")
def delete_calendar_outfit(outfit_date: date, user: CurrentUser = Depends(get_current_user)):
    return delete_calendar_outfit_controller(outfit_date, user)
