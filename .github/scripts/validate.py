import os
import sys
import json
from PIL import Image
from eth_utils import to_checksum_address, is_address

# --- 설정값 ---
MAX_FILE_SIZE_KB = 1024
MAX_DIMENSION = 512
REQUIRED_FIELDS = ["name", "type", "symbol", "decimal", "description", "website", "explorer", "id", "links"]

# Scam-proof whitelist
# Example format:
# "memecore": {
#     "USDT": "0xYourMemeCoreUSDT...",
#     "BTC": "0xYourMemeCoreBTC..."
# },
# "ethereum": {
#     "USDT": "0xdac17f958d2ee523a2206206994597c13d831ec7"
# } 
OFFICIAL_CONTRACTS = {
}

def fail(message):
    print(f"❌ {message}")
    sys.exit(1)

def validate_token_folder(base_path, chain_name, token_address):
    # base_path: blockchains/memecore/assets
    # chain_name: memecore
    # token_address: 0x123...
    
    # [Fix] Define folder_path correctly at the beginning
    folder_path = os.path.join(base_path, token_address)
    
    print(f"🔍 Checking [{chain_name}] token: {token_address}...")

    # 1. verify address checksum
    if not is_address(token_address):
        fail(f"Folder name '{token_address}' is not a valid EVM address.")
    
    expected_checksum = to_checksum_address(token_address)
    if token_address != expected_checksum:
        fail(f"Checksum Error! Folder name must be mixed-case.\n   Current: {token_address}\n   Correct: {expected_checksum}")

    # 2. verify file existence
    logo_path = os.path.join(folder_path, "logo.png")
    info_path = os.path.join(folder_path, "info.json")

    if not os.path.exists(logo_path): fail(f"Missing logo.png in {token_address}")
    if not os.path.exists(info_path): fail(f"Missing info.json in {token_address}")

    # 3. verify image
    # [Fix] folder_path is now defined, so os.listdir works
    if any(f.lower() == "logo.png" and f != "logo.png" for f in os.listdir(folder_path)):
        fail("Filename must be lowercase 'logo.png', not 'Logo.png' or 'LOGO.PNG'.")

    try:
        with Image.open(logo_path) as img:
            # 3-b. check format
            if img.format != "PNG":
                fail("Image format must be PNG.")
            
            # 3-c. check size
            w, h = img.size
            if w > MAX_DIMENSION or h > MAX_DIMENSION:
                fail(f"Image too big: {w}x{h}. Max allowed is {MAX_DIMENSION}x{MAX_DIMENSION}.")
            
            # 3-d. check 1:1 ratio
            if w != h:
                fail(f"Image must be square (1:1 ratio). Current: {w}x{h}.")

        # 3-e. check file size
        file_size_kb = os.path.getsize(logo_path) / 1024
        if file_size_kb > MAX_FILE_SIZE_KB:
            fail(f"Image size too large: {file_size_kb:.2f}KB. Max allowed is {MAX_FILE_SIZE_KB}KB.")

    except Exception as e:
        fail(f"Invalid image file: {str(e)}")


    # 4. verify JSON and scam
    # [Added] Check filename case for info.json as well
    if any(f.lower() == "info.json" and f != "info.json" for f in os.listdir(folder_path)):
        fail("Filename must be lowercase 'info.json'.")

    try:
        with open(info_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # [Added] Check REQUIRED_FIELDS
        missing = [field for field in REQUIRED_FIELDS if field not in data]
        if missing:
            fail(f"Missing fields in info.json: {', '.join(missing)}")
        
        # check ID
        if data.get('id') != token_address:
            fail(f"ID mismatch! JSON id ({data.get('id')}) != Folder name ({token_address})")

        # multichain scam-proof
        chain_key = chain_name.lower()
        if chain_key in OFFICIAL_CONTRACTS:
            symbol = data.get('symbol', '').upper()
            scam_list = OFFICIAL_CONTRACTS[chain_key]
            
            if symbol in scam_list:
                if data['id'] != scam_list[symbol]:
                    fail(f"⚠️ SCAM ALERT on {chain_name}: '{symbol}' must be {scam_list[symbol]}")

    except json.JSONDecodeError:
        fail("info.json is not a valid JSON file.")
    except Exception as e:
        fail(f"Error checking info.json: {str(e)}")

    print(f"✅ [{chain_name}] Token {token_address} passed!")

# --- main ---
if __name__ == "__main__":
    changed_files = os.environ.get("ALL_CHANGED_FILES", "")
    checked_folders = set()

    for file_path in changed_files.split():
        # split path: blockchains / [chain_name] / assets / [address] / logo.png
        parts = file_path.split(os.sep)
        
        # at least path must be 'blockchains/chain_name/assets/address/...'
        if len(parts) >= 4 and parts[0] == "blockchains" and parts[2] == "assets":
            chain_name = parts[1]       # e.g.: memecore, ethereum
            token_address = parts[3]    # e.g.: 0x123...
            
            # reconstructing path
            # base_path = blockchains/memecore/assets
            base_path = os.path.join(parts[0], parts[1], parts[2])
            
            # check redundancy
            unique_key = f"{chain_name}/{token_address}"
            
            if unique_key not in checked_folders:
                # check file existence
                # We construct the path here to check if folder exists
                check_path = os.path.join(base_path, token_address)
                if os.path.isdir(check_path):
                    validate_token_folder(base_path, chain_name, token_address)
                    checked_folders.add(unique_key)

    if not checked_folders:
        print("No asset files modified.")