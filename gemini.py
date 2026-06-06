import google.generativeai as genai
import json
from PIL import Image
import io

def extract_with_gemini(api_key, image, prompt):
    # 1. Initialize the API configuration
    genai.configure(api_key=api_key)

    # 2. Convert the input into a valid PIL Image if it isn't one already
    # This prevents the InvalidArgument exception
    if hasattr(image, "read"): 
        # Handles Streamlit UploadedFile objects automatically
        pil_image = Image.open(image)
    elif isinstance(image, bytes):
        # Handles raw bytes
        pil_image = Image.open(io.BytesIO(image))
    else:
        # Assumes it's already a PIL Image object
        pil_image = image

    # 3. Initialize the model with strict JSON output configuration
    model = genai.GenerativeModel(
        "gemini-1.5-flash",
        generation_config={"response_mime_type": "application/json"}
    )

    # 4. Pass the validated PIL image instead of the original raw variable
    response = model.generate_content([prompt, pil_image])

    # 5. Safely parse the JSON text
    try:
        return json.loads(response.text)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON. Raw API response: {response.text}")
        raise e
