# dupfinder

Find duplicate files in a directory tree by content hash.

## Description

`dupfinder` walks a directory, groups files by size and then by SHA-256 content
hash, and reports groups of identical files. Useful for reclaiming disk space and
cleaning up accidental copies. Zero dependencies, pure Python.

## Features

- Recursive directory scan.
- Size-first grouping to avoid hashing every file.
- SHA-256 content hashing for exact matches.
- Human-readable and JSON output.
- `--fail` exit code for CI gating.
- `--min-size` to ignore tiny files.

## Install

```bash
pip install -e .
```

Or run directly:

```bash
python -m dupfinder .
```

## Usage

```bash
# Scan current directory
dupfinder .

# Scan a specific path
dupfinder /path/to/folder

# JSON output
dupfinder . --json

# Ignore files smaller than 1 KiB
dupfinder . --min-size 1024

# Fail (exit 1) if duplicates exist
dupfinder . --fail
```

## License

MIT
