import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import "./Educational.css";

export default function Educational({ onBack }) {
  const [activeSection, setActiveSection] = useState(null);

  const sections = [
    {
      id: "hardware",
      title: "Hardware Schematics",
      icon: "⚙️",
      gradient: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    },
    {
      id: "security",
      title: "Security Best Practices",
      icon: "🔒",
      gradient: "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
    },
    {
      id: "soon",
      title: "More features coming soon...",
      icon: "⭐",
      gradient: "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
    },
  ];

  const hardwareInfo = {
    components: [
      { name: "Arduino Uno/Mega", description: "Main microcontroller board" },
      { name: "USB Cable", description: "For serial communication" },
      { name: "Power Supply", description: "5V power adapter or USB power" },
      { name: "Optional: OLED Display", description: "For displaying wallet info" },
      { name: "Optional: Buttons", description: "For hardware-based confirmation" },
    ],
    connections: [
      { step: 1, description: "Connect Arduino to your computer via USB cable" },
      { step: 2, description: "Ensure proper drivers are installed for serial communication" },
      { step: 3, description: "Upload the cold wallet firmware to Arduino" },
      { step: 4, description: "Configure serial port settings (default: 9600 baud)" },
    ],
    diagram: `
		╔════════════════════════════════════════╗
		║          ARDUINO UNO/MEGA              ║
		║                                        ║
		║       [USB Port] ←→ Computer           ║
		║                                        ║
		║  	Optional Components:             ║
		║  	├─ OLED Display (I2C)            ║
		║  	├─ Confirm Button (Pin 2)        ║
		║  	└─ Status LED (Pin 13)           ║
		║                                        ║
		╚════════════════════════════════════════╝
			          ↓
		          [USB Connection]
			          ↓
		╔════════════════════════════════════════╗
		║           YOUR COMPUTER                ║
		║  ColdVault Backend (Python + FastAPI)  ║
		║  ColdVault Frontend (React + Vite)     ║
		╚════════════════════════════════════════╝
    `,
  };

  const securityPractices = [
    {
      title: "Air-Gapped Operation",
      description: "Use a dedicated offline computer for maximum security.",
      icon: "🔌",
    },
    {
      title: "Verify Transactions",
      description: "Always verify transaction details on the Arduino before signing.",
      icon: "✅",
    },
    {
      title: "Backup Your Keys",
      description: "Store recovery phrases in multiple secure physical locations.",
      icon: "💾",
    },
    {
      title: "Keep Firmware Updated",
      description: "Update Arduino firmware and backend regularly.",
      icon: "🔄",
    },
    {
      title: "Use Strong Passwords",
      description: "Protect your system with strong and unique passwords.",
      icon: "🔐",
    },
  ];

  return (
    <div className="educational-container">
      {/* Back Button */}
      <motion.button
        className="back-button"
        onClick={onBack}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        ← Back to Home
      </motion.button>

      {/* Header */}
      <motion.div
        className="educational-header"
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <span className="educational-icon">📚</span>
        <h1 className="educational-title">Educational Hub</h1>
        <p className="educational-subtitle">
          Learn everything about ColdVault hardware and security
        </p>
      </motion.div>

      {/* Section Buttons */}
      <div className="sections-selector">
        {sections.map((section, i) => (
          <motion.button
            key={section.id}
            className={`section-button ${
              activeSection === section.id ? "active" : ""
            }`}
            style={{ "--section-gradient": section.gradient }}
            onClick={() => setActiveSection(section.id)}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1, duration: 0.5 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <span className="section-button-icon">{section.icon}</span>
            <span className="section-button-text">{section.title}</span>
          </motion.button>
        ))}
      </div>

      {/* Content Sections */}
      <AnimatePresence mode="wait">
        {/* Hardware Section */}
        {activeSection === "hardware" && (
          <motion.div
            key="hardware"
            className="content-section"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}
          >
            <h2 className="content-title">Hardware Schematics</h2>

            <div className="hardware-grid">
              {/* Components */}
              <div className="hardware-card">
                <h3 className="hardware-card-title">🔧 Required Components</h3>
                <ul className="components-list">
                  {hardwareInfo.components.map((c, i) => (
                    <li key={i} className="component-item">
                      <span className="component-name">{c.name}</span>
                      <span className="component-desc">{c.description}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Steps */}
              <div className="hardware-card">
                <h3 className="hardware-card-title">🔌 Setup Instructions</h3>
                <ol className="instructions-list">
                  {hardwareInfo.connections.map((step, i) => (
                    <li key={i} className="instruction-item">
                      <span className="step-number">Step {step.step}</span>
                      <span className="step-description">{step.description}</span>
                    </li>
                  ))}
                </ol>
              </div>
            </div>

            {/* Diagram */}
            <div className="diagram-card">
              <h3 className="diagram-title">📐 System Architecture</h3>
              <div className="architecture-container">
                <img
                  src="/hardware_schematics.png"
                  alt="Hardware Schematics"
                  className="hardware-schematic-image"
                />
                <pre className="diagram-content">{hardwareInfo.diagram}</pre>
              </div>
            </div>
          </motion.div>
        )}

        {/* Security Section */}
        {activeSection === "security" && (
          <motion.div
            key="security"
            className="content-section"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}
          >
            <h2 className="content-title">Security Best Practices</h2>

            <div className="security-grid">
              {securityPractices.map((p, i) => (
                <motion.div
                  key={i}
                  className="security-card"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: i * 0.1, duration: 0.4 }}
                  whileHover={{ scale: 1.05, y: -5 }}
                >
                  <span className="security-icon">{p.icon}</span>
                  <h3 className="security-title">{p.title}</h3>
                  <p className="security-description">{p.description}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* No selection placeholder */}
        {!activeSection && (
          <motion.div
            key="placeholder"
            className="placeholder-content"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            <span className="placeholder-icon">👆</span>
            <p className="placeholder-text">Select a section above to start learning</p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
