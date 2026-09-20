from pathlib import Path

from PIL import Image

from cleanframe import cli


def make_tagged_jpeg(path: Path) -> None:
    image = Image.new("RGB", (3, 2), (40, 80, 120))
    exif = Image.Exif()
    exif[0x010E] = "private note"
    exif[0x0132] = "2026:09:20 12:00:00"
    image.save(path, format="JPEG", exif=exif.tobytes())


def test_strip_removes_exif_and_keeps_image_content(tmp_path: Path) -> None:
    source = tmp_path / "input.jpg"
    destination = tmp_path / "output.jpg"
    make_tagged_jpeg(source)

    assert cli.main([str(source), str(destination)]) == 0

    with Image.open(destination) as output:
        assert output.getexif() == {}
        assert output.size == (3, 2)
        assert output.getpixel((1, 1)) == (42, 79, 121)


def test_existing_destination_requires_explicit_force(tmp_path: Path) -> None:
    source = tmp_path / "input.jpg"
    destination = tmp_path / "output.jpg"
    make_tagged_jpeg(source)
    destination.write_bytes(b"do not overwrite")

    assert cli.main([str(source), str(destination)]) == 2
    assert destination.read_bytes() == b"do not overwrite"

    assert cli.main([str(source), str(destination), "--force"]) == 0


def test_unsupported_format_is_rejected_without_output(tmp_path: Path) -> None:
    source = tmp_path / "input.bmp"
    destination = tmp_path / "output.bmp"
    Image.new("RGB", (2, 2)).save(source, format="BMP")

    assert cli.main([str(source), str(destination)]) == 2
    assert not destination.exists()


def test_destination_symlink_is_never_followed(tmp_path: Path) -> None:
    source = tmp_path / "input.jpg"
    destination = tmp_path / "output.jpg"
    sentinel = tmp_path / "sentinel"
    make_tagged_jpeg(source)
    sentinel.write_bytes(b"sentinel")
    destination.symlink_to(sentinel)

    assert cli.main([str(source), str(destination), "--force"]) == 2
    assert sentinel.read_bytes() == b"sentinel"


def test_same_input_and_output_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "input.jpg"
    make_tagged_jpeg(source)

    assert cli.main([str(source), str(source), "--force"]) == 2
