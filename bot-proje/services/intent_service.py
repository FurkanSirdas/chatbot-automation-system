from db import get_db

def add_intent(name, user_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO intents (name, user_id) VALUES (?, ?)",
        (name, user_id)
    )

    conn.commit()
    conn.close()