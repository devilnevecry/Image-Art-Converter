"""Пакет алгоритмов обработки изображений."""

from .grayscale import apply_grayscale
from .pixel_art import apply_pixel_art
from .pencil_sketch import apply_pencil_sketch
from .coloring_page import apply_coloring_page
from .ascii_art import apply_ascii_art, ASCII_SCHEMES

__all__ = [
    "apply_grayscale",
    "apply_pixel_art",
    "apply_pencil_sketch",
    "apply_coloring_page",
    "apply_ascii_art",
    "ASCII_SCHEMES",
]

EFFECTS = {
    "grayscale": {
        "name": "Оттенки серого",
        "func": apply_grayscale,
    },
    "pixel_art": {
        "name": "Пиксельная графика",
        "func": apply_pixel_art,
    },
    "pencil_sketch": {
        "name": "Карандашный эскиз",
        "func": apply_pencil_sketch,
    },
    "coloring_page": {
        "name": "Контурная раскраска",
        "func": apply_coloring_page,
    },
    "ascii_art": {
        "name": "ASCII Art",
        "func": apply_ascii_art,
    },
}
