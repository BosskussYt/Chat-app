from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, join_room, send
import sqlite3
import eventlet

eventlet.monkey_patch()

app = Flask(__name__)
app.secret_key = "secret-key"
socketio = SocketIO(app, cors_allowed_origins="*")

# ---------------- DATABASE ----------------
def db():
    conn = sqlite3.connect("data.db")
    return conn

def init_db():
    conn = db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room TEXT,
        user TEXT,
        msg TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- ROUTES ----------------
@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html", user=session["user"])

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["user"]

        conn = db()
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users VALUES (?)", (username,))
        conn.commit()
        conn.close()

        session["user"] = username
        return redirect("/")

    return """
    <form method="POST">
        <input name="user" placeholder="Username">
        <button>Join</button>
    </form>
    """

# ---------------- SOCKET ----------------
@socketio.on("join")
def on_join(data):
    join_room(data["room"])

@socketio.on("message")
def handle_message(data):
    conn = db()
    c = conn.cursor()

    c.execute("INSERT INTO messages (room,user,msg) VALUES (?,?,?)",
              (data["room"], data["user"], data["msg"]))
    conn.commit()
    conn.close()

    send(data, to=data["room"])

# ---------------- START ----------------
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)
