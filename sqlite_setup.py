import sqlite3
import json

def setup_sqlite():
    conn = sqlite3.connect("recipes.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            name TEXT PRIMARY KEY,
            ingredients TEXT,
            flavor_profile TEXT,
            calories INTEGER
        )
    ''')

    with open("data/recipes.json", "r") as f:
        data = json.load(f)

    for recipe in data:
        c.execute('''
            INSERT OR REPLACE INTO recipes (name, ingredients, flavor_profile, calories)
            VALUES (?, ?, ?, ?)
        ''', (
            recipe["name"],
            ", ".join(recipe["ingredients"]),
            recipe["flavor_profile"],
            recipe["calories"]
        ))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_sqlite()
