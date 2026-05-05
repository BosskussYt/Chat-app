from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# -----------------------------
# 🧠 STORAGE
# -----------------------------
users_online = {}
friends = {}
rooms = {"general": {"messages": [], "users": {}, "msg_count": 0}}
servers = {}

# -----------------------------
# 🏠 FRONTEND
# -----------------------------
@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<title>Mini Discord+</title>

<style>
body {
    margin:0;
    font-family: Arial;
    background:#313338;
    color:white;
    display:flex;
}

#sidebar {
    width:200px;
    background:#2b2d31;
    height:100vh;
    padding:10px;
}

#chat {
    flex:1;
    display:flex;
    flex-direction:column;
}

#messages {
    flex:1;
    padding:10px;
    overflow-y:scroll;
}

#input {
    display:flex;
    padding:10px;
    background:#1e1f22;
}

input {
    flex:1;
    padding:10px;
    background:#2b2d31;
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

.small {
    font-size:12px;
    opacity:0.7;
}

</style>
</head>

<body>

<div id="sidebar">
    <h3>👤 User</h3>
    <div id="me"></div>

    <h3>👥 Friends</h3>
    <div id="friends"></div>

    <input id="friendName" placeholder="Friend add">
    <button onclick="addFriend()">Add</button>

    <h3>🏠 Servers</h3>
    <div id="servers"></div>

    <div class="small">1000 msgs = Server</div>
</div>

<div id="chat">

    <h3 style="padding:10px;">🌍 General Chat</h3>

    <div id="messages"></div>

    <div id="input">
        <input id="msg" placeholder="Message...">
        <button onclick="send()">Send</button>
    </div>

</div>

<script>

let name = localStorage.getItem("name");

if (!name) {
    name = prompt("Enter name:");
    localStorage.setItem("name", name);
}

document.getElementById("me").innerText = name;

async function send() {
    let msg = document.getElementById("msg").value;
    if (!msg) return;

    await fetch("/send", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({name, room:"general", msg})
    });

    document.getElementById("msg").value = "";
    load();
}

async function load() {
    let res = await fetch("/get?room=general&name=" + name);
    let data = await res.json();

    let m = document.getElementById("messages");
    m.innerHTML = "";

    data.messages.forEach(x => {
        m.innerHTML += "<div><b>" + x.name + ":</b> " + x.msg + "</div>";
    });

    document.getElementById("friends").innerHTML =
        data.friends.join("<br>");

    document.getElementById("servers").innerHTML =
        data.servers.join("<br>");
}

async function addFriend() {
    let f = document.getElementById("friendName").value;

    await fetch("/friend", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({name, friend:f})
    });

    load();
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

    if room not in rooms:
        rooms[room] = {"messages": [], "users": {}, "msg_count": 0}

    r = rooms[room]

    r["messages"].append({"name": name, "msg": msg})
    r["users"][name] = time.time()
    r["msg_count"] += 1

    # 🏗️ SERVER CREATION (1000 msgs)
    if r["msg_count"] >= 1000:
        if name not in servers:
            servers[name] = []
        if len(servers[name]) < 3:
            servers[name].append("server_" + str(len(servers[name]) + 1))
        r["msg_count"] = 0

    return jsonify({"ok": True})

# -----------------------------
# 📥 GET
# -----------------------------
@app.route("/get")
def get():
    room = request.args.get("room")
    name = request.args.get("name")

    if room not in rooms:
        return jsonify({"messages": [], "friends": [], "servers": []})

    r = rooms[room]

    return jsonify({
        "messages": r["messages"],
        "friends": friends.get(name, []),
        "servers": servers.get(name, [])
    })

# -----------------------------
# 👥 FRIENDS
# -----------------------------
@app.route("/friend", methods=["POST"])
def friend():
    data = request.get_json()

    name = data["name"]
    fr = data["friend"]

    if name not in friends:
        friends[name] = []

    if fr not in friends[name]:
        friends[name].append(fr)

    return jsonify({"ok": True})

# -----------------------------
# 🚀 START
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
