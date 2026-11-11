"""Коррекция ориентации по EXIF."""

from PIL import Image, ImageOps


def apply_exif_orientation(image: Image.Image) -> Image.Image:
    """Применяет EXIF orientation к изображению.

    Args:
        image: Исходное изображение PIL.

    Returns:
        Изображение с корректной ориентацией.
    """
    try:
        return ImageOps.exif_transpose(image)
    except Exception:
        return image
