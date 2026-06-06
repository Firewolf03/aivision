import google.generativeai as genai
import json
from PIL import Image
import io

def extract_with_gemini(api_key, image_file, prompt):
    # 1. Configure the API
    genai.configure(api_key=api_key)
    
    # 2. Safely handle the image input
    # If it's a Streamlit UploadedFile or bytes, convert it to a PIL Image
    if hasattr(image_file, "read"):
        pil_image = Image.open(image_file)
    elif isinstance(image_file, bytes):
        pil_image = Image.open(io.BytesIO(image_file))
    else:
        pil_image = image_file # Assume it's already a PIL Image

    # 3. Enforce JSON output from the model itself
    model = genai.GenerativeModel(
        "gemini-1.5-flash",
        generation_config={"response_mime_type": "application/json"}
    )

    # 4. Generate content
    response = model.generate_content([prompt, pil_image])
    
    # 5. Parse safely (no need to manually strip markdown fences now!)
    try:
        return json.loads(response.text)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON. Raw response: {response.text}")
        raise e
