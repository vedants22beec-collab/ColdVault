import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import "./ReadmeChatbot.css";

// README content embedded for the chatbot
const README_CONTENT = `
# 🧊 ColdVault — Arduino-Based Cold Wallet

ColdVault is a secure, hardware-integrated Ethereum cold wallet that connects an Arduino to a web interface built with Python scripts + some frontend(used vite) + FastAPI.  
Each function (Create Key, Get Wallet, Sign Hash, Broadcast Tx) runs through Python scripts connected to your Arduino.

---
⚙️ Features

- 🔐 Generate and store private keys securely on Arduino  
- 💻 Run Python scripts directly from the website with live terminal output  
- ⚡ Real-time script execution via WebSocket  
- 🧩 FastAPI backend and React (Vite) frontend  
- 🎨 Beautiful custom UI (no Tailwind, pure CSS)  
- 🪄 One-click actions — 4 buttons trigger each backend Python script  

---
📁 Project Structure

coldvault-web/
├── backend/
│ ├── app.py #FastAPI backend (handles WebSocket + script execution)
│ ├── 1create_key.py # Creates new Ethereum wallet
│ ├── 2get_wallet.py # Fetches wallet info
│ ├── 3test_sign_hash.py # Signs Ethereum hashes
│ ├── 4broadcast_tx.py # Broadcasts signed transactions
│ └── .venv/ # Python virtual environment
│
├── frontend/
│ ├── src/
│ │ ├── App.jsx # UI with four buttons and live terminal
│ │ ├── Terminal.jsx # Terminal that shows live output
│ │ └── main.jsx
│ └── index.html
│
└── README.md

---

🧠 How It Works

Each button on the website runs a different Python script inside the backend via WebSocket:
- 🟢 Create Key → Runs 1create_key.py
- 🔵 Get Wallet → Runs 2get_wallet.py
- 🟣 Sign Hash → Runs 3test_sign_hash.py
- 🟠 Broadcast Tx → Runs 4broadcast_tx.py

The backend starts a subprocess for each script and streams the live terminal output line by line to the web UI.

---

🧰 Setup (Local)

1️⃣ Backend

cd backend
python -m venv .venv
.venv\\Scripts\\activate     # (on Windows)
pip install fastapi uvicorn pyserial
uvicorn app:app --host 127.0.0.1 --port 8000

2️⃣ Frontend
cd frontend
npm install
npm run dev

Then open the given local URL (usually http://localhost:5173).

💡 Usage

Connect your Arduino via USB.
Start the backend (FastAPI).
Start the frontend (Vite).
Click any of the four buttons to execute its script.
Watch live terminal output appear on the website.

Credits: @teamcoldvault
`;

export default function ReadmeChatbot() {
  const [messages, setMessages] = useState([
    {
      type: "bot",
      text: "👋 Hi! I'm your ColdVault README assistant. Ask me anything about the project setup, features, or how it works!",
    },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const getResponse = (question) => {
    const lowerQuestion = question.toLowerCase();
    
    // Try to find relevant content from README
    const findInReadme = (keywords) => {
      const lines = README_CONTENT.split('\n');
      const relevantLines = [];
      
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i].toLowerCase();
        if (keywords.some(keyword => line.includes(keyword))) {
          // Include context: previous line, current line, and next few lines
          if (i > 0) relevantLines.push(lines[i - 1]);
          relevantLines.push(lines[i]);
          for (let j = 1; j <= 5 && i + j < lines.length; j++) {
            relevantLines.push(lines[i + j]);
          }
          break;
        }
      }
      return relevantLines.join('\n').trim();
    };

    // Features
    if (
      lowerQuestion.includes("feature") ||
      lowerQuestion.includes("what can") ||
      lowerQuestion.includes("capabilities") ||
      lowerQuestion.includes("what does")
    ) {
      const content = findInReadme(["features", "⚙️"]);
      return content || "ColdVault offers secure key generation, real-time script execution, WebSocket communication, and a beautiful React/FastAPI interface!";
    }

    // Setup/Installation
    if (
      lowerQuestion.includes("setup") ||
      lowerQuestion.includes("install") ||
      lowerQuestion.includes("start") ||
      lowerQuestion.includes("run") ||
      lowerQuestion.includes("deploy")
    ) {
      const content = findInReadme(["setup", "backend", "frontend", "🧰"]);
      return content || "Check the Setup section in the README for detailed backend and frontend installation steps!";
    }

    // How it works
    if (
      lowerQuestion.includes("how") ||
      lowerQuestion.includes("work") ||
      lowerQuestion.includes("architecture") ||
      lowerQuestion.includes("explain")
    ) {
      const content = findInReadme(["how it works", "🧠", "button"]);
      return content || "Each button triggers a Python script via WebSocket. The backend runs the script and streams output to the UI in real-time!";
    }

    // Scripts/Python files
    if (
      lowerQuestion.includes("script") ||
      lowerQuestion.includes("python") ||
      lowerQuestion.includes("1create") ||
      lowerQuestion.includes("2get") ||
      lowerQuestion.includes("3test") ||
      lowerQuestion.includes("4broadcast") ||
      lowerQuestion.includes(".py")
    ) {
      const content = findInReadme(["create_key", "get_wallet", "sign_hash", "broadcast"]);
      return content || "📝 Four Python scripts handle operations:\n1create_key.py - Generate keys\n2get_wallet.py - Get wallet info\n3test_sign_hash.py - Sign hashes\n4broadcast_tx.py - Broadcast transactions";
    }

    // Arduino/Hardware
    if (
      lowerQuestion.includes("arduino") ||
      lowerQuestion.includes("hardware") ||
      lowerQuestion.includes("connection") ||
      lowerQuestion.includes("usb")
    ) {
      return "🔌 Arduino Connection:\n\n• Connect Arduino Uno/Mega via USB\n• Install proper serial drivers\n• Arduino stores private keys securely\n• Communicates via serial port (9600 baud)\n• Performs cryptographic operations offline";
    }

    // Security
    if (
      lowerQuestion.includes("secure") ||
      lowerQuestion.includes("safe") ||
      lowerQuestion.includes("security") ||
      lowerQuestion.includes("private key")
    ) {
      return "🔒 Security Features:\n\n• Private keys stored on Arduino hardware\n• Never exposed to computer/network\n• Hardware-based key generation\n• Air-gapped operation possible\n• Open-source for transparency\n• Local-only communication";
    }

    // Technology/Stack
    if (
      lowerQuestion.includes("tech") ||
      lowerQuestion.includes("stack") ||
      lowerQuestion.includes("built") ||
      lowerQuestion.includes("framework") ||
      lowerQuestion.includes("language")
    ) {
      const content = findInReadme(["fastapi", "react", "vite", "websocket"]);
      return content || "⚙️ Tech Stack:\n\nBackend: Python + FastAPI + PySerial\nFrontend: React + Vite + WebSocket\nHardware: Arduino Uno/Mega\nCommunication: WebSocket + USB Serial";
    }

    // Project structure
    if (
      lowerQuestion.includes("structure") ||
      lowerQuestion.includes("folder") ||
      lowerQuestion.includes("file") ||
      lowerQuestion.includes("organization")
    ) {
      const content = findInReadme(["project structure", "📁", "backend/", "frontend/"]);
      return content || "📁 Main folders:\n\nbackend/ - Python scripts and FastAPI\nfrontend/ - React UI and components\n\nSee README for complete structure!";
    }

    // Usage
    if (
      lowerQuestion.includes("use") ||
      lowerQuestion.includes("usage") ||
      lowerQuestion.includes("tutorial") ||
      lowerQuestion.includes("guide")
    ) {
      const content = findInReadme(["usage", "💡", "connect"]);
      return content || "💡 Usage:\n1. Connect Arduino via USB\n2. Start backend (FastAPI)\n3. Start frontend (Vite)\n4. Click buttons to run operations\n5. Watch live output in terminal";
    }

    // WebSocket
    if (
      lowerQuestion.includes("websocket") ||
      lowerQuestion.includes("real-time") ||
      lowerQuestion.includes("live") ||
      lowerQuestion.includes("stream")
    ) {
      return "⚡ Real-time Communication:\n\n• WebSocket connection between frontend and backend\n• Live streaming of script output\n• Instant feedback as scripts execute\n• No page refresh needed\n• Terminal updates in real-time";
    }

    // Specific questions about buttons
    if (lowerQuestion.includes("create key") || lowerQuestion.includes("generate")) {
      return "🔑 Create Key Button:\n\nRuns 1create_key.py which:\n• Generates new Ethereum private key on Arduino\n• Stores key securely in hardware\n• Returns wallet address\n• Never exposes private key to computer";
    }

    if (lowerQuestion.includes("get wallet") || lowerQuestion.includes("balance")) {
      return "📜 Get Wallet Info Button:\n\nRuns 2get_wallet.py which:\n• Retrieves wallet address from Arduino\n• Checks balance on blockchain\n• Displays wallet information\n• No private key exposure";
    }

    if (lowerQuestion.includes("sign")) {
      return "✍️ Sign Hash Button:\n\nRuns 3test_sign_hash.py which:\n• Takes transaction hash\n• Signs it using Arduino's private key\n• Returns signed transaction\n• All signing happens on Arduino";
    }

    if (lowerQuestion.includes("broadcast")) {
      return "🚀 Broadcast Transaction Button:\n\nRuns 4broadcast_tx.py which:\n• Takes signed transaction\n• Broadcasts to Ethereum network\n• Confirms transaction on blockchain\n• Returns transaction hash";
    }

    // Credits
    if (lowerQuestion.includes("credit") || lowerQuestion.includes("author") || lowerQuestion.includes("team")) {
      return "👥 Credits: @teamcoldvault\n\nColdVault is an open-source project for secure cold wallet management using Arduino hardware!";
    }

    // Default - search README for any matching content
    const keywords = lowerQuestion.split(' ').filter(word => word.length > 3);
    if (keywords.length > 0) {
      const content = findInReadme(keywords);
      if (content) return content;
    }

    // Fallback
    return "I'm here to help with ColdVault! You can ask me about:\n\n• 🎯 Features and capabilities\n• 🛠️ Setup and installation\n• 🧠 How the system works\n• 📝 Python scripts and operations\n• 🔌 Arduino connection\n• 🔒 Security features\n• ⚙️ Technology stack\n• 💡 Usage and tutorials\n\nWhat would you like to know? 😊";
  };

  const handleSend = () => {
    if (!input.trim()) return;

    // Add user message
    setMessages((prev) => [...prev, { type: "user", text: input }]);
    setInput("");
    setIsTyping(true);

    // Simulate typing delay and add bot response
    setTimeout(() => {
      const response = getResponse(input);
      setMessages((prev) => [...prev, { type: "bot", text: response }]);
      setIsTyping(false);
    }, 800);
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const suggestedQuestions = [
    "What are the features?",
    "How do I set it up?",
    "How does it work?",
    "Is it secure?",
  ];

  const handleSuggestion = (question) => {
    setInput(question);
  };

  return (
    <div className="chatbot-container">
      <div className="chatbot-header">
        <span className="chatbot-avatar">🤖</span>
        <div className="chatbot-header-info">
          <h3 className="chatbot-title">README Assistant</h3>
          <p className="chatbot-status">
            <span className="status-dot"></span>
            Online & Ready
          </p>
        </div>
      </div>

      <div className="chatbot-messages">
        <AnimatePresence>
          {messages.map((msg, index) => (
            <motion.div
              key={index}
              className={`message ${msg.type}`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              {msg.type === "bot" && <span className="message-avatar">🤖</span>}
              <div className="message-bubble">
                <pre className="message-text">{msg.text}</pre>
              </div>
              {msg.type === "user" && <span className="message-avatar">👤</span>}
            </motion.div>
          ))}
        </AnimatePresence>

        {isTyping && (
          <motion.div
            className="message bot"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <span className="message-avatar">🤖</span>
            <div className="message-bubble typing">
              <span className="typing-dot"></span>
              <span className="typing-dot"></span>
              <span className="typing-dot"></span>
            </div>
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {messages.length === 1 && (
        <div className="suggested-questions">
          <p className="suggestions-title">Try asking:</p>
          <div className="suggestions-grid">
            {suggestedQuestions.map((q, i) => (
              <button
                key={i}
                className="suggestion-btn"
                onClick={() => handleSuggestion(q)}
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="chatbot-input-container">
        <input
          type="text"
          className="chatbot-input"
          placeholder="Ask me anything about ColdVault..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
        />
        <motion.button
          className="chatbot-send-btn"
          onClick={handleSend}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <span className="send-icon">📤</span>
        </motion.button>
      </div>
    </div>
  );
}
