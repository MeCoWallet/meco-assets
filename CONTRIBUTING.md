# Contributing to MeCo Assets

Welcome to the **MeCo Asset Repository**! 👋
MeCo provides the official asset information for the **MemeCore Network**. We value **speed, freedom, and community**. We do not charge listing fees and aim to keep the barrier to entry as low as possible for all meme projects building on MemeCore.

However, to maintain a high-quality experience for users, MeCo enforces strict **technical standards** via automation bots. Please read this guide carefully before submitting your Pull Request (PR).

---

## 📂 Directory Structure

We follow the standard multi-chain structure. For tokens on the **MemeCore Network**, your files must be placed in:

```text
blockchains/
└── memecore/            <-- Network Name
    └── assets/
        └── 0x1234...ABCD/       <-- Folder Name (Checksum Address)
            ├── logo.png         <-- Image File (Must be lowercase)
            └── info.json        <-- Info File (Must be lowercase)
```

---

## ✅ Asset Requirements (Strictly Enforced)

The MeCo automated bot will **fail your build** if these requirements are not met.

### 1. Folder Name (Address)
*   **Format:** The folder name must be the **Checksummed Version** of the contract address.
    *   ❌ `0xabcd1234...` (All lowercase is NOT allowed for folders)
    *   ✅ `0xAbCd1234...` (Mixed-case checksum is required)
*   **Tip:** You can check the checksum address on a block explorer or use `ethers.utils.getAddress()` in JS / `to_checksum_address` in Python.

### 2. Image (`logo.png`)
*   **Filename:** Must be exactly `logo.png` (lowercase). `Logo.png` or `logo.PNG` will be rejected.
*   **Format:** PNG only.
*   **Dimensions:**
    *   Maximum: **512x512** pixels.
    *   Ratio: Must be **1:1 (Square)**.
*   **Size:** Under **100KB** (Recommended), Max **1MB** (Hard limit).
*   **Background:** Transparent background is highly recommended for circular cropping.

### 3. Token Info (`info.json`)
*   **Filename:** Must be exactly `info.json` (lowercase).
*   **Content:** Valid JSON format containing details about your project.
*   **Required Fields:**
    *   `name`: Project name
    *   `website`: Official website URL
    *   `description`: Short summary
    *   `explorer`: Block explorer link for the token
    *   `type`: Token standard (e.g., `MRC20`)
    *   `symbol`: Token symbol
    *   `decimals`: (number) e.g., 18
    *   `status`: `active`
    *   `id`: **Must match the folder name (Checksum Address)**

#### Example `info.json`
```json
{
    "name": "Pepe Meme Coin",
    "website": "https://pepe-meme.com",
    "description": "The most memeable coin on MemeCore Network.",
    "explorer": "https://memecorescan.io/token/0xAbCd...",
    "type": "MRC20",
    "symbol": "PEPE",
    "decimals": 18,
    "status": "active",
    "id": "0xAbCd..."
}
```

---

## 🚫 Rejection Criteria

While MeCo is open to all projects, we have a **Zero Tolerance Policy** for the following:

1.  **Impersonation (Scams):**
    *   Do not try to register fake versions of major tokens (e.g., USDT, USDC, WETH, WBTC).
    *   Our bot checks against the official MeCo whitelist. If you try to upload a fake USDT logo, it will be auto-rejected.
2.  **Harmful Content:**
    *   Images containing NSFW (pornography), hate speech, or illegal content will be rejected and the user banned.
3.  **Malicious Contracts:**
    *   Contracts identified as obvious honeypots or drainers may be removed without notice.

---

## 📝 How to Submit (Step-by-Step)

1.  **Fork** this repository to your GitHub account.
2.  **Create a Folder** in `blockchains/memecore/assets/` named after your token's **Checksum Address**.
3.  **Add Files**: Place your `logo.png` and `info.json` inside that folder.
4.  **Commit & Push** to your forked repository.
5.  **Create a Pull Request (PR)** to the `main` branch of this repository.
    *   **PR Title Example:** `Add logo for PEPE`
6.  **Wait for Bot Checks:**
    *   After submitting, the "Asset Validator" bot will run automatically.
    *   ✅ **Green Check:** Your PR is valid. The MeCo team will merge it soon.
    *   ❌ **Red Cross:** Something is wrong. Click "Details" to see the error message and fix it.

---

## ⚠️ Disclaimer

Listing on MeCo Assets is for **informational purposes only**.
*   It does **NOT** constitute an endorsement, approval, or investment advice by the MeCo or MemeCore team.
*   We do not verify the security or legitimacy of the token contracts.
*   Users are responsible for doing their own research (DYOR).