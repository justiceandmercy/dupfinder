"""Command-line interface for dupfinder."""

import argparse
import hashlib
import json
import os
import sys


def iter_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        for fn in filenames:
            path = os.path.join(dirpath, fn)
            if os.path.isfile(path) and not os.path.islink(path):
                yield path


def file_hash(path, chunk=65536):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            block = f.read(chunk)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def find_duplicates(root, min_size=1):
    by_size = {}
    for path in iter_files(root):
        try:
            size = os.path.getsize(path)
        except OSError:
            continue
        if size < min_size:
            continue
        by_size.setdefault(size, []).append(path)

    groups = []
    for size, files in by_size.items():
        if len(files) < 2:
            continue
        by_hash = {}
        for path in files:
            try:
                digest = file_hash(path)
            except OSError:
                continue
            by_hash.setdefault(digest, []).append(path)
        for digest, paths in by_hash.items():
            if len(paths) > 1:
                groups.append({"hash": digest, "size": size, "files": sorted(paths)})

    groups.sort(key=lambda g: (-g["size"], g["hash"]))
    return groups


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="dupfinder",
        description="Find duplicate files by content hash.",
    )
    parser.add_argument("path", nargs="?", default=".", help="Directory to scan.")
    parser.add_argument(
        "--min-size", type=int, default=1, metavar="BYTES",
        help="Minimum file size in bytes to consider (default: 1).",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    parser.add_argument(
        "--fail", action="store_true",
        help="Exit with status 1 when duplicates are found (useful for CI).",
    )
    args = parser.parse_args(argv)

    root = os.path.abspath(args.path)
    if not os.path.isdir(root):
        print(f"dupfinder: not a directory: {root}", file=sys.stderr)
        return 2

    groups = find_duplicates(root, min_size=args.min_size)

    if args.json:
        print(json.dumps({"root": root, "duplicates": groups}, indent=2))
    else:
        if not groups:
            print("No duplicate files found.")
        else:
            redundant = sum(len(g["files"]) - 1 for g in groups)
            print(f"Found {len(groups)} duplicate group(s) "
                  f"({redundant} redundant file(s)):")
            for group in groups:
                print(f"\n  hash={group['hash'][:12]}  size={group['size']} bytes")
                for path in group["files"]:
                    print(f"    {os.path.relpath(path, root)}")

    if args.fail and groups:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
