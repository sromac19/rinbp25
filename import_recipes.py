import sqlite3
import pandas as pd
import re

# ─── Funkcije za parsiranje ──────────────────────────────────────────────────

def parse_time_to_minutes(text: str) -> int:
    """
    Pokriva oblike:
      - "1 hr 30 min", "1 hrs 30 mins"
      - "25 mins", "2 hours", "45 m"
      - "1 h 5 m", "1hr45min" (zarez, razmaci i skraćenice)
      - "1 day 1 hrs 55 mins", "19 days 19 hrs 2 mins", "1 day 20 mins", itd.

    Vraća ukupan broj minuta.
    """
    if text is None:
        return 0
    text = str(text).strip().lower()
    if text == "":
        return 0

    days = 0
    hours = 0
    minutes = 0

    # 1) hvata "1 d", "1 day", "2 days"
    d_match = re.search(r'(\d+)\s*(?:d|day|days)\b', text)
    if d_match:
        days = int(d_match.group(1))

    # 2) hvata "1 h", "1 hr", "1 hrs", "1 hour", "1 hours"
    h_match = re.search(r'(\d+)\s*(?:h|hr|hrs?|hour|hours?)\b', text)
    if h_match:
        hours = int(h_match.group(1))

    # 3) hvata "30 m", "30 min", "30 mins", "30 minute", "30 minutes"
    m_match = re.search(r'(\d+)\s*(?:m|min|mins?|minute|minutes?)\b', text)
    if m_match:
        minutes = int(m_match.group(1))

    return days * 1440 + hours * 60 + minutes


def parse_ingredients(raw: str) -> list:
    if raw is None or raw == "":
        return []
    return [item.strip() for item in raw.split(',') if item.strip()]

def parse_nutrition(raw: str) -> dict:
    result = {}
    if raw is None or raw == "":
        return result
    pattern = re.compile(r'([A-Za-z ]+?)\s+(\d+(?:\.\d+)?)\s*(g|mg)\b')
    for match in pattern.finditer(raw):
        name = match.group(1).strip()
        amount = float(match.group(2))
        unit = match.group(3).lower()
        result[name] = (amount, unit)
    return result

# ─── Kreiranje SQLite tablica ────────────────────────────────────────────────

conn = sqlite3.connect("recipes.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    prep_minutes INTEGER,
    servings INTEGER,
    directions TEXT,
    rating REAL,
    nutrition_raw TEXT,
    cuisine TEXT,
    flavour_profile TEXT,
    healthiness TEXT,
    health_comment TEXT
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    ingredient TEXT NOT NULL,
    FOREIGN KEY(recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS nutrition (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    nutrient TEXT NOT NULL,
    amount REAL,
    unit TEXT,
    FOREIGN KEY(recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
);
""")

conn.commit()

# ─── Uvoz i parsiranje CSV-a ─────────────────────────────────────────────────

# Ako se tvoj CSV zove "recipes.csv", promijeni naziv ispod
df = pd.read_csv("recipes.csv")

for idx, row in df.iterrows():
    # 1) title (pretvori u string i strip)
    raw_title = row.get("title", "")
    title = "" if pd.isna(raw_title) else str(raw_title).strip()

    # 2) total_prep_time (može biti NaN)
    raw_time = row.get("total_prep_time", "")
    time_str = "" if pd.isna(raw_time) else str(raw_time)
    total_time = time_str.strip()

    # 3) servings (ako nije broj, ostavi None)
    servings = None
    raw_servings = row.get("servings", None)
    if not pd.isna(raw_servings):
        try:
            servings = int(raw_servings)
        except:
            try:
                servings = int(str(raw_servings).strip())
            except:
                servings = None

    # 4) directions (pretvori u string, izbjegni NaN)
    raw_directions = row.get("directions", "")
    directions = "" if pd.isna(raw_directions) else str(raw_directions).strip()

    # 5) rating (ako je NaN, ostavi None)
    raw_rating = row.get("rating", None)
    rating = None if pd.isna(raw_rating) else float(raw_rating)

    # 6) nutrition_raw (pretvori u string, izbjegni NaN)
    raw_nutrition = row.get("nutrition", "")
    nutrition_raw = "" if pd.isna(raw_nutrition) else str(raw_nutrition).strip()

    # 7) ingredients_raw (pretvori u string, izbjegni NaN)
    raw_ingredients = row.get("ingredients", "")
    ingredients_raw = "" if pd.isna(raw_ingredients) else str(raw_ingredients)

    # Parsiraj vrijeme u minute
    prep_minutes = parse_time_to_minutes(total_time)

    # Ubaci u tablicu recipes
    cursor.execute("""
        INSERT INTO recipes (
            title, prep_minutes, servings, directions, rating, nutrition_raw
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (title, prep_minutes, servings, directions, rating, nutrition_raw))
    recipe_id = cursor.lastrowid

    # Parsiraj i ubaci sastojke
    ingredients_list = parse_ingredients(ingredients_raw)
    for ing in ingredients_list:
        cursor.execute("""
            INSERT INTO ingredients (recipe_id, ingredient) 
            VALUES (?, ?)
        """, (recipe_id, ing))

    # Parsiraj i ubaci nutritivne vrijednosti
    nutrition_dict = parse_nutrition(nutrition_raw)
    for nutrient_name, (amount, unit) in nutrition_dict.items():
        cursor.execute("""
            INSERT INTO nutrition (recipe_id, nutrient, amount, unit) 
            VALUES (?, ?, ?, ?)
        """, (recipe_id, nutrient_name, amount, unit))

    # Povremeni commit
    if idx % 20 == 0:
        conn.commit()

conn.commit()
conn.close()
print("Uvoz u SQLite je gotov.")

