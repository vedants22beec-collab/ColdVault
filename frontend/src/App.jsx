import React, { useState } from "react";
import Home from "./components/Home";
import EVMWallet from "./components/EVMWallet";
import BitcoinWallet from "./components/BitcoinWallet";
import Educational from "./components/Educational";
import Community from "./components/Community";

export default function App() {
  const [currentPage, setCurrentPage] = useState("home");

  const renderPage = () => {
    switch (currentPage) {
      case "home":
        return <Home onNavigate={setCurrentPage} />;
      case "evm":
        return <EVMWallet onBack={() => setCurrentPage("home")} />;
      case "bitcoin":
        return <BitcoinWallet onBack={() => setCurrentPage("home")} />;
      case "education":
        return <Educational onBack={() => setCurrentPage("home")} />;
      case "community":
        return <Community onBack={() => setCurrentPage("home")} />;
      default:
        return <Home onNavigate={setCurrentPage} />;
    }
  };

  return <div className="app-container">{renderPage()}</div>;
}
