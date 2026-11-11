"""Конфигурация pytest и фикстуры."""

import numpy as np
import pytest
from PIL import Image


@pytest.fixture
def rgb_image():
    """RGB изображение 100x100 с градиентом."""
    arr = np.zeros((100, 100, 3), dtype=np.uint8)
    for y in range(100):
        for x in range(100):
            arr[y, x] = [x * 2 % 256, y * 2 % 256, 128]
    return Image.fromarray(arr, "RGB")


@pytest.fixture
def rgba_image():
    """RGBA изображение 100x100 с градиентом и альфа-каналом."""
    arr = np.zeros((100, 100, 4), dtype=np.uint8)
    for y in range(100):
        for x in range(100):
            arr[y, x] = [x * 2 % 256, y * 2 % 256, 128, 200]
    return Image.fromarray(arr, "RGBA")


@pytest.fixture
def small_rgb_image():
    """Маленькое RGB изображение 10x10."""
    arr = np.full((10, 10, 3), 100, dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


@pytest.fixture
def large_rgb_image():
    """Большое RGB изображение 500x500."""
    arr = np.random.randint(0, 256, (500, 500, 3), dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


@pytest.fixture
def solid_white_image():
    """Белое изображение 50x50."""
    arr = np.full((50, 50, 3), 255, dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


@pytest.fixture
def solid_black_image():
    """Чёрное изображение 50x50."""
    arr = np.zeros((50, 50, 3), dtype=np.uint8)
    return Image.fromarray(arr, "RGB")
