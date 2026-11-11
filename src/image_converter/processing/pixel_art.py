"""Эффект пиксельной графики."""

import numpy as np
from PIL import Image


def _quantize_palette(arr: np.ndarray, n_colors: int) -> np.ndarray:
    """Квантует палитру изображения до n_colors цветов с помощью k-meines-подобного подхода.

    Использует равномерную квантование по каждому каналу для детерминированного результата.
    """
    if n_colors <= 1:
        return arr

    # Количество уровней на канал: кубический корень из n_colors, округлён вверх
    levels = int(round(n_colors ** (1 / 3)))
    levels = max(2, min(levels, 256))

    step = 256 // levels
    quantized = (arr // step) * step + step // 2
    return np.clip(quantized, 0, 255).astype(np.uint8)


def apply_pixel_art(
    image: Image.Image,
    pixel_size: int = 10,
    n_colors: int = 0,
    intensity: float = 1.0,
) -> Image.Image:
    """Преобразует изображение в пиксельную графику.

    Алгоритм: уменьшение разрешения с последующим увеличением через NEAREST,
    с опциональной квантовой редукцией палитры.

    Args:
        image: Исходное изображение PIL.
        pixel_size: Размер одного пикселя в блоках (минимум 1).
        n_colors: Количество цветов в палитре (0 - без квантования).
        intensity: Интенсивность эффекта (0.0 - без изменений, 1.0 - полный).

    Returns:
        Пиксельное изображение.
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

    width, height = rgb.size
    pixel_size = max(1, int(pixel_size))

    # Уменьшение разрешения
    small_width = max(1, width // pixel_size)
    small_height = max(1, height // pixel_size)
    small = rgb.resize((small_width, small_height), Image.NEAREST)

    # Квантование палитры
    if n_colors and n_colors > 1:
        arr = np.array(small, dtype=np.uint8)
        arr = _quantize_palette(arr, n_colors)
        small = Image.fromarray(arr, "RGB")

    # Увеличение обратно через NEAREST для жёстких пикселей
    result = small.resize((width, height), Image.NEAREST)

    if intensity < 1.0:
        blended = Image.blend(rgb, result, intensity)
        result = blended

    if has_alpha and alpha is not None:
        result = Image.merge("RGBA", (*result.split(), alpha))

    return result
