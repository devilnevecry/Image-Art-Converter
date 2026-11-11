"""Эффект контурной раскраски."""

import cv2
import numpy as np
from PIL import Image


def apply_coloring_page(
    image: Image.Image,
    thickness: float = 1.0,
    threshold: float = 0.5,
) -> Image.Image:
    """Создаёт контурный рисунок для раскрашивания.

    Алгоритм: обнаружение контуров (Canny / Sobel), нормализация и
    пороговая бинаризация. Белый фон, чёрные контуры.

    Args:
        image: Исходное изображение PIL.
        thickness: Толщина контуров (0.5 - 3.0).
        threshold: Порог детализации (0.0 - 1.0).

    Returns:
        Чёрно-белое контурное изображение.
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

    arr = np.array(rgb, dtype=np.uint8)

    # Оттенки серого
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)

    # Размытие для удаления шума
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Обнаружение градиентов по Sobel
    sobelx = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.sqrt(sobelx ** 2 + sobely ** 2)

    # Нормализация в диапазон 0-255
    if magnitude.max() > 0:
        magnitude = (magnitude / magnitude.max() * 255).astype(np.uint8)
    else:
        magnitude = np.zeros_like(gray)

    # THRESH_BINARY: magnitude > threshold -> 255 (white edge), else 0 (black flat)
    thresh_val = threshold * 255
    _, binary = cv2.threshold(magnitude, thresh_val, 255, cv2.THRESH_BINARY)

    # Толщина контуров через дилатацию/эрозию (работаем с белыми краями)
    if thickness > 1.0:
        ksize = max(1, int(round(thickness)))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ksize, ksize))
        binary = cv2.dilate(binary, kernel, iterations=1)
    elif thickness < 1.0:
        ksize = max(1, int(round(1.0 / thickness)))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ksize, ksize))
        binary = cv2.erode(binary, kernel, iterations=1)

    # Инвертируем: контуры чёрные на белом фоне
    binary = 255 - binary

    result = Image.fromarray(np.stack([binary, binary, binary], axis=2), "RGB")

    if has_alpha and alpha is not None:
        result = Image.merge("RGBA", (*result.split(), alpha))

    return result
