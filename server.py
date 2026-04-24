from flask import Flask, request, render_template_string, redirect, session
import sqlite3
import os
import time
import random
import string

app = Flask(__name__)
app.secret_key = "SLASH_SECRET_123"

# ================= DATABASE =================
def db():
    return sqlite3.connect("keys.db")

def init_db():
    conn = db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS keys (
        key TEXT PRIMARY KEY,
        hwid TEXT,
        start_time REAL,
        status TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY,
        password TEXT
    )
    """)

    c.execute("INSERT OR IGNORE INTO admin VALUES (1,'SLASH_ADMIN')")

    conn.commit()
    conn.close()

def get_keys():
    conn = db()
    c = conn.cursor()
    c.execute("SELECT * FROM keys")
    rows = c.fetchall()
    conn.close()

    return {
        r[0]: {
            "hwid": r[1],
            "start_time": r[2],
            "status": r[3]
        } for r in rows
    }

def add_key(key):
    conn = db()
    c = conn.cursor()
    c.execute("INSERT INTO keys VALUES (?,?,?,?)",
              (key, None, None, "active"))
    conn.commit()
    conn.close()

def delete_key_db(key):
    conn = db()
    c = conn.cursor()
    c.execute("DELETE FROM keys WHERE key=?", (key,))
    conn.commit()
    conn.close()

# ================= EXPIRY (NOT TOUCH LOGIC) =================
def is_expired(start_time):
    if start_time is None:
        return False
    return (time.time() - start_time) > 86400

# ================= ADMIN =================
def login_required():
    return session.get("admin") == True

# ================= KEY GEN =================
def gen_key():
    return "SLASH-" + "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

# ================= UI =================
DASH = """
<!DOCTYPE html>
<html>
<head>
<title>CYBER PANEL</title>
<meta http-equiv="refresh" content="3">
<style>
body { background:#0d0d0d; color:#00ffcc; font-family:monospace; }
table { width:100%; border-collapse:collapse; }
th,td { border:1px solid #00ffcc33; padding:8px; }
th { background:#111; }
button { background:#00ffcc; border:none; padding:5px; cursor:pointer; }
.del { background:red; color:white; }
.glow { text-shadow:0 0 10px #00ffcc; }
</style>
</head>
<body>

<h2 class="glow">⚡ CYBER KEY PANEL</h2>

<a href="/logout">LOGOUT</a>

<form action="/generate">
<input name="amount" value="1">
<button>GEN</button>
</form>

<table>
<tr>
<th>KEY</th>
<th>HWID</th>
<th>START</th>
<th>ACTION</th>
</tr>

{% for k,v in KEYS.items() %}
<tr>
<td>{{k}}</td>
<td>{{v["hwid"]}}</td>
<td>{{v["start_time"]}}</td>
<td>
<button onclick="navigator.clipboard.writeText('{{k}}')">COPY</button>
<a href="/delete?key={{k}}"><button class="del">DEL</button></a>
</td>
</tr>
{% endfor %}

</table>

</body>
</html>
"""

LOGIN = """
<form method="post">
<input name="password" placeholder="admin">
<button>LOGIN</button>
</form>
"""

# ================= ROUTES =================
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        pw = request.form["password"]

        conn = db()
        c = conn.cursor()
        c.execute("SELECT password FROM admin WHERE id=1")
        real = c.fetchone()[0]
        conn.close()

        if pw == real:
            session["admin"] = True
            return redirect("/dashboard")

        return "wrong"

    return LOGIN

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/")
def home():
    return "Key Server Running"

@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect("/login")

    return render_template_string(DASH, KEYS=get_keys())

@app.route("/generate")
def generate():
    if not login_required():
        return "no access"

    amount = int(request.args.get("amount",1))

    keys = []
    for _ in range(amount):
        k = gen_key()
        add_key(k)
        keys.append(k)

    return "<br>".join(keys)

@app.route("/delete")
def delete():
    if not login_required():
        return "no access"

    key = request.args.get("key")
    delete_key_db(key)
    return redirect("/dashboard")

# ================= ORIGINAL LOGIC (UNCHANGED) =================
@app.route("/check")
def check():
    key = request.args.get("key")
    hwid = request.args.get("hwid")

    if not key or not hwid:
        return "invalid"

    conn = db()
    c = conn.cursor()
    c.execute("SELECT * FROM keys WHERE key=?", (key,))
    row = c.fetchone()
    conn.close()

    if not row:
        return "invalid"

    data = {
        "hwid": row[1],
        "start_time": row[2],
        "status": row[3]
    }

    if data["hwid"] is None:
        conn = db()
        c = conn.cursor()
        c.execute("UPDATE keys SET hwid=?, start_time=? WHERE key=?",
                  (hwid, time.time(), key))
        conn.commit()
        conn.close()
        return "binded"

    if data["hwid"] != hwid:
        return "hwid_error"

    if is_expired(data["start_time"]):
        return "expired"

    return "ok"

# ================= START =================
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
