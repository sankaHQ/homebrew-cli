#!/bin/sh
# Build and test a candidate in a task-owned keg without replacing installed Sanka.
set -eu
brew_bin=$(command -v brew)
if [ "$(uname -s)" = Darwin ] && [ "$("$brew_bin" --prefix)" = /opt/homebrew ]; then
    brew() { /usr/bin/arch -arm64 "$brew_bin" "$@"; }
else
    brew() { "$brew_bin" "$@"; }
fi
formula=${1:-Formula/sanka.rb}
tap="sanka-verification/cli-$$"
name="sanka-verification-$$"
brew tap-new --no-git "$tap" >/dev/null
tap_path=$(brew --repository "$tap")
cleanup() {
    brew uninstall --force "$tap/$name" >/dev/null 2>&1 || true
    brew untap "$tap" >/dev/null
}
trap cleanup EXIT
trap 'exit 1' HUP INT TERM
# Class and keg-only metadata are the only candidate changes. Dependencies,
# package bytes, install method and tests are identical to the reviewable formula.
sed -e "s/class Sanka < Formula/class SankaVerification$$ < Formula/" \
    -e '/include Language::Python::Virtualenv/a\
  keg_only "Isolated Sanka installation verification"\
' "$formula" > "$tap_path/Formula/$name.rb"
export HOMEBREW_NO_AUTO_UPDATE=1 HOMEBREW_NO_INSTALL_CLEANUP=1
brew install --build-from-source "$tap/$name"
brew test "$tap/$name"
"$(brew --prefix "$tap/$name")/bin/sanka" --version
