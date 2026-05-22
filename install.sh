#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

BIN_DIR="${1:-/usr/local/bin}"
MAN_DIR="${2:-/usr/local/share/man/man1}"

# check dependencies
for dep in rg sed; do
    if ! command -v "$dep" &>/dev/null; then
        echo "Error: '$dep' is required but not found in PATH." >&2
        [[ "$dep" == "rg" ]] && echo "  Install via: brew install ripgrep  (macOS)" >&2
        [[ "$dep" == "rg" ]] && echo "               apt install ripgrep  (Debian/Ubuntu)" >&2
        exit 1
    fi
done

# install binary
if [[ ! -d "$BIN_DIR" ]]; then
    echo "Creating $BIN_DIR ..."
    mkdir -p "$BIN_DIR"
fi

echo "Installing far -> $BIN_DIR/far"
install -m 755 "$SCRIPT_DIR/far" "$BIN_DIR/far"

# install man page
if [[ ! -d "$MAN_DIR" ]]; then
    echo "Creating $MAN_DIR ..."
    mkdir -p "$MAN_DIR"
fi

echo "Installing man page -> $MAN_DIR/far.1"
install -m 644 "$SCRIPT_DIR/far.1" "$MAN_DIR/far.1"

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

# warn if BIN_DIR not in PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo
    echo "Warning: '$BIN_DIR' is not in your PATH."
    echo "  Add to ~/.bashrc or ~/.zshrc:"
    echo "    export PATH=\"$BIN_DIR:\$PATH\""
fi
