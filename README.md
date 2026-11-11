# Image Art Converter

English | [Русский](README.ru.md)

A local Python + Streamlit web application for converting images into artistic styles. Suitable for a GitHub portfolio: all code is open, algorithms are implemented from scratch without neural networks or external APIs.

## Badges

[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests: pytest](https://img.shields.io/badge/tests-pytest-blue.svg)](tests/)

## Features

Upload an image (PNG, JPG, JPEG, WEBP) and apply one of the following effects:

| Effect | Description | Controls |
|---|---|---|
| Grayscale | Conversion to grayscale using the ITU-R BT.601 luminance formula | Intensity |
| Pixel Art | Resolution reduction with NEAREST upscaling and optional palette quantization | Pixel size, color count, intensity |
| Pencil Sketch | Classic color-dodge algorithm (inversion + Gaussian blur + division) | Intensity, contrast |
| Coloring Page | Edge detection (Sobel), normalization, and threshold binarization | Contour thickness, detail threshold |
| ASCII Art | Pixel brightness mapped to ASCII characters | Density, character set, output width |

### Export
- Graphical effects: download result as **PNG**.
- ASCII Art: download result as **TXT**.

### Interface
- Dark / light theme switch.
- Sidebar with controls.
- Side-by-side original vs. result comparison.
- Sliders, toggles, settings reset button.
- Processing indicator and error notifications.

All processing runs locally. No neural networks, external APIs, or cloud services are used.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.11+ | Core application |
| Streamlit | Web interface |
| Pillow (PIL) | Image loading and processing |
| NumPy | Pixel array manipulation |
| OpenCV (headless) | Blur, Sobel edge detection, morphology |
| pytest | Automated testing |

## Architecture

Processing algorithms are independent of Streamlit and can be imported and tested separately.

```
Image Art Converter/
├── app.py                    # Streamlit entry point and UI
├── pyproject.toml            # Project metadata and dependencies
├── README.md                 # English documentation
├── README.ru.md              # Russian documentation
├── LICENSE                   # MIT License
├── .gitignore                # Git ignore rules
├── .editorconfig             # Editor conventions
├── src/
│   └── image_converter/
│       ├── __init__.py       # Package init and effect registry
│       ├── processing/
│       │   ├── __init__.py   # Effects registry (EFFECTS)
│       │   ├── grayscale.py  # Grayscale conversion
│       │   ├── pixel_art.py  # Pixel art effect
│       │   ├── pencil_sketch.py  # Pencil sketch (color dodge)
│       │   ├── coloring_page.py  # Contour coloring page
│       │   └── ascii_art.py  # ASCII art conversion
│       └── utils/
│           ├── __init__.py
│           ├── validation.py # File validation and limits
│           ├── exif.py       # EXIF orientation handling
│           └── saving.py     # Save image/ASCII to bytes
├── tests/
│   ├── conftest.py           # Pytest fixtures
│   └── test_processing.py    # Algorithm tests (46 tests)
├── assets/                   # Reserved for local UI resources
└── docs/
    └── screenshots/          # UI screenshots
```

## Installation

### Requirements

- Python 3.11 or newer
- pip

### Windows PowerShell

```powershell
# Clone the repository
git clone <repository-url>
cd "Image Art Converter"

# Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -e .
```

### Linux / macOS

```bash
# Clone the repository
git clone <repository-url>
cd "Image Art Converter"

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .
```

## Usage

Run the application:

```bash
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`.

1. Upload an image via the sidebar (PNG, JPG, JPEG, WEBP, max 20 MB).
2. Select an effect from the sidebar.
3. Adjust the effect parameters with the sliders.
4. Compare the original and the result side by side.
5. Download the result (PNG for graphical effects, TXT for ASCII Art).

No additional configuration is required; the application works out of the box.

## Testing

The project includes 46 automated tests covering every processing algorithm, RGB and RGBA images, various image sizes, invalid/empty input, and result saving.

```bash
pytest
```

With coverage:

```bash
pytest --cov=src/image_converter
```

All 46 tests pass.

## Configuration

No `.env` file or environment variables are required. The application runs without additional setup.

Security limits are defined in `src/image_converter/utils/validation.py`:

- Maximum uploaded file size: 20 MB
- Maximum pixel count: 64 MP (protection against excessive RAM usage)
- Supported formats: PNG, JPEG, WEBP

## Limitations

- Maximum uploaded file size: 20 MB.
- Maximum image size: 64 megapixels.
- Supported input formats: PNG, JPEG, WEBP.
- Graphical results can be downloaded as PNG; ASCII Art as TXT.
- No neural networks or external APIs are used; effects are deterministic classical algorithms.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
