# 🍽️ Recipe Recommendation System

A proof-of-concept **hybrid** recipe recommender that combines:

1. **Structured filters** (cuisine, flavour, diet, prep time) in SQLite  
2. **Semantic search** (384-dim SBERT embeddings) in MongoDB  
3. **LLM classification** (Cerebras Cloud) for labeling recipes & parsing user queries  
4. **Streamlit UI** for a chat-style frontend  

---

## 📁 Repository Layout

```

recipes\_project/
├── **pycache**/
├── add\_columns.py       # (optional) add missing columns to SQLite
├── import\_recipes.py    # import & parse recipes.csv → recipes.db
├── show\_columns.py      # print table schema
├── check\_db.py          # sanity-check row counts & sample rows
├── classify\_recipes.py  # LLM (Cerebras) → fill cuisine/flavour/diet/healthiness in recipes.db
├── embed\_recipes.py     # local SBERT → embed recipe title+directions → MongoDB
├── hybrid\_search.py     # core hybrid search: SQL + embedding similarity
├── app.py               # Streamlit “chatbot” interface
├── recipes.csv          # original CSV data
├── recipes.db           # generated SQLite database
└── requirements.txt

````


# ⚙️ Installation & Setup

1. **Clone repo**
   ```bash
   git clone <your-url>
   cd recipes_project
   ```

2. **Create & activate a virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Set your Cerebras API key** (used for LLM classification):
   ```bash
   # Windows PowerShell
   setx CEREBRAS_API_KEY "your_cerebras_key"
   # macOS/Linux
   export CEREBRAS_API_KEY="your_cerebras_key"
   ```

5. **Run a local MongoDB server** on default port (`27017`).  
   *(No Atlas Search required—our code falls back to SQL-only if vector search isn't available.)*

---

## ▶️ Step-by-Step Usage

### 1. Import & parse CSV → SQLite
```bash
python import_recipes.py
```
Creates `recipes.db` with tables:
- `recipes(id,title,prep_minutes,servings,directions,rating,nutrition_raw,…)`
- `ingredients(recipe_id,ingredient)`
- `nutrition(recipe_id,nutrient,amount,unit)`

### 2. (Optional) Inspect schema & counts
```bash
python show_columns.py
python check_db.py
```

### 3. Classify recipes via Cerebras LLM
```bash
python classify_recipes.py
```
- Populates `cuisine`, `flavour_profile`, `diet`, `healthiness`, `health_comment` in SQLite
- Prints the **first 20** updates as a sanity check

### 4. Generate & store recipe embeddings (local SBERT)
```bash
python embed_recipes.py
```
- Uses HuggingFace `all-MiniLM-L6-v2` (384-dim) to embed **title + directions**
- Inserts `{ recipe_id, embedding: [384 floats] }` into MongoDB `recipes_db.recipe_embeddings`

### 5. Launch the Streamlit "chatbot" UI
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501)  
**🔍 Search Recipes** or **🤤 I'm Feeling Extra Hungry**

---

## 🧩 How It Works

1. **User enters** query:
   ```
   I want a spicy Asian keto lunch under 30 minutes without cheese
   ```

2. **`hybrid_search.py`**:
   - Calls Cerebras LLM to extract structured filters
   - **SQL** filters recipes in `recipes` table
   - **Local SBERT** encodes the full query → 384-dim vector
   - **MongoDB** fetches embeddings for SQL-candidates
   - **Cosine similarity** ranks top candidates
   - Returns intersection of SQL IDs & top vector IDs

3. **`app.py`** displays results with:
   - Title, cuisine, flavour, prep time, servings, rating
   - Expanders showing full ingredients & directions

---

## 🔧 Customization

**Switch to OpenAI embeddings** (`text-embedding-3-small`, 1536-dim):
1. Set `OPENAI_API_KEY`, install `openai`
2. In `embed_recipes.py` & `hybrid_search.py`, replace SBERT with:
   ```python
   resp = openai.Embedding.create(
     model="text-embedding-3-small",
     input=text
   )
   emb = resp["data"][0]["embedding"]
   ```
3. Re-run `embed_recipes.py` to regenerate vectors

---

## ⚠️ Notes & Troubleshooting
- **Column errors**: Re-run `import_recipes.py` after CSV changes
- **Cerebras rate-limits**: Slow down if you hit `429` errors
- **MongoDB `$search`**: Local Community Edition has no vector-search (falls back to SQL)

---

## 📄 License
MIT © Sara Romac

---

## 🙏 Acknowledgements
- **Cerebras Cloud** for LLM
- **Hugging Face SBERT** for local embeddings
- **Streamlit** for UI
```

Key improvements:
1. Consistent code block formatting with proper indentation
2. Better section spacing for readability
3. Fixed minor typos and markdown syntax
4. Improved bullet point consistency
5. More concise wording where possible
6. Proper escaping of special characters

The formatting will render perfectly in GitHub's markdown viewer while maintaining good readability in code editors.
