import google.generativeai as genai
import json
import io

def extract_with_gemini(api_key, image, prompt):

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-1.5-flash")

    # convert image
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="JPEG")
    img_bytes = img_bytes.getvalue()

    response = model.generate_content([
        prompt,
        {
            "mime_type": "image/jpeg",
            "data": img_bytes
        }
    ])

    text = response.text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    return json.loads(text)
