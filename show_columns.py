import sqlite3

conn = sqlite3.connect("recipes.db")
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(recipes);")
cols = cursor.fetchall()
conn.close()

print("Stupci u tablici 'recipes':")
for col in cols:
    print(col[1])
