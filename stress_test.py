import time
import random
from ainetwork_sdk import AINetworkSDK

sdk = AINetworkSDK(gateway_token="PROT_SECURE_KEY_2026")

print("--- [System Status]: Smart Yield Trading Engine Engaged ---")
time.sleep(1)

test_agents = ["Agent_Beta", "Agent_Gamma", "Agent_Delta", "Agent_Epsilon", "Agent_Omega"]

print("\n[Smart Protocol]: Agents are scanning market rates for arbitrage opportunities...")

for i in range(5):
    sender_node = "Agent_Sender"
    receiver_node = random.choice(test_agents)
    
    # Simulating a live market currency rate (USD/EUR exchange proxy)
    market_rate = round(random.uniform(0.90, 0.95), 4)
    random_amount = round(random.uniform(10.0, 25.0), 2)
    
    print(f"\n[Cycle {i+1}/5]: Active Rate: {market_rate} | Target Volume: {random_amount} USD")
    
    # Smart Autonomous Decision: Only trade if market rate is above threshold (0.92)
    if market_rate > 0.92:
        print(f"📈 [Decision]: Rate {market_rate} is profitable. Executing automated transfer...")
        success = sdk.trigger_autonomous_transfer(
            sender=sender_node,
            receiver=receiver_node,
            amount=random_amount
        )
        if success:
            print(f"✅ [Protocol Locked]: Asset successfully allocated to {receiver_node}.")
        else:
            print("❌ [Protocol Rejected]: Internal execution error or liquidity wall.")
    else:
        print(f"📉 [Decision]: Rate {market_rate} is NOT profitable. Transaction aborted to save capital.")
        
    time.sleep(1)

print("\n--- [System Status]: Smart Trading Cycle Complete. Capital Saved. ---")
