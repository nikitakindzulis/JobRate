"""One-off script: generates JobRate extension icons (16/48/128px) matching
the popup's purple gradient app-icon (#7c5cff -> #a78bfa), with rounded
corners and a white "JR" mark. Run with: python generate_icons.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT_DIR = Path(__file__).resolve().parent.parent / "extension" / "icons"
SIZES = [16, 48, 128]
COLOR_START = (124, 92, 255)  # #7c5cff
COLOR_END = (167, 139, 250)  # #a78bfa


def make_icon(size: int) -> Image.Image:
    scale = 4
    big = size * scale
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    for y in range(big):
        t = y / big
        r = round(COLOR_START[0] + (COLOR_END[0] - COLOR_START[0]) * t)
        g = round(COLOR_START[1] + (COLOR_END[1] - COLOR_START[1]) * t)
        b = round(COLOR_START[2] + (COLOR_END[2] - COLOR_START[2]) * t)
        draw.line([(0, y), (big, y)], fill=(r, g, b, 255))

    mask = Image.new("L", (big, big), 0)
    mask_draw = ImageDraw.Draw(mask)
    radius = round(big * 0.22)
    mask_draw.rounded_rectangle([0, 0, big - 1, big - 1], radius=radius, fill=255)
    img.putalpha(mask)

    text = "JR"
    font = None
    for name in ("arialbd.ttf", "DejaVuSans-Bold.ttf"):
        try:
            font = ImageFont.truetype(name, round(big * 0.42))
            break
        except OSError:
            continue
    if font is None:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        ((big - tw) / 2 - bbox[0], (big - th) / 2 - bbox[1]),
        text,
        font=font,
        fill=(255, 255, 255, 255),
    )

    return img.resize((size, size), Image.LANCZOS)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for size in SIZES:
        icon = make_icon(size)
        path = OUT_DIR / f"icon{size}.png"
        icon.save(path)
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
