import sqlite3

def get_db():
    return sqlite3.connect("data/bot.db")