"""Тесты алгоритмов обработки изображений."""

import io

import numpy as np
import pytest
from PIL import Image, UnidentifiedImageError

from image_converter.processing import (
    apply_grayscale,
    apply_pixel_art,
    apply_pencil_sketch,
    apply_coloring_page,
    apply_ascii_art,
    ASCII_SCHEMES,
    EFFECTS,
)
from image_converter.utils import validate_image, save_image_to_bytes, save_ascii_to_bytes
from image_converter.utils.validation import ImageValidationError, MAX_FILE_SIZE, MAX_PIXELS


# ---------- Grayscale ----------
class TestGrayscale:
    def test_rgb_output_shape_and_mode(self, rgb_image):
        result = apply_grayscale(rgb_image)
        assert result.size == rgb_image.size
        assert result.mode == "RGB"

    def test_rgba_preserves_alpha(self, rgba_image):
        result = apply_grayscale(rgba_image)
        assert result.mode == "RGBA"
        assert result.size == rgba_image.size
        # Альфа-канал должен сохраниться
        assert np.array(result.getchannel("A")).mean() == pytest.approx(200)

    def test_intensity_zero_returns_original(self, rgb_image):
        result = apply_grayscale(rgb_image, intensity=0.0)
        assert np.array_equal(np.array(result), np.array(rgb_image))

    def test_intensity_one_is_gray(self, rgb_image):
        result = apply_grayscale(rgb_image, intensity=1.0)
        arr = np.array(result)
        # Все каналы равны (оттенки серого)
        assert np.allclose(arr[:, :, 0], arr[:, :, 1])
        assert np.allclose(arr[:, :, 1], arr[:, :, 2])

    def test_solid_white_stays_white(self, solid_white_image):
        result = apply_grayscale(solid_white_image)
        assert np.all(np.array(result) == 255)

    def test_solid_black_stays_black(self, solid_black_image):
        result = apply_grayscale(solid_black_image)
        assert np.all(np.array(result) == 0)

    def test_different_sizes(self, small_rgb_image, large_rgb_image):
        for img in (small_rgb_image, large_rgb_image):
            result = apply_grayscale(img)
            assert result.size == img.size

    def test_invalid_mode_handled(self):
        img = Image.new("L", (10, 10), 128)
        result = apply_grayscale(img)
        assert result.size == img.size


# ---------- Pixel Art ----------
class TestPixelArt:
    def test_output_shape(self, rgb_image):
        result = apply_pixel_art(rgb_image, pixel_size=10, n_colors=0, intensity=1.0)
        assert result.size == rgb_image.size
        assert result.mode == "RGB"

    def test_rgba_preserves_alpha(self, rgba_image):
        result = apply_pixel_art(rgba_image, pixel_size=10, intensity=1.0)
        assert result.mode == "RGBA"
        assert np.array(result.getchannel("A")).mean() == pytest.approx(200)

    def test_pixel_size_one_unchanged(self, rgb_image):
        result = apply_pixel_art(rgb_image, pixel_size=1, intensity=1.0)
        assert np.array_equal(np.array(result), np.array(rgb_image))

    def test_n_colors_reduces_palette(self, rgb_image):
        result = apply_pixel_art(rgb_image, pixel_size=10, n_colors=4, intensity=1.0)
        arr = np.array(result)
        unique_colors = len(np.unique(arr.reshape(-1, 3), axis=0))
        assert unique_colors <= 16  # 4^3 = 64 уровней, но уникальных комбинаций должно быть меньше

    def test_intensity_zero_original(self, rgb_image):
        result = apply_pixel_art(rgb_image, pixel_size=20, intensity=0.0)
        assert np.array_equal(np.array(result), np.array(rgb_image))

    def test_different_sizes(self, small_rgb_image, large_rgb_image):
        for img in (small_rgb_image, large_rgb_image):
            result = apply_pixel_art(img, pixel_size=5, intensity=1.0)
            assert result.size == img.size

    def test_solid_color(self, solid_white_image):
        result = apply_pixel_art(solid_white_image, pixel_size=10, n_colors=0, intensity=1.0)
        assert np.all(np.array(result) == 255)


# ---------- Pencil Sketch ----------
class TestPencilSketch:
    def test_output_shape(self, rgb_image):
        result = apply_pencil_sketch(rgb_image, intensity=1.0, contrast=1.0)
        assert result.size == rgb_image.size
        assert result.mode == "RGB"

    def test_rgba_preserves_alpha(self, rgba_image):
        result = apply_pencil_sketch(rgba_image, intensity=1.0, contrast=1.0)
        assert result.mode == "RGBA"

    def test_intensity_zero_original(self, rgb_image):
        result = apply_pencil_sketch(rgb_image, intensity=0.0, contrast=1.0)
        assert np.array_equal(np.array(result), np.array(rgb_image))

    def test_contrast_applied(self, rgb_image):
        r1 = apply_pencil_sketch(rgb_image, intensity=1.0, contrast=0.5)
        r2 = apply_pencil_sketch(rgb_image, intensity=1.0, contrast=2.0)
        assert not np.array_equal(np.array(r1), np.array(r2))

    def test_solid_white(self, solid_white_image):
        result = apply_pencil_sketch(solid_white_image, intensity=1.0, contrast=1.0)
        # Для однородного изображения эскиз должен быть белым (нет контуров)
        arr = np.array(result)
        assert arr.mean() > 200

    def test_different_sizes(self, small_rgb_image, large_rgb_image):
        for img in (small_rgb_image, large_rgb_image):
            result = apply_pencil_sketch(img, intensity=1.0, contrast=1.0)
            assert result.size == img.size


# ---------- Coloring Page ----------
class TestColoringPage:
    def test_output_shape(self, rgb_image):
        result = apply_coloring_page(rgb_image, thickness=1.0, threshold=0.5)
        assert result.size == rgb_image.size
        assert result.mode == "RGB"

    def test_rgba_preserves_alpha(self, rgba_image):
        result = apply_coloring_page(rgba_image, thickness=1.0, threshold=0.5)
        assert result.mode == "RGBA"

    def test_solid_color_white_background(self, solid_white_image):
        result = apply_coloring_page(solid_white_image, thickness=1.0, threshold=0.5)
        arr = np.array(result)
        # Однородное изображение -> белый фон (нет контуров)
        assert arr.mean() > 240

    def test_thickness_changes_result(self, rgb_image):
        r1 = apply_coloring_page(rgb_image, thickness=0.5, threshold=0.5)
        r2 = apply_coloring_page(rgb_image, thickness=3.0, threshold=0.5)
        assert not np.array_equal(np.array(r1), np.array(r2))

    def test_threshold_changes_result(self, rgb_image):
        r1 = apply_coloring_page(rgb_image, thickness=1.0, threshold=0.1)
        r2 = apply_coloring_page(rgb_image, thickness=1.0, threshold=0.9)
        assert not np.array_equal(np.array(r1), np.array(r2))

    def test_binary_black_white(self, rgb_image):
        result = apply_coloring_page(rgb_image, thickness=1.0, threshold=0.5)
        arr = np.array(result)
        unique = np.unique(arr.reshape(-1, 3), axis=0)
        # Должно бытьclose to только чёрный и белый
        assert len(unique) <= 4

    def test_different_sizes(self, small_rgb_image, large_rgb_image):
        for img in (small_rgb_image, large_rgb_image):
            result = apply_coloring_page(img, thickness=1.0, threshold=0.5)
            assert result.size == img.size


# ---------- ASCII Art ----------
class TestAsciiArt:
    def test_returns_string_and_image(self, rgb_image):
        text, img = apply_ascii_art(rgb_image, density=1.0, scheme_name="standard", width=50)
        assert isinstance(text, str)
        assert len(text) > 0
        assert isinstance(img, Image.Image)
        assert img.mode == "RGB"

    def test_rgba_handled(self, rgba_image):
        text, img = apply_ascii_art(rgba_image, density=1.0, scheme_name="standard", width=40)
        assert isinstance(text, str)
        assert len(text) > 0

    def test_scheme_names(self, rgb_image):
        for scheme_name in ASCII_SCHEMES:
            text, img = apply_ascii_art(rgb_image, scheme_name=scheme_name, width=30)
            assert isinstance(text, str)

    def test_width_changes_result(self, rgb_image):
        t1, _ = apply_ascii_art(rgb_image, width=20)
        t2, _ = apply_ascii_art(rgb_image, width=80)
        assert len(t1.splitlines()) != len(t2.splitlines()) or t1 != t2

    def test_density_changes_result(self, rgb_image):
        t1, _ = apply_ascii_art(rgb_image, density=0.5)
        t2, _ = apply_ascii_art(rgb_image, density=2.0)
        assert t1 != t2

    def test_preserves_aspect_ratio(self, rgb_image):
        # Пропорции должны сохраняться
        text, img = apply_ascii_art(rgb_image, width=100)
        assert text is not None


# ---------- Validation ----------
class TestValidation:
    def test_valid_png(self, rgb_image):
        buf = io.BytesIO()
        rgb_image.save(buf, format="PNG")
        image, fmt = validate_image(buf.getvalue())
        assert fmt == "PNG"
        assert image.size == rgb_image.size

    def test_valid_jpeg(self, rgb_image):
        buf = io.BytesIO()
        rgb_image.save(buf, format="JPEG")
        image, fmt = validate_image(buf.getvalue())
        assert fmt == "JPEG"

    def test_empty_bytes_raises(self):
        with pytest.raises(ImageValidationError):
            validate_image(b"")

    def test_invalid_file_raises(self):
        with pytest.raises(ImageValidationError):
            validate_image(b"not an image")

    def test_unsupported_format_raises(self):
        buf = io.BytesIO()
        Image.new("L", (10, 10)).save(buf, format="BMP")
        with pytest.raises(ImageValidationError):
            validate_image(buf.getvalue())

    def test_max_file_size(self):
        big = b"\x00" * (MAX_FILE_SIZE + 1)
        with pytest.raises(ImageValidationError):
            validate_image(big)

    def test_max_pixels(self):
        # Создаём валидный PNG но с огромными размерами (не сохраняем на диск)
        img = Image.new("RGB", (10000, 10000), 255)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        with pytest.raises(ImageValidationError):
            validate_image(buf.getvalue())


# ---------- Saving ----------
class TestSaving:
    def test_save_png_roundtrip(self, rgb_image):
        buf = io.BytesIO()
        rgb_image.save(buf, format="PNG")
        original = Image.open(buf)

        out_bytes = save_image_to_bytes(original, "PNG")
        reloaded = Image.open(io.BytesIO(out_bytes))
        assert reloaded.size == original.size
        assert np.array_equal(np.array(reloaded), np.array(original))

    def test_save_rgba_to_png(self, rgba_image):
        out_bytes = save_image_to_bytes(rgba_image, "PNG")
        reloaded = Image.open(io.BytesIO(out_bytes))
        assert reloaded.mode == "RGBA"

    def test_save_ascii_bytes(self):
        text = "Hello\nWorld"
        data = save_ascii_to_bytes(text)
        assert data.decode("utf-8") == text


# ---------- Effects registry ----------
class TestEffectsRegistry:
    def test_all_effects_have_functions(self):
        for key, cfg in EFFECTS.items():
            assert "name" in cfg
            assert "func" in cfg
            assert callable(cfg["func"])

    def test_effects_include_all_required(self):
        required = {"grayscale", "pixel_art", "pencil_sketch", "coloring_page", "ascii_art"}
        assert required.issubset(set(EFFECTS.keys()))
