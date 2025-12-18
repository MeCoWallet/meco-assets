# tools/add_token.py
import os
import json
import sys
from eth_utils import to_checksum_address, is_address

def create_asset(chain, address):
    if not is_address(address):
        print("❌ Invalid address format")
        return

    checksum_addr = to_checksum_address(address)
    base_path = f"blockchains/{chain}/assets/{checksum_addr}"
    
    # create folder
    os.makedirs(base_path, exist_ok=True)
    
    # create info.json template
    info_data = {
        "name": "Token Name",
        "website": "https://...",
        "description": "...",
        "explorer": f"https://memecorescan.io/token/{checksum_addr}",
        "type": "MRC20",
        "symbol": "SYMBOL",
        "decimals": 18,
        "status": "active",
        "id": checksum_addr
    }
    
    with open(f"{base_path}/info.json", "w") as f:
        json.dump(info_data, f, indent=4)
        
    print(f"✅ Created folder: {base_path}")
    print(f"👉 Please add your 'logo.png' here and edit 'info.json'.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python tools/add_token.py <chain> <address>")
        print("Example: python tools/add_token.py memecore 0x1234...")
    else:
        create_asset(sys.argv[1], sys.argv[2])