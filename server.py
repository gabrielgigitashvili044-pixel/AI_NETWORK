from flask import Flask, jsonify, request
from flask_cors import CORS
from ainetwork_sdk import AINetworkSDK
import sqlite3
import secrets
import json
import os

app = Flask(__name__)
CORS(app)
sdk = AINetworkSDK(gateway_token="PROT_SECURE_KEY_2026")

KEYS_FILE = "api_keys.json"

def load_keys():
    if os.path.exists(KEYS_FILE):
        return json.load(open(KEYS_FILE))
    return {}

def save_keys(keys):
    json.dump(keys, open(KEYS_FILE, "w"))

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
        success = sdk.trigger_autonomous_transfer(sender=str(sender), receiver=str(receiver), amount=float(amount))
        if success:
            return jsonify({"status": "success", "message": "Transfer complete"}), 200
        return jsonify({"status": "error", "message": "Transfer failed"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("API Server running on port 5000")
    app.run(host='0.0.0.0', port=5000, threaded=True)