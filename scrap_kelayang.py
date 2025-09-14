from serpapi import GoogleSearch
import json
import pandas as pd
import time
import os

# ===== KONFIGURASI =====
API_KEY = "459f970f577b5b7c12cdb834271660d66040595e54022a6936b28135e7ebf194"
DATA_ID = "0x2e174209273af563:0xc9c43cbde970f945"
JSON_FILE = "data_kelayang.json"
EXCEL_FILE = "data_kelayang.xlsx"
MAX_PAGES = 100

# ===== FUNGSI =====
def load_existing_reviews():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_reviews_to_json(reviews):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)

def save_reviews_to_excel(reviews):
    df = pd.DataFrame(reviews)
    df.to_excel(EXCEL_FILE, index=False)

def review_key(review):
    # Kombinasi unik untuk deteksi duplikat
    return f"{review['name']}_{review['date']}_{review['snippet']}"

# ===== MULAI SCRAPING =====
existing_reviews = load_existing_reviews()
existing_keys = set(review_key(r) for r in existing_reviews)

print(f"Review lama ditemukan: {len(existing_reviews)}")

params = {
    "api_key": API_KEY,
    "engine": "google_maps_reviews",
    "hl": "id",
    "data_id": DATA_ID,
    "no_cache": "true"
}

search = GoogleSearch(params)
all_reviews = existing_reviews.copy()
page_num = 1

while page_num <= MAX_PAGES:
    results = search.get_dict()

    if "error" in results:
        print(f"Error: {results['error']}")
        break

    new_reviews = 0
    for result in results.get("reviews", []):
        snippet = result.get("snippet", "")
        if not snippet:
            continue  # Skip kosong

        review = {
           "name": result.get("user", {}).get("name"),
            "date": result.get("date"),
            "rating": result.get("rating"),
            "review": snippet,
        }

        key = review_key(review)
        if key not in existing_keys:
            all_reviews.append(review)
            existing_keys.add(key)
            new_reviews += 1

    print(f"Page {page_num}: {new_reviews} review baru")

    next_token = results.get("serpapi_pagination", {}).get("next_page_token")
    if next_token:
        search.params_dict.update({"next_page_token": next_token})
        page_num += 1
        time.sleep(2)
    else:
        print("Tidak ada halaman berikutnya.")
        break

# ===== SIMPAN HASIL =====
save_reviews_to_json(all_reviews)
save_reviews_to_excel(all_reviews)
print(f"\n Total review setelah update: {len(all_reviews)}")
print(f"Data disimpan ke '{JSON_FILE}' dan '{EXCEL_FILE}'")
