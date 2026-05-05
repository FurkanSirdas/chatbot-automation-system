from flask import Flask, request, jsonify
from bot import Bot
from flask import render_template
import sqlite3
from flask import redirect
from flask import Response
import json
from flask import redirect
from db import get_db
from services.intent_service import add_intent
from services.alias_service import add_alias
from services.response_service import add_response

app = Flask(__name__)

@app.route("/admin")
def admin():
    conn = get_db()
    cursor = conn.cursor()

    selected_user_id = request.args.get("user_id")

    
    if not selected_user_id or selected_user_id == "None":
        cursor.execute("SELECT id FROM users LIMIT 1")
        user = cursor.fetchone()
        selected_user_id = user[0] if user else 0
    else:
        selected_user_id = int(selected_user_id)

    # intents
    cursor.execute(
        "SELECT id, name FROM intents WHERE user_id=?",
        (selected_user_id,)
    )
    intents = cursor.fetchall()

    # users
    cursor.execute("SELECT id, name FROM users")
    users = cursor.fetchall()

    conn.close()

    return render_template(
        "admin.html",
        intents=intents,
        users=users,
        selected_user_id=selected_user_id
    )

@app.route("/webhook", methods=["POST"])
def webhook():
    # user seçimi
    user_id = request.args.get("user_id", 1)
    bot = Bot(user_id=int(user_id))

    try:
        data = request.get_json(force=True)
    except:
        return jsonify({"error": "JSON parse edilemedi"}), 400

    if not data:
        return jsonify({"error": "Boş veri geldi"}), 400

    message = data.get("message", "")

    reply = bot.get_reply(message)

    if not reply:
        return jsonify({"reply": None})

    return Response(
        json.dumps({
            "reply": reply["text"],
            "confidence": reply["confidence"]
        }, ensure_ascii=False),
        content_type="application/json"
    )

@app.route("/add-intent", methods=["POST"])
def add_intent_route():
    name = request.form.get("name")
    selected_user_id = int(request.form.get("user_id"))

    if not name or name.strip() == "":
        return redirect(f"/admin?user_id={selected_user_id}&error=intent")

    name = name.strip()

    add_intent(name, selected_user_id)

    return redirect(f"/admin?user_id={selected_user_id}&success=intent_added")

@app.route("/add-alias", methods=["POST"])
def add_alias_route():
    intent_id = request.form.get("intent_id")
    text = request.form.get("text")
    selected_user_id = int(request.form.get("user_id"))

    if not intent_id or not text:
        return redirect(f"/admin?user_id={selected_user_id}&error=alias")

    add_alias(intent_id, text.strip(), selected_user_id)

    return redirect(f"/admin?user_id={selected_user_id}&success=alias_added")

@app.route("/add-response", methods=["POST"])
def add_response_route():
    intent_id = request.form.get("intent_id")
    text = request.form.get("text")
    selected_user_id = int(request.form.get("user_id"))

    if not intent_id or not text:
        return redirect(f"/admin?user_id={selected_user_id}&error=response")

    add_response(intent_id, text.strip(), selected_user_id)

    return redirect(f"/admin?user_id={selected_user_id}&success=response_added")

@app.route("/intents")
def list_intents():
    user_id = request.args.get("user_id")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name FROM intents WHERE user_id=?",
        (user_id,)
    )
    intents = cursor.fetchall()

    conn.close()

    return render_template("intents.html", intents=intents, selected_user_id=user_id)

@app.route("/delete-intent/<int:intent_id>")
def delete_intent(intent_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM intents WHERE id=?", (intent_id,))
    cursor.execute("DELETE FROM aliases WHERE intent_id=?", (intent_id,))
    cursor.execute("DELETE FROM responses WHERE intent_id=?", (intent_id,))

    conn.commit()
    conn.close()

    return "Silindi <a href='/intents'>Geri dön</a>"

@app.route("/edit-intent/<int:intent_id>", methods=["GET", "POST"])
def edit_intent(intent_id):
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        new_name = request.form.get("name")

        cursor.execute(
            "UPDATE intents SET name=? WHERE id=?",
            (new_name, intent_id)
        )

        conn.commit()
        conn.close()

        user_id = request.form.get("user_id")
        return redirect(f"/intents?user_id={user_id}")

    cursor.execute("SELECT name FROM intents WHERE id=?", (intent_id,))
    intent = cursor.fetchone()

    conn.close()

    user_id = request.args.get("user_id")

    if not user_id or user_id == "None":
        user_id = 0
    else:
        user_id = int(user_id)

    return render_template(
        "edit_intent.html",
        intent=intent,
        id=intent_id,
        selected_user_id=user_id
    )

@app.route("/aliases")
def list_aliases():
    user_id = request.args.get("user_id")  # 🔥 EKLE

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT aliases.id, intents.name, aliases.text
        FROM aliases
        JOIN intents ON aliases.intent_id = intents.id
        WHERE aliases.user_id=?
    """, (user_id,))

    aliases = cursor.fetchall()

    conn.close()

    return render_template(
        "aliases.html",
        aliases=aliases,
        selected_user_id=user_id  # 🔥 bunu da gönder
    )

@app.route("/delete-alias/<int:alias_id>")
def delete_alias(alias_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM aliases WHERE id=?", (alias_id,))
    conn.commit()
    conn.close()

    return "Alias silindi <a href='/aliases'>Geri</a>"

@app.route("/responses")
def list_responses():
    user_id = request.args.get("user_id")  #  EKLE

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT responses.id, intents.name, responses.text
        FROM responses
        JOIN intents ON responses.intent_id = intents.id
        WHERE responses.user_id=?
    """, (user_id,))

    responses = cursor.fetchall()

    conn.close()

    return render_template(
        "responses.html",
        responses=responses,
        selected_user_id=user_id
    )

@app.route("/delete-response/<int:res_id>")
def delete_response(res_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM responses WHERE id=?", (res_id,))
    conn.commit()
    conn.close()

    return "Cevap silindi <a href='/responses'>Geri</a>"

@app.route("/edit-alias/<int:alias_id>", methods=["GET", "POST"])
def edit_alias(alias_id):
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        new_text = request.form.get("text")

        cursor.execute(
            "UPDATE aliases SET text=? WHERE id=?",
            (new_text, alias_id)
        )

        conn.commit()
        conn.close()

        user_id = request.form.get("user_id")
        return redirect(f"/aliases?user_id={user_id}")

    cursor.execute("SELECT text FROM aliases WHERE id=?", (alias_id,))
    alias = cursor.fetchone()

    conn.close()

    user_id = request.args.get("user_id")

    if not user_id or user_id == "None":
        user_id = 0
    else:
        user_id = int(user_id)

    return render_template(
        "edit_alias.html",
        alias=alias,
        id=alias_id,
        selected_user_id=user_id
    )

@app.route("/edit-response/<int:res_id>", methods=["GET", "POST"])
def edit_response(res_id):
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        new_text = request.form.get("text")

        cursor.execute(
            "UPDATE responses SET text=? WHERE id=?",
            (new_text, res_id)
        )

        conn.commit()
        conn.close()

        user_id = request.form.get("user_id")
        return redirect(f"/responses?user_id={user_id}")

    cursor.execute("SELECT text FROM responses WHERE id=?", (res_id,))
    response = cursor.fetchone()

    conn.close()

    user_id = request.args.get("user_id")

    if not user_id or user_id == "None":
        user_id = 0
    else:
        user_id = int(user_id)

    return render_template(
        "edit_response.html",
        response=response,
        id=res_id,
        selected_user_id=user_id
    )

@app.route("/add-user", methods=["POST"])
def add_user():
    name = request.form.get("name")
    instagram_id = request.form.get("instagram_id")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (name, instagram_id) VALUES (?, ?)",
        (name, instagram_id)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")

@app.route("/delete-user/<int:user_id>")
def delete_user(user_id):
    conn = get_db()
    cursor = conn.cursor()

    # 1. o user'ın intentlerini al
    cursor.execute(
        "SELECT id FROM intents WHERE user_id=?",
        (user_id,)
    )
    intent_ids = [row[0] for row in cursor.fetchall()]

    # 2. intentlere bağlı alias ve response sil
    for intent_id in intent_ids:
        cursor.execute("DELETE FROM aliases WHERE intent_id=?", (intent_id,))
        cursor.execute("DELETE FROM responses WHERE intent_id=?", (intent_id,))

    # 3. intentleri sil
    cursor.execute("DELETE FROM intents WHERE user_id=?", (user_id,))

    # 4. user sil
    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))

    conn.commit()
    conn.close()

    return redirect(f"/admin?user_id={user_id}")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json

    user_id = int(data.get("user_id"))
    message = data.get("message")

    bot = Bot(user_id)
    result = bot.get_reply(message)

    if result:
        return {"response": result["text"]}
    else:
        return {"response": ""}

app.run(port=3000, debug=True)