from flask import Flask, request, jsonify

app = Flask(__name__)

messages = []

# 🏠 CHAT WEBSEITE
@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mini Chat</title>
        <style>
            body {
                font-family: Arial;
                background: #1e1e1e;
                color: white;
                text-align: center;
            }
            #chat {
                width: 400px;
                height: 300px;
                margin: auto;
                border: 1px solid gray;
                overflow-y: scroll;
                padding: 10px;
                background: #2b2b2b;
            }
            input {
                width: 300px;
                padding: 10px;
            }
            button {
                padding: 10px;
                cursor: pointer;
            }
        </style>
    </head>

    <body>
        <h1>💬 Mini Chat</h1>

        <div id="chat"></div>

        <br>

        <input id="msg" placeholder="Nachricht...">
        <button onclick="sendMsg()">Senden</button>

        <script>
            async function loadMessages() {
                let res = await fetch("/get");
                let data = await res.json();

                let chat = document.getElementById("chat");
                chat.innerHTML = "";

                data.forEach(m => {
                    chat.innerHTML += "<p>" + m + "</p>";
                });

                chat.scrollTop = chat.scrollHeight;
            }

            async function sendMsg() {
                let msg = document.getElementById("msg").value;

                await fetch("/send", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({msg: msg})
                });

                document.getElementById("msg").value = "";
                loadMessages();
            }

            setInterval(loadMessages, 1000);
        </script>

    </body>
    </html>
    """

# 📩 Nachricht senden
@app.route("/send", methods=["POST"])
def send():
    data = request.get_json()

    if data and "msg" in data:
        messages.append(data["msg"])
        return jsonify({"status": "ok"})

    return jsonify({"status": "error"}), 400

# 📥 Nachrichten holen
@app.route("/get", methods=["GET"])
def get():
    return jsonify(messages)

# 🌐 START
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)