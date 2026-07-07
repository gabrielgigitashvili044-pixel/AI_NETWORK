from flask import Flask, jsonify, request
from ainetwork_sdk import AINetworkSDK
import sqlite3

app = Flask(__name__)
sdk = AINetworkSDK(gateway_token="PROT_SECURE_KEY_2026")

@app.route('/api/v1/balances', methods=['GET'])
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
            
        # Hardcoded precision mapping to secure type matching
        success = sdk.trigger_autonomous_transfer(sender=str(sender), receiver=str(receiver), amount=float(amount))
        
        if success:
            return jsonify({"status": "success", "message": "Cryptographic transfer finalized"}), 200
        return jsonify({"status": "error", "message": "Transfer rejected by Core Core"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("--- [System Status]: Global REST API Server Active on Port 5000 ---")
    app.run(host='0.0.0.0', port=5000, threaded=True)
