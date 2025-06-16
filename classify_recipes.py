import os
import sqlite3
import json
import requests
from cerebras.cloud.sdk import Cerebras

# ─── 1) Postavi ključ ─────────────────────────────────────────────────────
cerebras_api_key = os.environ.get("CEREBRAS_API_KEY")
if not cerebras_api_key:
    raise RuntimeError("CEREBRAS_API_KEY nije postavljen u varijabli okoline.")
client = Cerebras(api_key=cerebras_api_key)

# ─── 2) Kategorije ─────────────────────────────────────────────────────────
CUISINES = [
    "Italian", "Chinese", "Mexican", "Indian", "Japanese", "French", "Thai",
    "Mediterranean", "Greek", "Spanish", "Vietnamese", "Korean", "Turkish",
    "Lebanese", "Moroccan", "Ethiopian", "Brazilian", "Argentinian",
    "American", "Cajun", "Caribbean", "German", "Russian", "Peruvian",
    "Filipino", "Malaysian", "Indonesian", "Persian", "Sri Lankan",
    "Pakistani", "Nepalese", "Burmese", "Cambodian", "Portuguese",
    "Belgian", "Swedish", "Norwegian", "Finnish", "Polish", "Hungarian",
    "Czech", "Ukrainian", "Australian", "New Zealand", "South African",
    "Jamaican", "Chilean", "Colombian", "Venezuelan", "Costa Rican",
    "Nigerian", "Ghanaian", "Kenyan", "Tunisian", "Swiss", "Austrian",
    "Dutch", "Irish", "Scottish", "Afghan", "Bangladeshi", "West African",
    "Central American", "Eastern European"
]
FLAVOURS = [
    "Sweet", "Sour", "Salty", "Bitter", "Umami", "Spicy", "Savory", "Tangy",
    "Herbal", "Smoky", "Creamy", "Nutty", "Earthy", "Fruity", "Citrus",
    "Garlicky", "Peppery", "Minty", "Ginger", "Sesame", "Caramelized",
    "Chocolatey", "Cheesy", "Buttery", "Tart", "Zesty", "Floral"
]
DIETS = {
    "Vegan", "Vegetarian", "Pescatarian", "Gluten-Free", "Dairy-Free", "Keto",
    "Paleo", "Low Carb", "High Protein", "Low Fat", "Low Sodium", "Low Sugar",
    "Whole30", "Mediterranean", "Nut-Free", "Vegan Low Carb",
    "Vegetarian High Protein", "Diabetic-Friendly", "Heart-Healthy",
    "Kosher", "Halal", "DASH Diet", "FODMAP Friendly"
}

# ─── 3) Pomoćna funkcija za Cerebras chat ─────────────────────────────────
def cerebras_chat(prompt: str, max_tokens: int = 512):
    stream = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-4-scout-17b-16e-instruct",
        stream=True,
        max_completion_tokens=max_tokens,
        temperature=0.0,
        top_p=1
    )
    collected = ""
    for chunk in stream:
        collected += chunk.choices[0].delta.content or ""
    try:
        return json.loads(collected.strip())
    except json.JSONDecodeError:
        return {}

# ─── 4) classify_cuisine_flavour ───────────────────────────────────────────
def classify_cuisine_flavour(text: str):
    prompt = (
        "You are a culinary expert.\n"
        "Classify this recipe into exactly one cuisine from:\n"
        f"{CUISINES}\n"
        "Then one flavour from:\n"
        f"{FLAVOURS}\n"
        "Return only JSON: {\"cuisine\":...,\"flavour\":...}\n\n"
        f"RECIPE:\n{text}"
    )
    resp = cerebras_chat(prompt)
    return {
        "cuisine": resp.get("cuisine"),
        "flavour": resp.get("flavour")
    }

# ─── 5) classify_diet ──────────────────────────────────────────────────────
def classify_diet(text: str):
    prompt = (
        "You are a diet expert.\n"
        "From these nutritional values choose one from:\n"
        f"{DIETS}\n"
        "Return only JSON: {\"diet\":...,\"comment\":...}\n\n"
        f"NUTRITION:\n{text}"
    )
    resp = cerebras_chat(prompt)
    return {
        "diet": resp.get("diet"),
        "comment": resp.get("comment")
    }

# ─── 6) derive_healthiness ────────────────────────────────────────────────
def derive_healthiness_from_diet(diet: str):
    if not diet:
        return None, None
    if any(x in diet for x in ["Vegan","Vegetarian","High Protein","Pescatarian","Paleo"]):
        return "Healthy", f"{diet} typically considered healthy"
    if any(x in diet for x in ["Low Fat","Low Sugar","Low Carb","Low Sodium","Dairy-Free","Gluten-Free"]):
        return "Moderately Healthy", f"{diet} often moderately healthy"
    return "Unhealthy", f"{diet} may not be the healthiest"

# ─── 7) Glavna funkcija (samo prvih 20) ────────────────────────────────────
def main():
    conn = sqlite3.connect("recipes.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, directions, nutrition_raw
        FROM recipes
        WHERE cuisine IS NULL
           OR flavour_profile IS NULL
           OR healthiness IS NULL
           OR diet IS NULL
    """)
    rows = cursor.fetchall()

   # printed = 0
    for rid, title, directions, nutrit in rows:
        full = f"{title}\n\n{directions}"
        cf = classify_cuisine_flavour(full)
        df = classify_diet(nutrit)
        health, note = derive_healthiness_from_diet(df.get("diet"))

        cursor.execute("""
            UPDATE recipes
            SET cuisine = ?, flavour_profile = ?, healthiness = ?, health_comment = ?, diet = ?
            WHERE id = ?
        """, (
            cf.get("cuisine"),
            cf.get("flavour"),
            health,
            note,
            df.get("diet"),
            rid
        ))
        conn.commit()

       # if printed < 20:
        print(f"ID {rid} → cuisine={cf.get('cuisine')}, flavour={cf.get('flavour')}, healthiness={health}, diet={df.get('diet')}")
           # printed += 1

    conn.close()

if __name__ == "__main__":
    main()
