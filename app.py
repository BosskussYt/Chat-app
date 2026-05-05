from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# 🧠 RAM STORAGE
rooms = {}

# -----------------------------
# 🏠 HOME (Frontend)
# -----------------------------
@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mini Discord</title>
        <style>
            body { font-family: Arial; background:#1e1e1e; color:white; text-align:center; }
            input, button { padding:10px; margin:5px; }
            #chat { width:400px; height:250px; margin:auto; overflow-y:scroll; background:#2b2b2b; padding:10px; }
            #users { margin-top:10px; }
            #community { position:fixed; bottom:10px; right:10px; background:#444; padding:10px; cursor:pointer; }
        </style>
    </head>
    <body>

        <h1>💬 Mini Discord</h1>

        <div id="login">
            <input id="name" placeholder="Name">
            <input id="room" placeholder="Raum">
            <button onclick="join()">Join</button>
        </div>

        <div id="chatBox" style="display:none;">
            <h3 id="info"></h3>

            <div id="chat"></div>

            <input id="msg" placeholder="Nachricht">
            <button onclick="sendMsg()">Senden</button>

            <div id="users"></div>
        </div>

        <div id="community">🏆 Community</div>

        <script>
            let name = "";
            let room = "";

            function join() {
                name = document.getElementById("name").value;
                room = document.getElementById("room").value;

                if (!name || !room) return;

                document.getElementById("login").style.display = "none";
                document.getElementById("chatBox").style.display = "block";

                document.getElementById("info").innerText = "Raum: " + room;

                setInterval(load, 1000);
                load();
            }

            async function sendMsg() {
                let msg = document.getElementById("msg").value;
                if (!msg) return;

                await fetch("/send", {
                    method: "POST",
                    headers: {"Content-Type":"application/json"},
                    body: JSON.stringify({name, room, msg})
                });

                document.getElementById("msg").value = "";
                load();
            }

            async function load() {
                let res = await fetch("/get?room=" + room);
                let data = await res.json();

                let chat = document.getElementById("chat");
                chat.innerHTML = "";

                data.messages.forEach(m => {
                    chat.innerHTML += "<p><b>" + m.name + ":</b> " + m.msg + "</p>";
                });

                document.getElementById("users").innerHTML =
                    "👥 Online: " + data.users.join(", ");

                if (data.community) {
                    document.getElementById("community").innerText = "🏆 COMMUNITY ACTIVE";
                }
            }
        </script>

    </body>
    </html>
    """

# -----------------------------
# 💬 SEND MESSAGE
# -----------------------------
@app.route("/send", methods=["POST"])
def send():
    data = request.get_json()

    name = data["name"]
    room = data["room"]
    msg = data["msg"]

    now = time.time()

    if room not in rooms:
        rooms[room] = {
            "messages": [],
            "users": {},
            "msg_count": 0,
            "is_community": False,
            "expires": 0
        }

    r = rooms[room]

    # 👤 User online
    r["users"][name] = now

    # 💬 Message speichern
    r["messages"].append({"name": name, "msg": msg})

    # 🧹 Limit 100 messages
    if len(r["messages"]) > 100:
        r["messages"].pop(0)

    # 📊 Counter
    r["msg_count"] += 1

    # 🏆 Community erstellen
    if not r["is_community"] and r["msg_count"] >= 1000:
        r["is_community"] = True
        r["expires"] = now + 172800  # 2 Tage

    # ⏳ Community verlängern
    if r["is_community"] and r["msg_count"] >= 2000:
        r["expires"] += 172800
        r["msg_count"] = 0

    return jsonify({"status": "ok"})

# -----------------------------
# 📥 GET DATA
# -----------------------------
@app.route("/get")
def get():
    room = request.args.get("room")

    cleanup()

    if room not in rooms:
        return jsonify({"messages": [], "users": [], "community": False})

    r = rooms[room]

    return jsonify({
        "messages": r["messages"],
        "users": list(r["users"].keys()),
        "community": r["is_community"]
    })

# -----------------------------
# 🧹 CLEANUP SYSTEM
# -----------------------------
def cleanup():
    now = time.time()
    to_delete = []

    for room, r in rooms.items():

        # 👥 nur aktive user (15 sec)
        r["users"] = {
            u: t for u, t in r["users"].items()
            if now - t < 15
        }

        if r["is_community"]:
            # ⏳ Community Ablauf
            if now > r["expires"]:
                to_delete.append(room)
        else:
            # ❌ normale Räume löschen wenn leer
            if len(r["users"]) == 0:
                to_delete.append(room)

    for r in to_delete:
        del rooms[r]

# -----------------------------
# 🚀 START
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
