# MeCo Assets Repository

<div align="center">
  <img src="meco_logo.png" width="240" alt="MeCo Logo" />
  <br />
  
  ![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/MeCoWallet/meco-assets/validate.yml?branch=main&style=flat-square&label=Asset%20Validator)
  ![GitHub license](https://img.shields.io/github/license/MeCoWallet/meco-assets?style=flat-square)
  ![PRs Welcome](https://img.shields.io/badge/PRs-welcome-green.svg?style=flat-square)

  <p>
    <b>The official asset repository providing token information for the MemeCore Network.</b>
  </p>
</div>

---

## 📖 Introduction

**MeCo Assets Repository** serves as the **single source of truth** for tokens building on the **MemeCore Network**. It is designed to be:
- **Open:** Anyone can submit a token.
- **Automated:** Validated by CI/CD bots for quality control.
- **Multi-chain Ready:** Structured to support multiple blockchains in the future.

If you are a developer building on MemeCore, please submit your asset here to have it appear in MeCo-compatible wallets, explorers, and dApps.

---

## 📂 Directory Structure

We follow the industry-standard multi-chain structure.

```text
blockchains/
└── memecore/            # Network: MemeCore
    ├── info/
    │   └── logo.png     # Chain Logo
    └── assets/
        └── 0xAbCd.../   # Token Contract Address (Checksummed)
            ├── logo.png     # Token Logo
            └── info.json    # Token Metadata
```

---

## 🚀 How to Add Your Token

We love memes, but we also love clean data. Adding your token to MeCo is free and easy.

1.  **Fork** this repository.
2.  Create a folder with your **Checksummed Contract Address** in `blockchains/memecore/assets/`.
3.  Add your `logo.png` and `info.json`.
4.  Submit a **Pull Request**.

> 👉 **Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for strict technical requirements (image size, naming conventions, etc.).**

---

## 🛠️ For Developers (Integration)

Do you want to display MemeCore token logos in your wallet or dApp? 
Do not fetch from GitHub raw URLs directly. Use **jsDelivr CDN** via MeCo for the best performance.

### Base URL
```
https://cdn.jsdelivr.net/gh/MemeCore-Org/meco-assets@main/blockchains/memecore/assets/
```

### Example Usage

**1. Get Token Logo:**
```
https://cdn.jsdelivr.net/gh/MemeCore-Org/meco-assets@main/blockchains/memecore/assets/{CHECKSUM_ADDRESS}/logo.png
```

**2. Get Token Info:**
```
https://cdn.jsdelivr.net/gh/MemeCore-Org/meco-assets@main/blockchains/memecore/assets/{CHECKSUM_ADDRESS}/info.json
```

---

## 🛡️ Disclaimer

- **No Verification:** Listing in MeCo Assets does not imply endorsement by the MeCo or MemeCore team. 
- **Safety:** Users must do their own research (DYOR). We filter out obvious impersonation scams (e.g., fake USDT), but we do not audit token contracts.
- **Removal:** MeCo reserves the right to remove any asset that violates our policies (NSFW, scams, etc.).

## 📄 License

This repository is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.