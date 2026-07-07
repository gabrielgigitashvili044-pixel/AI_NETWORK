import requests
import time
import random

INTERNAL_GATEWAY_URL = "http://127.0.0.1:5000"
agents = ["Agent_Beta", "Agent_Delta", "Agent_Epsilon", "Agent_Gamma", "Agent_Omega"]

print("--- [Sovereign Autonomous Node]: Permanent Internal Streaming Engaged ---")

while True:
    try:
        sender_node = "Agent_Sender"
        receiver_node = random.choice(agents)
        # Dynamic float volume configuration
        random_amount = round(random.uniform(10.0, 30.0), 2)
        
        payload = {
            "sender": sender_node,
            "receiver": receiver_node,
            "amount": random_amount
        }
        
        response = requests.post(f"{INTERNAL_GATEWAY_URL}/api/v1/transfer", json=payload, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ [Stream Success]: Network Routed {random_amount} USD to {receiver_node}")
        else:
            print(f"❌ [Core Rejected]: Infrastructure declined transaction. Code: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ [Network Core Exception]: Synchronized link failure. Error: {str(e)}")
        
    time.sleep(4)
