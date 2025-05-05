# Recipe Recommender System

Projekt iz kolegija **Raspodijeljene i nerelacijske baze podataka**.

## ✔️ Tehnologije
- Python
- SQLite (relacijska baza za nutritivne informacije)
- Weaviate (nerelacijska vektorska baza za semantičko pretraživanje)
- JSON (ulazni recepti)

## 🚀 Kako pokrenuti
1. Instaliraj pakete:
   ```
   pip install -r requirements.txt
   ```

2. Pokreni lokalni Weaviate (moraš imati Docker):
   ```
   docker run -d -p 8080:8080 \
     -e OPENAI_APIKEY=sk-... \
     semitechnologies/weaviate \
     --modules 'text2vec-openai' --host 0.0.0.0
   ```

3. Pokreni glavni program:
   ```
   python main.py
   ```

## 📁 Struktura
- `data/recipes.json` – recepti u JSON-u
- `sqlite_setup.py` – puni SQLite bazu
- `weaviate_setup.py` – puni Weaviate
- `recommend.py` – semantičko pretraživanje
- `main.py` – centralna skripta

