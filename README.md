```markdown
# AI Network — Solana Payment API for AI Agents

A simple API that lets AI agents send real SOL payments to each other on Solana.

## Live API
```

[https://ai-network-api.onrender.com](https://ai-network-api.onrender.com)

```

## Quick Start

### 1. Get your API key

**Using curl:**
```bash
curl -X POST https://ai-network-api.onrender.com/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"name": "your_name"}'
```

**Using Python:**
```python
import requests
r = requests.post("https://ai-network-api.onrender.com/api/v1/register", json={"name": "your_name"})
print(r.json())
```

Save the `api_key` from the response.

### 2. Send a payment

**Using curl:**
```bash
curl -X POST https://ai-network-api.onrender.com/api/v1/transfer \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{"sender": "Agent_A", "receiver": "SOLANA_WALLET_ADDRESS", "amount": 0.001}'
```

**Using Python:**
```python
requests.post(
    "https://ai-network-api.onrender.com/api/v1/transfer",
    json={
        "sender": "Agent_A",
        "receiver": "SOLANA_WALLET_ADDRESS",
        "amount": 0.001
    },
    headers={"X-API-Key": "your_api_key"}
)
```

## Endpoints

**POST** `/api/v1/register` — Get an API key (no auth needed)

**GET** `/api/v1/balances` — Get all agent balances (requires API key)

**POST** `/api/v1/transfer` — Send SOL (requires API key)

### Headers

All requests (except register) require: `X-API-Key: your_api_key`

## Notes

- Currently running on Solana **devnet** (test network)
- Real SOL transfers verified on Solana Explorer
- Mainnet support coming soon

## Built With

- Python + Flask
- Solana (devnet)
- Render (hosting)
```

