import streamlit as st
from PIL import Image
import datetime
import requests

from gemini import extract_with_gemini   # Pastikan fungsi gemini.py dah dikemas kini

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
# INPUT (API KEY)
# =========================
api_key = st.text_input("Gemini API Key", type="password")

# Pilihan Input Imej yang lebih stabil menggunakan Tabs
tab1, tab2 = st.tabs(["📸 Ambil Gambar", "📁 Muat Naik Fail"])

file = None
with tab1:
    cam_file = st.camera_input("Snap Receipt")
    if cam_file:
        file = cam_file

with tab2:
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        file = uploaded_file

# =========================
# SEND FUNCTION
# =========================
def send_to_sheet(payload):
    try:
        response = requests.post(APPS_SCRIPT_URL, json=payload, timeout=10)
        return response
    except Exception as e:
        st.error(f"Gagal berhubung dengan Google Sheets: {e}")
        return None

# =========================
# PROCESS
# =========================
if st.button("🚀 Extract & Save"):

    if not api_key:
        st.error("Sila masukkan API key Gemini anda.")
        st.stop()

    if not file:
        st.error("Sila ambil gambar atau muat naik fail resit terlebih dahulu.")
        st.stop()

    # Paparkan imej di UI Streamlit
    image = Image.open(file)
    st.image(image, caption="Imej yang diproses", use_container_width=True)

    # =========================
    # GEMINI AI
    # =========================
    with st.spinner("AI sedang membaca resit..."):
        try:
            # Nota: Kita hantar 'image' (PIL Object) yang dah dibuka siap-siap
            data = extract_with_gemini(api_key, image, PROMPT)
            st.success("AI Extraction Done")
            st.json(data)
        except Exception as e:
            st.error(f"Gagal memproses imej dengan Gemini: {e}")
            st.stop()

    # =========================
    # FORMAT ITEMS
    # =========================
    # Menggunakan penanganan jika 'items' tiada atau bukan dalam bentuk list
    items_list = data.get("items") if isinstance(data.get("items"), list) else []
    items_text = "; ".join(
        [f"{i.get('item', 'Unknown')} x{i.get('qty', 1)}" for i in items_list]
    )

    # =========================
    # AUTO CATEGORY
    # =========================
    text = str(data).lower()

    if "restaurant" in text or "food" in text or "kedai makan" in text:
        category = "F&B"
    elif "invoice" in text or "service" in text:
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
        "currency": data.get("currency", "MYR"),
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
    with st.spinner("Menghantar data ke Google Sheets..."):
        res = send_to_sheet(payload)
        
        if res and res.status_code == 200:
            st.success("Berjaya disimpan ke Google Sheets!")
            st.write("Respon Apps Script:", res.text)
        else:
            st.error("Gagal menyimpan data. Sila semak Apps Script Web App URL anda.")
