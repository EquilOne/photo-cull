from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .constants import JPEG_EXTENSIONS, RAW_EXTENSIONS
from .exiftool import run_exiftool_json


@dataclass
class ManifestEntry:
    path: str
    capture_time: str | None
    exposure: float | None
    iso: int | None
    aperture: float | None
    file_type: str

    @property
    def is_scorable(self) -> bool:
        return self.file_type != "other"


def _file_type(path: str) -> str:
    suffix = Path(path).suffix.lower() if "." in path else ""
    ext = f"{suffix}"
    if ext in RAW_EXTENSIONS:
        return "raw"
    if ext in JPEG_EXTENSIONS:
        return "jpeg"
    return "other"


def _first(record: dict, *keys: str):
    for key in keys:
        value = record.get(key)
        if value is not None and value != "":
            return value
    return None


def _iso_capture_time(value: str | None) -> str | None:
    """EXIF dates look like '2024:05:03 10:22:31' -> ISO 8601."""
    if not value:
        return None
    date_part, _, time_part = value.partition(" ")
    return (
        f"{date_part.replace(':', '-')}T{time_part}"
        if time_part
        else date_part.replace(":", "-")
    )


def _aperature_value(record: dict, *keys: str) -> float | None:
    for key in keys:
        value = record.get(key)
        if value is None or value == "":
            continue
        try:
            value_f: float = float(value)
        except (TypeError, ValueError):
            continue
        if value_f == 0:
            continue
        return value_f
    return None


def _capture_date(entry: ManifestEntry) -> str | None:
    if entry.capture_time is None:
        return None
    return entry.capture_time.partition("T")[0]


def _date_span(dates: list[str], undated: int) -> str:
    unique = sorted(set(dates))
    if not unique:
        return "no dates"
    span = unique[0] if len(unique) == 1 else f"{unique[0]} → {unique[-1]}"
    return f"{span} (+{undated} undated)" if undated else span


def _tree_prefix(dirs: list[tuple[str, ...]], parts: tuple[str, ...]) -> str:
    prefix = ""
    for depth, part in enumerate(parts):
        siblings = [
            p[depth] for p in dirs if len(p) > depth and p[:depth] == parts[:depth]
        ]
        last = part == max(siblings)
        prefix += "└── " if last else "├── "
        if depth < len(parts) - 1:
            prefix += "    " if last else "│   "
    return prefix


def directory_summary(manifest: list[ManifestEntry], src_dir: Path) -> list[str]:
    """Folder-structure view: one line per directory with images.

    Shows the image count and the capture date (or date range) of that
    directory's files, relative to src_dir. Directories without images
    are skipped.
    """
    by_dir: dict[tuple[str, ...], list[ManifestEntry]] = {}
    for entry in manifest:
        rel = Path(entry.path).relative_to(src_dir)
        by_dir.setdefault(rel.parts[:-1], []).append(entry)
    by_dir.setdefault((), [])

    dirs = sorted(by_dir)
    if not dirs or not manifest:
        return []

    labels = ["." if not parts else "/".join(parts) + "/" for parts in dirs]
    prefixed = [
        _tree_prefix(dirs, parts) + label
        for parts, label in zip(dirs, labels, strict=True)
    ]
    name_width = max(len(line) for line in prefixed)
    count_width = max(len(str(len(by_dir[parts]))) for parts in dirs)

    lines = []
    for parts, label in zip(dirs, prefixed, strict=True):
        entries = by_dir[parts]
        if not entries:
            lines.append(".")
            continue
        dates = [date for entry in entries if (date := _capture_date(entry))]
        undated = len(entries) - len(dates)
        count = f"{len(entries)} photo{'' if len(entries) == 1 else 's'}"
        lines.append(
            f"{label:<{name_width}}  {count:>{count_width}}  "
            f"{_date_span(dates, undated)}"
        )
    return lines


def build_manifest(paths: list[str]) -> list[ManifestEntry]:
    """Build the manifest: one entry per file, missing EXIF fields are None."""
    records = run_exiftool_json(paths)

    entries = []
    for record in records:
        path = record.get("SourceFile", "")
        file_type: str = _file_type(path)
        entries.append(
            ManifestEntry(
                path=path,
                capture_time=_iso_capture_time(
                    _first(record, "DateTimeOriginal", "CreateDate")
                ),
                exposure=_first(record, "ExposureTime"),
                iso=_first(record, "ISO"),
                aperture=_aperature_value(record, "FNumber", "AperatureValue"),
                file_type=file_type,
            )
        )
    return entries
