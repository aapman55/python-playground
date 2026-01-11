
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps

def process_image(
    input_path: str,
    output_path: str,
    brightness_factor: float = 1.2,    # >1 brighter; <1 darker
    contrast_factor: float = 0.9,      # <1 lowers contrast; >1 increases
    sharpness_factor: float = 1.3,     # >1 sharper; 1.0 no change; <1 softer
    target_max_size: tuple[int, int] = (1600, 1600)  # fit within (W, H)
) -> None:
    """
    Process an image: brightness up, contrast down, sharpen, and scale with anti-aliasing.
    Preserves aspect ratio and creates the output directory if needed.

    Args:
        input_path: Path to the source image.
        output_path: Path to save the processed image (directories auto-created).
        brightness_factor: 1.0 no change; >1 brighter; <1 darker.
        contrast_factor:   1.0 no change; >1 more contrast; <1 less contrast.
        sharpness_factor:  1.0 no change; >1 sharper; <1 blurrier.
        target_max_size:   (max_width, max_height) bounding box for thumbnail.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input image not found: {input_path}")

    # Ensure output directory exists
    if output_path.parent and not output_path.parent.exists():
        output_path.parent.mkdir(parents=True, exist_ok=True)

    # Open and normalize orientation based on EXIF
    with Image.open(input_path) as im:
        im = ImageOps.exif_transpose(im)

        # Turn image into black and white
        im = ImageOps.grayscale(im)

        # Enhance brightness, contrast, and sharpness
        im = ImageEnhance.Brightness(im).enhance(brightness_factor)
        im = ImageEnhance.Contrast(im).enhance(contrast_factor)
        im = ImageEnhance.Sharpness(im).enhance(sharpness_factor)

        # Scale preserving aspect ratio; LANCZOS gives top-quality downsampling
        im.thumbnail(target_max_size, resample=Image.LANCZOS)

        # Preserve EXIF if available (for JPEG)
        exif_bytes = im.info.get("exif")

        # Save with sensible quality options depending on format
        suffix = output_path.suffix.lower()
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

        im.save(output_path, **save_params)

if __name__ == "__main__":

    from pathlib import Path
    image_input_path = "./res/"
    image_output_path = "./res/output/"

    for img in Path(image_input_path).rglob("*.png"):
        process_image(
            input_path=f"{image_input_path}{img.name}",
            output_path=f"{image_output_path}{img.name}",
            brightness_factor=1,      # a touch brighter
            contrast_factor=3,        # slightly flatter contrast
            sharpness_factor=5,        # mild sharpening
            target_max_size=(1920, 1080) # fit within 1080p bounds
        )
