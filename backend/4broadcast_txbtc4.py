#!/usr/bin/env python3

import json
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict

import requests
from bit import PrivateKeyTestnet

BASE_DIR = Path(__file__).resolve().parent
PENDING_FILE = BASE_DIR / "pending_transaction.json"
BLOCKSTREAM_TESTNET_API = "https://blockstream.info/testnet/api/tx"


def satoshis_to_btc(satoshis: int) -> Decimal:
    return Decimal(satoshis) / Decimal(100_000_000)


def load_pending_transaction() -> Dict[str, Any] | None:
    if not PENDING_FILE.exists():
        print("No pending Bitcoin transaction found! Run 3test_sign_hash first.")
        return None
    try:
        return json.loads(PENDING_FILE.read_text())
    except Exception as e:
        print("Error loading pending transaction:", e)
        return None


def verify_transaction_data(tx_data: Dict[str, Any]) -> bool:
    required = ["transaction", "private_key_wif", "address"]
    for r in required:
        if r not in tx_data:
            print(f"Missing field: {r}")
            return False

    tx = tx_data["transaction"]
    for f in ("from_address", "to_address", "amount_sats"):
        if f not in tx:
            print(f"Transaction missing: {f}")
            return False

    return True


def broadcast_raw_transaction(raw_tx_hex: str) -> str | None:
    """Broadcast signed raw TX using Blockstream REST API."""
    try:
        resp = requests.post(
            BLOCKSTREAM_TESTNET_API,
            data=raw_tx_hex,
            headers={"Content-Type": "text/plain"},
            timeout=30,
        )
        if resp.status_code == 200:
            txid = resp.text.strip()
            print("Raw transaction broadcasted! TXID:", txid)
            print("Explorer URL:", f"https://blockstream.info/testnet/tx/{txid}")
            return txid
        else:
            print("Broadcast failed:", resp.status_code, resp.text)
            return None
    except Exception as e:
        print("Network error while broadcasting:", e)
        return None


def python_fallback_broadcast(
    transaction: Dict[str, Any], wif: str, fee_sats: int | None
) -> str | None:
    print("DEBUG WIF BEFORE LOAD:", repr(wif))

    try:
        key = PrivateKeyTestnet(wif)
    except Exception as e:
        print("Could not load WIF:", e)
        return None

    outputs = [
        (transaction["to_address"], satoshis_to_btc(transaction["amount_sats"]), "btc")
    ]

    # STEP 1: create unsigned/signed tx
    try:
        raw_hex = key.create_transaction(outputs, fee=fee_sats, absolute_fee=True)
        print("\nRAW TX HEX:", raw_hex)
    except Exception as e:
        print("Error creating raw tx:", e)
        return None

    # STEP 2: sign TX if create_transaction produced unsigned hex
    try:
        signed_hex = key.sign_transaction(raw_hex)
        print("\nSIGNED TX HEX:", signed_hex)
    except Exception:
        # python-bit sometimes returns already-signed hex
        signed_hex = raw_hex
        print("\nSIGNED TX HEX (create_transaction already signed):", signed_hex)

    print("\nUse this hex to broadcast manually.\n")

    # STEP 3: Broadcast manually using Blockstream API
    print("Broadcasting via Blockstream API...")
    txid = broadcast_raw_transaction(signed_hex)
    return txid


def cleanup_pending():
    try:
        PENDING_FILE.unlink()
        print("Removed pending transaction file.")
    except Exception:
        pass


def main():
    print("=" * 60)
    print("BITCOIN TESTNET - BROADCAST TRANSACTION")
    print("=" * 60)

    tx_data = load_pending_transaction()
    if not tx_data:
        return

    if not verify_transaction_data(tx_data):
        return

    tx = tx_data["transaction"]
    sig = tx_data.get("signature")

    print("\nTransaction Details:")
    print(f"  From: {tx['from_address']}")
    print(f"  To: {tx['to_address']}")
    print(f"  Amount: {tx['amount_sats']} sats ({satoshis_to_btc(tx['amount_sats']):.8f} BTC)")
    print(f"  Fee: {tx.get('fee_sats', 0)} sats")
    print(f"  Signed (in JSON): {'yes' if sig else 'no'}")

    print("\nBroadcasting to Bitcoin TESTNET network...")

    txid = python_fallback_broadcast(tx, tx_data["private_key_wif"], tx.get("fee_sats"))

    if txid:
        cleanup_pending()
        print("\nTransaction successfully broadcasted!")
    else:
        print("\nBroadcast failed.")


if __name__ == "__main__":
    main()
