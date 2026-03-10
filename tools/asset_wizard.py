import argparse
from pathlib import Path

from PIL import Image, ImageOps

from add_token import CDN_BASE, ensure_chain_ref, ensure_token_id, target_path

MAX_FILE_SIZE_BYTES = 200 * 1024
EXPECTED_SIZE = (256, 256)


def prompt(text: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{text}{suffix}: ").strip()
    return value or default


def prompt_choice(text: str, choices: list[str], default: str) -> str:
    while True:
        value = prompt(f"{text} ({'/'.join(choices)})", default)
        if value in choices:
            return value
        print(f"Invalid choice: {value}")


def build_asset_image(source_path: Path, output_path: Path) -> None:
    with Image.open(source_path) as image:
        rgba = image.convert("RGBA")
        fitted = ImageOps.contain(rgba, EXPECTED_SIZE, Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", EXPECTED_SIZE, (0, 0, 0, 0))
        offset_x = (EXPECTED_SIZE[0] - fitted.width) // 2
        offset_y = (EXPECTED_SIZE[1] - fitted.height) // 2
        canvas.paste(fitted, (offset_x, offset_y), fitted)
        canvas.save(output_path, format="PNG", optimize=True, compress_level=9)


def make_template(output_path: Path) -> None:
    Image.new("RGBA", EXPECTED_SIZE, (0, 0, 0, 0)).save(
        output_path,
        format="PNG",
        optimize=True,
        compress_level=9,
    )


def ensure_max_file_size(path: Path) -> None:
    file_size = path.stat().st_size
    if file_size <= MAX_FILE_SIZE_BYTES:
        return
    path.unlink(missing_ok=True)
    raise ValueError(
        f"Generated PNG is too large ({file_size} bytes). Max allowed is {MAX_FILE_SIZE_BYTES} bytes."
    )


def run(args: argparse.Namespace) -> None:
    kind = args.kind
    chain_ref = args.chain_ref
    token_id = args.token_id
    source = args.source

    if not kind:
        kind = prompt_choice("Asset type", ["network", "native", "token"], "token")
    if not chain_ref:
        chain_ref = prompt("Chain reference", "eip155-4352")
    if kind == "token" and not token_id:
        token_id = prompt("Token ID")
    if not source:
        source = prompt(
            "Source image path (empty to create transparent template)",
            "",
        )

    ensure_chain_ref(chain_ref)
    if kind == "token":
        if not token_id:
            raise ValueError("token_id is required for token assets.")
        ensure_token_id(chain_ref, token_id)

    output = target_path(kind, chain_ref, token_id)
    output.parent.mkdir(parents=True, exist_ok=True)

    if output.exists() and not args.overwrite:
        overwrite = prompt_choice("Target exists. Overwrite", ["y", "n"], "n")
        if overwrite != "y":
            print("Canceled.")
            return

    if source:
        source_path = Path(source)
        if not source_path.exists() or not source_path.is_file():
            raise ValueError(f"Source image not found: {source_path.as_posix()}")
        build_asset_image(source_path, output)
        print("Asset image generated from source.")
    else:
        make_template(output)
        print("Transparent template image created.")

    ensure_max_file_size(output)

    print(f"Target path: {output.as_posix()}")
    print(f"CDN URL: {CDN_BASE}/{output.as_posix()}")
    print("Next step: commit this file and open a PR.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Interactive asset wizard for requesters.")
    parser.add_argument("--kind", choices=["network", "native", "token"], default="")
    parser.add_argument("--chain-ref", default="")
    parser.add_argument("--token-id", default="")
    parser.add_argument("--source", default="")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
