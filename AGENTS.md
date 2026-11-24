# AGENTS.md — PhotoCull

Small Python CLI: `photo-cull` — photo culling with LLM and decision-model assistance. Fresh scaffold: `src/photo_cull/__init__.py`, `cli.py`, and `tests/` are all **empty**; described features are not implemented yet. Verify files before assuming any behavior.

## Setup & Commands

```bash
uv sync            # create .venv (gitignored), install project
uv add <pkg>       # add dependency (currently zero runtime deps)
uv run photo-cull  # run the CLI
```

No build, lint, test, or typecheck commands are configured anywhere — do not invent or run them without adding the config first (e.g. if asked to test, set up pytest in `pyproject.toml` first).

## Conventions

- uv-managed project (backend `uv_build`), **Python 3.13 only** (`.python-version` pinned; `requires-python >=3.13`).
- Src layout: code lives in `src/photo_cull/`.
- **Entrypoint gotcha:** the console script maps `photo-cull = "photo_cull:main"` — `main()` must be importable from the package root (`__init__.py`), **not** `photo_cull.cli:main`. If you create `cli.py`, expose `main` from `__init__.py`.
- No CI, pre-commit, lockfile, or dev tooling exists yet.
