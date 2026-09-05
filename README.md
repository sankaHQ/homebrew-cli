# Homebrew Tap for Sanka CLI

Install the tap and formula:

```bash
brew tap sankaHQ/cli
brew install sankaHQ/cli/sanka
```

If you previously installed `sanka` from the older `sankaHQ/tap`
(`sankaHQ/homebrew-tap`) tap, remove that formula and untap it first:

```bash
brew uninstall sanka
brew untap sankaHQ/tap
brew tap sankaHQ/cli
brew install sankaHQ/cli/sanka
```

The formula installs the published [`sanka-cli`](https://pypi.org/project/sanka-cli/)
package. The maintained publisher is `sankaHQ/sanka`, workflow `publish.yml`,
PyPI environment `pypi`; the historical `sankaHQ/sanka-cli` release assets are no
longer the source for this tap.

For an update, verify the version's PyPI provenance and artifact checksum, update
`Formula/sanka.rb`, and regenerate its Python resources with
`brew update-python-resources sankaHQ/cli/sanka`. Preserve the Linux-only keyring
resources when generating on macOS. Run `brew install --build-from-source` and
`brew test` against the candidate before merging it.
