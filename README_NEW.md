ColdVault — Arduino-Based Cold Wallet

ColdVault is a secure, hardware-integrated cold wallet that pairs an Arduino device with a modern web interface (FastAPI backend + React/Vite frontend). It provides air-gapped key management and signing for Ethereum (EVM) and Bitcoin (testnet) workflows, with a polished web UI and real-time feedback via WebSockets.

Warning: ColdVault is experimental. Never use real/production funds unless you fully understand the risks. Always test on testnets first.

Table of contents

Key features

Project structure

Quick start

Prerequisites

Backend setup

Frontend setup

Arduino setup

How it works

Usage guide

Security & best practices

Troubleshooting

Contributing

License & credits

Key features

🔐 Air-gapped key management — Private keys are generated and kept on the Arduino device.

⚡ Real-time terminal — WebSocket streaming of script logs and live feedback.

🌐 EVM + Bitcoin support — Separate scripts and flows for Ethereum and Bitcoin testnets.

🎛️ Four core operations — Create Key, Get Wallet, Sign Hash, Broadcast Tx.

🧭 Modern UI — Clean landing page, interactive terminal, and quick external links (GitHub / Sandbox).

🧪 Testnet-first — Designed for testing on Sepolia (Ethereum) and Bitcoin testnet.

Project structure
backend/
  ├─ app.py                    # FastAPI app, WebSocket runner
  ├─ 1create_key.py
  ├─ 2get_wallet.py
  ├─ 3test_sign_hash.py
  ├─ 4broadcast_tx.py
  ├─ requirements.txt
  └─ .env                      # (local only — never commit secrets)
frontend/
  ├─ index.html
  ├─ package.json
  ├─ vite.config.js
  └─ src/
      ├─ App.jsx
      ├─ Terminal.jsx
      ├─ styles.css
      └─ components/...
README.md
LICENSE

Quick start
Prerequisites

Python 3.11+ (recommended)

Node.js 18+ and npm or yarn

Arduino Uno/Mega and USB cable

Git (optional — for cloning)

Backend setup

Open a terminal and go to the backend/ folder:

cd backend


Create and activate a virtual environment:

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate


Install dependencies:

pip install -r requirements.txt
# or (if you don't have requirements.txt)
pip install fastapi uvicorn pyserial eth-account eth-utils web3 python-dotenv bit


Create .env (do not commit it) and add keys:

ETH_RPC_URL=https://mainnet.infura.io/v3/YOUR_INFURA_KEY
ARDUINO_PORT=COM3
ARDUINO_BAUD_RATE=9600
BTC_NETWORK=testnet


Run the backend:

uvicorn app:app --host 0.0.0.0 --port 8000 --reload


The WebSocket endpoint for terminal commands is: ws://localhost:8000/ws/run.

Frontend setup

From the project root:

cd frontend
npm install
npm run dev


Open the app in your browser at http://localhost:5173 (Vite default).

Arduino setup

Connect the Arduino via USB.

Confirm the serial port (Device Manager on Windows or ls /dev/tty* on macOS/Linux).

Update .env with ARDUINO_PORT (e.g., COM3 or /dev/ttyUSB0).

Make sure the Arduino firmware implements the line-based serial protocol expected by the Python scripts (generate keys, sign, return signatures, etc.).

How it works (overview)

User clicks a control button in the web UI (e.g., Create Key).

Frontend sends a JSON WebSocket message: {"cmd":"create_key"} to ws://localhost:8000/ws/run.

Backend (app.py) maps create_key to 1create_key.py, spawns it (using the running Python venv), and streams stdout/stderr over the same WebSocket.

The Arduino performs cryptographic operations on the device and returns minimal outputs (private key never leaves the Arduino unless you explicitly print it).

The frontend terminal displays live output. After signing, transaction data is saved to pending_transaction.json and can be broadcasted by the broadcast_tx flow.

Usage guide
Ethereum flow (recommended: Sepolia testnet)

Create Key — Generates a new key on Arduino and stores it in device memory.

Get Wallet — Reads address (and optionally balance) and shows QR code.

Sign Hash — Sends transaction hash to the Arduino for user-confirmed signing. Arduino will prompt for CONFIRM/CANCEL.

Broadcast Tx — If the signed transaction is available, broadcast to configured RPC provider (ENV ETH_RPC_URL).

Bitcoin flow (testnet)

Analogous commands exist for Bitcoin scripts (1create_keybtc.py, etc.) and operate on testnet by default.

Security & best practices

Air-Gapped — Use a dedicated, offline machine for key generation and signing if you require higher security.

Do not expose private keys — The backend masks private-key-like strings in logs by default; avoid printing raw private keys.

Testnets first — Always validate flows using Sepolia (Ethereum) and Bitcoin testnet before any mainnet usage.

Use environment variables — Never hardcode API keys or private keys in the source tree.

Firmware verification — Verify Arduino firmware authenticity before using for signing.

Troubleshooting

WebSocket connection fails

Ensure backend is running on 0.0.0.0:8000.

Verify firewall rules and CORS configuration if connecting remotely.

I/O errors with Arduino

Confirm correct serial port and baud rate in .env.

Make sure no other program (e.g., Arduino IDE serial monitor) is using the port.

Insufficient funds error when broadcasting

This indicates a test wallet has 0 balance. Use free Sepolia faucets (Alchemy / QuickNode / Chainstack) to add test ETH to your wallet address.

Contributing

Contributions welcome — please:

Fork the repository

Create a feature branch: git checkout -b feat/your-feature

Commit changes: git commit -m "feat: add ..."

Push and open a pull request

Add issues for bugs or feature requests and tag them appropriately.

License & credits

License: MIT — see LICENSE file.

Commands to Run - cd c:\Users\krkar\Downloads\Cold_Vault\ColdVault-Open-Source-Wallet\backend; pip install -r requirements.txt; npm install; cd ..\frontend; npm install; Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd c:\Users\krkar\Downloads\Cold_Vault\ColdVault-Open-Source-Wallet\backend; python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000"; npm run dev

Author: Heykaranraj — many thanks to contributors and community testers.