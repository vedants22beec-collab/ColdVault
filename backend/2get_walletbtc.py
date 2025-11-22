#!/usr/bin/env python3
"""
Get Wallet Script for Arduino Bitcoin Testnet Cold Wallet
This script retrieves the current wallet information from Arduino
"""

import json
import serial
import time
from pathlib import Path

from bit import PrivateKeyTestnet

BASE_DIR = Path(__file__).resolve().parent
WALLET_FILE = BASE_DIR / "btc_wallet_info.json"


def connect_to_arduino(port=None, baudrate=9600, timeout=10):
    """Connect to Arduino and wait for ready signal"""
    if port is None:
        # Auto-detect common Arduino ports
        import serial.tools.list_ports

        ports = []
        for port_info in serial.tools.list_ports.comports():
            if (
                "Arduino" in port_info.description
                or "ACM" in port_info.device
                or "USB" in port_info.description
            ):
                ports.append(port_info.device)

        if not ports:
            print("❌ No Arduino found! Please connect Arduino and try again.")
            return None

        port = ports[0]
        print(f"🔍 Auto-detected Arduino on {port}")

    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        print(f"✅ Connected to Arduino on {port}")

        # Wait for Arduino ready signal
        print("⏳ Waiting for Arduino to initialize...")
        while True:
            line = ser.readline().decode().strip()
            if line == "ARDUINO_COLD_WALLET_READY":
                print("✅ Arduino is ready!")
                break
            elif line:
                print(f"📥 Arduino: {line}")

        # Check if wallet was loaded
        while True:
            line = ser.readline().decode().strip()
            if line == "WALLET_LOADED":
                print("✅ Wallet loaded from memory!")
                break
            elif line == "NO_WALLET":
                print("ℹ️  No wallet in memory")
                break
            elif line:
                print(f"📥 Arduino: {line}")

        return ser
    except Exception as e:
        print(f"❌ Failed to connect to Arduino: {e}")
        print(" Make sure Arduino is connected and the correct port is selected")
        return None


def check_wallet_status(ser):
    """Check if Arduino has a wallet"""
    print("🔍 Checking wallet status...")
    ser.write(b"GET_STATUS\n")

    while True:
        line = ser.readline().decode().strip()
        if line == "STATUS:HAS_KEY":
            print("✅ Arduino has a wallet")
            return True
        elif line == "STATUS:NO_KEY":
            print("❌ Arduino has no wallet")
            return False
        elif line:
            print(f"📥 Arduino: {line}")


def normalize_private_key(private_key: str) -> str:
    """Normalize private key string from Arduino output"""
    key = private_key.strip()
    if key.startswith("0x"):
        key = key[2:]
    return key.lower()


def get_wallet_info(ser):
    """Get wallet information from Arduino"""
    print("📋 Retrieving wallet information...")
    ser.write(b"GET_WALLET\n")

    while True:
        line = ser.readline().decode().strip()
        if line.startswith("PRIVATE_KEY:"):
            private_key = normalize_private_key(line[12:])
            print(f"✅ Private key retrieved: {private_key}")
            return private_key
        elif line.startswith("ERROR:"):
            print(f"❌ Error: {line}")
            return None
        elif line:
            print(f"📥 Arduino: {line}")


def generate_wallet(private_key: str):
    """Generate Bitcoin testnet address and WIF from private key"""
    try:
        key = PrivateKeyTestnet.from_hex(private_key)
        return key.address, key.to_wif()
    except Exception as e:
        print(f"❌ Failed to generate Bitcoin wallet: {e}")
        return None, None


def load_saved_wallet():
    """Load saved wallet information if available"""
    try:
        if not WALLET_FILE.exists():
            return None
        return json.loads(WALLET_FILE.read_text())
    except Exception as e:
        print(f"⚠️  Could not load saved wallet: {e}")
        return None


def save_wallet_info(address: str, private_key: str, wif: str):
    """Save wallet information to file"""
    wallet_data = {
        "address": address,
        "private_key_hex": private_key,
        "private_key_wif": wif,
        "retrieved_at": time.time(),
        "network": "bitcoin-testnet",
        "note": "Retrieved from Arduino Cold Wallet",
    }

    WALLET_FILE.write_text(json.dumps(wallet_data, indent=2))
    print(f" Wallet information saved to '{WALLET_FILE.name}'")


def main():
    print("=" * 60)
    print("ARDUINO COLD WALLET - GET BITCOIN TESTNET WALLET INFO")
    print("=" * 60)

    ser = connect_to_arduino()
    if not ser:
        return

    try:
        if not check_wallet_status(ser):
            print("\n❌ No wallet found on Arduino!")
            print(" Run 'python BTC\\1create_key.py' to create a new wallet")
            return

        private_key = get_wallet_info(ser)
        if not private_key:
            return

        address, wif = generate_wallet(private_key)
        if not address or not wif:
            return

        print("\n" + "=" * 40)
        print("CURRENT BITCOIN TESTNET WALLET")
        print("=" * 40)
        print(f" Address: {address}")
        print(f" Private Key (hex): {private_key}")
        print(f" Private Key (WIF): {wif}")
        print("=" * 40)

        save_wallet_info(address, private_key, wif)

        saved_wallet = load_saved_wallet()
        if saved_wallet:
            if saved_wallet.get("address") == address:
                print("✅ Wallet matches saved information")
            else:
                print("⚠️  Wallet differs from saved information")
                print("   This might be a new wallet or the saved info is outdated")

        print("\n✅ Wallet information retrieved successfully!")
        print("🔒 Private key is stored securely on Arduino")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        ser.close()
        print(" Disconnected from Arduino")


if __name__ == "__main__":
    main()

