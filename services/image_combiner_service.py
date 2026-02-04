from PIL import Image
from io import BytesIO
import requests
from typing import List, Dict

from services.s3_service import upload_outfit_image
from config import MINIO_ENDPOINT, MINIO_PUBLIC_URL, MINIO_SECURE

class ImageCombinerService:
    @staticmethod
    def download_image(url: str) -> Image.Image:
        """Download image from URL and return PIL Image."""
        # Convert public URL to internal URL for Docker networking
        protocol = "https" if MINIO_SECURE else "http"
        public_prefix = f"{protocol}://{MINIO_PUBLIC_URL}/"
        internal_prefix = f"{protocol}://{MINIO_ENDPOINT}/"

        internal_url = url
        if url.startswith(public_prefix):
            internal_url = url.replace(public_prefix, internal_prefix)

        response = requests.get(internal_url)
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

        upper_height = int(size * 0.50)  # Upper wear area - equal split
        bottom_height = int(size * 0.50)  # Bottom wear area - equal split

        # Size hierarchy: clothing (largest) > footwear > accessories (smallest)
        main_item_size = int(size * 0.46)  # Max size for main clothing items
        footwear_size = int(size * 0.32)   # Medium size for footwear (increased)
        accessory_size = int(size * 0.22)  # Smallest size for accessories

        # Place upper wear (top-left) - largest
        if upper_wear:
            img = upper_wear[0]
            resized = ImageCombinerService.resize_contain(img, main_item_size, main_item_size)
            x = (left_width - resized.width) // 2
            y = (upper_height - resized.height) // 2
            combined.paste(resized, (x, y), resized if resized.mode == 'RGBA' else None)

        # Track outer wear height for accessories positioning
        outer_wear_area_height = 0

        # Place outer wear (top-right) - same size as upper wear
        if outer_wear:
            img = outer_wear[0]
            outer_wear_area_height = int(size * 0.45)  # Top 45% of right side for outer wear
            resized = ImageCombinerService.resize_contain(img, right_width - 10, main_item_size)
            x = left_width + (right_width - resized.width) // 2
            y = (outer_wear_area_height - resized.height) // 2
            combined.paste(resized, (x, y), resized if resized.mode == 'RGBA' else None)

        # Place bottom wear (bottom-left) - same size as upper wear
        if bottom_wear:
            img = bottom_wear[0]
            resized = ImageCombinerService.resize_contain(img, main_item_size, main_item_size)
            x = (left_width - resized.width) // 2
            y = upper_height + (bottom_height - resized.height) // 2
            combined.paste(resized, (x, y), resized if resized.mode == 'RGBA' else None)

        # Place footwear (bottom-right) - medium size
        if footwear:
            img = footwear[0]
            foot_area_height = int(size * 0.32)
            resized = ImageCombinerService.resize_contain(img, footwear_size, footwear_size)
            x = left_width + (right_width - resized.width) // 2
            y = size - foot_area_height + (foot_area_height - resized.height) // 2
            combined.paste(resized, (x, y), resized if resized.mode == 'RGBA' else None)

        # Place accessories (stacked on right side, below outer wear if present) - smallest
        if accessories:
            foot_area_height = int(size * 0.32)
            acc_start_y = outer_wear_area_height
            acc_area_height = size - foot_area_height - outer_wear_area_height
            acc_item_height = acc_area_height // max(len(accessories), 1)

            for idx, img in enumerate(accessories[:3]):  # Max 3 accessories
                resized = ImageCombinerService.resize_contain(img, accessory_size, accessory_size)
                x = left_width + (right_width - resized.width) // 2
                y = acc_start_y + idx * acc_item_height + (acc_item_height - resized.height) // 2
                combined.paste(resized, (x, y), resized if resized.mode == 'RGBA' else None)

        # Convert to RGB for JPEG
        combined_rgb = Image.new('RGB', combined.size, (255, 255, 255))
        combined_rgb.paste(combined, mask=combined.split()[3] if combined.mode == 'RGBA' else None)

        # Save to bytes
        buffer = BytesIO()
        combined_rgb.save(buffer, format='JPEG', quality=90)
        buffer.seek(0)

        # Upload to S3
        return upload_outfit_image(buffer)
