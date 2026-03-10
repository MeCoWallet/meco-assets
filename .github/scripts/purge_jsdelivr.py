import argparse
import sys
import urllib.error
import urllib.parse
import urllib.request


def purge_url(repo: str, ref: str, path: str) -> tuple[str, bool, str]:
    encoded_path = urllib.parse.quote(path)
    purge_endpoint = f"https://purge.jsdelivr.net/gh/{repo}@{ref}/{encoded_path}"

    request = urllib.request.Request(purge_endpoint, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            status = response.getcode()
            if 200 <= status < 300:
                return purge_endpoint, True, f"status={status}"
            return purge_endpoint, False, f"status={status}"
    except urllib.error.HTTPError as error:
        return purge_endpoint, False, f"http_error={error.code}"
    except urllib.error.URLError as error:
        return purge_endpoint, False, f"url_error={error.reason}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Purge changed asset paths from jsDelivr cache.")
    parser.add_argument("--files", default="", help="Space-separated changed file paths")
    parser.add_argument("--repo", default="MeCoWallet/meco-assets", help="GitHub repo owner/name")
    parser.add_argument("--ref", default="main", help="Git ref used in CDN URLs")
    args = parser.parse_args()

    changed = args.files.split()
    repo = args.repo
    ref = args.ref

    paths = sorted({p for p in changed if p.startswith("assets/")})
    if not paths:
        print("No changed asset files to purge.")
        return

    failures: list[str] = []
    for path in paths:
        endpoint, ok, detail = purge_url(repo, ref, path)
        prefix = "✅" if ok else "❌"
        print(f"{prefix} {endpoint} ({detail})")
        if not ok:
            failures.append(path)

    if failures:
        print(f"Failed to purge {len(failures)} path(s).")
        sys.exit(1)

    print(f"Purged {len(paths)} jsDelivr path(s).")


if __name__ == "__main__":
    main()
