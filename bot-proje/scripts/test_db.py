import sqlite3

conn = sqlite3.connect("data/bot.db")
print("Database oluşturuldu!")

conn.close()