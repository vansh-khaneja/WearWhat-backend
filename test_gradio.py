"""
Gradio Web App for ComfyUI Image Processing API
"""

import gradio as gr
from api_client import ComfyAPIClient
from PIL import Image
from io import BytesIO

# Modal API URL from deployment
API_URL = "https://vanshkhaneja2004--advanced-image-processing-comfyui-api.modal.run"

# Initialize the client
client = ComfyAPIClient(API_URL)


def process_image(image, prompt):
    """
    Process an image with the given prompt using the Modal API.
    
    Args:
        image: PIL Image or numpy array from Gradio
        prompt: Text prompt for image editing
    
    Returns:
        Processed image or error message
    """
    if image is None:
        return None, "Please upload an image first."
    
    if not prompt or prompt.strip() == "":
        return None, "Please enter a prompt."
    
    try:
        # Convert Gradio image to PIL Image if needed
        if isinstance(image, Image.Image):
            pil_image = image
        else:
            # Gradio might pass numpy array
            pil_image = Image.fromarray(image)
        
        # Process the image
        output_bytes = client.process_image(
            image=pil_image,
            prompt=prompt.strip()
        )
        
        # Convert bytes to PIL Image for display
        output_image = Image.open(BytesIO(output_bytes))
        
        return output_image, "✓ Image processed successfully!"
        
    except Exception as e:
        error_msg = str(e)
        return None, f"✗ Error: {error_msg}"


# Create Gradio interface
with gr.Blocks(title="ComfyUI Image Processing") as app:
    gr.Markdown(
        """
        # 🎨 ComfyUI Image Processing
        
        Upload an image and enter a prompt to process it using the ComfyUI API.
        
        **Example prompts:**
        - "turn these shoes in black color instead of brown"
        - "remove background and make it white"
        - "change the color of the shirt to blue"
        """
    )
    
    with gr.Row():
        with gr.Column():
            input_image = gr.Image(
                label="Upload Image",
                type="pil",
                height=400
            )
            prompt = gr.Textbox(
                label="Prompt",
                placeholder="Enter your image editing prompt here...",
                lines=3
            )
            submit_btn = gr.Button("Process Image", variant="primary", size="lg")
        
        with gr.Column():
            output_image = gr.Image(
                label="Processed Image",
                type="pil",
                height=400
            )
            status = gr.Textbox(
                label="Status",
                interactive=False,
                lines=2
            )
    
    # Example section
    gr.Markdown("### 📝 Example Prompts")
    examples = gr.Examples(
        examples=[
            ["turn these shoes in black color instead of brown"],
            ["remove background and make it white"],
            ["change the color of the shirt to blue"],
        ],
        inputs=prompt,
        label="Click to use example prompts"
    )
    
    # Set up the processing function
    submit_btn.click(
        fn=process_image,
        inputs=[input_image, prompt],
        outputs=[output_image, status]
    )
    
    # Also process on Enter key in prompt box
    prompt.submit(
        fn=process_image,
        inputs=[input_image, prompt],
        outputs=[output_image, status]
    )


if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=8092,
        share=False
    )
