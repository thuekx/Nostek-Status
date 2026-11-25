#!/usr/bin/env python3
"""Public-repo hygiene check: fail when a tracked file holds data that must never be in this public repo.

Generic rules (always on): private and internal IPv4 ranges (RFC 1918, 100.64.0.0/10 CGNAT / tailnet, 169.254.0.0/16
link-local incl. cloud metadata 169.254.169.254), private keys, and common token shapes. Documentation addresses
(RFC 5737: 192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24) and loopback are allowed.

Site-specific rules stay OUT of the repo: put one regular expression per line in `.hygiene-deny` (git-ignored) to also
refuse your own host names, public ranges or domains. Usage: python3 scripts/check_public.py [repo_dir]
Prints one `FAIL <file>:<line> <rule>` per hit, then `RESULT public-hygiene PASS|FAIL files=N hits=M`.
"""
import ipaddress
import pathlib
import re
import subprocess
import sys

BLOCKED_NETS = [ipaddress.ip_network(n) for n in (
    "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "100.64.0.0/10", "169.254.0.0/16")]
IPV4 = re.compile(r"(?<![\d.])(\d{1,3}(?:\.\d{1,3}){3})(?:/\d{1,2})?(?![\d.])")
SECRETS = [
    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("aws-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("slack-token", re.compile(r"\bxox[abpr]-[A-Za-z0-9-]{10,}\b")),
    ("telegram-bot-token", re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b")),
]
SKIP_SUFFIX = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff", ".woff2", ".otf", ".ttf"}
SELF = "scripts/check_public.py"


def tracked(root: pathlib.Path) -> list[str]:
    out = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], capture_output=True, check=True).stdout
    return [p for p in out.decode().split("\0") if p]


def site_rules(root: pathlib.Path) -> list[re.Pattern[str]]:
    f = root / ".hygiene-deny"
    if not f.is_file():
        return []
    return [re.compile(line.strip()) for line in f.read_text().splitlines()
            if line.strip() and not line.startswith("#")]


def scan(root: pathlib.Path) -> tuple[int, list[str]]:
    rules = site_rules(root)
    hits: list[str] = []
    files = tracked(root)
    for rel in files:
        # this script holds the rule ranges themselves; every other tracked file is checked
        if pathlib.PurePath(rel).suffix.lower() in SKIP_SUFFIX or rel in (".hygiene-deny", SELF):
            continue
        try:
            text = (root / rel).read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(text.splitlines(), 1):
            for m in IPV4.finditer(line):
                try:
                    ip = ipaddress.ip_address(m.group(1))
                except ValueError:
                    continue
                if any(ip in net for net in BLOCKED_NETS):
                    hits.append(f"FAIL {rel}:{n} internal-address")
            for name, rx in SECRETS:
                if rx.search(line):
                    hits.append(f"FAIL {rel}:{n} {name}")
            for i, rx in enumerate(rules, 1):
                if rx.search(line):
                    hits.append(f"FAIL {rel}:{n} site-rule-{i}")
    return len(files), hits


def main() -> int:
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    n, hits = scan(root)
    for h in hits:
        print(h)
    print(f"RESULT public-hygiene {'FAIL' if hits else 'PASS'} files={n} hits={len(hits)}")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
