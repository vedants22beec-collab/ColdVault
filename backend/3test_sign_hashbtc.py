#!/usr/bin/env python3
"""
Test Hash Signing Script for Arduino Bitcoin Testnet Cold Wallet
This script generates transaction hashes and sends them to Arduino for signing
"""

import hashlib
import json
import serial
import time
from pathlib import Path

from bit import PrivateKeyTestnet

BASE_DIR = Path(__file__).resolve().parent
PENDING_FILE = BASE_DIR / "pending_btc_transaction.json"


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


def create_test_transaction(sender_address: str, recipient_address: str | None = None, amount_sats: int = 10_000):
    """Create a simple test transaction template"""
    if recipient_address is None:
        recipient_address = "tb1qj0w0f0zt3vud4lv5z0s0z9v4eftt8v9rxkdz0w"  # Example testnet address

    transaction = {
        "from_address": sender_address,
        "to_address": recipient_address,
        "amount_sats": amount_sats,
        "fee_sats": 500,
        "network": "bitcoin-testnet",
        "memo": "Arduino test transaction",
        "timestamp": int(time.time()),
    }

    return transaction


def generate_transaction_hash(transaction: dict):
    """Generate transaction hash using double SHA256 for Arduino signing"""
    try:
        payload = json.dumps(transaction, sort_keys=True, separators=(",", ":"))
        tx_hash = hashlib.sha256(hashlib.sha256(payload.encode()).digest()).hexdigest()
        print(f"✅ Transaction hash generated: {tx_hash}")
        return tx_hash
    except Exception as e:
        print(f"❌ Failed to generate transaction hash: {e}")
        return None


def send_hash_to_arduino(ser, tx_hash: str):
    """Send transaction hash to Arduino for signing"""
    print(f"📤 Sending transaction hash to Arduino: {tx_hash}")

    ser.write(f"SIGN_HASH:{tx_hash}\n".encode())

    print("⏳ Waiting for Arduino response...")
    while True:
        response = ser.readline().decode().strip()
        if not response:
            continue

        print(f"📥 Arduino: {response}")

        if response == "PRESS_BUTTON":
            print(" Press CONFIRM button on Arduino to sign")
            print(" Press CANCEL button to abort")
            continue
        elif response.startswith("HASH_SIGNATURE:"):
            signature = response[15:]  # Remove "HASH_SIGNATURE:" prefix
            print(f"✅ Hash signature received: {signature}")
            return signature
        elif response == "CANCELLED":
            print("❌ Transaction cancelled by user")
            return None
        elif response == "TIMEOUT":
            print("❌ Signing timed out")
            return None
        elif response.startswith("ERROR:"):
            print(f"❌ Error: {response}")
            return None


def verify_signature_locally(tx_hash: str, signature: str):
    """Basic signature sanity checks (full Bitcoin validation requires Arduino pubkey)"""
    if not signature:
        print("❌ No signature received for verification")
        return False

    try:
        bytes.fromhex(signature)
    except ValueError:
        print("❌ Signature is not valid hex")
        return False

    if len(signature) < 140:
        print("⚠️  Signature shorter than typical DER-encoded ECDSA signature")
    else:
        print("✅ Signature format looks plausible (hex-encoded DER)")

    print("⚠️  Full verification requires Arduino to expose the public key")
    return True


def save_transaction_data(transaction: dict, signature: str | None, private_key: str, wif: str, address: str, tx_hash: str):
    """Save transaction data to file for later broadcasting"""
    tx_data = {
        "transaction": transaction,
        "signature": signature,
        "private_key_hex": private_key,
        "private_key_wif": wif,
        "address": address,
        "transaction_hash": tx_hash,
        "network": "bitcoin-testnet",
        "timestamp": time.time(),
        "signed_by": "arduino" if signature else "unknown",
    }

    PENDING_FILE.write_text(json.dumps(tx_data, indent=2))
    print(f"Transaction data saved to '{PENDING_FILE.name}'")
    print("   You can now use 'python BTC\\4broadcast_tx.py' to broadcast this transaction")


def main():
    print("=" * 60)
    print("ARDUINO COLD WALLET - BITCOIN TESTNET HASH SIGNING")
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
        print("CREATING TEST TRANSACTION TEMPLATE")
        print("=" * 40)

        transaction = create_test_transaction(address)
        print(" Transaction Details:")
        print(f"   From: {transaction['from_address']}")
        print(f"   To: {transaction['to_address']}")
        print(f"   Amount: {transaction['amount_sats']} sats ({transaction['amount_sats']/1e8:.8f} BTC)")
        print(f"   Fee: {transaction['fee_sats']} sats")
        print(f"   Memo: {transaction['memo']}")

        print("\n" + "=" * 40)
        print("GENERATING TRANSACTION HASH")
        print("=" * 40)

        tx_hash = generate_transaction_hash(transaction)
        if not tx_hash:
            return

        print("\n" + "=" * 40)
        print("SENDING HASH TO ARDUINO FOR SIGNING")
        print("=" * 40)

        signature = send_hash_to_arduino(ser, tx_hash)

        if signature:
            print("\n" + "=" * 40)
            print("SIGNATURE VERIFICATION")
            print("=" * 40)

            if verify_signature_locally(tx_hash, signature):
                print("✅ Transaction hash signed successfully!")
                print(f" Signature: {signature}")
            else:
                print("⚠️  Signature verification incomplete - manual review recommended")
        else:
            print("⚠️  Transaction signing failed or was cancelled")

        save_transaction_data(transaction, signature, private_key, wif, address, tx_hash)

        print("\n" + "=" * 40)
        print("NEXT STEPS")
        print("=" * 40)
        print("1. ✅ Transaction hash prepared and optionally signed by Arduino")
        print(f"2.  Data saved to '{PENDING_FILE.name}'")
        print("3.  Run 'python BTC\\4broadcast_tx.py' to broadcast to Bitcoin testnet")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        ser.close()
        print(" Disconnected from Arduino")


if __name__ == "__main__":
    main()

