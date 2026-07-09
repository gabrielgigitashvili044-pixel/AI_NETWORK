import sqlite3
import os
import hashlib
import json
from datetime import datetime
from cryptography.fernet import Fernet
import httpx
import base58
from dotenv import load_dotenv
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import transfer, TransferParams
from solders.transaction import Transaction
from solders.message import Message
from solders.hash import Hash

load_dotenv()

SOLANA_RPC = "https://api.devnet.solana.com"

class AINetworkSDK:
    def __init__(self, gateway_token: str, key_file_path: str = "secret.key", db_path: str = "ai_network.db"):
        self.gateway_token = gateway_token
        self.db_path = db_path
        self.rpc_url = SOLANA_RPC
        private_key = os.getenv("SOLANA_PRIVATE_KEY")
        if not private_key:
            raise ValueError("SOLANA_PRIVATE_KEY not found in .env")
        key_bytes = base58.b58decode(private_key)
        self.keypair = Keypair.from_bytes(key_bytes)
        if not os.path.exists(key_file_path):
            raise FileNotFoundError("secret.key not found.")
        self.cipher_suite = Fernet(open(key_file_path, "rb").read())

    def _encrypt(self, data_str: str) -> bytes:
        return self.cipher_suite.encrypt(data_str.encode('utf-8'))

    def _decrypt(self, data_bytes: bytes) -> str:
        return self.cipher_suite.decrypt(data_bytes).decode('utf-8')

    def _verify_gateway(self) -> bool:
        return self.gateway_token == "PROT_SECURE_KEY_2026"

    def _get_blockhash(self) -> str:
        response = httpx.post(self.rpc_url, json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getLatestBlockhash",
            "params": []
        })
        return response.json()["result"]["value"]["blockhash"]

    def check_node_balance(self, agent_name: str) -> float:
        if not self._verify_gateway():
            return 0.0
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM balances WHERE agent_name = ?", (agent_name,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return float(self._decrypt(row[0]))
        return 0.0

    def trigger_autonomous_transfer(self, sender: str, receiver: str, amount: float) -> bool:
        if not self._verify_gateway():
            return False
        try:
            receiver_pubkey = Pubkey.from_string(receiver)
            lamports = int(amount * 1_000_000_000)
            blockhash_str = self._get_blockhash()
            blockhash = Hash.from_string(blockhash_str)
            ix = transfer(TransferParams(
                from_pubkey=self.keypair.pubkey(),
                to_pubkey=receiver_pubkey,
                lamports=lamports
            ))
            msg = Message.new_with_blockhash([ix], self.keypair.pubkey(), blockhash)
            tx = Transaction([self.keypair], msg, blockhash)
            tx_bytes = bytes(tx)
            import base64
            tx_b64 = base64.b64encode(tx_bytes).decode()
            response = httpx.post(self.rpc_url, json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sendTransaction",
                "params": [tx_b64, {"encoding": "base64"}]
            })
            result = response.json()
            if "result" in result:
                sig = result["result"]
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_entry = f"[{timestamp}] SOLANA_TX: {sender} -> {receiver} | Amount: {amount} SOL | SIG: {sig}\n"
                with open("ledger.txt", "a", encoding="utf-8") as f:
                    f.write(log_entry)
                print(f"Solana Transfer Success: {sig}")
                return True
            else:
                print(f"Solana Error: {result}")
                return False
        except Exception as e:
            print(f"Solana Transfer Error: {e}")
            return False