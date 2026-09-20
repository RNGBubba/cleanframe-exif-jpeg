"""Remove EXIF metadata from JPEG images without unsafe overwrites."""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

from PIL import Image, UnidentifiedImageError

_SUPPORTED_FORMATS = {"JPEG"}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cleanframe",
        description="Strip EXIF metadata from a JPEG image.",
    )
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument(
        "--force",
        action="store_true",
        help="replace an existing regular destination file",
    )
    return parser


def _safe_destination(path: Path, force: bool) -> bool:
    if path.is_symlink():
        print("destination must not be a symbolic link", file=sys.stderr)
        return False
    if path.exists() and (not path.is_file() or not force):
        print("destination exists; use --force to replace a regular file", file=sys.stderr)
        return False
    return True


def strip_exif(source: Path, destination: Path, force: bool = False) -> None:
    source = source.expanduser()
    destination = destination.expanduser()
    if source.resolve() == destination.resolve():
        raise ValueError("source and destination must be different files")
    if not source.is_file() or source.is_symlink():
        raise ValueError("source must be a regular file")
    if not _safe_destination(destination, force):
        raise FileExistsError("unsafe destination")
    destination.parent.mkdir(parents=True, exist_ok=True)

    try:
        with Image.open(source) as image:
            if image.format not in _SUPPORTED_FORMATS:
                raise ValueError("only JPEG images are supported")
            pixels = image.convert("RGB")
    except UnidentifiedImageError as exc:
        raise ValueError("source is not a recognized image") from exc

    fd, temporary_name = tempfile.mkstemp(
        dir=destination.parent,
        prefix=f".{destination.name}.",
        suffix=".tmp",
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "wb") as output:
            pixels.save(output, format="JPEG", quality=95, optimize=True)
            output.flush()
            os.fsync(output.fileno())
        if destination.is_symlink() or (destination.exists() and not force):
            raise FileExistsError("destination changed during operation")
        os.replace(temporary, destination)
    finally:
        pixels.close()
        temporary.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        strip_exif(args.source, args.destination, force=args.force)
    except (FileExistsError, ValueError, OSError) as exc:
        print(f"cleanframe: {exc}", file=sys.stderr)
        return 2
    print(f"wrote {args.destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
