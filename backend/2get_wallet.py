#!/usr/bin/env python3
"""
Get Wallet Script for Arduino Cold Wallet
This script retrieves the current wallet information from Arduino
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
os.environ["PYTHONUNBUFFERED"] = "1"

import serial
import time
import json
from eth_account import Account

def connect_to_arduino(port=None, baudrate=9600, timeout=10):
    """Connect to Arduino and wait for ready signal"""
    if port is None:
        import serial.tools.list_ports
        ports = []
        for port_info in serial.tools.list_ports.comports():
            if 'Arduino' in port_info.description or 'ACM' in port_info.device or 'USB' in port_info.description:
                ports.append(port_info.device)
        
        if not ports:
            print("No Arduino found! Please connect Arduino and try again.")
            return None
        
        port = ports[0]
        print(f"Auto-detected Arduino on {port}")
    
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        print(f"Connected to Arduino on {port}")
        
        print("Waiting for Arduino to initialize...")
        while True:
            line = ser.readline().decode().strip()
            if line == "ARDUINO_COLD_WALLET_READY":
                print("Arduino is ready!")
                break
            elif line:
                print(f"Arduino: {line}")
        
        while True:
            line = ser.readline().decode().strip()
            if line == "WALLET_LOADED":
                print("Wallet loaded from memory!")
                break
            elif line == "NO_WALLET":
                print("No wallet in memory")
                break
            elif line:
                print(f"Arduino: {line}")
        
        return ser
    except Exception as e:
        print(f"Failed to connect to Arduino: {e}")
        print("Make sure Arduino is connected and the correct port is selected")
        return None

def check_wallet_status(ser):
    """Check if Arduino has a wallet"""
    print("Checking wallet status...")
    ser.write(b"GET_STATUS\n")
    
    while True:
        line = ser.readline().decode().strip()
        if line == "STATUS:HAS_KEY":
            print("Arduino has a wallet")
            return True
        elif line == "STATUS:NO_KEY":
            print("Arduino has no wallet")
            return False
        elif line:
            print(f"Arduino: {line}")

def get_wallet_info(ser):
    """Get wallet information from Arduino"""
    print("Retrieving wallet information...")
    ser.write(b"GET_WALLET\n")
    
    while True:
        line = ser.readline().decode().strip()
        if line.startswith("PRIVATE_KEY:"):
            private_key = line[12:]
            print(f"Private key retrieved: 0x{private_key}")
            return private_key
        elif line.startswith("ERROR:"):
            print(f"Error: {line}")
            return None
        elif line:
            print(f"Arduino: {line}")

def generate_address(private_key):
    """Generate Ethereum address from private key"""
    try:
        account = Account.from_key(f"0x{private_key}")
        address = account.address
        print(f"Ethereum address: {address}")
        return address
    except Exception as e:
        print(f"Failed to generate address: {e}")
        return None

def load_saved_wallet():
    """Load saved wallet information if available"""
    try:
        with open("wallet_info.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Could not load saved wallet: {e}")
        return None

def save_wallet_info(address, private_key):
    """Save wallet information to file"""
    wallet_data = {
        "address": address,
        "private_key": f"0x{private_key}",
        "retrieved_at": time.time(),
        "note": "Retrieved from Arduino Cold Wallet"
    }
    
    with open("wallet_info.json", "w") as f:
        json.dump(wallet_data, f, indent=2)
    
    print("Wallet information saved to 'wallet_info.json'")

def main():
    print("="*60)
    print("ARDUINO COLD WALLET - GET WALLET INFO")
    print("="*60)
    
    ser = connect_to_arduino()
    if not ser:
        return
    
    try:
        if not check_wallet_status(ser):
            print("\nNo wallet found on Arduino!")
            print("Run 'python create_key.py' to create a new wallet")
            return
        
        private_key = get_wallet_info(ser)
        if not private_key:
            return
        
        address = generate_address(private_key)
        if not address:
            return
        
        print("\n" + "="*40)
        print("CURRENT WALLET")
        print("="*40)
        print(f"Address: {address}")
        print(f"Private Key: 0x{private_key}")
        print("="*40)
        
        save_wallet_info(address, private_key)
        
        saved_wallet = load_saved_wallet()
        if saved_wallet:
            if saved_wallet.get("address") == address:
                print("Wallet matches saved information")
            else:
                print("Wallet differs from saved information")
                print("This might be a new wallet or the saved info is outdated")
        
        print("\nWallet information retrieved successfully!")
        print("Private key is stored securely on Arduino")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ser.close()
        print("Disconnected from Arduino")

if __name__ == "__main__":
    main()
