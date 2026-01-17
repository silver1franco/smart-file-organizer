# File Organizer

A command-line tool that automatically sorts messy directories by file type or date, and detects duplicate files using MD5 hashing. Supports dry-run mode to preview changes before committing.

## Requirements

- Python 3.10+
- No external dependencies (standard library only)

## Installation

```bash
git clone https://github.com/yourusername/file-organizer.git
cd file-organizer
chmod +x main.py  # Unix/macOS
```

## Usage

```bash
python main.py <directory> [options]
```

### Options

| Flag | Description |
|------|-------------|
| `-n, --dry-run` | Preview changes without moving files |
| `-r, --recursive` | Include files in subdirectories |
| `-o, --output DIR` | Specify output directory (default: organize in place) |
| `--by-type` | Sort files into folders by type (images, documents, videos, etc.) |
| `--by-date` | Sort files into folders by date (this_week, this_month, older) |
| `--duplicates` | Find duplicates and move copies to `_duplicates/` |

### Examples

Preview what would happen without moving anything:
```bash
python main.py ~/Downloads --by-type --dry-run
```

Organize downloads by file type:
```bash
python main.py ~/Downloads --by-type
```

Sort documents by when they were last modified:
```bash
python main.py ~/Documents --by-date
```

Find and isolate duplicate files:
```bash
python main.py ~/Pictures --duplicates -r
```

Organize to a different directory:
```bash
python main.py ~/Downloads --by-type -o ~/Sorted
```

Combine operations:
```bash
python main.py ~/Downloads --duplicates --by-type
```

## File Categories

Files are sorted into these folders when using `--by-type`:

| Folder | Extensions |
|--------|------------|
| images | jpg, jpeg, png, gif, bmp, webp, svg, ico, tiff, raw, heic |
| documents | pdf, doc, docx, txt, rtf, odt, xls, xlsx, ppt, pptx, csv, md |
| videos | mp4, mkv, avi, mov, wmv, flv, webm, m4v, mpeg |
| audio | mp3, wav, flac, aac, ogg, wma, m4a, opus |
| archives | zip, rar, 7z, tar, gz, bz2, xz, tgz |
| code | py, js, ts, html, css, java, cpp, c, h, go, rs, rb, php, sh |
| executables | exe, msi, dmg, app, deb, rpm, pkg |
| other | everything else |

## Date Ranges

When using `--by-date`, files are sorted based on last modified time:

- **this_week** — modified within the last 7 days
- **this_month** — modified within the last 30 days
- **older** — everything else

## Duplicate Detection

The `--duplicates` flag uses a two-pass approach:

1. Groups files by size (fast filter)
2. Computes MD5 hash only for files with matching sizes

The oldest file (by modification time) is kept, and duplicates are moved to `_duplicates/`. Empty files are ignored.

## Notes

- Hidden files (starting with `.`) are skipped
- Name collisions are handled by appending `_1`, `_2`, etc.
- Operations run in order: duplicates → type → date
- Recursive mode flattens subdirectories into the output folder

## License

MIT
