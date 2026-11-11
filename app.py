"""Точка входа и интерфейс приложения Image Art Converter."""

import io
from typing import Optional, Tuple

import streamlit as st
from PIL import Image

from image_converter.processing import EFFECTS, ASCII_SCHEMES
from image_converter.utils import (
    validate_image,
    apply_exif_orientation,
    save_image_to_bytes,
    save_ascii_to_bytes,
    MAX_FILE_SIZE,
)

st.set_page_config(
    page_title="Image Art Converter",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Константы ----------
MAX_UPLOAD_MB = MAX_FILE_SIZE / (1024 * 1024)

# ---------- Тема ----------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# ---------- Сброс состояния ----------
def reset_settings() -> None:
    st.session_state.effect = "grayscale"
    st.session_state.intensity = 1.0
    st.session_state.contrast = 1.0
    st.session_state.thickness = 1.0
    st.session_state.threshold = 0.5
    st.session_state.pixel_size = 10
    st.session_state.n_colors = 0
    st.session_state.ascii_density = 1.0
    st.session_state.ascii_scheme = "standard"
    st.session_state.ascii_width = 100
    st.session_state.processed_image = None
    st.session_state.ascii_text = None

# ---------- CSS ----------
def inject_css() -> None:
    dark = st.session_state.theme == "dark"
    bg = "#0e1117" if dark else "#ffffff"
    panel = "#1a1c22" if dark else "#f5f7fa"
    text = "#eaeaea" if dark else "#1a1a1a"
    accent = "#7c4dff"
    border = "#333640" if dark else "#d1d5db"

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {bg};
            color: {text};
        }}
        .main-header {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            letter-spacing: -0.5px;
        }}
        .sub-header {{
            color: #888;
            margin-bottom: 1.5rem;
        }}
        .card {{
            background: {panel};
            border: 1px solid {border};
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }}
        .compare-label {{
            text-align: center;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}
        .stButton > button {{
            background: {accent};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
        }}
        .stButton > button:hover {{
            opacity: 0.9;
        }}
        .download-btn {{
            background: {accent};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }}
        .error-box {{
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #fca5a5;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }}
        .success-box {{
            background: rgba(34, 197, 94, 0.1);
            border: 1px solid rgba(34, 197, 94, 0.3);
            color: #4ade80;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

inject_css()

# ---------- Заголовок ----------
st.markdown('<div class="main-header">🎨 Image Art Converter</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Локальное преобразование изображений в художественные стили</div>', unsafe_allow_html=True)

# ---------- Боковая панель ----------
with st.sidebar:
    st.header("⚙️ Настройки")
    st.toggle("Тёмная тема", value=(st.session_state.theme == "dark"), key="theme_toggle")

    # Переключатель темы
    if st.session_state.theme_toggle != (st.session_state.theme == "dark"):
        st.session_state.theme = "dark" if st.session_state.theme_toggle else "light"
        st.rerun()

    st.divider()

    uploaded_file = st.file_uploader(
        "Загрузите изображение",
        type=["png", "jpg", "jpeg", "webp"],
        help=f"Поддерживаемые форматы: PNG, JPG, JPEG, WEBP. Максимум {MAX_UPLOAD_MB:.0f} МБ.",
    )

    st.divider()

    effect_keys = list(EFFECTS.keys())
    effect_names = [EFFECTS[k]["name"] for k in effect_keys]

    if "effect" not in st.session_state:
        reset_settings()

    effect_idx = effect_keys.index(st.session_state.effect) if st.session_state.effect in effect_keys else 0
    selected_effect_name = st.selectbox(
        "Эффект",
        options=effect_names,
        index=effect_idx,
        key="effect_select",
    )
    st.session_state.effect = effect_keys[effect_names.index(selected_effect_name)]

    # Параметры эффекта
    st.subheader("Параметры")
    effect = st.session_state.effect

    if effect == "pixel_art":
        st.session_state.pixel_size = st.slider("Размер пикселя", 1, 50, st.session_state.pixel_size)
        st.session_state.n_colors = st.slider("Количество цветов", 0, 256, st.session_state.n_colors, help="0 — без квантования палитры")
        st.session_state.intensity = st.slider("Интенсивность", 0.0, 1.0, st.session_state.intensity, 0.05)
    elif effect == "pencil_sketch":
        st.session_state.intensity = st.slider("Интенсивность", 0.0, 1.0, st.session_state.intensity, 0.05)
        st.session_state.contrast = st.slider("Контраст", 0.5, 2.0, st.session_state.contrast, 0.1)
    elif effect == "coloring_page":
        st.session_state.thickness = st.slider("Толщина контуров", 0.5, 3.0, st.session_state.thickness, 0.1)
        st.session_state.threshold = st.slider("Порог детализации", 0.0, 1.0, st.session_state.threshold, 0.05)
    elif effect == "ascii_art":
        st.session_state.ascii_density = st.slider("Плотность символов", 0.1, 2.0, st.session_state.ascii_density, 0.1)
        st.session_state.ascii_scheme = st.selectbox(
            "Набор символов",
            options=list(ASCII_SCHEMES.keys()),
            index=list(ASCII_SCHEMES.keys()).index(st.session_state.ascii_scheme) if st.session_state.ascii_scheme in ASCII_SCHEMES else 0,
        )
        st.session_state.ascii_width = st.slider("Ширина (символов)", 20, 200, st.session_state.ascii_width)
    elif effect == "grayscale":
        st.session_state.intensity = st.slider("Интенсивность", 0.0, 1.0, st.session_state.intensity, 0.05)

    st.divider()

    col_reset, col_theme = st.columns(2)
    with col_reset:
        if st.button("Сбросить настройки", use_container_width=True):
            reset_settings()
            st.rerun()

# ---------- Основная область ----------
if uploaded_file is None:
    st.info("Загрузите изображение, чтобы начать.")
else:
    try:
        file_bytes = uploaded_file.getvalue()
        image, fmt = validate_image(file_bytes)
        image = apply_exif_orientation(image)

        # Гарантируем RGB/RGBA
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA") if "A" in image.mode else image.convert("RGB")

        col_orig, col_res = st.columns(2)

        with col_orig:
            st.markdown('<div class="compare-label">Оригинал</div>', unsafe_allow_html=True)
            st.image(image, use_container_width=True)

        with col_res:
            st.markdown('<div class="compare-label">Результат</div>', unsafe_allow_html=True)

            with st.spinner("Обработка..."):
                effect_cfg = EFFECTS[st.session_state.effect]
                func = effect_cfg["func"]

                processed_image = None
                ascii_text = None

                if st.session_state.effect == "pixel_art":
                    processed_image = func(
                        image,
                        pixel_size=st.session_state.pixel_size,
                        n_colors=st.session_state.n_colors,
                        intensity=st.session_state.intensity,
                    )
                elif st.session_state.effect == "pencil_sketch":
                    processed_image = func(
                        image,
                        intensity=st.session_state.intensity,
                        contrast=st.session_state.contrast,
                    )
                elif st.session_state.effect == "coloring_page":
                    processed_image = func(
                        image,
                        thickness=st.session_state.thickness,
                        threshold=st.session_state.threshold,
                    )
                elif st.session_state.effect == "ascii_art":
                    ascii_text, processed_image = func(
                        image,
                        density=st.session_state.ascii_density,
                        scheme_name=st.session_state.ascii_scheme,
                        width=st.session_state.ascii_width,
                    )
                elif st.session_state.effect == "grayscale":
                    processed_image = func(
                        image,
                        intensity=st.session_state.intensity,
                    )

                st.session_state.processed_image = processed_image
                st.session_state.ascii_text = ascii_text

            if st.session_state.ascii_text is not None:
                st.code(st.session_state.ascii_text, language=None)
            elif st.session_state.processed_image is not None:
                st.image(st.session_state.processed_image, use_container_width=True)

            st.success("Готово!")

    except Exception as exc:  # noqa: BLE001
        st.markdown(f'<div class="error-box"><b>Ошибка:</b> {exc}</div>', unsafe_allow_html=True)

# ---------- Скачивание ----------
if st.session_state.get("processed_image") is not None or st.session_state.get("ascii_text"):
    st.divider()
    st.subheader("Скачать результат")

    dl_col1, dl_col2 = st.columns(2)

    if st.session_state.get("processed_image") is not None:
        img_bytes = save_image_to_bytes(st.session_state.processed_image, "PNG")
        with dl_col1:
            st.download_button(
                label="Скачать PNG",
                data=img_bytes,
                file_name="result.png",
                mime="image/png",
                use_container_width=True,
            )

    if st.session_state.get("ascii_text") is not None:
        txt_bytes = save_ascii_to_bytes(st.session_state.ascii_text)
        with dl_col2:
            st.download_button(
                label="Скачать TXT",
                data=txt_bytes,
                file_name="ascii_art.txt",
                mime="text/plain",
                use_container_width=True,
            )
