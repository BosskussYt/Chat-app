from flask import Flask, request, jsonify

app = Flask(__name__)

messages = []

# 🏠 Chat Seite
@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chat</title>
        <style>
            body { font-family: Arial; text-align:center; background:#1e1e1e; color:white; }
            #chat { width:400px; height:300px; margin:auto; overflow-y:scroll; background:#2b2b2b; padding:10px; }
            input { width:300px; padding:10px; }
            button { padding:10px; }
        </style>
    </head>
    <body>

        <h1>💬 Chat</h1>

        <div id="chat"></div><br>

        <input id="msg" placeholder="Nachricht...">
        <button onclick="sendMsg()">Senden</button>

        <script>
            async function load() {
                let res = await fetch("/get");
                let data = await res.json();

                let chat = document.getElementById("chat");
                chat.innerHTML = "";

                data.forEach(m => {
                    chat.innerHTML += "<p>" + m + "</p>";
                });
            }

            async function sendMsg() {
                let msg = document.getElementById("msg").value;

                if (!msg) return;

                await fetch("/send", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ msg: msg })
                });

                document.getElementById("msg").value = "";
                load();
            }

            setInterval(load, 1000);
            load();
        </script>

    </body>
    </html>
    """

# 📩 Nachricht senden (FIXED)
@app.route("/send", methods=["POST"])
def send():
    data = request.get_json(force=True)

    msg = data.get("msg")

    if msg:
        messages.append(msg)
        return jsonify({"status": "ok"})

    return jsonify({"status": "error"}), 400

# 📥 Nachrichten holen
@app.route("/get", methods=["GET"])
def get():
    return jsonify(messages)

# 🌐 Start
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
