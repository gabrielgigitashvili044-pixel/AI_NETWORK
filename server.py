from flask import Flask, jsonify, request
from flask_cors import CORS
from ainetwork_sdk import AINetworkSDK
import sqlite3
import secrets
import json
import os
import time

app = Flask(__name__)
CORS(app)
sdk = AINetworkSDK(gateway_token="PROT_SECURE_KEY_2026")

KEYS_FILE = "api_keys.json"
SPEND_FILE = "spend_history.json"

# Default limits per API key
DEFAULT_DAILY_CAP = 1.0  # 1 SOL per day
DEFAULT_PER_TX_CAP = 0.1  # 0.1 SOL per transaction
VELOCITY_WINDOW = 60  # seconds
VELOCITY_MAX_TX = 5  # max 5 transactions per 60 seconds

def load_keys():
    if os.path.exists(KEYS_FILE):
        return json.load(open(KEYS_FILE))
    return {}

def save_keys(keys):
    json.dump(keys, open(KEYS_FILE, "w"))

def load_spend():
    if os.path.exists(SPEND_FILE):
        return json.load(open(SPEND_FILE))
    return {}

def save_spend(spend):
    json.dump(spend, open(SPEND_FILE, "w"))

def check_limits(api_key, amount):
    """Check per-tx cap, daily cap, and velocity."""
    if amount > DEFAULT_PER_TX_CAP:
        return False, f"Amount exceeds per-transaction cap ({DEFAULT_PER_TX_CAP} SOL)"

    spend = load_spend()
    now = time.time()
    day_ago = now - 86400
    window_ago = now - VELOCITY_WINDOW

    history = spend.get(api_key, [])
    # Clean old entries (older than 24h)
    history = [tx for tx in history if tx["timestamp"] > day_ago]

    # Daily cap check
    daily_total = sum(tx["amount"] for tx in history)
    if daily_total + amount > DEFAULT_DAILY_CAP:
        return False, f"Daily cap exceeded ({DEFAULT_DAILY_CAP} SOL/day)"

    # Velocity check
    recent_tx = [tx for tx in history if tx["timestamp"] > window_ago]
    if len(recent_tx) >= VELOCITY_MAX_TX:
        return False, f"Velocity limit: max {VELOCITY_MAX_TX} tx per {VELOCITY_WINDOW}s"

    return True, None

def record_spend(api_key, amount):
    spend = load_spend()
    if api_key not in spend:
        spend[api_key] = []
    spend[api_key].append({"timestamp": time.time(), "amount": amount})
    save_spend(spend)

def require_api_key(f):
    def wrapper(*args, **kwargs):
        key = request.headers.get("X-API-Key")
        if not key:
            return jsonify({"status": "error", "message": "Missing API key. Get one at /api/v1/register"}), 401
        keys = load_keys()
        if key not in keys:
            return jsonify({"status": "error", "message": "Invalid API key"}), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/api/v1/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"status": "error", "message": "Send JSON with your name: {\"name\": \"your_name\"}"}), 400
    name = data["name"]
    key = "ainet_" + secrets.token_hex(16)
    keys = load_keys()
    keys[key] = name
    save_keys(keys)
    return jsonify({"status": "success", "api_key": key, "message": "Save this key. Include it as X-API-Key header in all requests."}), 200

@app.route('/api/v1/limits', methods=['GET'])
@require_api_key
def get_limits():
    key = request.headers.get("X-API-Key")
    spend = load_spend()
    now = time.time()
    day_ago = now - 86400
    history = [tx for tx in spend.get(key, []) if tx["timestamp"] > day_ago]
    daily_spent = sum(tx["amount"] for tx in history)
    return jsonify({
        "status": "success",
        "per_transaction_cap": DEFAULT_PER_TX_CAP,
        "daily_cap": DEFAULT_DAILY_CAP,
        "daily_spent": round(daily_spent, 6),
        "daily_remaining": round(DEFAULT_DAILY_CAP - daily_spent, 6),
        "velocity_limit": f"{VELOCITY_MAX_TX} tx per {VELOCITY_WINDOW}s",
        "tx_count_24h": len(history)
    }), 200

@app.route('/api/v1/balances', methods=['GET'])
@require_api_key
def get_global_balances():
    try:
        conn = sqlite3.connect("ai_network.db")
        cursor = conn.cursor()
        cursor.execute("SELECT agent_name, currency FROM balances")
        rows = cursor.fetchall()
        conn.close()
        nodes = []
        for row in rows:
            agent = row[0]
            curr = row[1]
            bal = sdk.check_node_balance(agent)
            nodes.append({"agent_name": agent, "currency": curr, "liquidity": bal})
        return jsonify({"status": "success", "network_nodes": nodes}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/v1/transfer', methods=['POST'])
@require_api_key
def execute_global_transfer():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Missing payload"}), 400
        sender = data.get("sender")
        receiver = data.get("receiver")
        amount = data.get("amount")
        if not sender or not receiver or amount is None:
            return jsonify({"status": "error", "message": "Missing required parameters"}), 400

        api_key = request.headers.get("X-API-Key")
        ok, err = check_limits(api_key, float(amount))
        if not ok:
            return jsonify({"status": "error", "message": err, "code": "LIMIT_EXCEEDED"}), 429

        success = sdk.trigger_autonomous_transfer(sender=str(sender), receiver=str(receiver), amount=float(amount))
        if success:
            record_spend(api_key, float(amount))
            return jsonify({"status": "success", "message": "Transfer complete"}), 200
        return jsonify({"status": "error", "message": "Transfer failed"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("API Server running on port 5000")
    app.run(host='0.0.0.0', port=5000, threaded=True)