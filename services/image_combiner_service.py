from PIL import Image
from io import BytesIO
import requests
from typing import List, Dict

from services.cloudinary_service import cloudinary
import cloudinary.uploader

class ImageCombinerService:
    @staticmethod
    def download_image(url: str) -> Image.Image:
        """Download image from URL and return PIL Image."""
        response = requests.get(url)
        return Image.open(BytesIO(response.content)).convert("RGBA")

    @staticmethod
    def resize_contain(img: Image.Image, target_width: int, target_height: int) -> Image.Image:
        """Resize image to fit within target dimensions, maintaining aspect ratio."""
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height

        if img_ratio > target_ratio:
            # Image is wider - fit to width
            new_width = target_width
            new_height = int(target_width / img_ratio)
        else:
            # Image is taller - fit to height
            new_height = target_height
            new_width = int(target_height * img_ratio)

        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    @staticmethod
    def combine_outfit_images(items: List[Dict], size: int = 800) -> str:
        """
        Combine outfit images in a styled layout:
        - Upper wear: large, top-left
        - Bottom wear: large, below upper wear on left
        - Footwear: bottom-right
        - Accessories: stacked on right side (top area)

        items should have 'image_url' and 'categoryGroup' keys
        """
        if not items:
            return None

        # Group items by category
        upper_wear = []
        bottom_wear = []
        footwear = []
        outer_wear = []
        accessories = []

        for item in items:
            url = item.get('image_url')
            category_group = item.get('categoryGroup', '').lower()

            if not url:
                continue

            try:
                img = ImageCombinerService.download_image(url)
                if 'upper' in category_group:
                    upper_wear.append(img)
                elif 'bottom' in category_group:
                    bottom_wear.append(img)
                elif 'foot' in category_group:
                    footwear.append(img)
                elif 'outer' in category_group:
                    outer_wear.append(img)
                else:
                    accessories.append(img)
            except Exception as e:
                print(f"Failed to download image {url}: {e}")
                continue

        # Create canvas with white background
        combined = Image.new('RGBA', (size, size), (255, 255, 255, 255))

        # Layout dimensions
        left_width = int(size * 0.6)  # Left column 60%
        right_width = size - left_width  # Right column 40%

        upper_height = int(size * 0.45)  # Upper wear area
        bottom_height = int(size * 0.55)  # Bottom wear area

        # Place upper wear (top-left, large)
        if upper_wear:
            img = upper_wear[0]
            resized = ImageCombinerService.resize_contain(img, left_width - 20, upper_height - 20)
            x = (left_width - resized.width) // 2
            y = (upper_height - resized.height) // 2
            combined.paste(resized, (x, y), resized if resized.mode == 'RGBA' else None)

        # Place outer wear (over upper wear if exists, or in upper area)
        if outer_wear:
            img = outer_wear[0]
            resized = ImageCombinerService.resize_contain(img, left_width - 40, upper_height - 40)
            x = (left_width - resized.width) // 2
            y = (upper_height - resized.height) // 2
            combined.paste(resized, (x, y), resized if resized.mode == 'RGBA' else None)

        # Place bottom wear (bottom-left, large)
        if bottom_wear:
            img = bottom_wear[0]
            resized = ImageCombinerService.resize_contain(img, left_width - 20, bottom_height - 20)
            x = (left_width - resized.width) // 2
            y = upper_height + (bottom_height - resized.height) // 2
            combined.paste(resized, (x, y), resized if resized.mode == 'RGBA' else None)

        # Place footwear (bottom-right)
        if footwear:
            img = footwear[0]
            foot_height = int(size * 0.35)
            resized = ImageCombinerService.resize_contain(img, right_width - 20, foot_height - 20)
            x = left_width + (right_width - resized.width) // 2
            y = size - foot_height + (foot_height - resized.height) // 2
            combined.paste(resized, (x, y), resized if resized.mode == 'RGBA' else None)

        # Place accessories (stacked on right side, top area)
        if accessories:
            acc_area_height = int(size * 0.65)  # Top 65% of right side
            acc_item_height = acc_area_height // max(len(accessories), 1)

            for idx, img in enumerate(accessories[:4]):  # Max 4 accessories
                resized = ImageCombinerService.resize_contain(img, right_width - 30, acc_item_height - 15)
                x = left_width + (right_width - resized.width) // 2
                y = idx * acc_item_height + (acc_item_height - resized.height) // 2
                combined.paste(resized, (x, y), resized if resized.mode == 'RGBA' else None)

        # Convert to RGB for JPEG
        combined_rgb = Image.new('RGB', combined.size, (255, 255, 255))
        combined_rgb.paste(combined, mask=combined.split()[3] if combined.mode == 'RGBA' else None)

        # Save to bytes
        buffer = BytesIO()
        combined_rgb.save(buffer, format='JPEG', quality=90)
        buffer.seek(0)

        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            buffer,
            folder="outfit_recommendations",
            resource_type="image"
        )

        return result.get("secure_url")
