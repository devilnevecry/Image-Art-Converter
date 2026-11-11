"""Преобразование изображения в ASCII-арт."""

from typing import Tuple

import numpy as np
from PIL import Image

ASCII_SCHEMES = {
    "standard": "@%#*+=-:. ",
    "detailed": "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^'. ",
    "blocks": "█▓▒░ ",
    "simple": "#S*o+.; ",
    "braille": "⣿⣷⣯⣟⡿⢿⣻⣽⣾⣶⣤⣄⡀ ",
}

DEFAULT_SCHEME = "standard"


def _to_grayscale(image: Image.Image) -> np.ndarray:
    """Переводит изображение в массив яркости 0-255."""
    if image.mode != "L":
        image = image.convert("L")
    return np.array(image, dtype=np.float32)


def apply_ascii_art(
    image: Image.Image,
    density: float = 1.0,
    scheme_name: str = DEFAULT_SCHEME,
    width: int = 100,
) -> Tuple[str, Image.Image]:
    """Преобразует изображение в ASCII-строку и монокартинку.

    Args:
        image: Исходное изображение PIL.
        density: Плотность символов (0.1 - 2.0). Меньше = больше символов.
        scheme_name: Имя набора символов.
        width: Ширина вывода в символах.

    Returns:
        Кортеж (ascii_string, ascii_image).
    """
    scheme = ASCII_SCHEMES.get(scheme_name, ASCII_SCHEMES[DEFAULT_SCHEME])

    # Сохраняем пропорции: символы выше, чем широкие (соотношение примерно 2:1)
    orig_width, orig_height = image.size
    aspect_ratio = orig_height / orig_width
    out_width = max(10, int(width))
    out_height = max(1, int(out_width * aspect_ratio * 0.5 / density))

    # Изменяем размер и переводим в оттенки серого
    small = image.resize((out_width, out_height), Image.NEAREST)
    gray = _to_grayscale(small)

    # Нормализуем яркость к индексам символов
    n_chars = len(scheme)
    indices = (gray / 255.0 * (n_chars - 1)).astype(int)
    indices = np.clip(indices, 0, n_chars - 1)

    lines = []
    for row in indices:
        lines.append("".join(scheme[i] for i in row))

    ascii_string = "\n".join(lines)

    # Создаём изображение из ASCII (чёрный текст на белом фоне)
    char_width = 8
    char_height = 16
    img_width = out_width * char_width
    img_height = out_height * char_height
    ascii_img = Image.new("RGB", (img_width, img_height), "white")

    # Рисуем текст пиксель за пиксель через numpy для скорости
    arr = np.full((img_height, img_width, 3), 255, dtype=np.uint8)
    for y, line in enumerate(lines):
        for x, ch in enumerate(line):
            if ch != " ":
                px_x = x * char_width
                px_y = y * char_height
                arr[px_y : px_y + char_height, px_x : px_x + char_width] = [0, 0, 0]

    ascii_img = Image.fromarray(arr, "RGB")

    return ascii_string, ascii_img
