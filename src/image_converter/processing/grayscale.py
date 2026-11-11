"""Преобразование в оттенки серого."""

import numpy as np
from PIL import Image


def apply_grayscale(image: Image.Image, intensity: float = 1.0) -> Image.Image:
    """Преобразует изображение в оттенки серого.

    Args:
        image: Исходное изображение PIL.
        intensity: Интенсивность эффекта (0.0 - без изменений, 1.0 - полный).

    Returns:
        Изображение в оттенках серого с сохранением режима RGBA при наличии
        альфа-канала.
    """
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGBA") if "A" in image.mode else image.convert("RGB")

    has_alpha = image.mode == "RGBA"
    rgb = image.convert("RGB")
    arr = np.array(rgb, dtype=np.float32)

    # Стандартная luminance формула ITU-R BT.601
    gray = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    gray = np.stack([gray, gray, gray], axis=2)

    if intensity < 1.0:
        arr = arr * (1.0 - intensity) + gray * intensity
    else:
        arr = gray

    arr = np.clip(arr, 0, 255).astype(np.uint8)
    result = Image.fromarray(arr, "RGB")

    if has_alpha:
        alpha = image.getchannel("A")
        result = Image.merge("RGBA", (*result.split(), alpha))

    return result
