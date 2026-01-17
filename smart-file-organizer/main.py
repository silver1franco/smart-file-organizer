#!/usr/bin/env python3
"""Smart file organizer with duplicate detection."""

import argparse
import hashlib
import shutil
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

CATEGORIES = {
    'images': {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.heic', '.raw'},
    'documents': {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.xls', '.xlsx', '.ppt', '.pptx', '.csv', '.md'},
    'videos': {'.mp4', '.mkv', '.avi', '.mov', '.webm'},
    'audio': {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'},
    'archives': {'.zip', '.rar', '.7z', '.tar', '.gz'},
    'code': {'.py', '.js', '.ts', '.html', '.css', '.java', '.cpp', '.c', '.go', '.rs', '.sh', '.json'},
}

EXT_MAP = {ext: cat for cat, exts in CATEGORIES.items() for ext in exts}


def file_hash(path: Path) -> str | None:
    h = hashlib.md5()
    try:
        with open(path, 'rb') as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def get_mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def find_duplicates(files: list[Path]) -> list[Path]:
    """Returns list of duplicate files to move (keeps oldest of each group)."""
    by_size: dict[int, list[Path]] = defaultdict(list)
    for f in files:
        try:
            if (sz := f.stat().st_size) > 0:
                by_size[sz].append(f)
        except OSError:
            continue

    by_hash: dict[str, list[Path]] = defaultdict(list)
    for candidates in by_size.values():
        if len(candidates) < 2:
            continue
        for f in candidates:
            if h := file_hash(f):
                by_hash[h].append(f)

    to_move = []
    for paths in by_hash.values():
        if len(paths) > 1:
            paths.sort(key=get_mtime)
            print(f"  Keeping: {paths[0].name}")
            to_move.extend(paths[1:])
    return to_move


def move_file(src: Path, dest_dir: Path, dry_run: bool) -> bool:
    if not src.exists():
        return False

    dest = dest_dir / src.name
    if dest.exists() and dest.resolve() == src.resolve():
        return False

    # handle name conflicts
    if dest.exists():
        n = 1
        while dest.exists():
            dest = dest_dir / f"{src.stem}_{n}{src.suffix}"
            n += 1

    if dry_run:
        print(f"  [DRY RUN] {src} -> {dest}")
        return True

    dest_dir.mkdir(parents=True, exist_ok=True)
    try:
        shutil.move(src, dest)
        print(f"  {src.name} -> {dest.parent.name}/")
        return True
    except (OSError, shutil.Error) as e:
        print(f"  Error: {src.name} - {e}")
        return False


def main():
    p = argparse.ArgumentParser(
        description='Organize files by type, date, or find duplicates',
        epilog='Example: %(prog)s ~/Downloads --by-type --dry-run'
    )
    p.add_argument('source', type=Path)
    p.add_argument('-o', '--output', type=Path, help='output directory (default: in place)')
    p.add_argument('-n', '--dry-run', action='store_true', help='preview without moving')
    p.add_argument('-r', '--recursive', action='store_true', help='include subdirectories')
    p.add_argument('--by-type', action='store_true', help='sort by file type')
    p.add_argument('--by-date', action='store_true', help='sort by modification date')
    p.add_argument('--duplicates', action='store_true', help='find and isolate duplicates')
    args = p.parse_args()

    source = args.source.expanduser().resolve()
    if not source.is_dir():
        print(f"Error: '{args.source}' is not a valid directory")
        return 1

    if not (args.by_type or args.by_date or args.duplicates):
        p.print_help()
        print("\nError: specify at least one action (--by-type, --by-date, or --duplicates)")
        return 1

    out = args.output.expanduser().resolve() if args.output else source
    dry = args.dry_run

    print(f"Source: {source}")
    print(f"Output: {out}")
    if dry:
        print("Mode: DRY RUN")

    if args.recursive:
        print("Note: recursive mode flattens directory structure")

    pattern = source.rglob('*') if args.recursive else source.iterdir()
    files = [f for f in pattern if f.is_file() and not f.name.startswith('.')]
    moved = 0
    seen: set[Path] = set()

    if args.duplicates:
        print(f"\n[Scanning {len(files)} files for duplicates]")
        dupes = find_duplicates(files)
        if dupes:
            print(f"Found {len(dupes)} duplicate(s)\n")
            for f in dupes:
                if move_file(f, out / '_duplicates', dry):
                    moved += 1
                    seen.add(f)
        else:
            print("No duplicates found.")

    if args.by_type:
        print("\n[Organizing by type]")
        for f in files:
            if f in seen:
                continue
            cat = EXT_MAP.get(f.suffix.lower(), 'other')
            if move_file(f, out / cat, dry):
                moved += 1
                seen.add(f)

    if args.by_date:
        print("\n[Organizing by date]")
        now = datetime.now()
        for f in files:
            if f in seen:
                continue
            try:
                age = now - datetime.fromtimestamp(f.stat().st_mtime)
            except OSError:
                cat = 'unknown'
            else:
                if age < timedelta(days=7):
                    cat = 'this_week'
                elif age < timedelta(days=30):
                    cat = 'this_month'
                else:
                    cat = 'older'
            if move_file(f, out / cat, dry):
                moved += 1

    print(f"\n{'Would move' if dry else 'Moved'} {moved} file(s).")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
