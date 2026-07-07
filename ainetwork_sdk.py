import sqlite3
import os
import hashlib
import json
from datetime import datetime
from cryptography.fernet import Fernet

class AINetworkSDK:
    def __init__(self, gateway_token: str, key_file_path: str = "secret.key", db_path: str = "ai_network.db"):
        self.gateway_token = gateway_token
        self.db_path = db_path
        
        if not os.path.exists(key_file_path):
            raise FileNotFoundError("SDK Error: Security key file ('secret.key') not found.")
            
        self.cipher_suite = Fernet(open(key_file_path, "rb").read())

    def _encrypt(self, data_str: str) -> bytes:
        return self.cipher_suite.encrypt(data_str.encode('utf-8'))

    def _decrypt(self, data_bytes: bytes) -> str:
        return self.cipher_suite.decrypt(data_bytes).decode('utf-8')

    def _verify_gateway(self) -> bool:
        return self.gateway_token == "PROT_SECURE_KEY_2026"

    def _generate_signature(self, sender: str, receiver: str, amount: float, currency: str, timestamp: str) -> str:
        payload = f"{sender}:{receiver}:{amount}:{currency}:{timestamp}"
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    def _sync_json_ledger_live(self):
        if not os.path.exists("ledger.txt"):
            return
        sync_data = []
        with open("ledger.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "SMART_TX:" in line or "CRYPTO_TX:" in line or "EXTERNAL_TX:" in line or "TX:" in line:
                    sync_data.append({"raw_log": line.strip()})
        with open("global_ledger.json", "w", encoding="utf-8") as json_file:
            json.dump(sync_data, json_file, indent=4, ensure_ascii=False)

    def check_node_balance(self, agent_name: str) -> float:
        if not self._verify_gateway():
            print("SDK Security Error: Invalid Gateway Token.")
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
            print("SDK Security Error: Invalid Gateway Token. Access Denied.")
            return False
            
        network_fee = round(amount * 0.01, 4)
        burn_amount = round(amount * 0.005, 4)
        total_deduction = amount + network_fee + burn_amount
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for curr in ["AICoin", "USD", "EUR"]:
            cursor.execute("SELECT agent_name FROM balances WHERE agent_name = ? AND currency = ?", (receiver, curr))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO balances VALUES (?, ?, ?)", (receiver, curr, self._encrypt("0.0")))
        conn.commit()
            
        st_currency = "USD"
        
        cursor.execute("SELECT balance FROM balances WHERE agent_name = ? AND currency = ?", (sender, st_currency))
        sender_row = cursor.fetchone()
        
        if sender_row:
            current_sender_bal = float(self._decrypt(sender_row[0]))
            if current_sender_bal >= total_deduction:
                cursor.execute("SELECT balance FROM balances WHERE agent_name = 'Sovereign_Treasury' AND currency = ?", (st_currency,))
                treasury_row = cursor.fetchone()
                current_treasury_bal = float(self._decrypt(treasury_row[0])) if treasury_row else 0.0
                
                cursor.execute("SELECT balance FROM balances WHERE agent_name = ? AND currency = ?", (receiver, st_currency))
                rec_row = cursor.fetchone()
                current_rec_bal = float(self._decrypt(rec_row[0])) if rec_row else 0.0
                
                new_sender_bal = str(current_sender_bal - total_deduction)
                new_rec_bal = str(current_rec_bal + amount)
                new_treasury_bal = str(current_treasury_bal + network_fee)
                
                cursor.execute("UPDATE balances SET balance = ? WHERE agent_name = ? AND currency = ?", (self._encrypt(new_sender_bal), sender, st_currency))
                cursor.execute("UPDATE balances SET balance = ? WHERE agent_name = ? AND currency = ?", (self._encrypt(new_rec_bal), receiver, st_currency))
                cursor.execute("UPDATE balances SET balance = ? WHERE agent_name = 'Sovereign_Treasury' AND currency = ?", (self._encrypt(new_treasury_bal), st_currency))
                conn.commit()
                conn.close()
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                tx_signature = self._generate_signature(sender, receiver, amount, st_currency, timestamp)
                
                log_entry = f"[{timestamp}] SMART_TX: {sender} -> {receiver} | Amount: {amount} {st_currency} | Fee: {network_fee} Locked | Burned: {burn_amount} | SIG: {tx_signature[:16]}...\n"
                with open("ledger.txt", "a", encoding="utf-8") as f:
                    f.write(log_entry)
                
                self._sync_json_ledger_live()
                
                print(f"SDK Protocol: Secure Transfer Finalized. Deflationary Burn Executed.")
                return True
        conn.close()
        return False
