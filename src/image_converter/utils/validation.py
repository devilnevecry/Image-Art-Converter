"""Валидация загружаемых изображений."""

import io
from typing import Tuple

from PIL import Image, UnidentifiedImageError

# Лимиты безопасности
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 МБ
MAX_PIXELS = 64_000_000  # 64 Мп (например 8000x8000)

SUPPORTED_FORMATS = {"PNG", "JPEG", "WEBP"}


class ImageValidationError(Exception):
    """Ошибка валидации изображения."""


def validate_image(file_bytes: bytes) -> Tuple[Image.Image, str]:
    """Проверяет и открывает загруженный файл изображения.

    Args:
        file_bytes: Байты загруженного файла.

    Returns:
        Кортеж (PIL.Image, формат).

    Raises:
        ImageValidationError: если файл некорректен, повреждён или не поддерживается.
    """
    if len(file_bytes) == 0:
        raise ImageValidationError("Файл пуст.")

    if len(file_bytes) > MAX_FILE_SIZE:
        size_mb = MAX_FILE_SIZE / (1024 * 1024)
        raise ImageValidationError(
            f"Файл слишком большой. Максимальный размер: {size_mb:.0f} МБ."
        )

    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.load()  # форсируем чтение для обнаружения повреждений
    except UnidentifiedImageError:
        raise ImageValidationError("Не удалось определить формат изображения.")
    except Exception as exc:  # noqa: BLE001
        raise ImageValidationError(f"Повреждённый или некорректный файл: {exc}")

    fmt = image.format
    if fmt not in SUPPORTED_FORMATS:
        raise ImageValidationError(
            f"Формат '{fmt}' не поддерживается. Доступны: {', '.join(sorted(SUPPORTED_FORMATS))}."
        )

    # Проверка количества пикселей
    width, height = image.size
    total_pixels = width * height
    if total_pixels > MAX_PIXELS:
        raise ImageValidationError(
            f"Изображение слишком большое ({total_pixels:,} пикселей). "
            f"Максимум: {MAX_PIXELS:,} пикселей."
        )

    return image, fmt
