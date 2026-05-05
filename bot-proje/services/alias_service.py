from db import get_db

def add_alias(intent_id, text, user_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO aliases (intent_id, text, user_id) VALUES (?, ?, ?)",
        (intent_id, text, user_id)
    )

    conn.commit()
    conn.close()