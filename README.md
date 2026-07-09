```markdown
# AI Network — Solana Payment API for AI Agents

A simple API that lets AI agents send real SOL payments to each other on Solana.

## Live API
```

[https://ai-network-api.onrender.com](https://ai-network-api.onrender.com)

```

## Quick Start

Send a payment between two AI agents:

```python
import requests

response = requests.post(
    "https://ai-network-api.onrender.com/api/v1/transfer",
    json={
        "sender": "Agent_A",
        "receiver": "YOUR_SOLANA_WALLET_ADDRESS",
        "amount": 0.001
    }
)
print(response.json())
```

## Endpoints

**GET** `/api/v1/balances` — Get all agent balances

**POST** `/api/v1/transfer` — Send SOL from one agent to another

### Transfer Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| sender | string | Yes | Sender agent name |
| receiver | string | Yes | Receiver Solana wallet address |
| amount | float | Yes | Amount in SOL |

## Built With

- Python + Flask
- Solana (devnet)
- Render (hosting)
```

