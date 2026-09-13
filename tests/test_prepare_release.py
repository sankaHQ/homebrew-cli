import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("prepare", ROOT / "scripts/prepare_release.py")
prepare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare)


class PreparationTest(unittest.TestCase):
    def test_linux_keyring_resources_are_preserved_and_crypto_is_common(self):
        resources = "\n".join(
            f'  resource "{name}" do\n    url "https://example.com/{name}.tar.gz"\n    sha256 "abc"\n  end\n'
            for name in ["cryptography", "cffi", "jeepney", "secretstorage", "httpx"]
        )
        formula = prepare.render("https://files.pythonhosted.org/sanka.tar.gz", "a" * 64, resources)
        linux = formula.split("  on_linux do\n", 1)[1].split("\n  end\n", 1)[0]
        self.assertIn('resource "jeepney"', linux)
        self.assertIn('resource "secretstorage"', linux)
        self.assertNotIn('resource "cryptography"', linux)
        self.assertEqual(formula.count('resource "cryptography"'), 1)
        self.assertIn('"--expected-version", version.to_s', formula)

    def test_incomplete_resource_resolution_fails(self):
        with self.assertRaises(ValueError):
            prepare.render("url", "digest", "")

    def test_wrong_release_hash_fails_before_resolution_or_writes(self):
        package = {"info": {"version": "0.2.10"}, "urls": [{
            "packagetype": "sdist", "yanked": False,
            "filename": "sanka_cli-0.2.10.tar.gz",
            "url": "https://files.pythonhosted.org/sanka_cli-0.2.10.tar.gz",
            "digests": {"sha256": "b" * 64},
        }]}
        with tempfile.TemporaryDirectory() as directory:
            formula = Path(directory) / "sanka.rb"
            formula.write_text("preserved")
            args = ["prepare", "--version", "0.2.10", "--expected-sha256", "a" * 64,
                    "--formula", str(formula)]
            with patch("sys.argv", args), patch("urllib.request.urlopen", return_value=io.BytesIO(
                json.dumps(package).encode()
            )), patch("subprocess.check_output") as brew:
                with self.assertRaises(AssertionError):
                    prepare.main()
                brew.assert_not_called()
            self.assertEqual(formula.read_text(), "preserved")


if __name__ == "__main__":
    unittest.main()
