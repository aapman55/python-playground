
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps

def process_image(
    input_path: str,
    output_path: str,
    scale_factor: float,               # e.g., 2.0 for 2×; 1.5 for 150%
    brightness_factor: float = 1.2,    # >1 brighter; <1 darker
    contrast_factor: float = 0.9,      # <1 lowers contrast; >1 increases
    sharpness_factor: float = 1.3,     # >1 sharper; 1.0 no change; <1 softer
    pure_bw: bool = False,             # True -> convert to 1-bit after enhancements
    bw_threshold: int = 128,           # threshold used if pure_bw=True (0–255)
    dither: bool = True                # dithering for 1-bit conversion
) -> None:
    """
    Enlarge the image by a scale factor.
    Steps:
      1) Normalize EXIF orientation,
      2) Convert to grayscale (black & white) BEFORE enhancements,
      3) Apply brightness & contrast on grayscale,
      4) Resize by `scale_factor` with high-quality resampling,
      5) Apply sharpening (post-resize for best results),
      6) Optional pure black/white (1-bit) conversion,
      7) Save (auto-create directories; preserve EXIF for JPEGs).
    """
    if scale_factor <= 0:
        raise ValueError("scale_factor must be > 0")

    in_path = Path(input_path)
    out_path = Path(output_path)

    if not in_path.exists():
        raise FileNotFoundError(f"Input image not found: {in_path}")

    # Ensure output directory exists
    if out_path.parent and not out_path.parent.exists():
        out_path.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(in_path) as im:
        # Normalize orientation based on EXIF
        im = ImageOps.exif_transpose(im)

        # 1) Convert to black & white (grayscale) BEFORE enhancements
        im = ImageOps.grayscale(im)  # mode 'L'

        # 2) Apply brightness & contrast
        im = ImageEnhance.Brightness(im).enhance(brightness_factor)
        im = ImageEnhance.Contrast(im).enhance(contrast_factor)

        # 3) Resize by scale factor (upscale)
        new_w = max(1, int(round(im.width * scale_factor)))
        new_h = max(1, int(round(im.height * scale_factor)))
        # LANCZOS provides high-quality resampling; BICUBIC is also good for upscaling
        im = im.resize((new_w, new_h), resample=Image.LANCZOS)

        # 4) Apply sharpening after resizing
        im = ImageEnhance.Sharpness(im).enhance(sharpness_factor)

        # 5) Optional pure black/white (1-bit) conversion
        if pure_bw:
            # Threshold first for predictable binarization
            im = im.point(lambda p: 255 if p >= bw_threshold else 0, mode='L')
            im = im.convert('1', dither=Image.FLOYDSTEINBERG if dither else Image.NONE)

        # Preserve EXIF if available (mostly relevant for JPEG)
        exif_bytes = im.info.get("exif")

        # 6) Save with format-appropriate options
        suffix = out_path.suffix.lower()
        save_params = {}

        if suffix in {".jpg", ".jpeg"}:
            # High-quality JPEG: 4:4:4, optimized, reasonable quality
            save_params.update(dict(quality=90, subsampling=0, optimize=True))
            if exif_bytes:
                save_params["exif"] = exif_bytes
        elif suffix == ".webp":
            # WebP with near-lossless setting (feel free to adjust)
            save_params.update(dict(quality=95, method=6))
        elif suffix == ".png":
            # PNG is lossless; optimize flag helps reduce size
            save_params.update(dict(optimize=True))

        im.save(out_path, **save_params)


if __name__ == "__main__":

    from pathlib import Path
    root_folder = "E:/OneDrive/fayinschool.nl/Projecten - Documents/Nieuwe werkboeken/ABC-作業/下學期/六年级"
    edited_postfix = "_edited"

    # Example usage: enlarge 2×
    for img in Path(root_folder).rglob("*.png"):
        if img.name.endswith(edited_postfix+img.suffix):
            continue

        print(f"Editing: {img.as_posix()}")
        process_image(
            input_path=img.as_posix(),
            output_path=(img.parent / (img.stem + edited_postfix +img.suffix) ).as_posix(),
            scale_factor=4.0,           # enlarge by 2 times
            brightness_factor=1,
            contrast_factor=3,
            sharpness_factor=2,
            pure_bw=True               # set True for 1-bit B/W (PNG recommended)
        )

