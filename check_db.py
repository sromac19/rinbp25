import sqlite3

conn = sqlite3.connect("recipes.db")
cursor = conn.cursor()

for table in ["recipes", "ingredients", "nutrition"]:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"Tablica '{table}' ima {count} zapisa.")

print("\nPrvih 3 retka iz tablice recipes:")
cursor.execute("SELECT id, title, prep_minutes, servings FROM recipes LIMIT 3;")
for row in cursor.fetchall():
    print(row)

print("\nPrvih 3 retka iz tablice ingredients:")
cursor.execute("SELECT id, recipe_id, ingredient FROM ingredients LIMIT 3;")
for row in cursor.fetchall():
    print(row)

print("\nPrvih 3 retka iz tablice nutrition:")
cursor.execute("SELECT id, recipe_id, nutrient, amount, unit FROM nutrition LIMIT 3;")
for row in cursor.fetchall():
    print(row)

conn.close()
