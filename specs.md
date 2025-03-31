# **Recipe Recommendation with Weaviate and SQLite**

## **1. Opis projekta**
Ovaj projekt implementira sustav za preporuku recepata koristeći:
- **Weaviate** – vektorsku bazu podataka za semantičko pretraživanje recepata na temelju sastojaka, okusa i korisničkih preferencija.
- **SQLite** – relacijsku bazu podataka za pohranu strukturiranih podataka o receptima, sastojcima, kalorijskoj vrijednosti i ostalim prehrambenim informacijama.

Cilj projekta je omogućiti korisnicima intuitivno pretraživanje recepata koristeći prirodni jezik i semantičku sličnost umjesto klasičnih ključnih riječi.

---

## **2. Tehnologije**
- **Backend**: Python (FastAPI/Flask)
- **Weaviate**: Vektorska baza podataka za semantičko pretraživanje
- **SQLite**: Relacijska baza za strukturirane podatke
- **Embedding model**: OpenAI, Cohere ili Hugging Face modeli za pretvaranje teksta u vektore
- **Frontend**: React/Vue.js za korisničko sučelje
- **Containerization**: Docker za jednostavno postavljanje i skaliranje

---

## **3. Arhitektura sustava**

### **Komponente sustava**
- **Korisnici** (posjetitelji i registrirani korisnici)
- **Pretraživanje recepata** (Weaviate)
  - Korisnik može unijeti popis sastojaka ili upit u prirodnom jeziku
  - Weaviate vraća najbolje podudarajuće recepte temeljem semantičkog pretraživanja
- **Pohrana recepata** (SQLite)
  - Recepti su pohranjeni s definiranim sastojcima, kategorijama i nutritivnim vrijednostima
- **Preporuka recepata**
  - Koristi kombinaciju semantičkog pretraživanja i filtriranja prema kalorijskoj vrijednosti, vrsti obroka (doručak, ručak, večera) ili dijetetskim restrikcijama (vegetarijansko, bez glutena itd.)

---

## **4. Model podataka**

### **Weaviate (Vektorska baza podataka, semantičko pretraživanje)**
```json
{
  "id": "recipe-12345",
  "name": "Pasta Primavera",
  "ingredients": ["pasta", "paprika", "tikvica", "maslinovo ulje"],
  "flavor_profile": [0.12, -0.45, 0.89, ...],
  "cuisine": "Talijanska",
  "embedding": [0.31, -0.22, 0.78, ...]
}
```
- Svaki recept se sprema kao dokument s vektorskom reprezentacijom sastojaka i profila okusa.

### **SQLite (Relacijska baza podataka)**
```sql
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY,
    name TEXT,
    cuisine TEXT,
    calories INTEGER,
    meal_type TEXT CHECK(meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    diet TEXT CHECK(diet IN ('vegan', 'vegetarian', 'gluten-free', 'none'))
);

CREATE TABLE ingredients (
    id INTEGER PRIMARY KEY,
    recipe_id INTEGER REFERENCES recipes(id),
    name TEXT,
    amount TEXT
);
```
- SQLite čuva strukturirane podatke o receptima i njihovim sastojcima.

---

## **5. API specifikacija**

- **GET /recipes** – Dohvati sve recepte iz SQLite baze
- **GET /search?query=upit** – Semantičko pretraživanje recepata putem Weaviatea
- **POST /recipes** – Dodaj novi recept (Weaviate + SQLite)
- **GET /recipes/{id}** – Dohvati detalje određenog recepta
- **GET /recommend?ingredients=lista_sastojaka** – Preporuči recepte na temelju sastojaka

---

## **6. Funkcionalnosti**
- **Pretraživanje recepata pomoću prirodnog jezika** – Korisnici mogu upisati upite poput "zdravi doručak s jajima".
- **Preporuka na temelju sastojaka** – Ako korisnik unese dostupne sastojke, sustav predlaže recepte koji se najbolje podudaraju.
- **Filtriranje prema prehrambenim preferencijama** – Veganski, bez glutena, visoko-proteinski recepti.
- **Detaljan prikaz recepta** – Korisnici mogu vidjeti sastojke, način pripreme i nutritivne vrijednosti.

---

## **7. Testiranje**
- **Jedinično testiranje API-ja** (PyTest, Postman)
- **Integracijsko testiranje pretraživanja** (provjera relevantnosti preporuka)
- **Testiranje performansi Weaviatea** (brzina dohvaćanja rezultata, optimizacija vektorskih pretraga)

---

## **8. Zaključak**
Ovaj projekt demonstrira kako se kombinacija vektorskih baza podataka i relacijskih baza može koristiti za napredne sustave preporuke. Weaviate omogućava pretraživanje na temelju značenja, dok SQLite osigurava dosljednost i strukturirane podatke.

---

## **9. Alternativne tehnologije**

### **Umjesto Weaviatea:**
- **Pinecone** – Popularna alternativa za vektorsku pretragu
- **FAISS (Facebook AI Similarity Search)** – Brza implementacija vektorske pretrage

### **Umjesto SQLite:**
- **PostgreSQL + pgvector** – Omogućuje hibrid relacijskog i vektorskog pretraživanja
- **MongoDB** – Ako je potrebna fleksibilnija NoSQL struktura

Projekt može biti proširen dodatnim značajkama poput korisničkih ocjena recepata, prilagodljivih preporuka i podrške za različite jezike.

