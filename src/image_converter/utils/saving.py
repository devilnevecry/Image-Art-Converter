"""Сохранение изображений в байты для скачивания."""

import io
from PIL import Image


def save_image_to_bytes(image: Image.Image, fmt: str = "PNG") -> bytes:
    """Сохраняет изображение в байты в указанном формате.

    Args:
        image: Изображение PIL.
        fmt: Формат ('PNG', 'JPEG', 'WEBP').

    Returns:
        Байты изображения.
    """
    buf = io.BytesIO()
    save_fmt = fmt.upper()
    if save_fmt == "JPEG" and image.mode == "RGBA":
        image = image.convert("RGB")
    image.save(buf, format=save_fmt)
    return buf.getvalue()


def save_ascii_to_bytes(text: str) -> bytes:
    """Сохраняет ASCII-строку в байты (UTF-8)."""
    return text.encode("utf-8")
