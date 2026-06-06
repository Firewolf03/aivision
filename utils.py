import hashlib

def generate_hash(vendor, total, date):
    key = f"{vendor}_{total}_{date}"
    return hashlib.md5(key.encode()).hexdigest()

def items_to_text(items):
    if not items:
        return None

    return "; ".join([
        f"{i.get('item')} x{i.get('qty',1)}"
        for i in items
    ])

def items_to_text(items):
    if not items:
        return None

    return "; ".join([
        f"{i.get('item')} x{i.get('qty',1)}"
        for i in items
    ])

def detect_category(text):
    text = str(text).lower()

    if any(x in text for x in ["mcd", "kfc", "restaurant", "cafe", "coffee"]):
        return "F&B"
    elif any(x in text for x in ["petrol", "shell", "petronas"]):
        return "Transport"
    elif "invoice" in text:
        return "Services"
    elif "quotation" in text:
        return "Sales"
    else:
        return "Others"
