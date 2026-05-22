# far

**Find and replace across files** -- a minimal CLI tool combining [`rg`](https://github.com/BurntSushi/ripgrep) and `sed` for fast, targeted in-place substitution.

```bash
far '*.cpp' 'OldClass' 'NewClass'
far '*.cpp' 'OldClass' 'NewClass' ./src
far -n '*.h' 'TODO' 'FIXME'        # dry run
far -y -b '*.txt' 'foo' 'bar'      # skip prompt, write backups
```

## Why

`rg` is the fastest way to find files containing a string. `sed` is the
standard tool for in-place substitution. `far` wires them together with
a confirmation step, dry-run mode, and optional backups so you don't
shoot yourself in the foot.

## Dependencies

| Tool | Purpose |
|------|---------|
| [`rg`](https://github.com/BurntSushi/ripgrep) | Fast parallel file search |
| `sed` | In-place substitution |
| `bash` | Runtime |

`sed` and `bash` are standard on all POSIX systems. Install `rg` via your package manager:

```bash
# macOS
brew install ripgrep

# Debian / Ubuntu
apt install ripgrep

# Arch
pacman -S ripgrep

# Cargo
cargo install ripgrep
```

## Installation

```bash
git clone https://github.com/cschladetsch/far.git
cd far
sudo ./install.sh
```

Custom install paths:

```bash
sudo ./install.sh /usr/local/bin /usr/local/share/man/man1
```

The installer will:
- Check that `rg` is present
- Copy `far` to the bin directory
- Install the man page
- Update the man database
- Warn if the bin directory is not in `PATH`

## Usage

```
far [OPTIONS] <glob> <find> <replace> [root]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `glob` | Filename glob pattern, e.g. `*.cpp` |
| `find` | Text or regex to search for |
| `replace` | Replacement string |
| `root` | Directory to search under (default: `.`) |

### Options

| Flag | Description |
|------|-------------|
| `-y` | Skip the confirmation prompt |
| `-n` | Dry run -- list matching files, make no changes |
| `-b` | Write `.bak` backups before modifying |
| `-h` | Show help |

### Exit codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Invalid arguments |
| `2` | No matching files found |
| `3` | User aborted at confirmation prompt |

## Examples

Replace across all C++ source files in the current tree:

```bash
far '*.cpp' 'OldClass' 'NewClass'
```

Restrict to a subdirectory:

```bash
far '*.cpp' 'OldClass' 'NewClass' ./src
```

Preview without modifying anything:

```bash
far -n '*.h' 'OldClass' 'NewClass'
```

Apply immediately with no prompt, keeping backups:

```bash
far -y -b '*.cpp' 'OldClass' 'NewClass'
```

Use in a CI pipeline (non-interactive, fails loudly):

```bash
far -y '*.md' 'v1\.0\.0' 'v1.1.0' ./docs
```

## Caveats

- `find` and `replace` are passed directly to `sed`. Strings containing `/` or `&` must be escaped.
- Without `-b` there is no undo. Use `-n` first when in doubt.
- `rg` respects `.gitignore` by default, so files excluded from version control are skipped.

## Man page

```bash
man far
```

## License

MIT -- see [LICENSE](LICENSE).
