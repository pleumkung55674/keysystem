from flask import Flask, request

app = Flask(__name__)

KEYS = {
    "SLASH123": {"hwid": None}
}

@app.route("/")
def home():
    return "Key Server Running"

@app.route("/check")
def check():
    key = request.args.get("key")
    hwid = request.args.get("hwid")

    if key not in KEYS:
        return "invalid"

    if KEYS[key]["hwid"] is None:
        KEYS[key]["hwid"] = hwid
        return "binded"

    if KEYS[key]["hwid"] != hwid:
        return "hwid_error"

    return "ok"


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)