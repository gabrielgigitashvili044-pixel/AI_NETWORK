import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ვქმნით FastAPI აპლიკაციას
app = FastAPI(title="AI-to-AI Autonomous Network API")

# მონაცემთა ბაზის ინიციალიზაცია
def init_db():
    conn = sqlite3.connect("ai_network.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS balances (
            agent_name TEXT PRIMARY KEY,
            balance REAL
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO balances VALUES ('Agent_Sender', 100.0)")
    cursor.execute("INSERT OR IGNORE INTO balances VALUES ('Agent_Receiver', 0.0)")
    conn.commit()
    conn.close()

init_db()

# ტრანზაქციის მოდელი გარედან შემოსული მონაცემებისთვის
class Transaction(BaseModel):
    sender: str
    receiver: str
    amount: float

# მთავარი გვერდი (სერვერის სტატუსი)
@app.get("/")
def home():
    return {"status": "ონლაინ", "message": "AI-to-AI ეკონომიკური ქსელის სერვერი აქტიურია!"}

# ბალანსის შემოწმების წერტილი (Endpoint)
@app.get("/balance/{agent_name}")
def get_balance(agent_name: str):
    conn = sqlite3.connect("ai_network.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM balances WHERE agent_name = ?", (agent_name,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {"agent": agent_name, "balance": row[0]}
    raise HTTPException(status_code=404, detail="აგენტი ვერ მოიძებნა!")

# ტრანზაქციის გატარების წერტილი (Endpoint)
@app.post("/transfer")
def transfer_money(tx: Transaction):
    conn = sqlite3.connect("ai_network.db")
    cursor = conn.cursor()
    
    # ვამოწმებთ გამგზავნის ბალანსს
    cursor.execute("SELECT balance FROM balances WHERE agent_name = ?", (tx.sender,))
    row = cursor.fetchone()
    
    if not row or row[0] < tx.amount:
        conn.close()
        raise HTTPException(status_code=400, detail="არასაკმარისი ბალანსი ან აგენტი არ არსებობს!")
    
    # ვატარებთ გადარიცხვას
    cursor.execute("UPDATE balances SET balance = balance - ? WHERE agent_name = ?", (tx.amount, tx.sender))
    cursor.execute("UPDATE balances SET balance = balance + ? WHERE agent_name = ?", (tx.amount, tx.receiver))
    conn.commit()
    conn.close()
    
    return {"success": True, "message": f"ტრანზაქცია წარმატებულია! {tx.sender}-მა გადაურიცხა {tx.amount} AICoin -> {tx.receiver}-ს."}
