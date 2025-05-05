import sqlite3
import json

def initialize_sqlite_db():
    connection = sqlite3.connect("recipes.db")
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            name TEXT PRIMARY KEY,
            ingredients TEXT,
            flavor_profile TEXT,
            calories INTEGER
        )
    ''')

    with open("data/recipes.json", "r") as file:
        recipes = json.load(file)

    for recipe in recipes:
        cursor.execute('''
            INSERT OR REPLACE INTO recipes (name, ingredients, flavor_profile, calories)
            VALUES (?, ?, ?, ?)
        ''', (
            recipe["name"],
            ", ".join(recipe["ingredients"]),
            recipe["flavor_profile"],
            recipe["calories"]
        ))

    connection.commit()
    connection.close()

if __name__ == "__main__":
    initialize_sqlite_db()
