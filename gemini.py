import io

def extract_with_gemini(api_key, image, prompt):

    client = genai.Client(api_key=api_key)

    # convert image safely
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="JPEG")
    img_bytes = img_bytes.getvalue()

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=[
            prompt,
            types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
        ],
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json"
        )
    )

    text = response.text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    return json.loads(text)
