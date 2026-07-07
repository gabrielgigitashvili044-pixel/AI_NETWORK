import streamlit as st
import sqlite3
import pandas as pd
import os
import time

# Premium Institutional Branding Configuration
st.set_page_config(page_title="AI-Network Global Core", page_icon="💎", layout="wide")

if "refresh_counter" not in st.session_state:
    st.session_state.refresh_counter = 0

st.markdown("""
    <style>
    .stApp { background-color: #0A0D14; color: #F0F4F8; }
    </style>
""", unsafe_allow_html=True)

st.title("AI-to-AI Autonomous Capital Infrastructure")
st.write("Global Multi-Currency Liquidity & Decentralized Network Core. Operating on Synchronized Node Framework.")

ADMIN_PASSWORD = "SOVEREIGN_MASTER_2026"

from cryptography.fernet import Fernet
KEY_FILE = "secret.key"
if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)

cipher_suite = Fernet(open(KEY_FILE, "rb").read())

def encrypt_data(data_str):
    return cipher_suite.encrypt(data_str.encode('utf-8'))

def decrypt_data(data_bytes):
    return cipher_suite.decrypt(data_bytes).decode('utf-8')

def get_balances_df():
    conn = sqlite3.connect("ai_network.db")
    cursor = conn.cursor()
    cursor.execute("SELECT agent_name, currency, balance FROM balances")
    rows = cursor.fetchall()
    conn.close()
    
    decrypted_data = []
    for row in rows:
        try:
            agent_name = row[0]
            currency_type = row[1]
            decrypted_val = float(decrypt_data(row[2]))
            decrypted_data.append({"Node Name": agent_name, "Currency": currency_type, "Liquidity (Amount)": decrypted_val})
        except:
            decrypted_data.append({"Node Name": str(row[0]), "Currency": str(row[1]), "Liquidity (Amount)": 0.0})
    return pd.DataFrame(decrypted_data)

def mint_currency_capital(agent, currency, amount):
    conn = sqlite3.connect("ai_network.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM balances WHERE agent_name = ? AND currency = ?", (agent, currency))
    row = cursor.fetchone()
    if row:
        current_bal = float(decrypt_data(row[0]))
        new_bal = str(current_bal + amount)
        cursor.execute("UPDATE balances SET balance = ? WHERE agent_name = ? AND currency = ?", (encrypt_data(new_bal), agent, currency))
    else:
        cursor.execute("INSERT INTO balances VALUES (?, ?, ?)", (agent, currency, encrypt_data(str(amount))))
    conn.commit()
    conn.close()

def read_last_ledger_entries(limit=10):
    if not os.path.exists("ledger.txt"):
        return []
    with open("ledger.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
    return lines[-limit:]

def calculate_network_metrics():
    if not os.path.exists("ledger.txt"):
        return 0.0, 0.0, 0
    total_volume = 0.0
    total_revenue = 0.0
    success_count = 0
    with open("ledger.txt", "r", encoding="utf-8") as f:
        for line in f:
            if "Amount:" in line:
                try:
                    parts = line.split("Amount: ")
                    amt = float(parts[1].split(" ")[0])
                    total_volume += amt
                    success_count += 1
                    if "Fee:" in line:
                        fee_part = line.split("Fee: ")
                        fee = float(fee_part[1].split(" ")[0])
                        total_revenue += fee
                except:
                    continue
    return round(total_volume, 2), round(total_revenue, 4), success_count

df_balances = get_balances_df()
net_volume, net_revenue, tx_count = calculate_network_metrics()

st.subheader("Live Network Financial Metrics")
m_col1, m_col2, m_col3 = st.columns(3)
with m_col1:
    st.metric(label="Total Network Volume (USD/AICoin)", value=f"{net_volume} Tokens")
with m_col2:
    st.metric(label="Total Treasury Revenue (1% Fee)", value=f"{net_revenue} USD")
with m_col3:
    st.metric(label="Total Settled Protocols", value=f"{tx_count} TXs")

st.divider()

st.subheader("Global Capital Distribution Analytics")
# Upgraded layout width standard definition
st.bar_chart(data=df_balances, x='Node Name', y='Liquidity (Amount)', color='Currency', width='stretch')

st.divider()

st.subheader("Sovereign Owner Controls (Liquidity Injection)")
admin_key_input = st.text_input("Enter Master Owner Authentication Key:", type="password")

col_a, col_b, col_c = st.columns(3)
with col_a:
    target_node = st.selectbox("Select Target Node:", ["Agent_Sender", "Agent_Receiver", "Sovereign_Treasury"])
with col_b:
    selected_currency = st.selectbox("Select Currency Type:", ["AICoin", "USD", "EUR"])
with col_c:
    mint_amount = st.number_input("Injection Volume:", min_value=10.0, max_value=1000.0, value=100.0)

if st.button("Execute Capital Injection"):
    if admin_key_input == ADMIN_PASSWORD:
        mint_currency_capital(target_node, selected_currency, mint_amount)
        st.success(f"Sovereign Success: Injected {mint_amount} {selected_currency} into {target_node}.")
        time.sleep(1)
        st.rerun()
    else:
        st.error("Access Denied: Invalid Master Owner Authentication Key.")

st.divider()

st.subheader("Global REST API Communication Gateway (External Node Routing)")
st.info("API Status: Active | Listening Protocol: Localhost Unified Mapping")
st.code("""
[GET]  /api/v1/balances   -> Retrieve fully encrypted network distribution nodes.
[POST] /api/v1/transfer   -> Dispatch secure machine-to-machine cryptographic asset allocation.
""", language="text")

st.divider()

st.subheader("Active Network Node Registry")
st.dataframe(df_balances, width='stretch', hide_index=True)

st.divider()

st.subheader("Live Network Ledger Audit Trail (Executive View)")
ledger_entries = read_last_ledger_entries()
if ledger_entries:
    for entry in reversed(ledger_entries):
        st.text(entry.strip())
else:
    st.info("No transaction logs detected in the public ledger repository.")

st.divider()

time.sleep(3)
st.rerun()
