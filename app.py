from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# 🧠 Speicher (RAM)
rooms = {}

# -----------------------------
# 🏠 FRONTEND
# -----------------------------
@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<title>Mini Discord</title>

<style>
body {
    margin:0;
    font-family: Arial;
    background:#313338;
    color:white;
    display:flex;
}

#servers {
    width:70px;
    background:#1e1f22;
    height:100vh;
    display:flex;
    flex-direction:column;
    align-items:center;
    padding-top:10px;
}

.server {
    width:45px;
    height:45px;
    background:#5865F2;
    border-radius:50%;
    margin:10px;
    display:flex;
    align-items:center;
    justify-content:center;
    cursor:pointer;
}

#friends {
    width:200px;
    background:#2b2d31;
    height:100vh;
    padding:10px;
}

#chatArea {
    flex:1;
    display:flex;
    flex-direction:column;
    height:100vh;
}

#chat {
    flex:1;
    padding:10px;
    overflow-y:scroll;
}

#inputBar {
    display:flex;
    padding:10px;
    background:#2b2d31;
}

input {
    flex:1;
    padding:10px;
    background:#1e1f22;
    border:none;
    color:white;
}

button {
    padding:10px;
    margin-left:5px;
    background:#5865F2;
    border:none;
    color:white;
    cursor:pointer;
}

.msg {
    margin:5px 0;
}

</style>
</head>

<body>

<div id="servers">
    <div class="server">S</div>
    <div class="server">+</div>
</div>

<div id="friends">
    <h3>👥 Friends</h3>
    <div style="font-size:12px; opacity:0.6;">soon</div>
</div>

<div id="chatArea">

    <div id="chat"></div>

    <div id="inputBar">
        <input id="msg" placeholder="Nachricht...">
        <button onclick="sendMsg()">Send</button>
    </div>

</div>

<script>

let room = "main";
let name = localStorage.getItem("name");

if (!name) {
    name = prompt("Name eingeben:");
    localStorage.setItem("name", name);
}

async function sendMsg() {
    let msg = document.getElementById("msg").value;
    if (!msg) return;

    await fetch("/send", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({name, room, msg})
    });

    document.getElementById("msg").value = "";
    load();
}

async function load() {
    let res = await fetch("/get?room=" + room + "&name=" + name);
    let data = await res.json();

    let chat = document.getElementById("chat");
    chat.innerHTML = "";

    data.messages.forEach(m => {
        chat.innerHTML += "<div class='msg'><b>" + m.name + ":</b> " + m.msg + "</div>";
    });
}

setInterval(load, 1000);
load();

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
            "is_community": False,
            "msg_count": 0,
            "expires": 0
        }

    r = rooms[room]

    # 👤 online user
    r["users"][name] = now

    # 💬 message
    r["messages"].append({"name": name, "msg": msg})

    # 🧹 limit 100 messages
    if len(r["messages"]) > 100:
        r["messages"].pop(0)

    # 📊 counter
    r["msg_count"] += 1

    # 🏆 community (100 messages)
    if not r["is_community"] and r["msg_count"] >= 100:
        r["is_community"] = True
        r["expires"] = now + 172800  # 2 Tage

    # 🔥 extend (200 messages)
    if r["is_community"] and r["msg_count"] >= 200:
        r["expires"] += 172800
        r["msg_count"] = 0

    return jsonify({"status": "ok"})

# -----------------------------
# 📥 GET
# -----------------------------
@app.route("/get")
def get():
    room = request.args.get("room")

    cleanup()

    if room not in rooms:
        return jsonify({"messages": []})

    return jsonify({
        "messages": rooms[room]["messages"]
    })

# -----------------------------
# 🧹 CLEANUP
# -----------------------------
def cleanup():
    now = time.time()
    to_delete = []

    for room, r in rooms.items():

        # ❌ remove inactive users
        r["users"] = {
            u: t for u, t in r["users"].items()
            if now - t < 15
        }

        # 🧹 delete empty rooms
        if len(r["users"]) == 0:
            to_delete.append(room)

        # 🏆 community expiry
        if r["is_community"]:
            if now > r["expires"]:
                to_delete.append(room)

    for r in to_delete:
        del rooms[r]

# -----------------------------
# 🚀 START
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
