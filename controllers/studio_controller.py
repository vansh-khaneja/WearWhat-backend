import io
import requests
from uuid import UUID

from repositories.wardrobe_repository import WardrobeRepository
from repositories.studio_repository import StudioRepository
from repositories.user_repository import UserRepository
from services.studio_image_service import StudioImageService
from services.cloudinary_service import upload_image


# Category-specific prompts for garment reconstruction
CATEGORY_PROMPTS = {
    "upperWear": """Reconstruct this upper body garment (shirt/t-shirt/blouse/top) into a clean, factory-new product image. Preserve exact fabric texture, color, stitching, buttons/zippers, and proportions. Smooth the fabric naturally, remove all wrinkles and creases. Straighten the collar, cuffs, hem, and sleeves with balanced symmetry. Studio lighting, sharp focus, pure white background, no people or props. Show the garment laid flat or on invisible mannequin.""",

    "bottomWear": """Reconstruct this bottom wear garment (pants/jeans/shorts/skirt) into a clean, factory-new product image. Preserve exact fabric texture, color, stitching, pockets, belt loops, and proportions. Smooth the fabric naturally, remove all wrinkles and creases. Straighten the waistband, seams, and hem with balanced symmetry. Studio lighting, sharp focus, pure white background, no people or props. Show the garment laid flat or on invisible mannequin.""",

    "footwear": """Reconstruct this footwear (shoes/sneakers/boots/sandals) into a clean, factory-new product image. Preserve exact material texture, color, stitching, laces, soles, and proportions. Remove any scuffs, dirt, or wear marks. Show the shoe at a 3/4 angle for best visibility. Studio lighting, sharp focus, pure white background, no people or props. Make it look brand new from store.""",

    "accessories": """Reconstruct this accessory (watch/bag/belt/jewelry/hat/scarf) into a clean, factory-new product image. Preserve exact material, color, hardware details, and proportions. Remove any scratches, wear marks, or imperfections. Studio lighting, sharp focus, pure white background, no people or props. Show the item at its best angle for visibility.""",

    "outerWear": """Reconstruct this outerwear garment (jacket/coat/blazer/hoodie) into a clean, factory-new product image. Preserve exact fabric texture, color, stitching, zippers, buttons, pockets, and proportions. Smooth the fabric naturally, remove all wrinkles and creases. Straighten the collar, cuffs, hem, and sleeves with balanced symmetry. Studio lighting, sharp focus, pure white background, no people or props. Show the garment laid flat or on invisible mannequin.""",
}


def get_prompt_for_category(category_group: str) -> str:
    """Get the appropriate prompt based on category group."""
    return CATEGORY_PROMPTS.get(category_group, CATEGORY_PROMPTS["upperWear"])


def generate_studio_image_controller(user_id: str, item_id: str) -> dict:
    """
    Controller for generating studio image from a wardrobe item.

    1. Fetch item from database
    2. Verify item belongs to user
    3. Download image from Cloudinary
    4. Choose prompt based on category
    5. Generate studio image via Gemini
    6. Upload generated image to Cloudinary
    7. Save record to database
    8. Return URL

    Args:
        user_id: User ID
        item_id: Wardrobe item ID

    Returns:
        Dict with generated image URL
    """
    try:
        # 1. Check user tokens
        tokens = UserRepository.get_tokens(UUID(user_id))
        if tokens <= 0:
            return {"success": False, "message": "No tokens available. Please purchase more tokens.", "tokens": 0}

        # 2. Fetch item from database
        item = WardrobeRepository.get_by_id(item_id)

        if not item:
            return {"success": False, "message": "Item not found"}

        # 3. Verify item belongs to user
        if str(item["user_id"]) != user_id:
            return {"success": False, "message": "Item not found"}

        image_url = item["image_url"]
        category_group = item["category_group"]

        print(f"[STUDIO CONTROLLER] Processing item: {item_id}")
        print(f"[STUDIO CONTROLLER] Category: {category_group}")
        print(f"[STUDIO CONTROLLER] Original image URL: {image_url}")

        # 2. Download image from Cloudinary
        response = requests.get(image_url)
        response.raise_for_status()
        image_bytes = io.BytesIO(response.content)

        # 3. Choose prompt based on category
        prompt = get_prompt_for_category(category_group)
        print(f"[STUDIO CONTROLLER] Using prompt for: {category_group}")

        # 4. Generate studio image via Gemini
        result = StudioImageService.generate_studio_image(
            image_file=image_bytes,
            prompt=prompt
        )

        if not result["success"]:
            return result

        generated_image = result["image"]

        # 5. Upload generated image to Cloudinary
        img_buffer = io.BytesIO()
        generated_image.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        cloudinary_url = upload_image(img_buffer, folder="wearwhat/studio")
        print(f"[STUDIO CONTROLLER] Uploaded to Cloudinary: {cloudinary_url}")

        # 6. Save record to database
        record = StudioRepository.save(
            user_id=UUID(user_id),
            item_id=UUID(item_id),
            original_image_url=image_url,
            studio_image_url=cloudinary_url,
            category_group=category_group
        )
        print(f"[STUDIO CONTROLLER] Saved record: {record['id']}")

        # 7. Update wardrobe item with new studio image
        WardrobeRepository.update_image(
            item_id=UUID(item_id),
            user_id=UUID(user_id),
            image_url=cloudinary_url
        )
        print(f"[STUDIO CONTROLLER] Updated wardrobe item image")

        # 9. Deduct token after successful generation
        token_result = UserRepository.deduct_token(UUID(user_id))
        remaining_tokens = token_result.get("tokens", 0)
        print(f"[STUDIO CONTROLLER] Token deducted. Remaining: {remaining_tokens}")

        # 10. Return URL with tokens
        return {
            "success": True,
            "id": record["id"],
            "image_url": cloudinary_url,
            "item_id": item_id,
            "category_group": category_group,
            "original_image_url": image_url,
            "created_at": record["created_at"],
            "tokens": remaining_tokens
        }

    except Exception as e:
        print(f"[STUDIO CONTROLLER] Error: {str(e)}")
        return {"success": False, "message": str(e)}


def get_available_prompts() -> dict:
    """Get all available category prompts."""
    return {
        "success": True,
        "categories": list(CATEGORY_PROMPTS.keys()),
        "prompts": CATEGORY_PROMPTS
    }
