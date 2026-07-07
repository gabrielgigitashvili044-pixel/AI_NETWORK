import time
from ainetwork_sdk import AINetworkSDK

# Initializing the high-precision multi-currency SDK
sdk = AINetworkSDK(gateway_token="PROT_SECURE_KEY_2026")

print("--- External Developer Environment Initialized ---")
time.sleep(1)

# Dynamic test: Executing an autonomous institutional transaction in USD
print("\n[SDK Request]: Dispatching autonomous USD multi-agent asset allocation...")
success = sdk.trigger_autonomous_transfer(
    sender="Agent_Sender", 
    receiver="Agent_Receiver", 
    amount=50.0  # Sending 50.0 USD
)

if success:
    print("✅ [SDK Status]: USD Asset allocation successfully committed to the database ledger.")
else:
    print("❌ [SDK Status]: Transaction rejected by Core Network.")
