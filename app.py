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
            button { padding:10px; cursor:pointer; }
        </style>
    </head>

    <body>
        <h1>💬 Chat</h1>

        <div id="chat"></div><br>

        <input id="msg" placeholder="Nachricht...">
        <button id="sendBtn">Senden</button>

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

            async function sendMessage() {
                let msgInput = document.getElementById("msg");
                let msg = msgInput.value;

                if (!msg) return;

                await fetch("/send", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ msg: msg })
                });

                msgInput.value = "";
                loadMessages();
            }

            document.getElementById("sendBtn").addEventListener("click", sendMessage);

            loadMessages();
            setInterval(loadMessages, 1000);
        </script>

    </body>
    </html>
    """
    app.run(host="0.0.0.0", port=10000)
