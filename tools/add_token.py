import argparse
import re
from pathlib import Path

from PIL import Image


CHAIN_REF_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)+$")
TOKEN_ID_GENERIC_RE = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
TOKEN_ID_RULES: dict[str, re.Pattern[str]] = {
    "eip155": re.compile(r"^0x[a-f0-9]{40}$"),
    "solana": re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$"),
    "aptos": re.compile(r"^0x[a-f0-9]{1,64}$"),
    "sui": re.compile(r"^0x[a-f0-9]{1,64}$"),
    "tron": re.compile(r"^T[1-9A-HJ-NP-Za-km-z]{33}$"),
}
CDN_BASE = "https://cdn.jsdelivr.net/gh/MeCoWallet/meco-assets@main"


def ensure_chain_ref(chain_ref: str) -> None:
    if not CHAIN_REF_RE.fullmatch(chain_ref):
        raise ValueError(
            "Invalid chainRef. Use lowercase namespace format like eip155-1 or solana-mainnet."
        )


def namespace_from_chain_ref(chain_ref: str) -> str:
    return chain_ref.split("-", maxsplit=1)[0]


def ensure_token_id(chain_ref: str, token_id: str) -> None:
    namespace = namespace_from_chain_ref(chain_ref)
    rule = TOKEN_ID_RULES.get(namespace, TOKEN_ID_GENERIC_RE)
    if not rule.fullmatch(token_id):
        raise ValueError(
            f"Invalid tokenId '{token_id}' for chainRef '{chain_ref}'. "
            "Check README token ID rules."
        )


def target_path(kind: str, chain_ref: str, token_id: str) -> Path:
    if kind == "network":
        return Path("assets") / "networks" / f"{chain_ref}.png"
    if kind == "native":
        return Path("assets") / "tokens" / "native" / f"{chain_ref}.png"
    return Path("assets") / "tokens" / chain_ref / f"{token_id}.png"


def write_template_png(path: Path, overwrite: bool) -> bool:
    if path.exists() and not overwrite:
        return False
    image = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    image.save(path, format="PNG", optimize=True)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Show deterministic multichain wallet asset path.")
    parser.add_argument(
        "kind",
        choices=["network", "native", "token"],
        help="Asset type",
    )
    parser.add_argument("chain_ref", help="Chain reference (for example eip155-1, solana-mainnet)")
    parser.add_argument("token_id", nargs="?", default="", help="Token ID for token icons")
    parser.add_argument(
        "--init-template",
        action="store_true",
        help="Create a transparent 256x256 PNG template at target path.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacing existing file when used with --init-template.",
    )
    args = parser.parse_args()

    ensure_chain_ref(args.chain_ref)
    if args.kind == "token":
        if not args.token_id:
            raise ValueError("token_id is required when kind is 'token'.")
        ensure_token_id(args.chain_ref, args.token_id)

    path = target_path(args.kind, args.chain_ref, args.token_id)
    path.parent.mkdir(parents=True, exist_ok=True)

    if args.overwrite and not args.init_template:
        raise ValueError("--overwrite requires --init-template.")

    if args.init_template:
        created = write_template_png(path, overwrite=args.overwrite)
        if created:
            print("Template image created.")
        else:
            print("Template image not created because file already exists. Use --overwrite to replace.")

    print(f"Target path: {path.as_posix()}")
    print(f"CDN URL: {CDN_BASE}/{path.as_posix()}")
    print("Add a PNG file (256x256, transparent, <=200KB) at this path.")


if __name__ == "__main__":
    main()
