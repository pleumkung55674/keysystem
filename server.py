from flask import Flask, request
import json
import os
import random
import string

app = Flask(__name__)

# ================= CONFIG =================
ADMIN_PASSWORD = "SLASH_ADMIN"  # 🔐 เปลี่ยนอันนี้

# ================= LOAD KEYS =================
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

load_keys()

# ================= HOME =================
@app.route("/")
def home():
    return "Key Server Running"

# ================= CHECK KEY =================
@app.route("/check")
def check():
    key = request.args.get("key")
    hwid = request.args.get("hwid")

    if not key or not hwid:
        return "invalid"

    if key not in KEYS:
        return "invalid"

    data = KEYS[key]

    if data.get("hwid") is None:
        data["hwid"] = hwid
        save_keys()
        return "binded"

    if data["hwid"] != hwid:
        return "hwid_error"

    return "ok"

# ================= ADD KEY =================
@app.route("/add")
def add_key():
    password = request.args.get("password")
    key = request.args.get("key")

    if password != ADMIN_PASSWORD:
        return "unauthorized"

    if key in KEYS:
        return "exists"

    KEYS[key] = {"hwid": None}
    save_keys()
    return "added"

# ================= DELETE KEY =================
@app.route("/delete")
def delete_key():
    password = request.args.get("password")
    key = request.args.get("key")

    if password != ADMIN_PASSWORD:
        return "unauthorized"

    if key in KEYS:
        del KEYS[key]
        save_keys()
        return "deleted"

    return "notfound"

# ================= GENERATE KEY =================
@app.route("/generate")
def generate_key():
    password = request.args.get("password")

    if password != ADMIN_PASSWORD:
        return "unauthorized"

    key = "SLASH-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

    KEYS[key] = {"hwid": None}
    save_keys()

    return key

# ================= VIEW ALL KEYS =================
@app.route("/admin")
def admin():
    password = request.args.get("password")

    if password != ADMIN_PASSWORD:
        return "unauthorized"

    return KEYS


# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
