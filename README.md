# CleanFrame EXIF

CleanFrame is a small local CLI that removes EXIF metadata from JPEG images before sharing them.

## Install

```sh
uv sync
```

## Use

```sh
uv run cleanframe private-photo.jpg shareable-photo.jpg
```

The command refuses to overwrite an existing file unless `--force` is supplied, and it never follows a destination symlink. It writes through a temporary file before replacing the destination so an interrupted conversion does not leave a partial output.

Only JPEG input is supported. Image pixels are decoded and re-encoded without carrying EXIF metadata forward.

## Test

```sh
uv run pytest
```

MIT licensed. See `LICENSE`.
