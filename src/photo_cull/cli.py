import argparse
import os
import sys
from pathlib import Path

from .constants import IMG_FILE_TYPES
from .exiftool import ExiftoolNotFound
from .ingest import build_manifest, directory_summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="photo-cull",
        description="A cli photo culling app with llm and decision model escalation.",
    )
    parser.add_argument("-n", "--dry-run", action="store_true", help="Preview output")
    parser.add_argument("src_path", help="Directory containing source images")
    parser.add_argument(
        "-T", "--threshold", type=float, default=0.75, help="Minimum score to keep"
    )
    parser.add_argument(
        "-x",
        "--exiftool",
        help="Path to the exiftool binary (overrides $PHOTO_CULL_EXIFTOOL)",
    )
    parser.add_argument(
        "-V", "--verbose", help="Prints the full manifest.", action="store_true"
    )
    return parser


def find_image_paths(src_path) -> list[str]:
    img_types: list = IMG_FILE_TYPES
    image_paths: list[str] = []
    for path, _dirs, files in Path.walk(Path.absolute(src_path)):
        for file in files:
            if Path(file).suffix.lower() in img_types:
                image_paths.append(str((path / file).absolute()))
    return image_paths


def main():
    args: argparse.Namespace = build_parser().parse_args()
    if args.exiftool:
        os.environ["PHOTO_CULL_EXIFTOOL"] = args.exiftool

    src_dir = Path(args.src_path).expanduser().absolute()
    candidates: list[str] = find_image_paths(src_dir)

    try:
        manifest = build_manifest(candidates)
        if args.verbose:
            for item in manifest:
                print(
                    f"Name: {Path(item.path).name}\n"
                    f"File type: {item.file_type}\n"
                    f"Capture time: {item.capture_time}\n"
                    f"Exposure: {item.exposure}\n"
                    f"ISO: {item.iso}\n"
                    f"Aperature: {item.aperture}"
                )
                print(f"Scorable: {item.is_scorable}")
        if args.dry_run:
            print(f"Manifest contains {len(manifest)} photos")
            for line in directory_summary(manifest, src_dir):
                print(line)

    except ExiftoolNotFound as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
