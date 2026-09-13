#!/usr/bin/env python3
"""Read back live PyPI/Homebrew channel synchronization. Exit 2 means pending."""
import json
import re
import urllib.request


def main():
    with urllib.request.urlopen("https://pypi.org/pypi/sanka-cli/json", timeout=30) as response:
        package = json.load(response)
    with urllib.request.urlopen(
        "https://raw.githubusercontent.com/sankaHQ/homebrew-cli/main/Formula/sanka.rb", timeout=30
    ) as response:
        formula = response.read().decode()
    match = re.search(r'sanka_cli-(\d+\.\d+\.\d+)\.tar\.gz"\n  sha256 "([a-f0-9]{64})"', formula)
    if not match:
        raise ValueError("Published formula has no recognizable version and source digest")
    version, digest = match.groups()
    sources = [item for item in package["urls"] if item["packagetype"] == "sdist"]
    synced = (version == package["info"]["version"] and len(sources) == 1
              and digest == sources[0]["digests"]["sha256"])
    print(json.dumps({"pypi_version": package["info"]["version"], "homebrew_version": version,
                      "homebrew_source_sha256": digest,
                      "status": "synchronized" if synced else "homebrew_update_pending"}, indent=2))
    raise SystemExit(0 if synced else 2)


if __name__ == "__main__":
    main()
