import shutil
import struct


def png_size(path):
    with open(path, "rb") as fh:
        data = fh.read(24)
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("%s is not a PNG" % path)
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def place_og(src_root, docs_assets, placeholder):
    custom = src_root / "content" / "og.png"
    dest = docs_assets / "og.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if custom.exists():
        size = png_size(custom)
        if size != (1200, 630):
            raise ValueError("content/og.png is %sx%s, want 1200x630" % size)
        shutil.copyfile(custom, dest)
        return
    shutil.copyfile(placeholder, dest)
