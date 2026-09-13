"""The public installer and Homebrew formula must select the same release."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class InstallerVersionTest(unittest.TestCase):
    def test_installer_matches_formula(self):
        installer = re.search(r"^    version=(\d+\.\d+\.\d+)$", (ROOT / "install.sh").read_text(), re.M)
        formula = re.search(r"/sanka_cli-(\d+\.\d+\.\d+)\.tar\.gz", (ROOT / "Formula/sanka.rb").read_text())
        self.assertIsNotNone(installer)
        self.assertIsNotNone(formula)
        self.assertEqual(installer[1], formula[1])


if __name__ == "__main__":
    unittest.main()
