import argparse
import os
import re
import sys
from pathlib import Path

from PIL import Image

MAX_FILE_SIZE_BYTES = 200 * 1024
EXPECTED_SIZE = (256, 256)
CHAIN_REF_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)+$")
TOKEN_ID_GENERIC_RE = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
TOKEN_ID_RULES: dict[str, re.Pattern[str]] = {
    "eip155": re.compile(r"^0x[a-f0-9]{40}$"),
    "solana": re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$"),
    "aptos": re.compile(r"^0x[a-f0-9]{1,64}$"),
    "sui": re.compile(r"^0x[a-f0-9]{1,64}$"),
    "tron": re.compile(r"^T[1-9A-HJ-NP-Za-km-z]{33}$"),
}


def fail(message: str) -> None:
    print(f"❌ {message}")
    sys.exit(1)


def is_chain_ref(value: str) -> bool:
    return bool(CHAIN_REF_RE.fullmatch(value))


def namespace_from_chain_ref(chain_ref: str) -> str:
    return chain_ref.split("-", maxsplit=1)[0]


def validate_token_id(chain_ref: str, token_id: str, path: str) -> None:
    namespace = namespace_from_chain_ref(chain_ref)
    rule = TOKEN_ID_RULES.get(namespace, TOKEN_ID_GENERIC_RE)
    if not rule.fullmatch(token_id):
        if namespace == "eip155":
            fail(f"Invalid eip155 token ID. Expected lowercase EVM address: {path}")
        if namespace == "solana":
            fail(f"Invalid solana token ID. Expected base58 mint address: {path}")
        if namespace in {"aptos", "sui"}:
            fail(f"Invalid {namespace} token ID. Expected lowercase hex with 0x prefix: {path}")
        if namespace == "tron":
            fail(f"Invalid tron token ID. Expected base58 account format: {path}")
        fail(f"Invalid token ID for chain '{chain_ref}': {path}")


def validate_png(path: Path) -> None:
    if path.suffix != ".png":
        fail(f"Only PNG files are allowed: {path.as_posix()}")

    file_size = path.stat().st_size
    if file_size > MAX_FILE_SIZE_BYTES:
        fail(
            f"File too large ({file_size} bytes): {path.as_posix()} "
            f"(max {MAX_FILE_SIZE_BYTES} bytes)"
        )

    try:
        with Image.open(path) as img:
            if img.format != "PNG":
                fail(f"Image is not PNG: {path.as_posix()}")

            if img.size != EXPECTED_SIZE:
                fail(
                    f"Invalid image size {img.size} for {path.as_posix()}. "
                    f"Expected {EXPECTED_SIZE}."
                )

            if img.width != img.height:
                fail(f"Image must be square: {path.as_posix()}")

    except OSError as error:
        fail(f"Cannot open image {path.as_posix()}: {error}")


def validate_path(path: Path) -> None:
    rel = path.as_posix()
    parts = rel.split("/")

    if parts[0] != "assets":
        fail(f"Invalid root path (must start with assets/): {rel}")

    if len(parts) >= 2 and parts[1].startswith("."):
        return

    if len(parts) == 3 and parts[1] == "networks":
        filename = parts[2]
        if not filename.endswith(".png"):
            fail(f"Network icon must be PNG: {rel}")
        chain_ref = filename[:-4]
        if not is_chain_ref(chain_ref):
            fail(f"Invalid network chain reference filename: {rel}")
        validate_png(path)
        return

    if len(parts) == 4 and parts[1] == "tokens" and parts[2] == "native":
        filename = parts[3]
        if not filename.endswith(".png"):
            fail(f"Native token icon must be PNG: {rel}")
        chain_ref = filename[:-4]
        if not is_chain_ref(chain_ref):
            fail(f"Invalid native token chain reference filename: {rel}")
        validate_png(path)
        return

    if len(parts) == 4 and parts[1] == "tokens":
        chain_ref = parts[2]
        filename = parts[3]
        if not is_chain_ref(chain_ref):
            fail(f"Invalid token chain reference directory: {rel}")
        if not filename.endswith(".png"):
            fail(f"Token icon must be PNG: {rel}")
        token_id = filename[:-4]
        validate_token_id(chain_ref, token_id, rel)
        validate_png(path)
        return

    if len(parts) == 3 and parts[1] == "fallback" and parts[2] == "default-token.png":
        validate_png(path)
        return

    if path.name.startswith("."):
        return

    fail(f"Invalid asset path structure: {rel}")


def collect_paths(args: argparse.Namespace) -> list[Path]:
    if args.files:
        raw_paths = args.files.split()
        unique = sorted(set(raw_paths))
        return [Path(p) for p in unique if p.startswith("assets/") and Path(p).exists()]

    assets_root = Path("assets")
    if not assets_root.exists():
        return []

    collected: list[Path] = []
    for path in assets_root.rglob("*"):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue
        collected.append(path)
    return sorted(collected)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate wallet asset repository files.")
    parser.add_argument(
        "--files",
        default="",
        help="Space-separated changed file paths. If omitted, validates all files under assets/.",
    )
    args = parser.parse_args()

    paths = collect_paths(args)
    if not paths:
        print("No asset files to validate.")
        return

    for path in paths:
        validate_path(path)

    print(f"✅ Validation passed for {len(paths)} asset file(s).")


if __name__ == "__main__":
    main()
