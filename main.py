from flask import Flask, request, jsonify, send_file, render_template, redirect
import requests
from db import Session, ChatHistory

app = Flask(__name__)

@app.route("/")
def home():
    return send_file("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

    if not user_message:
        return jsonify({"error": "Pesan kosong. Kirim 'message' di JSON body."}), 400

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": user_message,
                "stream": False
            },
            timeout=60
        )

        data = response.json()
        bot_reply = data.get("response", "Tidak ada balasan dari model.")

        # Simpan ke file
        with open("chat_history.txt", "a") as f:
            f.write(f"User: {user_message}\nBot: {bot_reply}\n\n")

        # Simpan ke database
        session = Session()
        history = ChatHistory(user_message=user_message, bot_reply=bot_reply)
        session.add(history)
        session.commit()
        session.close()

        return jsonify({"reply": bot_reply})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Gagal konek ke Ollama: {str(e)}"}), 500

@app.route("/history")
def show_history():
    session = Session()
    all_history = session.query(ChatHistory).all()
    session.close()
    return render_template("history.html", history=all_history)

@app.route("/export")
def export_chat():
    session = Session()
    chats = session.query(ChatHistory).all()
    session.close()

    with open("exported_chat.txt", "w") as f:
        for chat in chats:
            f.write(f"User: {chat.user_message}\nBot: {chat.bot_reply}\n\n")

    return "✅ Chat berhasil diexport ke 'exported_chat.txt'"

@app.route("/delete/<int:chat_id>")
def delete_history(chat_id):
    session = Session()
    history = session.query(ChatHistory).get(chat_id)
    if history:
        session.delete(history)
        session.commit()
    session.close()
    return redirect("/history")
@app.route("/edit/<int:chat_id>", methods=["GET", "POST"])
def edit_history(chat_id):
    session = Session()
    chat = session.query(ChatHistory).get(chat_id)

    if request.method == "POST":
        new_user_message = request.form.get("user_message")
        new_bot_reply = request.form.get("bot_reply")

        if chat:
            chat.user_message = new_user_message
            chat.bot_reply = new_bot_reply
            session.commit()

        session.close()
        return redirect(f"/edit/{chat_id}?updated=1")  # 🔥 Tambahkan ?updated=1

    session.close()
    return render_template("edit.html", chat=chat)


if __name__ == "__main__":
    app.run(debug=True)
