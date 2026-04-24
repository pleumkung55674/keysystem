from flask import Flask, request, render_template_string
import json
import os
import time
import random
import string

app = Flask(__name__)

# ================= LOAD / SAVE KEYS =================
def load_keys():
    global KEYS
    try:
        with open("keys.json", "r") as f:
            KEYS = json.load(f)
    except:
        KEYS = {}

def save_keys():
    with open("keys.json", "w") as f:
        json.dump(KEYS, f, indent=4)

# ================= EXPIRE CHECK (24h) =================
def is_expired(start_time):
    if start_time is None:
        return False
    return (time.time() - start_time) > 86400

# ================= ADMIN =================
ADMIN_PASS = "SLASH_ADMIN"

def gen_key():
    return "SLASH-" + "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

# ================= DASHBOARD UI =================
DASH = """
<!DOCTYPE html>
<html>
<head>
<title>Key Dashboard</title>
<meta http-equiv="refresh" content="3">
<style>
body { background:#111; color:white; font-family:Arial; }
table { width:100%; border-collapse:collapse; }
th,td { border:1px solid #333; padding:8px; text-align:center; }
th { background:#6c5ce7; }
button { padding:5px; cursor:pointer; }
.copy { background:green; color:white; border:none; }
.del { background:red; color:white; border:none; }
</style>
</head>
<body>

<h2>🔑 KEY DASHBOARD</h2>

<form action="/generate" method="get">
<input type="password" name="pass" placeholder="admin pass">
<button>GENERATE KEY</button>
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
<td>{{v.get("hwid")}}</td>
<td>{{v.get("start_time")}}</td>
<td>
<button class="copy" onclick="copyKey('{{k}}')">COPY</button>
<a href="/delete?key={{k}}"><button class="del">DEL</button></a>
</td>
</tr>
{% endfor %}

</table>

<script>
function copyKey(k){
    navigator.clipboard.writeText(k);
    alert("Copied: " + k);
}
</script>

</body>
</html>
"""

# ================= ROUTES =================
@app.route("/")
def home():
    return "Key Server Running"

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    return render_template_string(DASH, KEYS=KEYS)

# ---------------- GENERATE KEY ----------------
@app.route("/generate")
def generate():
    if request.args.get("pass") != ADMIN_PASS:
        return "unauthorized"

    key = gen_key()

    KEYS[key] = {
        "hwid": None,
        "start_time": None,
        "status": "active"
    }

    save_keys()
    return f"generated: {key}"

# ---------------- DELETE KEY ----------------
@app.route("/delete")
def delete():
    key = request.args.get("key")

    if key in KEYS:
        del KEYS[key]
        save_keys()

    return "deleted"

# ================= YOUR ORIGINAL LOGIC (UNCHANGED) =================
@app.route("/check")
def check():
    key = request.args.get("key")
    hwid = request.args.get("hwid")

    if not key or not hwid:
        return "invalid"

    if key not in KEYS:
        return "invalid"

    data = KEYS[key]

    # 🔥 bind ครั้งแรก
    if data.get("hwid") is None:
        data["hwid"] = hwid
        data["start_time"] = time.time()
        save_keys()
        return "binded"

    # ❌ คนละเครื่อง
    if data["hwid"] != hwid:
        return "hwid_error"

    # 🔥 หมดอายุ 1 วัน
    if is_expired(data["start_time"]):
        return "expired"

    return "ok"

# ================= START =================
load_keys()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
