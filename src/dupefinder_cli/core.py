"""Duplicate-file detection engine.

Strategy: group files by size first (cheap), then hash only within groups
that share a size (skips hashing unique-sized files entirely), which keeps
large directory scans fast.
"""
from __future__ import annotations

import hashlib
import os
from collections import defaultdict
from typing import Dict, Iterable, List


def iter_files(root: str, min_size: int = 0) -> Iterable[str]:
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            path = os.path.join(dirpath, name)
            try:
                if os.path.getsize(path) >= min_size:
                    yield path
            except OSError:
                continue


def _hash_file(path: str, chunk_size: int = 65536) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_duplicates(root: str, min_size: int = 0) -> Dict[str, List[str]]:
    """Return {sha256: [paths]} for every group of 2+ identical files."""
    by_size: Dict[int, List[str]] = defaultdict(list)
    for path in iter_files(root, min_size=min_size):
        try:
            size = os.path.getsize(path)
        except OSError:
            continue
        by_size[size].append(path)

    by_hash: Dict[str, List[str]] = defaultdict(list)
    for paths in by_size.values():
        if len(paths) < 2:
            continue
        for path in paths:
            try:
                h = _hash_file(path)
            except OSError:
                continue
            by_hash[h].append(path)

    return {h: sorted(paths) for h, paths in by_hash.items() if len(paths) > 1}


def wasted_bytes(duplicates: Dict[str, List[str]]) -> int:
    total = 0
    for paths in duplicates.values():
        if not paths:
            continue
        try:
            size = os.path.getsize(paths[0])
        except OSError:
            continue
        total += size * (len(paths) - 1)
    return total
