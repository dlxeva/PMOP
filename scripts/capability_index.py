#!/usr/bin/env python3
"""Inventory explicitly selected skill roots without config, network or runtime probes."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path


def build_index(roots: list[Path]) -> dict:
    rows = []
    seen = set()
    for number, root in enumerate(roots, 1):
        if not root.is_dir():
            raise ValueError(f'root {number} is not a directory')
        root = root.resolve()
        for file in sorted(root.rglob('SKILL.md')):
            resolved = file.resolve()
            if not resolved.is_relative_to(root):
                continue  # Never follow an entry outside the explicitly selected root.
            if resolved in seen or not resolved.is_file():
                continue
            seen.add(resolved)
            content = resolved.read_bytes()
            rows.append({'root': number, 'path': str(file.relative_to(root)),
                         'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()})
    counts = {}
    for row in rows:
        counts[row['sha256']] = counts.get(row['sha256'], 0) + 1
    for row in rows:
        row['exact_duplicate'] = counts[row['sha256']] > 1
    return {'schema_version': 1, 'status': 'installed files only; runtime visibility unverified',
            'skills': rows}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, action='append', required=True,
                        help='explicit directory to inventory; repeatable')
    parser.add_argument('--format', choices=['json', 'markdown'], default='markdown')
    args = parser.parse_args()
    try:
        index = build_index(args.root)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'Cannot inventory selected roots: {exc}\n')
    if args.format == 'json':
        print(json.dumps(index, indent=2))
    else:
        print('# Capability files\n\n' + index['status'] + '\n')
        for row in index['skills']:
            print(f"- root {row['root']}: {row['path']} ({row['bytes']} bytes)")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
