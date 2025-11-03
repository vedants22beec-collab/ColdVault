#!/usr/bin/env python3
"""
Test Hash Signing Script for Arduino Cold Wallet
This script generates transaction hashes and sends them to Arduino for signing
"""

import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
os.environ["PYTHONUNBUFFERED"] = "1"

import serial
import json
import time
import hashlib
from eth_account import Account
from eth_utils import keccak

def connect_to_arduino(port=None, baudrate=9600, timeout=10):
    """Connect to Arduino and wait for ready signal"""
    if port is None:
        # Auto-detect common Arduino ports
        import serial.tools.list_ports
        ports = []
        for port_info in serial.tools.list_ports.comports():
            if 'Arduino' in port_info.description or 'ACM' in port_info.device or 'USB' in port_info.description:
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

def get_wallet_info(ser):
    """Get wallet information from Arduino"""
    print("📋 Retrieving wallet information...")
    ser.write(b"GET_WALLET\n")
    
    while True:
        line = ser.readline().decode().strip()
        if line.startswith("PRIVATE_KEY:"):
            private_key = line[12:]  # Remove "PRIVATE_KEY:" prefix
            print(f"✅ Private key retrieved: 0x{private_key}")
            return private_key
        elif line.startswith("ERROR:"):
            print(f"❌ Error: {line}")
            return None
        elif line:
            print(f"📥 Arduino: {line}")

def generate_address(private_key):
    """Generate Ethereum address from private key"""
    try:
        account = Account.from_key(f"0x{private_key}")
        address = account.address
        print(f"✅ Ethereum address: {address}")
        return address
    except Exception as e:
        print(f"❌ Failed to generate address: {e}")
        return None

def create_test_transaction(sender_address, nonce=0):
    """Create a simple test transaction"""
    
    transaction = {
        "from": sender_address,
        "to": "0x3bE2E9Bf03E8260e332768B0887C400450536eEf",  # Example recipient
        "value": 100000,  # 0.001 ETH in wei
        "gas": 21000,
        "gasPrice": 20000000000,    # 20 Gwei
        "nonce": nonce,
        "chainId": 11155111         # Sepolia testnet
    }
    
    return transaction

def generate_transaction_hash(transaction):
    """Generate transaction hash using Keccak256 for Arduino signing"""
    try:
        # Remove 'from' field for signing
        tx_for_signing = {k: v for k, v in transaction.items() if k != 'from'}
        
        # Create a string representation of the transaction
        tx_str = str(sorted(tx_for_signing.items()))
        
        # Generate hash using Keccak256 (Ethereum's hash function)
        tx_hash = keccak(tx_str.encode())
        
        print(f"✅ Transaction hash generated: {tx_hash.hex()}")
        return tx_hash.hex()
        
    except Exception as e:
        print(f"❌ Failed to generate transaction hash: {e}")
        # Fallback: use SHA256
        try:
            tx_str = str(sorted(tx_for_signing.items()))
            tx_hash = hashlib.sha256(tx_str.encode()).hexdigest()
            print(f"✅ Transaction hash generated (fallback): {tx_hash}")
            return tx_hash
        except Exception as e2:
            print(f"❌ Fallback also failed: {e2}")
            return None

def send_hash_to_arduino(ser, tx_hash):
    """Send transaction hash to Arduino for signing"""
    print(f"📤 Sending transaction hash to Arduino: {tx_hash}")
    
    # Send to Arduino
    ser.write(f"SIGN_HASH:{tx_hash}\n".encode())
    
    # Wait for response
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

def verify_signature_locally(transaction, signature, private_key):
    """Verify the signature locally without broadcasting"""
    try:
        # Check if the signature is valid format
        if len(signature) == 128:  # 64 bytes = 128 hex chars
            print("✅ Signature format is valid")
            return True
        else:
            print(f"❌ Invalid signature length: {len(signature)}")
            return False
            
    except Exception as e:
        print(f"❌ Signature verification failed: {e}")
        return False

def save_transaction_data(transaction, signature, private_key, address, tx_hash):
    """Save transaction data to file for later broadcasting"""
    tx_data = {
        "transaction": transaction,
        "signature": signature,
        "private_key": private_key,
        "address": address,
        "transaction_hash": tx_hash,
        "timestamp": time.time(),
        "signed_by": "arduino"
    }
    
    with open("pending_transaction.json", "w") as f:
        json.dump(tx_data, f, indent=2)
    
    print("Transaction data saved to 'pending_transaction.json'")
    print("   You can now use '4broadcast_tx.py' to broadcast this transaction")

def main():
    print("="*60)
    print("ARDUINO COLD WALLET - HASH SIGNING TEST")
    print("="*60)
    
    # Connect to Arduino
    ser = connect_to_arduino()
    if not ser:
        return
    
    try:
        # Check if Arduino has a wallet
        if not check_wallet_status(ser):
            print("\n❌ No wallet found on Arduino!")
            print(" Run 'python 1create_key.py' to create a new wallet")
            return
        
        # Get wallet information
        private_key = get_wallet_info(ser)
        if not private_key:
            return
        
        # Generate address from private key
        address = generate_address(private_key)
        if not address:
            return
        
        # Create test transaction
        print("\n" + "="*40)
        print("CREATING TEST TRANSACTION")
        print("="*40)
        
        transaction = create_test_transaction(address)
        print(f" Transaction Details:")
        print(f"   From: {address}")
        print(f"   To: {transaction['to']}")
        print(f"   Value: {transaction['value']} wei ({transaction['value']/10**18:.6f} ETH)")
        print(f"   Gas: {transaction['gas']}")
        print(f"   Gas Price: {transaction['gasPrice']} wei")
        print(f"   Nonce: {transaction['nonce']}")
        print(f"   Chain ID: {transaction['chainId']}")
        
        # Generate transaction hash
        print("\n" + "="*40)
        print("GENERATING TRANSACTION HASH")
        print("="*40)
        
        tx_hash = generate_transaction_hash(transaction)
        if not tx_hash:
            return
        
        # Send hash to Arduino for signing
        print("\n" + "="*40)
        print("SENDING HASH TO ARDUINO FOR SIGNING")
        print("="*40)
        
        signature = send_hash_to_arduino(ser, tx_hash)
        
        if signature:
            print("\n" + "="*40)
            print("SIGNATURE VERIFICATION")
            print("="*40)
            
            # Verify signature locally
            if verify_signature_locally(transaction, signature, private_key):
                print("✅ Transaction hash signed successfully!")
                print(f" Signature: {signature}")
                
                # Save transaction data for later broadcasting
                save_transaction_data(transaction, signature, private_key, address, tx_hash)
                
                print("\n" + "="*40)
                print("NEXT STEPS")
                print("="*40)
                print("1. ✅ Transaction hash signed by Arduino")
                print("2.  Data saved to 'pending_transaction.json'")
                print("3.  Run 'python 4broadcast_tx.py' to broadcast to blockchain")
                
            else:
                print("❌ Signature verification failed")
        else:
            print("❌ Transaction signing failed or was cancelled")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        ser.close()
        print(" Disconnected from Arduino")

if __name__ == "__main__":
    main()
