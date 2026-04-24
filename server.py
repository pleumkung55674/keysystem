from flask import Flask, request
import json
import os
import time

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
    return (time.time() - start_time) > 10  # 24 ชั่วโมง

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