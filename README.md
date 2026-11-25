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
uv run photo-cull <shoot-dir> --dry-run   # prints the photo count, e.g. "137 photos"
```

That's the full working state today: a fresh clone with Python 3.13, uv, and exiftool reaches `--dry-run` without any extra steps.

## Usage

```bash
uv run photo-cull <shoot-dir> [flags]
```

| Flag | Description |
| --- | --- |
| `-n` / `--dry-run` | Preview the photo count (currently the only output — wiring this flag to skip work is still pending) |
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

```bash
uv run ruff check     # lint
uv run ruff format    # format
uv run ty check       # type check
```

No tests, CI, or pre-commit yet. `uv.lock` is committed — use `uv sync` rather than plain `pip install`.

## License

[Apache License 2.0](LICENSE)
