# dupefinder-cli

Find duplicate files anywhere in a directory tree by comparing content
hashes (not just filenames), and optionally clean them up.

## Why

Filenames lie. This tool groups files first by size (fast, cheap) and then
hashes only the files that share a size, so scanning large directories stays
efficient. It never deletes anything unless you explicitly pass `--delete`
or `--move`, and always supports `--dry-run` to preview first.

## Install

```bash
pip install .
```

## Usage

```bash
dupefinder-cli ~/Downloads
```

```
a1b2c3d4e5f6  (3 copies)
  /Users/me/Downloads/photo.jpg
  /Users/me/Downloads/photo (1).jpg
  /Users/me/Downloads/backup/photo.jpg

Wasted space: 8241664 bytes
```

### Cleaning up

```bash
# Preview what would be deleted (keeps the first file alphabetically per group)
dupefinder-cli ~/Downloads --delete --dry-run

# Actually delete
dupefinder-cli ~/Downloads --delete

# Or move duplicates somewhere instead of deleting
dupefinder-cli ~/Downloads --move ~/Downloads/_duplicates
```

### Options

| Flag             | Description                                              |
|------------------|------------------------------------------------------------|
| `--min-size N`   | Ignore files smaller than N bytes                          |
| `--delete`       | Delete all but one copy in each duplicate group             |
| `--move DEST`    | Move duplicates into DEST instead of deleting                |
| `--dry-run`      | Preview `--delete`/`--move` without changing anything        |
| `--json`         | Emit machine-readable JSON                                   |

## Development

```bash
pip install -e .
python -m unittest discover -s tests -v
```

## License

All rights reserved. This code is public for viewing and reference only —
no license is granted to use, copy, modify, or redistribute it. See
[LICENSE](LICENSE) for details.
