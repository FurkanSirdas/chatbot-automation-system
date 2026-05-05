import sqlite3

conn = sqlite3.connect("data/bot.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS intents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS aliases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    intent_id INTEGER,
    text TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    intent_id INTEGER,
    text TEXT
)
""")

conn.commit()
conn.close()

print("Tablolar oluşturuldu!")