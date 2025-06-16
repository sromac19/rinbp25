import sqlite3

# Spoji se na SQLite bazu
conn = sqlite3.connect("recipes.db")
c = conn.cursor()

# Dodaj stupce ako već ne postoje
try:
    c.execute("ALTER TABLE recipes ADD COLUMN cuisine TEXT")
except sqlite3.OperationalError:
    pass

try:
    c.execute("ALTER TABLE recipes ADD COLUMN flavour_profile TEXT")
except sqlite3.OperationalError:
    pass

try:
    c.execute("ALTER TABLE recipes ADD COLUMN diet TEXT")
except sqlite3.OperationalError:
    pass

try:
    c.execute("ALTER TABLE recipes ADD COLUMN health_comment TEXT")
except sqlite3.OperationalError:
    pass

conn.commit()
conn.close()
print("Stupci su kreirani (ili su već postojali).")
