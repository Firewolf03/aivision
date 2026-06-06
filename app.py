import streamlit as st
from PIL import Image
import datetime
import requests

from gemini import extract_with_gemini   # or paste function directly

# =========================
# CONFIG
# =========================
APPS_SCRIPT_URL = "YOUR_WEB_APP_URL"

st.title("📸 AI Receipt Scanner (Gemini + Streamlit)")


# =========================
# PROMPT
# =========================
PROMPT = """
Extract receipt/invoice/quotation into JSON:

{
  "document_type": "receipt | invoice | quotation",
  "document_number": null,
  "vendor_name": null,
  "currency": "MYR",
  "subtotal": null,
  "tax_amount": null,
  "total_amount": null,
  "items": [],
  "payment_method": null,
  "location": null,
  "confidence_score": 0.0
}
"""


# =========================
# INPUT
# =========================
api_key = st.text_input("Gemini API Key", type="password")

file = st.camera_input("📸 Snap Receipt") or st.file_uploader("Upload Image")

# =========================
# SEND FUNCTION
# =========================
def send_to_sheet(payload):
    return requests.post(APPS_SCRIPT_URL, json=payload)


# =========================
# PROCESS
# =========================
if st.button("🚀 Extract & Save"):

    if not api_key:
        st.error("Missing API key")
        st.stop()

    if not file:
        st.error("No image")
        st.stop()

    image = Image.open(file)
    st.image(image)

    # =========================
    # GEMINI AI
    # =========================
    data = extract_with_gemini(api_key, image, PROMPT)

    st.success("AI Extraction Done")
    st.json(data)

    # =========================
    # FORMAT ITEMS
    # =========================
    items_text = "; ".join(
        [f"{i.get('item')} x{i.get('qty',1)}" for i in data.get("items", [])]
    )

    # =========================
    # AUTO CATEGORY
    # =========================
    text = str(data).lower()

    if "restaurant" in text or "food" in text:
        category = "F&B"
    elif "invoice" in text:
        category = "Services"
    else:
        category = "Others"

    # =========================
    # BUILD PAYLOAD
    # =========================
    payload = {
        "document_type": data.get("document_type"),
        "document_number": data.get("document_number"),
        "vendor_name": data.get("vendor_name"),
        "currency": data.get("currency"),
        "subtotal": data.get("subtotal"),
        "tax_amount": data.get("tax_amount"),
        "total_amount": data.get("total_amount"),
        "items_text": items_text,
        "category": category,
        "payment_method": data.get("payment_method"),
        "location": data.get("location"),
        "confidence_score": data.get("confidence_score"),
        "image_url": "NOT_SET_YET"
    }

    # =========================
    # SEND TO SHEET
    # =========================
    res = send_to_sheet(payload)

    st.success("Saved to Google Sheets")
    st.write(res.text)
