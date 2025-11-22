🧊 ColdVault — Arduino-Based Ethereum Cold Wallet

A lightweight, secure, hardware-assisted cold wallet using Arduino + Python + FastAPI + React (Vite).

ColdVault is a secure, hardware-integrated cold wallet system that stores private keys inside an Arduino, while exposing wallet actions through a modern web interface.
All wallet operations — Create Key, Get Wallet, Sign Hash, Broadcast Transaction — are executed through Python scripts, triggered from the UI and streamed live via WebSocket.

This project is designed for education, experimentation, and air-gapped crypto key handling.

⚙️ Features

🔐 Hardware-level key security

Keys are generated and stored on the Arduino.

Private keys never leave the device.

💻 Live Terminal Output

Python scripts run from the website and stream output in real-time via WebSocket.

⚡ FastAPI Backend

Handles script execution + WebSocket communication.

🌐 React (Vite) Frontend

Clean custom UI (pure CSS — no Tailwind).

Terminal emulator built using xterm.js.

🪄 One-Click Crypto Actions

Create Key

Get Wallet

Sign Hash

Broadcast Transaction

🔌 Simple & Modular Code Structure

Easy to expand into multi-chain wallet in the future.

📁 Project Structure
coldvault-web/
│
├── backend/
│   ├── app.py                 # FastAPI backend (WebSocket + script runner)
│   ├── 1create_key.py         # Generates Ethereum private key + public address
│   ├── 2get_wallet.py         # Shows wallet info + balance
│   ├── 3test_sign_hash.py     # Signs hashes using Arduino-stored key
│   ├── 4broadcast_tx.py       # Broadcasts signed transactions to network
│   ├── wallet_info.json       # Stores generated wallet details
│   └── .venv/                 # Python virtual environment
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # UI + 4 crypto control buttons
│   │   ├── Terminal.jsx       # Live terminal component (WebSocket)
│   │   └── main.jsx
│   ├── index.html
│   └── styles.css
│
└── README.md

🧠 How the System Works
🔌 Execution Flow

When you click any of the 4 buttons:

Frontend sends command → FastAPI WebSocket

FastAPI runs Python script → using a subprocess

Python communicates with Arduino → over serial USB

Arduino performs crypto operations → keygen / sign

Backend streams output → line-by-line to browser

Terminal on website displays it live

Actions Mapped to Scripts
Action	Script
🟢 Create Key	1create_key.py
🔵 Get Wallet	2get_wallet.py
🟣 Sign Hash	3test_sign_hash.py
🟠 Broadcast Tx	4broadcast_tx.py

This structure keeps the system clean and fully modular.

🧰 Installation & Setup (Local)
1️⃣ Backend Setup
cd backend
python -m venv .venv


Activate environment:

Windows

.\.venv\Scripts\activate


Install dependencies:

pip install fastapi uvicorn pyserial web3 eth-account python-dotenv


Run the backend:

uvicorn app:app --host 127.0.0.1 --port 8000


Backend WebSocket URL:

ws://127.0.0.1:8000/ws/run

2️⃣ Frontend Setup
cd frontend
npm install
npm run dev


Open browser:

http://localhost:5173

3️⃣ Usage Flow

Connect Arduino through USB

Start backend (FastAPI)

Start frontend (Vite)

Click any button:

Create Key

Get Wallet

Sign Hash

Broadcast Tx

Watch real-time terminal output on the web UI

🔒 Security Notes

Private keys never leave Arduino unless you explicitly print them

Avoid running unstable serial monitors while using backend

Always test on testnets first

Use air-gapped PC for maximum security if using with real funds

Do not commit your .env or private data to GitHub

🤝 Credits

If you use or modify this project, please credit the team:

@teamcoldvault

Created by: Heykaranraj