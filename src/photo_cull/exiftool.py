"""Thin wrapper around the exiftool binary."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

EXIFTOOL_ENV_VAR = "PHOTO_CULL_EXIFTOOL"

INSTALL_HINTS = """exiftool was not found on this machine.

Install it with one of:
  Arch / Manjaro  : sudo pacman -S perl-image-exiftool
  Debian / Ubuntu : sudo apt install libimage-exiftool-perl
  macOS (Homebrew) : brew install exiftool

Or point photo-cull at an existing binary:
  export PHOTO_CULL_EXIFTOOL=/path/to/exiftool
"""

EXIFTOOL_TAGS = [
    "-SourceFile",
    "-FileTypeExtension",
    "-DateTimeOriginal",
    "-CreateDate",
    "-ExposureTime",
    "-ShutterSpeedValue",
    "-ISO",
    "-FNumber",
    "-ApertureValue",
]


class ExiftoolNotFound(RuntimeError):
    """Raised when the exiftool binary cannot be located."""


def _bundled_candidate() -> Path | None:
    """PyInstaller extraction dir, if this ever runs frozen."""
    base = getattr(sys, "_MEIPASS", None)
    if not base:
        return None
    candidate = Path(base) / ("exiftool.exe" if os.name == "nt" else "exiftool")
    return candidate if candidate.exists() else None


def find_exiftool() -> str:
    """Resolve the exiftool binary: explicit override, then bundled, then PATH."""
    override = os.environ.get(EXIFTOOL_ENV_VAR)
    if override:
        if not Path(override).exists():
            raise ExiftoolNotFound(
                f"{EXIFTOOL_ENV_VAR} points at {override!r}, which does not exist."
            )
        return override
    for candidate in (_bundled_candidate(), shutil.which("exiftool")):
        if candidate and Path(candidate).exists():
            return str(candidate)

    raise ExiftoolNotFound(INSTALL_HINTS)


def run_exiftool_json(paths: list[str]) -> list[dict]:
    """Run exiftool once over `pahts`; return one dict per file.
    Files with no EXIF simply omit the relevant keys - callers use .get().
    """
    if not paths:
        return []

    cmd = [
        find_exiftool(),
        "-j",  # JSON output
        "-n",  # numeric ExposureTime / FNumber / ISO
        "-config",
        "",  # ignore the user's ~/.ExifTool_config
        "-m",  # minor errors don't abort the batch
        "-charset",
        "filename=utf8",  # non-ASCII paths
        *EXIFTOOL_TAGS,
        *paths,
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0:
        raise RuntimeError(
            f"exiftool failed (exit {proc.returncode}): {proc.stderr.strip()}"
        )
    return json.loads(proc.stdout)
