from google import genai
from google.genai import types
import json

def extract_with_gemini(api_key, image, prompt):

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=[prompt, image],
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json"
        )
    )

    text = response.text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    return json.loads(text)
