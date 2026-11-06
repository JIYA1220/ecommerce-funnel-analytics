"""Fail if tracked files contain credential-like patterns or forbidden file names.

Usage: python -m scripts.check_secrets
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

PATTERNS = {
    "private key block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "google api key": re.compile(r"AIza[0-9A-Za-z_\-]{35}"),
    "service account json": re.compile(r'"type"\s*:\s*"service_account"'),
    "private_key_id field": re.compile(r'"private_key_id"\s*:'),
    "oauth refresh token": re.compile(r'"refresh_token"\s*:\s*"[^"]+"'),
    "github token": re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"),
}
FORBIDDEN_NAMES = ("application_default_credentials.json", ".env")
SELF = Path(__file__).name


def scan_text(text: str) -> list[str]:
    """Return the names of patterns found in text."""
    return [name for name, rx in PATTERNS.items() if rx.search(text)]


def is_forbidden_name(path: str) -> bool:
    base = Path(path).name
    return base in FORBIDDEN_NAMES or base.startswith(".env.") and base != ".env.example"


def tracked_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        capture_output=True, text=True, check=True,
    ).stdout
    return [line for line in out.splitlines() if line]


def main() -> int:
    bad: list[str] = []
    for f in tracked_files():
        if is_forbidden_name(f):
            bad.append(f"{f}: forbidden file name")
            continue
        p = Path(f)
        if p.name == SELF or not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        bad.extend(f"{f}: {hit}" for hit in scan_text(text))
    if bad:
        print("Possible secrets found:\n" + "\n".join(bad), file=sys.stderr)
        return 1
    print("No credential patterns found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
