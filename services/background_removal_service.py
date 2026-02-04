from rembg import remove
from PIL import Image
import io


def remove_background(file) -> io.BytesIO:
    """Removes outfit background, auto-crops to content bounds, and adds white background."""
    input_image = Image.open(file)
    output_image = remove(input_image)

    # Auto-crop to content bounds using alpha channel
    # getbbox() returns bounding box of non-zero (non-transparent) regions
    alpha_channel = output_image.split()[3]
    bbox = alpha_channel.getbbox()

    if bbox:
        # Add small padding around the content (5% of dimensions)
        padding_x = int((bbox[2] - bbox[0]) * 0.05)
        padding_y = int((bbox[3] - bbox[1]) * 0.05)

        # Ensure padding doesn't go outside image bounds
        padded_bbox = (
            max(0, bbox[0] - padding_x),
            max(0, bbox[1] - padding_y),
            min(output_image.width, bbox[2] + padding_x),
            min(output_image.height, bbox[3] + padding_y)
        )

        # Crop to the content bounding box with padding
        output_image = output_image.crop(padded_bbox)

    # Create white background and paste the image with transparency
    white_bg = Image.new("RGBA", output_image.size, (255, 255, 255, 255))
    white_bg.paste(output_image, mask=output_image.split()[3])

    # Convert to RGB (removes alpha channel)
    final_image = white_bg.convert("RGB")

    output_buffer = io.BytesIO()
    final_image.save(output_buffer, format="PNG")
    output_buffer.seek(0)

    return output_buffer
