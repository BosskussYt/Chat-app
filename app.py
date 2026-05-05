from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# -------------------------
# 🧠 STORAGE
# -------------------------
rooms = {
    "general": {
        "messages": [],
        "msg_count": {}
    }
}

friends = {}
servers = {}

# -------------------------
# 🏠 FRONTEND (DISCORD STYLE)
# -------------------------
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

#sidebar {
    width:250px;
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

.server {
    padding:5px;
    margin:5px 0;
    background:#404249;
    cursor:pointer;
}
</style>
</head>

<body>

<div id="sidebar">
    <h3>👤 User</h3>
    <div id="me"></div>

    <h3>👥 Friends</h3>
    <div id="friends"></div>

    <input id="friendInput" placeholder="Add friend">
    <button onclick="addFriend()">Add</button>

    <h3>🏠 Servers</h3>
    <div id="servers"></div>

    <div style="font-size:12px;opacity:0.6;margin-top:10px;">
        1000 Messages = Server Unlock
    </div>
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
    name = prompt("Name eingeben:");
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
    let res = await fetch("/get?name=" + name);
    let data = await res.json();

    let m = document.getElementById("messages");
    m.innerHTML = "";

    data.messages.forEach(x => {
        m.innerHTML += "<div><b>" + x.name + ":</b> " + x.msg + "</div>";
    });

    document.getElementById("friends").innerHTML =
        data.friends.join("<br>");

    document.getElementById("servers").innerHTML =
        data.servers.map(s => "<div class='server'>" + s + "</div>").join("");
}

async function addFriend() {
    let f = document.getElementById("friendInput").value;

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

# -------------------------
# 💬 SEND MESSAGE
# -------------------------
@app.route("/send", methods=["POST"])
def send():
    data = request.get_json()

    name = data["name"]
    room = data["room"]
    msg = data["msg"]

    if room not in rooms:
        rooms[room] = {"messages": [], "msg_count": {}}

    r = rooms[room]

    r["messages"].append({"name": name, "msg": msg})

    if name not in r["msg_count"]:
        r["msg_count"][name] = 0

    r["msg_count"][name] += 1

    # 🏗️ SERVER FREISCHALTUNG
    if r["msg_count"][name] >= 1000:
        if name not in servers:
            servers[name] = []

        if len(servers[name]) < 3:
            servers[name].append("Server_" + str(len(servers[name]) + 1))

        r["msg_count"][name] = 0

    return jsonify({"ok": True})

# -------------------------
# 📥 GET
# -------------------------
@app.route("/get")
def get():
    name = request.args.get("name")

    return jsonify({
        "messages": rooms["general"]["messages"],
        "friends": friends.get(name, []),
        "servers": servers.get(name, [])
    })

# -------------------------
# 👥 FRIENDS
# -------------------------
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

# -------------------------
# 🚀 START
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
