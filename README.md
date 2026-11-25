# PhotoCull

A Python CLI that culls photo shoots — ingest a folder, build a manifest, and (eventually) keep only the keepers.

## What This Does

PhotoCull scans a photo shoot folder recursively, reads each image's EXIF data via exiftool, and builds a photo manifest (path, capture time, exposure, ISO, aperture, file type). It is the first stage of a planned pipeline that will score, cluster, and export a clean folder of keeper photos — currently **only the ingest stage is implemented**.

## Getting Started

Prerequisites:

- **Python 3.13** (only — the project is pinned to it) with [uv](https://docs.astral.sh/uv/)
- **exiftool** — a system binary, not a pip dependency:
  - Arch: `sudo pacman -S perl-image-exiftool`
  - Debian/Ubuntu: `sudo apt install libimage-exiftool-perl`
  - macOS: `brew install exiftool`
  - Verify with `exiftool -ver`

Install and run:

```bash
git clone git@github.com:EquilOne/photo-cull.git
cd PhotoCull
uv sync                              # creates .venv and installs the project
uv run photo-cull <shoot-dir> --dry-run   # prints the photo count and a folder-structure summary
```

That's the full working state today: ingest with its `--dry-run` summary is the only stage — a fresh clone with Python 3.13, uv, and exiftool reaches it without any extra steps.

## Usage

```bash
uv run photo-cull <shoot-dir> [flags]
```

| Flag | Description |
| --- | --- |
| `-n` / `--dry-run` | Print the total photo count plus a folder-structure summary: one line per directory (tree-indented) with its image count and capture date, `earliest → latest` date range, `(+N undated)` for files missing EXIF dates, or `no dates` when a directory has none |
| `-V` / `--verbose` | Print the full manifest, one entry per photo (file type, capture time, exposure, ISO, aperture) |
| `-T` / `--threshold` | Scoring threshold (float, default `0.75`) — kept for the not-yet-implemented scoring stage |
| `-x` / `--exiftool` | Path to the exiftool binary, overriding automatic detection |

Exiftool is located in this order: the `--exiftool` flag, the `PHOTO_CULL_EXIFTOOL` environment variable, the bundled copy (PyInstaller builds), then `PATH`. If none is found, PhotoCull prints an install hint to stderr and exits with code 1.

## Supported Formats

- **RAW**: `.arw` `.cr2` `.cr3` `.nef` `.orf` `.rw2` `.dng` `.raf` `.srw` `.pef` `.araw`
- **JPEG**: `.jpg` `.jpeg` `.jpe` `.jfif`
- **Other images** (parsed, tagged `other`): png, webp, tif/tiff, bmp, heic/heif, avif, psd, gif, jxl, exr, hdr, tga, svg, ico, xcf

## Status & Roadmap

Implemented:

- [x] Ingest — recursive folder scan and EXIF manifest

Planned, in order:

- [ ] Sharpness / exposure scoring
- [ ] Burst and bracket clustering
- [ ] Export of a clean keepers folder
- [ ] LLM / decision-model escalation for borderline picks

## How It Works

Each scan shells out to exiftool once as a batch JSON call (`-j -n -config "" -m`), and each result becomes a `ManifestEntry` dataclass. Missing EXIF fields are `None` (not placeholders), capture times are normalized to ISO 8601, and `file_type` is derived from the file extension.

## Development

Requirements: Python 3.13 only (`.python-version` is pinned) with [uv](https://docs.astral.sh/uv/), plus exiftool (see [Getting Started](#getting-started)). `uv.lock` is committed — use `uv sync`, not plain `pip install`:

```bash
uv sync                      # creates .venv and installs the project + dev group
uv run photo-cull <shoot-dir> --dry-run
```

Linting and type checking (dev group):

```bash
uv run ruff check            # lint
uv run ruff format           # format
uv run ty check              # type check
```

Ruff uses `select = ["E", "F", "I", "UP", "B", "SIM"]` with a line length of 88. Runtime `dependencies` must stay empty — dev tooling lives in `[dependency-groups] dev` only.

No tests, CI, or pre-commit exist yet. There is an empty `tests/` directory, but pytest is not set up — a contributor wanting to test would need to add it to `pyproject.toml` first.

`ty` is pre-1.0 and pinned (`>=0.0.109`) and ships breaking config changes often. Upgrade it deliberately with `uv lock --upgrade-package ty` — never a blanket `uv lock --upgrade`.

Project layout (`src/photo_cull/`):

| Module | Purpose |
| --- | --- |
| `exiftool.py` | Binary wrapper — the only module that shells out |
| `ingest.py` | Manifest building, `ManifestEntry` dataclass |
| `cli.py` | Argparse and `main()` |
| `constants.py` | Extension lists and `file_type` derivation |

Note for contributors: the console script maps `photo-cull = "photo_cull:main"`, and `__init__.py` re-exports `main` from `.cli` (its `__all__` satisfies ruff F401). Never point the script at `photo_cull.cli:main`.

## License

[Apache License 2.0](LICENSE)
