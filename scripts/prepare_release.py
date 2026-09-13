#!/usr/bin/env python3
"""Prepare a reviewable Homebrew candidate from verified public PyPI bytes."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import urllib.request
from pathlib import Path


def render(url: str, digest: str, resources: str) -> str:
    blocks = re.findall(r'^  resource "([^"\n]+)" do\n.*?^  end\n', resources, re.M | re.S)
    records = re.findall(r'^  resource "[^"\n]+" do\n.*?^  end\n', resources, re.M | re.S)
    if len(blocks) != len(set(blocks)) or not {"cryptography", "jeepney", "secretstorage"} <= set(blocks):
        raise ValueError("Incomplete or duplicate Python resources")
    linux = {"jeepney", "secretstorage"}
    common = "\n".join(block for name, block in zip(blocks, records) if name not in linux)
    linux_blocks = "\n".join(
        "\n".join("  " + line for line in block.rstrip().splitlines()) + "\n"
        for name, block in zip(blocks, records) if name in linux
    )
    return f'''class Sanka < Formula
  include Language::Python::Virtualenv

  desc "CLI for hosted APIs and local migrations"
  homepage "https://sanka.com"
  url "{url}"
  sha256 "{digest}"
  license all_of: ["Apache-2.0", "AGPL-3.0-only"]

  depends_on "pkgconf" => :build
  depends_on "rust" => :build
  depends_on "libyaml"
  depends_on "openssl@3"
  depends_on "python@3.12"

  on_linux do
{linux_blocks}  end

{common}
  def install
    virtualenv_install_with_resources
  end

  test do
    ENV["XDG_CONFIG_HOME"] = testpath/"config"
    ENV["PYTHON_KEYRING_BACKEND"] = "keyring.backends.null.Keyring"
    ENV.delete("SANKA_ACCESS_TOKEN")
    assert_match "sanka, version #{{version}}", shell_output("#{{bin}}/sanka --version")
    assert_match "Inspect a Django/DRF source", shell_output("#{{bin}}/sanka scan --help")
    assert_match "No access token configured", shell_output("#{{bin}}/sanka auth status 2>&1", 1)
    if version >= Version.new("0.2.11")
      system bin/"sanka", "doctor", "--json", "--expected-version", version.to_s
    end
  end
end
'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument("--expected-sha256", required=True, help="Source archive hash from the release run")
    parser.add_argument("--formula", type=Path, default=Path("Formula/sanka.rb"))
    parser.add_argument("--resources-file", type=Path, help="Previously generated brew resources")
    parser.add_argument("--report", type=Path, default=Path("release-status.json"))
    args = parser.parse_args()
    if not re.fullmatch(r"\d+\.\d+\.\d+", args.version):
        parser.error("Use an exact stable version")
    if not re.fullmatch(r"[a-f0-9]{64}", args.expected_sha256):
        parser.error("Expected source SHA256 must be 64 lowercase hex characters")
    with urllib.request.urlopen(f"https://pypi.org/pypi/sanka-cli/{args.version}/json", timeout=30) as response:
        metadata = json.load(response)
    assert metadata["info"]["version"] == args.version
    sources = [item for item in metadata["urls"] if item["packagetype"] == "sdist"]
    assert len(sources) == 1 and not sources[0]["yanked"]
    source = sources[0]
    assert source["url"].startswith("https://files.pythonhosted.org/")
    assert source["filename"] == f"sanka_cli-{args.version}.tar.gz"
    assert source["digests"]["sha256"] == args.expected_sha256
    with urllib.request.urlopen(source["url"], timeout=60) as response:
        assert hashlib.sha256(response.read()).hexdigest() == args.expected_sha256
    resources = args.resources_file.read_text() if args.resources_file else subprocess.check_output(
        ["brew", "update-python-resources", "--print-only", f"--version={args.version}",
         "--ignore-main-package-cooldown", "--extra-packages=jeepney,secretstorage",
         "sankaHQ/cli/sanka"], text=True,
    )
    content = render(source["url"], args.expected_sha256, resources)
    args.formula.write_text(content)
    args.report.write_text(json.dumps({
        "version": args.version, "pypi": "verified", "source_sha256": args.expected_sha256,
        "homebrew": "prepared", "homebrew_validation": "pending",
        "formula_sha256": hashlib.sha256(content.encode()).hexdigest(),
        "next": "Run scripts/check_formula.sh, then open a Change Bot PR and obtain exact-head approval.",
    }, indent=2) + "\n")
    print(f"Prepared Homebrew {args.version}; validation and human review remain required.")


if __name__ == "__main__":
    main()
