import React, { useRef } from "react";
import Terminal from "./Terminal";

export default function App() {
  const termRef = useRef();
  const wsUrl = "ws://localhost:8000/ws/run";

  return (
    <div
      style={{
        background: "linear-gradient(135deg, #f8fafc, #eef2ff)",
        minHeight: "100vh",
        fontFamily: "Inter, 'Segoe UI', sans-serif",
        color: "#111827",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        padding: "40px 20px",
      }}
    >
      <h1
        style={{
          fontSize: "2.5rem",
          fontWeight: "700",
          marginBottom: "10px",
        }}
      >
        ColdVault
      </h1>
      <p
        style={{
          opacity: 0.7,
          marginBottom: "30px",
        }}
      >
        A secure interface for your Arduino cold wallet scripts.
      </p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "30px",
          width: "90%",
          maxWidth: "1100px",
        }}
      >
        {/* Left Card */}
        <div
          style={{
            background: "#fff",
            borderRadius: "16px",
            boxShadow: "0 6px 20px rgba(0,0,0,0.08)",
            padding: "24px",
          }}
        >
          <h2
            style={{
              fontSize: "1.3rem",
              fontWeight: "600",
              marginBottom: "20px",
            }}
          >
            Controls
          </h2>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "10px",
            }}
          >
            <button
              style={buttonStyle("#3b82f6")}
              onClick={() => termRef.current?.runCmd("create_key")}
            >
              🔑 Create New Key
            </button>

            <button
              style={buttonStyle("#38bdf8")}
              onClick={() => termRef.current?.runCmd("get_wallet")}
            >
              📜 Get Wallet Info
            </button>

            <button
              style={buttonStyle("#facc15")}
              onClick={() => termRef.current?.runCmd("sign_hash")}
            >
              ✍️ Sign Test Tx
            </button>

            <button
              style={buttonStyle("#22c55e")}
              onClick={() => termRef.current?.runCmd("broadcast_tx")}
            >
              🚀 Broadcast Tx
            </button>

            <button
              style={buttonStyle("#6b7280")}
              onClick={() => termRef.current?.clear()}
            >
              🧹 Clear Terminal
            </button>
          </div>
        </div>

        {/* Right Card */}
        <div
          style={{
            background: "#fff",
            borderRadius: "16px",
            boxShadow: "0 6px 20px rgba(0,0,0,0.08)",
            padding: "24px",
          }}
        >
          <h2
            style={{
              fontSize: "1.3rem",
              fontWeight: "600",
              marginBottom: "8px",
            }}
          >
            Activity Log
          </h2>
          <p
            style={{
              fontSize: "0.9rem",
              color: "#6b7280",
              marginBottom: "20px",
            }}
          >
            Shows real-time output from your Python scripts.
          </p>

          <Terminal ref={termRef} wsUrl={wsUrl} />
        </div>
      </div>
    </div>
  );
}

function buttonStyle(bg) {
  return {
    background: bg,
    color: "white",
    border: "none",
    borderRadius: "8px",
    padding: "12px",
    fontWeight: "500",
    cursor: "pointer",
    fontSize: "0.9rem",
    transition: "all 0.2s ease",
  };
}
