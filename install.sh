#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CPPSED_DIR="$SCRIPT_DIR/CppSed"

BIN_DIR="${1:-/usr/local/bin}"
MAN_DIR="${2:-/usr/local/share/man/man1}"

# install binary
if [[ ! -d "$BIN_DIR" ]]; then
    echo "Creating $BIN_DIR ..."
    mkdir -p "$BIN_DIR"
fi

echo "Installing far -> $BIN_DIR/far"
install -m 755 "$SCRIPT_DIR/far" "$BIN_DIR/far"

if [[ ! -d "$CPPSED_DIR" ]]; then
    echo "Error: missing CppSed submodule at $CPPSED_DIR" >&2
    echo "Run: git submodule update --init --recursive" >&2
    exit 1
fi

echo "Building bundled fastsed ..."
(cd "$CPPSED_DIR" && FASTSED_IPO=ON ./b --no-install Release)

echo "Installing fastsed -> $BIN_DIR/fsed"
install -m 755 "$CPPSED_DIR/Bin/fastsed" "$BIN_DIR/fsed"

# install man page
if [[ ! -d "$MAN_DIR" ]]; then
    echo "Creating $MAN_DIR ..."
    mkdir -p "$MAN_DIR"
fi

echo "Installing man page -> $MAN_DIR/far.1"
install -m 644 "$SCRIPT_DIR/far.1" "$MAN_DIR/far.1"

echo "Installing bundled fastsed man page -> $MAN_DIR/fsed.1"
install -m 644 "$CPPSED_DIR/Man/fsed.1" "$MAN_DIR/fsed.1"

# update man db if possible
if command -v mandb &>/dev/null; then
    mandb -q 2>/dev/null || true
elif command -v makewhatis &>/dev/null; then
    makewhatis "$MAN_DIR" 2>/dev/null || true
fi

echo
echo "Installed successfully."
echo "  Run:      far --help"
echo "  Man page: man far"

# warn about deps if not found -- advisory only, not fatal
for dep in fd rg; do
    if ! command -v "$dep" &>/dev/null; then
        echo "Warning: '$dep' not found in PATH -- far requires it at runtime."
    fi
done

# warn if BIN_DIR not in PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo
    echo "Warning: '$BIN_DIR' is not in your PATH."
    echo "  Add to ~/.bashrc or ~/.zshrc:"
    echo "    export PATH=\"$BIN_DIR:\$PATH\""
fi
