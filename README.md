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

This tap publishes the generated `sanka.rb` formula from the
[`sankaHQ/sanka-cli`](https://github.com/sankaHQ/sanka-cli) release process.
