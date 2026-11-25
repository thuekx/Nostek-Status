"""Tests for scripts/check_public.py: planted data must FAIL, documentation examples must PASS."""
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_public.py"


def run_on(files: dict[str, str], deny: str | None = None) -> subprocess.CompletedProcess[str]:
    d = pathlib.Path(tempfile.mkdtemp())
    subprocess.run(["git", "init", "-q", str(d)], check=True)
    for name, body in files.items():
        p = d / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
    if deny is not None:
        (d / ".hygiene-deny").write_text(deny)
    subprocess.run(["git", "-C", str(d), "add", "-A"], check=True)
    return subprocess.run([sys.executable, "-I", str(SCRIPT), str(d)], capture_output=True, text=True)


class CheckPublic(unittest.TestCase):
    def test_docs_addresses_pass(self) -> None:
        r = run_on({"README.md": "probe https://app.example.com 203.0.113.10 192.0.2.1 127.0.0.1\n"})
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("RESULT public-hygiene PASS", r.stdout)

    def test_private_and_tailnet_fail(self) -> None:
        # planted values are built at run time so this file itself stays clean
        for parts in ((10, 1, 2, 3), (172, 20, 0, 5), (192, 168, 1, 10), (100, 100, 1, 1), (169, 254, 169, 254)):
            ip = ".".join(str(p) for p in parts)
            with self.subTest(ip=ip):
                r = run_on({"conf.yaml": f"target: {ip}\n"})
                self.assertEqual(r.returncode, 1, r.stdout)
                self.assertIn("FAIL conf.yaml:1 internal-address", r.stdout)

    def test_private_key_fails(self) -> None:
        r = run_on({"k.txt": "-----BEGIN " + "OPENSSH PRIVATE " + "KEY-----\n"})
        self.assertEqual(r.returncode, 1)
        self.assertIn("private-key", r.stdout)

    def test_site_rule_from_untracked_file(self) -> None:
        r = run_on({"a.md": "host intra.example.net\n"}, deny="intra\\.example\\.net\n")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("site-rule-1", r.stdout)

    def test_repo_itself_is_clean(self) -> None:
        r = subprocess.run([sys.executable, "-I", str(SCRIPT), str(ROOT)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)


if __name__ == "__main__":
    unittest.main()
