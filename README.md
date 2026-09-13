# Homebrew Tap for Sanka CLI

Install Sanka with its own Python runtime on macOS/Linux:

```bash
curl -fLsS https://raw.githubusercontent.com/sankaHQ/homebrew-cli/main/install.sh -o /tmp/sanka-install.sh
sh /tmp/sanka-install.sh
sanka doctor
```

This public repository distributes the reviewed installer alongside the matching
Homebrew formula. See [installation and recovery](docs/install.md) for uv, pip,
Windows and existing installations.

Install the tap and formula:

```bash
brew trust --formula sankahq/cli/sanka
brew tap sankaHQ/cli
brew install sankaHQ/cli/sanka
```

If you previously installed `sanka` from the older `sankaHQ/tap`
(`sankaHQ/homebrew-tap`) tap, remove that formula and untap it first:

```bash
brew uninstall sanka
brew untap sankaHQ/tap
brew trust --formula sankahq/cli/sanka
brew tap sankaHQ/cli
brew install sankaHQ/cli/sanka
```

The formula installs the published [`sanka-cli`](https://pypi.org/project/sanka-cli/)
package. The maintained publisher is `sankaHQ/sanka`, workflow `publish.yml`,
PyPI environment `pypi`; the historical `sankaHQ/sanka-cli` release assets are no
longer the source for this tap.

The formula manages Python 3.12 in its own environment. It does not use the
Python selected by a user's `pip` command. Upgrade through the same channel:

```bash
brew update
brew upgrade sankaHQ/cli/sanka
sanka --version
```

For maintainers, `scripts/prepare_release.py` verifies the exact source archive
against PyPI and the hash from the CLI publication run, then regenerates all
Python resources. Linux keyring dependencies stay under `on_linux`; cryptography
is installed on both platforms. Run from this checkout:

```bash
python3 scripts/prepare_release.py --version VERSION --expected-sha256 RELEASE_SDIST_SHA256
sh scripts/check_formula.sh
```

The check creates a separate keg-only test formula, builds it from source and
runs its version/help/auth/doctor tests. It removes its own test keg and tap at
exit. Existing Sanka installations remain intact. CI repeats this on macOS and Linux.

Each CLI PyPI publication prepares this candidate automatically, validates it,
and retains `homebrew.patch` and `release-status.json` as a GitHub Actions artifact.
The report distinguishes published PyPI, tested Homebrew candidate, and pending
Homebrew review. Open the candidate through the workspace `sanka-pr-flow` Change
Bot; it requires exact-head human approval. Never mark the Homebrew channel
complete until the formula is merged and its published version is read back.
Merge this tooling before the CLI release workflow that consumes it.
