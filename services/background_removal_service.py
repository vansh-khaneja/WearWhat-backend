from rembg import remove
from PIL import Image
import io


def remove_background(file) -> io.BytesIO:
    """Removes outfit background and adds white background."""
    input_image = Image.open(file)
    output_image = remove(input_image)

    # Create white background and paste the image with transparency
    white_bg = Image.new("RGBA", output_image.size, (255, 255, 255, 255))
    white_bg.paste(output_image, mask=output_image.split()[3])

    # Convert to RGB (removes alpha channel)
    final_image = white_bg.convert("RGB")

    output_buffer = io.BytesIO()
    final_image.save(output_buffer, format="PNG")
    output_buffer.seek(0)

    return output_buffer
