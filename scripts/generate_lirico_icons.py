from pathlib import Path

from PIL import Image


ASSETS = Path("buzz/assets")
SOURCE = ASSETS / "liricoai-icon.png"


def main() -> None:
    image = Image.open(SOURCE).convert("RGBA")
    image = image.resize((1024, 1024), Image.Resampling.LANCZOS)

    image.save(ASSETS / "liricoai-icon-1024.png")
    image.save(
        ASSETS / "liricoai.ico",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    image.save(ASSETS / "liricoai.icns", format="ICNS")


if __name__ == "__main__":
    main()
