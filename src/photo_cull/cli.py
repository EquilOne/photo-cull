import argparse
from pathlib import Path

from .constants import IMG_FILE_TYPES


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="photo-cull",
        description="A cli photo culling application with llm and decision model escalation.",
    )
    parser.add_argument("-n", "--dry-run", action="store_true", help="Preview output")
    parser.add_argument("src_path", help="Directory containing source images")
    parser.add_argument(
        "-T", "--threshold", type=float, default=0.75, help="Minimum score to keep"
    )
    return parser


def find_image_paths(src_path) -> list[str]:
    img_types: list = IMG_FILE_TYPES
    image_paths: list[str] = []
    for path, dirs, files in Path.walk(Path.absolute(src_path)):
        for file in files:
            if Path(file).suffix.lower() in img_types:
                image_paths.append(str((path / file).absolute()))
    return image_paths


def main():
    args: argparse.Namespace = build_parser().parse_args()
    src_dir = Path(args.src_path).expanduser().absolute()
    candidates: list[str] = find_image_paths(src_dir)
    print(candidates)
