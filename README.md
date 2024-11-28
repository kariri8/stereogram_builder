
# Stereogram Generator

This project generates stereograms and stereogram-based GIFs using depth maps extracted from input images or GIF frames. The depth maps are processed and converted into stereograms, which can be saved or displayed.

---

## Features

- Generate stereograms from input images.
- Create animated stereogram GIFs from input GIFs.
- Visualize depth maps alongside stereograms.

---

## Requirements

To run this project, ensure you have the following installed:

- Python 3.8 or later
- Libraries:
  - `opencv-python`
  - `torch`
  - `rembg`
  - `numpy`
  - `matplotlib`
  - `Pillow`
  - `onnxruntime`
  - `timm`

---

## Installation

1. Clone the repository or download the script:
   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. Install the required libraries:
   ```bash
   pip install opencv-python torch rembg numpy matplotlib Pillow onnxruntime timm
   ```

---

## Usage

### Running the Script

The script provides two primary functions:

#### 1. **Generate a Stereogram**
Generate a stereogram from an input image:
   ```bash
   python stereogram_generator.py show_stereogram <input_image> <output_image>
   ```
   - `<input_image>`: Path to the input image file (e.g., `example.jpg`).
   - `<output_image>`: Path to save the output stereogram image (e.g., `stereogram.jpg`).

#### 2. **Generate a Stereogram GIF**
Create an animated stereogram from an input GIF:
   ```bash
   python stereogram_generator.py generate_stereo_gif <input_gif> <output_gif>
   ```
   - `<input_gif>`: Path to the input GIF file (e.g., `example.gif`).
   - `<output_gif>`: Path to save the output stereogram GIF (e.g., `stereogram.gif`).

---

## Examples

### Example 1: Generating a Stereogram
To generate a stereogram from an image named `example.jpg` and save it as `output_stereogram.jpg`:
```bash
python stereogram_generator.py show_stereogram example.jpg output_stereogram.jpg
```

### Example 2: Creating a Stereogram GIF
To create a stereogram GIF from an input animation `input_animation.gif` and save it as `output_animation.gif`:
```bash
python stereogram_generator.py generate_stereo_gif input_animation.gif output_animation.gif
```

---

## Notes

- Ensure your input files are valid images or GIFs.
- The `show_stereogram` function will display the original image, depth map, and stereogram using Matplotlib.
- The `generate_stereo_gif` function will create an animated stereogram GIF using all frames in the input GIF.

