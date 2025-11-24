ColdVault is a secure, hardware-integrated cold wallet. It provides air-gapped key management and transaction signing for Ethereum (EVM) and Bitcoin (testnet) workflows. The system includes a backend powered by Python scripts and FastAPI, with a modern frontend using Vite and React.

**Warning:** ColdVault is experimental. Never use real funds unless you fully understand the risks. Always test on Sepolia (Ethereum) and Bitcoin testnets first.

---

## Table of Contents

1. Key Features  
2. Project Structure  
3. Prerequisites  
4. Backend Setup  
5. Frontend Setup  
6. Arduino Setup  
7. How It Works  
8. Usage Guide  
9. Security and Best Practices  
10. Troubleshooting  
11. Contributing  
12. License and Credits  

---

## Key Features

- Air-gapped key management: Private keys are generated and stored on the Arduino device.
- Real-time terminal output: Logs and script output streamed via WebSocket.
- Supports Ethereum (Sepolia) and Bitcoin testnet.
- Four main operations: Create Key, Get Wallet, Sign Hash, Broadcast Transaction.
- Clean and responsive web UI for monitoring and controlling scripts.
- Testnet-first design to prevent accidental use of mainnet funds.

---

## Project Structure

```

coldvault-web/
├── backend/
│   ├── app.py                # FastAPI backend and WebSocket runner
│   ├── 1create_key.py        # Create new Ethereum wallet
│   ├── 2get_wallet.py        # Retrieve wallet information
│   ├── 3test_sign_hash.py    # Sign Ethereum transaction hashes
│   ├── 4broadcast_tx.py      # Broadcast signed transactions
│   ├── requirements.txt
│   └── .env                  # Local environment variables (do not commit)
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx
│       ├── Terminal.jsx
│       ├── main.jsx
│       └── styles.css
│
└── README.md

```

---

## Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher with npm or yarn
- Arduino Uno or Mega with USB cable
- Git (optional, for cloning the repository)
- Raspberrypi with latest os updates

---

## Backend Setup

1. Navigate to the backend folder:

```

cd backend

```

2. Create and activate a Python virtual environment:

```

python -m venv .venv

# Windows

.venv\Scripts\activate

# macOS/Linux

source .venv/bin/activate

```

3. Install dependencies:

```

pip install -r requirements.txt

# or, if missing requirements.txt

pip install fastapi uvicorn pyserial eth-account eth-utils web3 python-dotenv bit

```

4. Create a `.env` file with the following configuration:

```

ARDUINO_PORT=<your_arduino_port>
ARDUINO_BAUD_RATE=9600
BTC_NETWORK=testnet

```

5. Start the backend server:

```

uvicorn app:app --host 0.0.0.0 --port 8000 --reload

```

The WebSocket endpoint for terminal commands is:

```

ws://localhost:8000/ws/run

```

---

## Frontend Setup

1. Navigate to the frontend folder:

```

cd frontend

```

2. Install dependencies and start the frontend:

```

npm install
npm run dev

```

3. Open the local development server in a browser (default URL: localhost:5173).

---

## Arduino Setup

1. Connect the Arduino via USB.
2. Identify the correct serial port (Device Manager on Windows or `ls /dev/tty*` on macOS/Linux).
3. Update `.env` with the ARDUINO_PORT.
4. Ensure Arduino firmware implements the line-based serial protocol expected by the Python scripts.

---

## How It Works

1. A user clicks a control button in the web UI (Create Key, Get Wallet, Sign Hash, Broadcast Tx).
2. The frontend sends a JSON command over WebSocket.
3. The backend executes the corresponding Python script as a subprocess.
4. The Arduino performs cryptographic operations and returns minimal outputs. Private keys never leave the device unless explicitly printed.
5. Output is streamed live to the web UI terminal.
6. Signed transactions are stored in `pending_transaction.json` and can be broadcast using the Broadcast Tx operation.

**UI Button → Script → Function Table**

| Button        | Script               | Function                                      |
|---------------|--------------------|----------------------------------------------|
| Create Key    | 1create_key.py      | Generates a new keypair on Arduino           |
| Get Wallet    | 2get_wallet.py      | Retrieves wallet address and balance         |
| Sign Hash     | 3test_sign_hash.py  | Signs a transaction hash via Arduino         |
| Broadcast Tx  | 4broadcast_tx.py    | Broadcasts a signed transaction to network  |

---

## Usage Guide

**Ethereum Flow (Sepolia Testnet)**

1. Create Key — Generates a new key on Arduino.
2. Get Wallet — Reads wallet address and optionally balance; displays QR code.
3. Sign Hash — Sends transaction hash to Arduino for confirmation.
4. Broadcast Tx — Sends signed transaction to the configured RPC provider.

**Bitcoin Flow (Testnet)**

1. Equivalent scripts exist for Bitcoin (`1create_keybtc.py`, etc.) and operate on the testnet by default.

---

## Security and Best Practices

- Use an air-gapped machine for key generation and signing if possible.
- Avoid printing or exposing private keys.
- Always test on Sepolia and Bitcoin testnet before any mainnet usage.
- Store sensitive information in environment variables; never hardcode secrets.
- Verify Arduino firmware authenticity before signing transactions.

---

## Troubleshooting

**WebSocket Connection Issues**

- Ensure the backend is running.
- Check firewall settings and network configuration.

**Arduino I/O Errors**

- Verify the correct serial port and baud rate.
- Ensure no other program is using the port.

**Insufficient Funds Error**

- Indicates wallet balance is zero. Use a testnet faucet to fund the wallet.

---

## Contributing

1. Fork the repository.
2. Create a feature branch:

```

git checkout -b feat/your-feature

```

3. Commit changes:

```

git commit -m "feat: description"

```

4. Push the branch and open a pull request.

---

## License and Credits

- License: GNU General Public License (GPL) 
- Author: vedants22beec-collab

- Contributors: Community developers and testers

Please credit the creators if you use or modify this project.



