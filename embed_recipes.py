import sqlite3
import time
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

# ─── 1) Učitaj lokalni model (jednokratno će skinuti 'all-MiniLM-L6-v2') ───
print("Učitavam lokalni embedding model…")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model učitan uspješno.")

# ─── 2) Spoji se na SQLite ──────────────────────────────────────────────────
conn = sqlite3.connect("recipes.db")
cursor = conn.cursor()

# ─── 3) Spoji se na MongoDB (mora biti pokrenut lokalno) ────────────────────
client = MongoClient("mongodb://localhost:27017")
db = client["recipes_db"]
embeddings_col = db["recipe_embeddings"]

# ─── 4) Dohvati sve recepte iz SQLite ───────────────────────────────────────
cursor.execute("SELECT id, title, directions FROM recipes")
rows = cursor.fetchall()

# ─── 5) Prođi kroz sve recepte i generiraj embeddinge lokalno ───────────────
for recipe_id, title, directions in rows:
    # Ako embedding već postoji, preskoči
    if embeddings_col.find_one({"recipe_id": recipe_id}):
        continue

    full_text = f"{title}\n\n{directions}"

    # Generiraj embedding localno
    try:
        embedding_vector = model.encode(full_text, show_progress_bar=False)
    except Exception as e:
        print(f"Warning: ne mogu dobiti embedding lokalno za ID {recipe_id} ({e})")
        continue

    # Spremi embedding u MongoDB
    embeddings_col.insert_one({
        "recipe_id": recipe_id,
        "embedding": embedding_vector.tolist()
    })
    print(f"Embedding (lokalno) spremljen za recept ID {recipe_id}")

    # (opcionalno) kratka pauza da ne bi preopteretila disk ili CPU
    time.sleep(0.1)

conn.close()
print("Proces embediranja (lokalno) je dovršen.")
