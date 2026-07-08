import time
import random
import requests

# Unified cloud integration URL endpoint configuration
BASE_URL = "https://ai-network-api.onrender.com"

print("--- [System Status]: Smart Yield Trading Engine Engaged ---")
time.sleep(1)

test_agents = ["Agent_Beta", "Agent_Gamma", "Agent_Delta", "Agent_Epsilon", "Agent_Omega"]

print("\n[Smart Protocol]: Agents are scanning market rates for arbitrage opportunities...")

for i in range(5):
    sender_node = "Agent_Sender"
    receiver_node = random.choice(test_agents)
    
    market_rate = round(random.uniform(0.90, 0.95), 4)
    random_amount = round(random.uniform(10.0, 25.0), 2)
    
    print(f"\n[Cycle {i+1}/5]: Active Rate: {market_rate} | Target Volume: {random_amount} USD")
    
    if market_rate > 0.92:
        print(f"📈 [Decision]: Rate {market_rate} is profitable. Executing automated cloud transfer...")
        
        payload = {
            "sender": sender_node,
            "receiver": receiver_node,
            "amount": random_amount
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/v1/transfer", json=payload, timeout=10)
            if response.status_code == 200:
                print(f"✅ [Protocol Locked]: Asset successfully allocated to {receiver_node}.")
            else:
                print(f"❌ [Protocol Rejected]: Cloud rejected transaction. Code: {response.status_code}")
        except Exception as e:
            print(f"❌ [Network Wall]: Cannot bridge connection to Cloud. Detail: {str(e)}")
    else:
        print(f"📉 [Decision]: Rate {market_rate} is NOT profitable. Transaction aborted to save capital.")
        
    time.sleep(1)

print("\n--- [System Status]: Smart Trading Cycle Complete. Capital Saved. ---")
