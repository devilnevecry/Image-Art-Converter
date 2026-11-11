"""Эффект карандашного эскиза."""

import cv2
import numpy as np
from PIL import Image


def apply_pencil_sketch(
    image: Image.Image,
    intensity: float = 1.0,
    contrast: float = 1.0,
) -> Image.Image:
    """Создаёт эффект карандашного эскиза.

    Классический алгоритм color dodge:
    1. Перевод в оттенки серого.
    2. Инверсия.
    3. Размытие по Гауссу.
    4. Color dodge blend оригинала с размытой инверсией.
    5. Регулировка контраста.

    Args:
        image: Исходное изображение PIL.
        intensity: Интенсивность эффекта (0.0 - без изменений, 1.0 - полный).
        contrast: Коэффициент контраста (0.5 - 2.0).

    Returns:
        Изображение с эффектом карандашного эскиза.
    """
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGBA") if "A" in image.mode else image.convert("RGB")

    has_alpha = image.mode == "RGBA"
    if has_alpha:
        rgb = image.convert("RGB")
        alpha = image.getchannel("A")
    else:
        rgb = image
        alpha = None

    arr = np.array(rgb, dtype=np.float32)

    # Оттенки серого
    gray = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    gray = np.clip(gray, 0, 255).astype(np.uint8)

    # Инверсия
    inverted = 255 - gray

    # Размытие по Гауссу (ядро должно быть нечётным)
    blur_ksize = 21
    blurred = cv2.GaussianBlur(inverted, (blur_ksize, blur_ksize), 0)

    # Color dodge: result = gray / (255 - blurred)
    # Делим на (255 - blurred), чтобы избежать деления на ноль добавляем эпсилон
    denominator = 255.0 - blurred
    denominator = np.clip(denominator, 1.0, 255.0)

    sketch = (gray.astype(np.float32) * 255.0) / denominator
    sketch = np.clip(sketch, 0, 255).astype(np.uint8)

    # Контраст
    if contrast != 1.0:
        sketch = np.clip(
            (sketch.astype(np.float32) - 128) * contrast + 128,
            0,
            255,
        ).astype(np.uint8)

    # Собираем обратно в RGB
    sketch_rgb = np.stack([sketch, sketch, sketch], axis=2)

    if intensity < 1.0:
        sketch_rgb = (arr * (1.0 - intensity) + sketch_rgb * intensity).astype(np.uint8)

    result = Image.fromarray(sketch_rgb, "RGB")

    if has_alpha and alpha is not None:
        result = Image.merge("RGBA", (*result.split(), alpha))

    return result
