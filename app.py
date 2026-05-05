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

/* LEFT SIDEBAR (SERVERS) */
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

/* FRIENDS PANEL */
#friends {
    width:200px;
    background:#2b2d31;
    height:100vh;
    padding:10px;
}

/* CHAT AREA */
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

.small {
    font-size:12px;
    opacity:0.7;
}

</style>
</head>

<body>

<!-- SERVERS -->
<div id="servers">
    <div class="server">S</div>
    <div class="server">+</div>
</div>

<!-- FRIENDS -->
<div id="friends">
    <h3>👥 Friends</h3>
    <div class="small">online system coming</div>
</div>

<!-- CHAT -->
<div id="chatArea">

    <div id="chat"></div>

    <div id="inputBar">
        <input id="msg" placeholder="Nachricht...">
        <button onclick="sendMsg()">Send</button>
    </div>

</div>

<script>

let room = "main";
let name = localStorage.getItem("name") || prompt("Name eingeben:");
localStorage.setItem("name", name);

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
