"""
Simple Python API Client for Modal ComfyUI Image Processing

This client allows you to send images and prompts to your deployed Modal API
and receive processed images back.
"""

import base64
import requests
from pathlib import Path
from typing import Union, Optional
from io import BytesIO
from PIL import Image


class ComfyAPIClient:
    """Client for interacting with the Modal ComfyUI API endpoint."""
    
    def __init__(self, api_url: str):
        """
        Initialize the API client.
        
        Args:
            api_url: The Modal API endpoint URL (e.g., "https://your-username--advanced-image-processing-api.modal.run")
        """
        self.api_url = api_url.rstrip('/')
    
    def process_image(
        self,
        image: Union[str, Path, bytes, Image.Image],
        prompt: Optional[str] = None,
        output_path: Optional[Union[str, Path]] = None
    ) -> bytes:
        """
        Process an image with the given prompt.
        
        Args:
            image: Image input - can be:
                - File path (str or Path)
                - Image bytes
                - PIL Image object
            prompt: Optional text prompt for image editing
            output_path: Optional path to save the output image
        
        Returns:
            bytes: The processed image as PNG bytes
        
        Raises:
            requests.RequestException: If the API request fails
            ValueError: If the image cannot be loaded
        """
        # Prepare the request payload
        payload = {}
        
        # Handle different image input types
        if isinstance(image, (str, Path)):
            # File path
            image_path = Path(image)
            if not image_path.exists():
                raise ValueError(f"Image file not found: {image_path}")
            
            # Read and encode as base64
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            payload['image_base64'] = base64.b64encode(image_bytes).decode('utf-8')
            
        elif isinstance(image, bytes):
            # Already bytes - encode as base64
            payload['image_base64'] = base64.b64encode(image).decode('utf-8')
            
        elif isinstance(image, Image.Image):
            # PIL Image - convert to bytes
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            image_bytes = buffer.getvalue()
            payload['image_base64'] = base64.b64encode(image_bytes).decode('utf-8')
            
        else:
            raise ValueError(f"Unsupported image type: {type(image)}")
        
        # Add prompt if provided
        if prompt:
            payload['prompt'] = prompt
        
        # Make the API request
        print(f"Sending request to {self.api_url}...")
        response = requests.post(
            self.api_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=300  # 5 minute timeout for processing
        )
        
        # Check for errors
        if response.status_code != 200:
            try:
                error_data = response.json()
                error_msg = error_data.get('error', 'Unknown error')
            except:
                error_msg = response.text
            raise requests.RequestException(
                f"API request failed with status {response.status_code}: {error_msg}"
            )
        
        # Get the image bytes from response
        output_image_bytes = response.content
        
        # Save to file if output path is provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(output_image_bytes)
            print(f"Output image saved to: {output_path}")
        
        return output_image_bytes
    
    def process_image_from_url(
        self,
        image_url: str,
        prompt: Optional[str] = None,
        output_path: Optional[Union[str, Path]] = None
    ) -> bytes:
        """
        Process an image from a URL with the given prompt.
        
        Args:
            image_url: URL to the input image
            prompt: Optional text prompt for image editing
            output_path: Optional path to save the output image
        
        Returns:
            bytes: The processed image as PNG bytes
        """
        payload = {'image_url': image_url}
        
        if prompt:
            payload['prompt'] = prompt
        
        print(f"Sending request to {self.api_url}...")
        response = requests.post(
            self.api_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=300
        )
        
        if response.status_code != 200:
            try:
                error_data = response.json()
                error_msg = error_data.get('error', 'Unknown error')
            except:
                error_msg = response.text
            raise requests.RequestException(
                f"API request failed with status {response.status_code}: {error_msg}"
            )
        
        output_image_bytes = response.content
        
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(output_image_bytes)
            print(f"Output image saved to: {output_path}")
        
        return output_image_bytes


# Example usage
if __name__ == "__main__":
    # Modal API URL from deployment
    API_URL = "https://vanshkhaneja2004--advanced-image-processing-comfyui-api.modal.run"
    
    # Initialize the client
    client = ComfyAPIClient(API_URL)
    
    # Example 1: Process image from file path
    try:
        input_image = "shirt.jpg"  # Replace with your image path
        prompt = "turn tthis shirt from red to blue"
        output_image = client.process_image(
            image=input_image,
            prompt=prompt,
            output_path="output_image.png"
        )
        print("✓ Image processed successfully!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    

