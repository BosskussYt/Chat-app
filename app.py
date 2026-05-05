from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, join_room, send
import sqlite3
import time

app = Flask(__name__)
app.secret_key = "secret"
socketio = SocketIO(app)

# ---------------- DB ----------------
def db():
    conn = sqlite3.connect("db.db")
    return conn

def init():
    conn = db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        online INTEGER DEFAULT 0
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room TEXT,
        user TEXT,
        msg TEXT,
        time REAL
    )
    """)

    conn.commit()
    conn.close()

init()

# ---------------- PAGES ----------------
@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html", user=session["user"])

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["user"]
        p = request.form["pass"]

        conn = db()
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p))
        user = c.fetchone()

        if not user:
            c.execute("INSERT INTO users VALUES (?, ?, 1)", (u,p))
        else:
            c.execute("UPDATE users SET online=1 WHERE username=?", (u,))

        conn.commit()
        conn.close()

        session["user"] = u
        return redirect("/")

    return """
    <form method="POST">
    <input name="user" placeholder="User"><br>
    <input name="pass" type="password" placeholder="Pass"><br>
    <button>Login</button>
    </form>
    """

# ---------------- SOCKET ----------------
@socketio.on("join")
def join(data):
    join_room(data["room"])

@socketio.on("message")
def msg(data):
    conn = db()
    c = conn.cursor()

    c.execute("INSERT INTO messages (room,user,msg,time) VALUES (?,?,?,?)",
              (data["room"], data["user"], data["msg"], time.time()))

    conn.commit()
    conn.close()

    send(data, to=data["room"])

# ---------------- RUN ----------------
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)
