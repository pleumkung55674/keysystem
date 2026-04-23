from flask import Flask, request
import json
import os

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

# ================= ROUTES =================
@app.route("/")
def home():
    return "Key Server Running"

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
        save_keys()
        return "binded"

    # ❌ ใช้คนละเครื่อง
    if data["hwid"] != hwid:
        return "hwid_error"

    return "ok"


# ================= START =================
load_keys()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
