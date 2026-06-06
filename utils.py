import hashlib

def generate_hash(vendor, total, date):
    key = f"{vendor}_{total}_{date}"
    return hashlib.md5(key.encode()).hexdigest()
