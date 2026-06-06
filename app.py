# ==========================================
# AI RECEIPT SYSTEM - MISDEC VERSION
# Streamlit App (Production Structure)
# ==========================================

import streamlit as st
from PIL import Image
import datetime
import tempfile

from google_sheets import GoogleSheetService
from google_drive import upload_image
from utils import generate_hash, items_to_text, detect_category


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="AI Receipt Scanner",
    page_icon="📸",
    layout="centered"
)

st.title("📸 AI Receipt / Invoice Scanner")
st.caption("MISDEC AI Automation System")

st.markdown("---")


# =========================
# INIT SERVICES
# =========================
sheet_service = GoogleSheetService()


# =========================
# CAMERA + UPLOAD
# =========================
uploaded_file = st.file_uploader(
    "📁 Upload Receipt / Invoice",
    type=["jpg", "jpeg", "png"]
)

camera_file = st.camera_input("📸 Snap Receipt")

image_file = uploaded_file or camera_file


# =========================
# MAIN PROCESS
# =========================
if st.button("🚀 Process Document", use_container_width=True):

    if not image_file:
        st.error("Please upload or capture an image first.")
        st.stop()

    # =========================
    # SHOW IMAGE
    # =========================
    image = Image.open(image_file)
    st.image(image, caption="Input Document", use_container_width=True)


    # =========================
    # SAVE TEMP FILE (FOR DRIVE UPLOAD)
    # =========================
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(image_file.getbuffer())
        temp_path = tmp.name


    # =========================
    # UPLOAD TO GOOGLE DRIVE
    # =========================
    image_url = upload_image(temp_path)


    # =========================
    # MOCK AI OUTPUT (REPLACE WITH GEMINI LATER)
    # =========================
    data = {
        "document_type": "receipt",
        "document_number": None,
        "vendor_name": "Example Shop Sdn Bhd",
        "currency": "MYR",
        "subtotal": None,
        "tax_amount": None,
        "total_amount": 25.50,
        "items": [
            {"item": "Nasi Lemak", "qty": 2, "price": 5.00},
            {"item": "Teh O", "qty": 1, "price": 2.50}
        ],
        "payment_method": "cash",
        "location": "Melaka",
        "confidence_score": 0.95,
        "date": str(datetime.date.today())
    }


    # =========================
    # LOGIC PROCESSING
    # =========================
    category = detect_category(data)

    items_text = items_to_text(data.get("items"))

    doc_hash = generate_hash(
        data.get("vendor_name"),
        data.get("total_amount"),
        data.get("date")
    )


    # =========================
    # BUILD ROW (MATCH YOUR SHEET)
    # =========================
    row = [
        str(datetime.datetime.now()),        # Timestamp
        data.get("document_type"),           # Document Type
        data.get("document_number"),         # Document Number
        data.get("vendor_name"),             # Vendor Name
        data.get("currency"),                # Currency
        data.get("subtotal"),                # Subtotal
        data.get("tax_amount"),              # Tax Amount
        data.get("total_amount"),            # Total Amount
        items_text,                          # Items Text
        category,                            # Category
        data.get("payment_method"),         # Payment Method
        data.get("location"),               # Location
        data.get("confidence_score"),       # Confidence Score
        image_url                            # Image URL
    ]


    # =========================
    # SAVE TO GOOGLE SHEETS
    # =========================
    try:
        sheet_service.append_row(row)
        st.success("✅ Saved to Google Sheets successfully!")

    except Exception as e:
        st.error(f"❌ Failed to save: {str(e)}")
        st.stop()


    # =========================
    # SHOW OUTPUT
    # =========================
    st.markdown("### 📊 Extracted Data")
    st.json(data)

    st.markdown("### 🧾 Final Row Sent to Sheet")
    st.code(row)


    st.markdown("### 🔐 Document Hash (Duplicate Check Ready)")
    st.code(doc_hash)


# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("🚀 MISDEC AI Automation System • Streamlit + Gemini + Google Cloud")
