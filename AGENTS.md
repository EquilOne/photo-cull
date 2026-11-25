# AGENTS.md — PhotoCull

Python CLI `photo-cull` — photo culling with LLM and decision-model escalation. Early stage: only the ingest stage (folder scan + exiftool manifest) is implemented. `README.md` documents usage — keep it in sync, don't duplicate its content here.

## Toolchain & Commands

- uv-managed, backend `uv_build`, **Python 3.13 only** (`.python-version` pinned; `requires-python = ">=3.13"`). Src layout: `src/photo_cull/`. `uv.lock` committed; `.venv/`, `__pycache__/`, `.ruff_cache/` gitignored.
- Dev tooling (in `[dependency-groups] dev`; runtime `dependencies = []` must stay empty): ruff 0.17.6 (select E, F, I, UP, B, SIM; line-length 88), ty 0.0.109. No CI, no pre-commit.

```bash
uv sync                  # create .venv (gitignored), install project
uv run photo-cull        # run the CLI
uv run ruff check [--fix] / uv run ruff format
uv run ty check
```

- **pytest does NOT exist** — no tests, no test config, no `tests/` dir. Do not run or invent pytest; set it up in `pyproject.toml` first if asked to test.
- **`test_shoots/` is a local fixture dir, gitignored** (real JPG/RAW/XMP test files). Use it for manual runs: `uv run photo-cull test_shoots -n` — never commit or reference it as if tracked.
- **ty is pre-1.0 and pinned** (`>=0.0.109`), ships breaking config changes often. Upgrade deliberately: `uv lock --upgrade-package ty`, never blanket `uv lock --upgrade`.

## Conventions

- **Entrypoint gotcha:** console script maps `photo-cull = "photo_cull:main"` — `main` must be importable from the package root. `__init__.py` does `from .cli import main` + `__all__ = ["main"]` (the `__all__` satisfies ruff F401 — don't remove it). Never point the script at `photo_cull.cli:main`.
- **exiftool is a system binary prerequisite, not a pip dependency.** Resolution order in `src/photo_cull/exiftool.py::find_exiftool()`: `$PHOTO_CULL_EXIFTOOL` env (set via CLI flag `-x/--exiftool`) → PyInstaller `_MEIPASS` bundle → `shutil.which("exiftool")` → raises `ExiftoolNotFound` with install hints (CLI exits 1, message on stderr). Route all exiftool calls through this one module.
- **exiftool invocation:** batch JSON with `-j -n -config "" -m -charset filename=utf8`. `-config ""` ignores the user's `~/.ExifTool_config` (output stability); `-n` gives numeric values; `-m` keeps one bad file from aborting the batch. **Do NOT add `-f`**: missing EXIF fields must yield `None` in manifest entries (acceptance requirement), not `-`.
- Structure: `exiftool.py` (binary wrapper — only module that shells out), `ingest.py` (manifest building, `ManifestEntry` dataclass, `directory_summary()` folder-tree output), `cli.py` (argparse + `main()`), `constants.py` (extension lists; `RAW_EXTENSIONS`/`JPEG_EXTENSIONS` derive `file_type` = raw|jpeg|other).
- **CLI output:** `-n/--dry-run` prints the total photo count plus a `directory_summary()` folder-structure view (per-directory counts + capture-date spans); `-V/--verbose` prints the full manifest. Dry run does not yet skip the manifest build.

## Work Tracking

Development is tracked in Linear — Personal team, project "AI Photo Culling Pipeline", Build 1 parent issue P-1461 (ingest stage) with numbered step sub-issues. Check Linear for the current step rather than guessing scope.
