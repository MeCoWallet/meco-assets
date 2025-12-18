import os
import sys
import json
from PIL import Image
from eth_utils import to_checksum_address, is_address

MAX_FILE_SIZE_KB = 1024  # 1MB
MAX_DIMENSION = 512      # 512px
REQUIRED_FIELDS = ["name", "type", "symbol", "decimals", "description", "website", "explorer", "id", "status"]

# Scam-proof whitelist
OFFICIAL_CONTRACTS = {
    # "memecore": {
    #     "USDT": "0x...",
    # },
}

def fail(message):
    print(f"❌ {message}")
    sys.exit(1)

def validate_token_folder(base_path, chain_name, token_address):
    # [Fix] Define folder_path correctly at the beginning
    folder_path = os.path.join(base_path, token_address)
    
    print(f"🔍 Checking [{chain_name}] token folder: {token_address}...")

    # 1. Check address and checksum
    if not is_address(token_address):
        fail(f"Invalid Folder Name: '{token_address}' is not a valid EVM address.")
    
    expected_checksum = to_checksum_address(token_address)
    if token_address != expected_checksum:
        fail(f"Checksum Error! Folder name must be mixed-case.\n   Current: {token_address}\n   Correct: {expected_checksum}")

    # 2. check file existance
    logo_path = os.path.join(folder_path, "logo.png")
    info_path = os.path.join(folder_path, "info.json")

    if not os.path.exists(logo_path): fail(f"Missing file: 'logo.png' is required in {token_address}")
    if not os.path.exists(info_path): fail(f"Missing file: 'info.json' is required in {token_address}")

    # 3. check image
    if any(f.lower() == "logo.png" and f != "logo.png" for f in os.listdir(folder_path)):
        fail("Filename Error: Must be lowercase 'logo.png', not 'Logo.png'.")

    try:
        with Image.open(logo_path) as img:
            if img.format != "PNG":
                fail("Image Format Error: Must be PNG.")
            
            w, h = img.size
            if w > MAX_DIMENSION or h > MAX_DIMENSION:
                fail(f"Image Size Error: Too big ({w}x{h}). Max allowed is {MAX_DIMENSION}x{MAX_DIMENSION}.")
            
            if w != h:
                fail(f"Image Ratio Error: Must be square (1:1). Current: {w}x{h}.")

        file_size_kb = os.path.getsize(logo_path) / 1024
        if file_size_kb > MAX_FILE_SIZE_KB:
            fail(f"File Size Error: Too large ({file_size_kb:.2f}KB). Max allowed is {MAX_FILE_SIZE_KB}KB.")

    except Exception as e:
        fail(f"Image Validation Failed: {str(e)}")

    # 4. check info.json
    if any(f.lower() == "info.json" and f != "info.json" for f in os.listdir(folder_path)):
        fail("Filename Error: Must be lowercase 'info.json'.")

    try:
        with open(info_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # check field
        missing = [field for field in REQUIRED_FIELDS if field not in data]
        if missing:
            fail(f"JSON Error: Missing required fields in info.json: {', '.join(missing)}")
        
        # check ID and file
        if data.get('id') != token_address:
            fail(f"JSON Error: 'id' field ({data.get('id')}) must match folder name ({token_address}).")

        # check scam-proof
        chain_key = chain_name.lower()
        if chain_key in OFFICIAL_CONTRACTS:
            symbol = data.get('symbol', '').upper()
            scam_list = OFFICIAL_CONTRACTS[chain_key]
            
            if symbol in scam_list:
                if data['id'] != scam_list[symbol]:
                    fail(f"⚠️ SCAM ALERT: The symbol '{symbol}' is reserved. You cannot list a fake version.")

    except json.JSONDecodeError:
        fail("JSON Error: info.json is not a valid JSON file.")
    except Exception as e:
        fail(f"Info Validation Failed: {str(e)}")

    print(f"✅ [{chain_name}] Token {token_address} passed validation!")

# --- main ---
if __name__ == "__main__":
    changed_files = os.environ.get("ALL_CHANGED_FILES", "")
    checked_folders = set()

    for file_path in changed_files.split():
        parts = file_path.split('/')
        
        # check path: blockchains/[chain_name]/assets/[contents]
        if len(parts) >= 4 and parts[0] == "blockchains" and parts[2] == "assets":
            chain_name = parts[1]       # e.g. memecore
            item_name = parts[3]        # e.g. 0x123... folder or files
            
            base_path = os.path.join(parts[0], parts[1], parts[2])
            full_path = os.path.join(base_path, item_name)
            
            # strict mode
            if os.path.isfile(full_path):
                fail(f"❌ Strict Mode Error: Invalid file location '{item_name}'.\n   Files are NOT allowed directly in 'assets/'.\n   You must create a token folder (e.g. assets/0x123.../logo.png).")

            unique_key = f"{chain_name}/{item_name}"
            
            if unique_key not in checked_folders:
                if os.path.isdir(full_path):
                    validate_token_folder(base_path, chain_name, item_name)
                    checked_folders.add(unique_key)

    if not checked_folders:
        print("No valid asset folders modified (Ignored non-asset files).")