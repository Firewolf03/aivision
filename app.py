import streamlit as st
import json
import hashlib
import os
import datetime
import pandas as pd
from PIL import Image
from google import genai
from google.genai import types
from googlesheets import GoogleSheetService

sheet_service = GoogleSheetService("Sheet1")

# =========================
# CONFIG
# =========================
QUEUE_FILE = "offline_queue.json"

st.set_page_config(page_title="AI Receipt System", layout="centered")

st.title("📸 AI Receipt + Invoice Scanner (PRO)")

# =========================
# OFFLINE QUEUE SYSTEM
# =========================
def load_queue():
    if os.path.exists(QUEUE_FILE):
        return json.load(open(QUEUE_FILE))
    return []

def save_queue(queue):
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=2)

def add_to_queue(data):
    queue = load_queue()
    queue.append(data)
    save_queue(queue)

def sync_queue(sheet_func):
    queue = load_queue()
    if not queue:
        return "No pending data"

    success = 0
    remaining = []

    for item in queue:
        try:
            sheet_func(item)
            success += 1
        except:
            remaining.append(item)

    save_queue(remaining)
    return f"Synced {success} items"

# =========================
# DUPLICATE DETECTION
# =========================
def generate_hash(data):
    key = f"{data['vendor_name']}_{data['total_amount']}_{data['date']}"
    return hashlib.md5(key.encode()).hexdigest()

def is_duplicate(new_hash, existing_hashes):
    return new_hash in existing_hashes

# =========================
# IMAGE HASH (optional strong duplicate detection)
# =========================
def image_hash(image):
    return hashlib.md5(image.tobytes()).hexdigest()

# =========================
# GEMINI CALL
# =========================
def extract_data(api_key, image, prompt):

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
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
  "confidence_score": 0.0,
  "date": null
}
"""

# =========================
# UI INPUT
# =========================
api_key = st.text_input("Gemini API Key", type="password")

uploaded = st.file_uploader("Upload OR Camera", type=["png","jpg","jpeg"])

camera = st.camera_input("📸 Snap Receipt")

image = uploaded or camera

# =========================
# MAIN PROCESS
# =========================
if st.button("🚀 Process"):

    if not api_key:
        st.error("Missing API key")
        st.stop()

    if not image:
        st.error("No image")
        st.stop()

    img = Image.open(image)

    st.image(img, caption="Input Image")

    with st.spinner("Processing AI..."):

        data = extract_data(api_key, img, PROMPT)

        # =========================
        # AUTO CATEGORY
        # =========================
        text = str(data)

        if "restaurant" in text.lower():
            category = "F&B"
        elif "invoice" in text.lower():
            category = "Services"
        else:
            category = "Others"

        # =========================
        # DUPLICATE HASH
        # =========================
        doc_hash = generate_hash({
            "vendor_name": data.get("vendor_name"),
            "total_amount": data.get("total_amount"),
            "date": data.get("date")
        })

        # =========================
        # SHOW RESULT
        # =========================
        st.success("Extracted Data")
        st.json(data)

        st.info(f"Hash: {doc_hash}")

        # =========================
        # OFFLINE MODE (QUEUE)
        # =========================
        record = {
            "timestamp": str(datetime.datetime.now()),
            "data": data,
            "category": category,
            "hash": doc_hash
        }

        add_to_queue(record)

        st.success("Saved to offline queue (safe mode)")

# =========================
# SYNC BUTTON
# =========================
st.markdown("---")

if st.button("🔄 Sync Queue to Google Sheets"):
    st.success("Sync triggered (connect your sheet function here)")
