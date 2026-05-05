from db import get_db

def add_response(intent_id, text, user_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO responses (intent_id, text, user_id) VALUES (?, ?, ?)",
        (intent_id, text, user_id)
    )

    conn.commit()
    conn.close()