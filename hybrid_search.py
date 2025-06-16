# hybrid_search.py

import os
import re
import json
import sqlite3

import numpy as np
from cerebras.cloud.sdk import Cerebras
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ─── 0) Init Cerebras LLM client ─────────────────────────────────────────────
cerebras_key = os.getenv("CEREBRAS_API_KEY")
if not cerebras_key:
    raise RuntimeError("CEREBRAS_API_KEY nije postavljen u varijablama okoline.")
cclient = Cerebras(api_key=cerebras_key)

# ─── 1) Constants ────────────────────────────────────────────────────────────
EMBED_DIM    = 384
CUISINES     = [
    "Italian","Chinese","Mexican","Indian","Japanese","French","Thai",
    "Mediterranean","Greek","Spanish","Vietnamese","Korean","Turkish",
    "Lebanese","Moroccan","Ethiopian","Brazilian","Argentinian","American",
    "Cajun","Caribbean","German","Russian","Peruvian","Filipino","Malaysian",
    "Indonesian","Persian","Sri Lankan","Pakistani","Nepalese","Burmese",
    "Cambodian","Portuguese","Belgian","Swedish","Norwegian","Finnish","Polish",
    "Hungarian","Czech","Ukrainian","Australian","New Zealand","South African",
    "Jamaican","Chilean","Colombian","Venezuelan","Costa Rican","Nigerian",
    "Ghanaian","Kenyan","Tunisian","Swiss","Austrian","Dutch","Irish","Scottish",
    "Afghan","Bangladeshi","West African","Central American","Eastern European"
]
FLAVOURS     = [
    "Sweet","Sour","Salty","Bitter","Umami","Spicy","Savory","Tangy","Herbal",
    "Smoky","Creamy","Nutty","Earthy","Fruity","Citrus","Garlicky","Peppery",
    "Minty","Ginger","Sesame","Caramelized","Chocolatey","Cheesy","Buttery",
    "Tart","Zesty","Floral"
]
VALID_DIETS  = {
    "Vegan","Vegetarian","Pescatarian","Gluten-Free","Dairy-Free","Keto","Paleo",
    "Low Carb","High Protein","Low Fat","Low Sodium","Low Sugar","Whole30",
    "Mediterranean","Nut-Free","Vegan Low Carb","Vegetarian High Protein",
    "Diabetic-Friendly","Heart-Healthy","Kosher","Halal","DASH Diet","FODMAP Friendly"
}
VALID_HEALTH = {"Healthy","Moderately Healthy","Unhealthy"}
STOP_WORDS   = {"i","love","like","want","the","a","an"}

# ─── 2) Heuristics ────────────────────────────────────────────────────────────
def heuristic_excludes(query, existing):
    if existing:
        return existing
    m = re.search(r"(?:without|hate|exclude)[-\s]*([\w\s,]+)", query, re.I)
    if not m:
        return []
    toks = re.split(r"[,\s]+", m.group(1))
    return [t.lower() for t in toks if t and t.lower() not in STOP_WORDS]

def heuristic_includes(query, existing):
    if existing:
        return existing
    m = re.search(r"\bwith\s+([^,\.]+)", query, re.I)
    if not m:
        return []
    items = re.split(r",|\band\b", m.group(1))
    return [i.strip().lower() for i in items if i.strip() and i.strip().lower() not in STOP_WORDS]

def heuristic_health(query):
    if re.search(r"\bmoderately healthy\b", query, re.I):
        return "Moderately Healthy"
    if re.search(r"\bhealthy\b", query, re.I):
        return "Healthy"
    if re.search(r"\bunhealthy\b", query, re.I):
        return "Unhealthy"
    return ""

def heuristic_max_prep(query):
    m = re.search(r"ispod\s+(\d+)", query, re.I) or \
        re.search(r"under\s+(\d+)\s*minutes?", query, re.I)
    return int(m.group(1)) if m else None

# ─── 3) Parse user query via Cerebras LLM ───────────────────────────────────
def llm_parse_user_query(query: str) -> dict:
    system = (
        "Ti si asistent za recepte. Odgovori samo čistim JSON‐om:\n"
        f'  "cuisine": jedan od {CUISINES} ili "Other",\n'
        f'  "flavour_profile": jedan od {FLAVOURS} ili "Other",\n'
        '  "include_ingredients": [...],\n'
        '  "exclude_ingredients": [...],\n'
        f'  "nutrition_pref": jedan od {list(VALID_DIETS)} ili "",\n'
        f'  "healthiness_pref": jedan od {list(VALID_HEALTH)} ili "".\n'
        "Bez dodatnog teksta."
    )
    stream = cclient.chat.completions.create(
        model="llama-4-scout-17b-16e-instruct",
        messages=[{"role":"system","content":system},
                  {"role":"user","content":query}],
        temperature=0.0, top_p=1,
        max_completion_tokens=200, stop=["}\n"],
        stream=True
    )
    collected = "".join(c.choices[0].delta.content or "" for c in stream).strip() + "}"
    try:
        filt = json.loads(collected)
    except json.JSONDecodeError:
        filt = {
            "cuisine":"Other","flavour_profile":"Other",
            "include_ingredients":[],"exclude_ingredients":[],
            "nutrition_pref":"","healthiness_pref":""
        }

    # Normalize + heuristics
    nut = filt.get("nutrition_pref","").title()
    filt["nutrition_pref"]   = nut if nut in VALID_DIETS else ""
    filt["healthiness_pref"] = filt.get("healthiness_pref","") or heuristic_health(query)
    filt["exclude_ingredients"] = heuristic_excludes(query, filt.get("exclude_ingredients",[]))
    filt["include_ingredients"] = heuristic_includes(query, filt.get("include_ingredients",[]))
    filt["max_prep_time"]       = heuristic_max_prep(query)

    # Regex fallback for cuisine/flavour
    if filt["cuisine"]=="Other":
        for c in CUISINES:
            if c.lower() in query.lower():
                filt["cuisine"] = c; break
    if filt["flavour_profile"]=="Other":
        for f in FLAVOURS:
            if f.lower() in query.lower():
                filt["flavour_profile"] = f; break

    # Final validation
    if filt["cuisine"] not in CUISINES: filt["cuisine"]="Other"
    if filt["flavour_profile"] not in FLAVOURS: filt["flavour_profile"]="Other"
    print("DEBUG filters:", filt)
    return filt

# ─── 4) Build SQL query ─────────────────────────────────────────────────────
def build_sql_query(f: dict) -> str:
    conds = []
    if f["cuisine"]!="Other":        conds.append(f"cuisine='{f['cuisine']}'")
    if f["flavour_profile"]!="Other": conds.append(f"flavour_profile='{f['flavour_profile']}'")
    if f.get("nutrition_pref"):       conds.append(f"diet='{f['nutrition_pref']}'")
    if f.get("healthiness_pref"):     conds.append(f"healthiness='{f['healthiness_pref']}'")
    if f.get("max_prep_time") is not None:
        conds.append(f"prep_minutes <= {f['max_prep_time']}")
    for ing in f["include_ingredients"]:
        conds.append(
            "EXISTS(SELECT 1 FROM ingredients "
            f"WHERE recipe_id=recipes.id AND lower(ingredient) LIKE '%{ing}%')"
        )
    for ing in f["exclude_ingredients"]:
        conds.append(
            "NOT EXISTS(SELECT 1 FROM ingredients "
            f"WHERE recipe_id=recipes.id AND lower(ingredient) LIKE '%{ing}%')"
        )
    where = " AND ".join(conds) if conds else "1=1"
    return f"SELECT id FROM recipes WHERE {where};"

# ─── 5) Local embedding (384-dim) ──────────────────────────────────────────
local_model = SentenceTransformer("all-MiniLM-L6-v2")
def get_query_embedding(text: str) -> list:
    return local_model.encode(text).tolist()

# ─── 6) MongoDB setup ───────────────────────────────────────────────────────
mongo   = MongoClient("mongodb://localhost:27017")
emb_col = mongo["recipes_db"]["recipe_embeddings"]

# ─── 7) Hybrid search ───────────────────────────────────────────────────────
def hybrid_search(query: str, top_k: int = 5, vector_candidate_k: int = 30) -> list:
    f = llm_parse_user_query(query)

    # SQL faza
    conn = sqlite3.connect("recipes.db"); cur = conn.cursor()
    cur.execute(build_sql_query(f))
    sql_ids = [r[0] for r in cur.fetchall()]
    conn.close()
    if not sql_ids:
        return []

    # Query embedding
    q_emb = get_query_embedding(query)

    # Fetch candidate embeddings
    cand_ids, cand_embs = [], []
    for rid in sql_ids:
        doc = emb_col.find_one({"recipe_id": rid})
        emb = doc.get("embedding") if doc else None
        if isinstance(emb, list) and len(emb) == EMBED_DIM:
            cand_ids.append(rid); cand_embs.append(emb)

    if not cand_embs:
        return _sql_only(sql_ids, top_k)

    # Cosine similarity
    sims     = cosine_similarity([q_emb], np.array(cand_embs))[0]
    top_idxs = np.argsort(-sims)[:vector_candidate_k]
    vec_ids  = [cand_ids[i] for i in top_idxs]

    # Intersection + top_k
    final_ids = [rid for rid in vec_ids if rid in sql_ids][:top_k]

    # Fetch final details including prep_minutes
    conn = sqlite3.connect("recipes.db"); cur = conn.cursor()
    results = []
    for rid in final_ids:
        cur.execute("""
            SELECT id,title,servings,cuisine,flavour_profile,
                   prep_minutes,rating
            FROM recipes WHERE id = ?
        """, (rid,))
        row = cur.fetchone()
        if row:
            results.append({
                "id":            row[0],
                "title":         row[1],
                "servings":      row[2],
                "cuisine":       row[3],
                "flavour_profile": row[4],
                "prep_minutes":  row[5],
                "rating":        row[6]
            })
    conn.close()
    return results

def _sql_only(ids: list, k: int) -> list:
    conn = sqlite3.connect("recipes.db"); cur = conn.cursor()
    out  = []
    for rid in ids[:k]:
        cur.execute("""
            SELECT id,title,servings,cuisine,flavour_profile,
                   prep_minutes,rating
            FROM recipes WHERE id = ?
        """, (rid,))
        r = cur.fetchone()
        if r:
            out.append({
                "id":            r[0],
                "title":         r[1],
                "servings":      r[2],
                "cuisine":       r[3],
                "flavour_profile": r[4],
                "prep_minutes":  r[5],
                "rating":        r[6]
            })
    conn.close()
    return out
