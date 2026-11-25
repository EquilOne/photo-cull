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


def _file_type(path: str) -> str:
    suffix = Path(path).suffix.lower() if "." in path else ""
    ext = f".{suffix}"
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


def build_manifest(paths: list[str]) -> list[ManifestEntry]:
    """Build the manifest: one entry per file, missing EXIF fields are None."""
    records = run_exiftool_json(paths)

    entries = []
    for record in records:
        path = record.get("SourceFile", "")
        entries.append(
            ManifestEntry(
                path=path,
                capture_time=_iso_capture_time(
                    _first(record, "DateTimeOriginal", "CreateDate")
                ),
                exposure=_first(record, "ExposureTime"),
                iso=_first(record, "ISO"),
                aperture=_first(record, "FNumber", "AperatureValue"),
                file_type=_file_type(path),
            )
        )
    return entries
