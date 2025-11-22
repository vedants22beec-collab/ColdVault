#!/usr/bin/env python3
"""
Broadcast Transaction Script for Arduino Bitcoin Testnet Cold Wallet
This script broadcasts a prepared transaction to the Bitcoin testnet network
"""

import json
import time
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict

import requests
from bit import PrivateKeyTestnet

BASE_DIR = Path(__file__).resolve().parent
PENDING_FILE = BASE_DIR / "pending_btc_transaction.json"
BLOCKSTREAM_TESTNET_API = "https://blockstream.info/testnet/api/tx"


def satoshis_to_btc(satoshis: int) -> Decimal:
    return Decimal(satoshis) / Decimal(100_000_000)


def load_pending_transaction() -> Dict[str, Any] | None:
    """Load pending transaction from file"""
    if not PENDING_FILE.exists():
        print("❌ No pending Bitcoin transaction found!")
        print("   Run 'python BTC\\3test_sign_hash.py' first to create a signed transaction template")
        return None

    try:
        return json.loads(PENDING_FILE.read_text())
    except Exception as e:
        print(f"❌ Error loading transaction: {e}")
        return None


def verify_transaction_data(tx_data: Dict[str, Any]) -> bool:
    """Verify the transaction data is complete"""
    required_fields = [
        "transaction",
        "private_key_hex",
        "private_key_wif",
        "address",
    ]

    for field in required_fields:
        if field not in tx_data:
            print(f"❌ Missing required field: {field}")
            return False

    transaction = tx_data["transaction"]
    tx_required = ["from_address", "to_address", "amount_sats"]
    for field in tx_required:
        if field not in transaction:
            print(f"❌ Transaction missing required field: {field}")
            return False

    print("✅ Transaction data verification passed")
    return True


def broadcast_transaction(tx_data: Dict[str, Any]) -> str | None:
    """Broadcast the transaction, using Arduino signature if provided or Python fallback"""
    transaction = tx_data["transaction"]
    signature = tx_data.get("signature")
    wif = tx_data["private_key_wif"]

    print("📋 Transaction Details:")
    print(f"   From: {transaction['from_address']}")
    print(f"   To: {transaction['to_address']}")
    print(f"   Amount: {transaction['amount_sats']} sats ({satoshis_to_btc(transaction['amount_sats']):.8f} BTC)")
    fee_sats = transaction.get("fee_sats", 0)
    print(f"   Fee: {fee_sats} sats ({satoshis_to_btc(fee_sats):.8f} BTC)")
    print(f"   Network: {transaction.get('network', 'bitcoin-testnet')}")
    print(f"   Memo: {transaction.get('memo', '')}")
    print(f"   Signed by Arduino: {'yes' if signature else 'no'}")

    if signature and tx_data.get("raw_transaction_hex"):
        print("🔐 Attempting to broadcast Arduino-signed raw transaction...")
        return broadcast_raw_transaction(tx_data["raw_transaction_hex"])

    print("🔐 Arduino signature not available or raw TX missing - using Python fallback")
    return broadcast_with_python_fallback(transaction, wif, fee_sats)


def broadcast_raw_transaction(raw_tx_hex: str) -> str | None:
    """Broadcast a raw transaction hex string via Blockstream API"""
    try:
        response = requests.post(
            BLOCKSTREAM_TESTNET_API,
            data=raw_tx_hex,
            headers={"Content-Type": "text/plain"},
            timeout=30,
        )
        if response.status_code == 200:
            tx_id = response.text.strip()
            print("✅ Raw transaction broadcasted successfully!")
            print(f"📝 Transaction Hash: {tx_id}")
            print(f"🔍 View on Explorer: https://blockstream.info/testnet/tx/{tx_id}")
            return tx_id

        print(f"❌ Broadcast failed with status {response.status_code}: {response.text}")
        return None
    except requests.RequestException as e:
        print(f"❌ Network error while broadcasting raw transaction: {e}")
        return None


def broadcast_with_python_fallback(transaction: Dict[str, Any], wif: str, fee_sats: int) -> str | None:
    """Fallback to Python signing and broadcasting using the Bit library"""
    try:
        key = PrivateKeyTestnet.from_wif(wif)
    except Exception as e:
        print(f"❌ Could not load private key from WIF: {e}")
        return None

    outputs = [
        (transaction["to_address"], satoshis_to_btc(transaction["amount_sats"]), "btc")
    ]

    try:
        if fee_sats:
            print("📡 Broadcasting via Bit library with explicit fee...")
            tx_hex = key.send(outputs, fee=fee_sats, absolute_fee=True)
        else:
            print("📡 Broadcasting via Bit library...")
            tx_hex = key.send(outputs)
    except Exception as e:
        print(f"❌ Python signing/broadcast failed: {e}")
        return None

    print("✅ Transaction broadcasted successfully via Bit library!")
    print(f"📝 Transaction Hash: {tx_hex}")
    print(f"🔍 View on Explorer: https://blockstream.info/testnet/tx/{tx_hex}")
    return tx_hex


def cleanup_pending_transaction():
    """Remove the pending transaction file after successful broadcast"""
    try:
        PENDING_FILE.unlink()
        print(f"🧹 Cleaned up {PENDING_FILE.name}")
    except FileNotFoundError:
        print("⚠️  Pending transaction file already removed")
    except Exception as e:
        print(f"⚠️  Could not remove pending transaction file: {e}")


def main():
    print("=" * 60)
    print("ARDUINO COLD WALLET - BITCOIN TESTNET BROADCASTER")
    print("=" * 60)

    tx_data = load_pending_transaction()
    if not tx_data:
        return

    if not verify_transaction_data(tx_data):
        return

    if "timestamp" in tx_data:
        age_seconds = int(time.time() - tx_data["timestamp"])
        print(f"⏰ Transaction age: {age_seconds} seconds")
        if age_seconds > 3600:
            print("⚠️  Warning: Transaction is over 1 hour old. UTXOs may have changed.")

    print("\n" + "=" * 40)
    print("CONFIRMATION")
    print("=" * 40)
    response = input("🚀 Do you want to broadcast this transaction to Bitcoin testnet? (y/N): ").strip().lower()

    if response not in {"y", "yes"}:
        print("❌ Transaction broadcast cancelled")
        return

    print("\n" + "=" * 40)
    print("BROADCASTING TRANSACTION")
    print("=" * 40)

    tx_hash = broadcast_transaction(tx_data)
    if tx_hash:
        print("\n" + "=" * 40)
        print("SUCCESS!")
        print("=" * 40)
        print("✅ Transaction successfully broadcasted to Bitcoin testnet!")
        print(f"📝 Transaction Hash: {tx_hash}")
        cleanup_pending_transaction()
    else:
        print("\n" + "=" * 40)
        print("FAILED")
        print("=" * 40)
        print("❌ Transaction broadcast failed")
        print("   Check the error message above and try again")


if __name__ == "__main__":
    main()

