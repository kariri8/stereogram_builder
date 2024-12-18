# -*- coding: utf-8 -*-
"""robt310final.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1boayBwXgGVy3ExPNHD7nfxVSWdggVvEZ
"""

import cv2
import torch
from rembg import remove
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import math
import sys


def get_depth_map(image, model_type="DPT_Hybrid"):
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    midas = torch.hub.load("intel-isl/MiDaS", model_type)
    midas.to(device)
    midas.eval()

    midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
    if model_type == "DPT_Large" or model_type == "DPT_Hybrid":
        transform = midas_transforms.dpt_transform
    else:
        transform = midas_transforms.small_transform

    input_batch = transform(img).to(device)

    with torch.no_grad():
        prediction = midas(input_batch)
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=img.shape[:2],
            mode="bicubic",
            align_corners=False,
        ).squeeze()

    output = prediction.cpu().numpy()
    depth_map_normalized = cv2.normalize(output, None, 0, 255, cv2.NORM_MINMAX)
    depth_map_8bit = depth_map_normalized.astype(np.uint8)

    return depth_map_8bit


def adjust_gamma(image, gamma=0.5):
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)


def process(img, gamma=0.5, remove_bg=True, adj_contr=True, sharpen=True):
    output = img
    if remove_bg:
        output = remove(output, bgcolor=(0, 0, 0, 0))
    output = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
    if adj_contr:
        output = adjust_gamma(output, gamma)
    if sharpen:
        laplacian = cv2.Laplacian(output, cv2.CV_64F)
        laplacian_uint8 = cv2.convertScaleAbs(laplacian)
        output = cv2.addWeighted(output, 1, laplacian_uint8, 0.5, 0)
    return output

def generate_pattern(depth_map):
  size_x, size_y = depth_map.shape
  pattern = np.random.uniform(0,1, (size_y,64,3))
  return pattern


def generate_stereogram(depth_map, pattern):
  E = 3  # Distance between the observer's eyes (inches)
  b = 1.0 # Distance between the near and far plane
  a = 4 # Distance between the autostereogram plane and the near plane
  autostereogram = np.zeros(
        shape=[depth_map.shape[0], depth_map.shape[1], 3],
        dtype=pattern.dtype)
  for row in range(depth_map.shape[0]):
        for column in range(depth_map.shape[1]):
            # If the current column is smaller than the amount of columns
            # in the pattern
            if column < pattern.shape[1]:
                # Copy in the current row/col the pattern
                autostereogram[row][column] = pattern[
                    row % pattern.shape[0]][column]
                continue

            # otherwise, apply the autostereogram algorithm
            grey_value = depth_map[row, column]
            s_on_two = math.floor(
                (
                    ((a - (b * grey_value / 255)) * E) / 2 *
                    (1 + a - (b * grey_value / 255))
                ) + 0.5
            )
            autostereogram[row][column] = autostereogram[
                row][column - pattern.shape[1] + s_on_two]
            if column - pattern.shape[1] - s_on_two > 0:
                autostereogram[row][column] = autostereogram[
                    row][column - pattern.shape[1] - s_on_two]
  return autostereogram

def generate_stereo_gif(giffile, ffilename):
  gif = Image.open(giffile)

  frames = []
  for frame in range(gif.n_frames):
    gif.seek(frame)
    frame_array = np.array(gif.convert("RGB"))
    frame_array = cv2.cvtColor(frame_array, cv2.COLOR_RGB2BGR)
    frames.append(frame_array)

  pattern = generate_pattern(get_depth_map(frames[0]))

  stereogram_frames = []
  for frame in frames:
    depth_map = get_depth_map(frame)
    stereogram = generate_stereogram(depth_map, pattern)
    stereogram = np.clip(stereogram*255, 0, 255)
    stereogram_image = Image.fromarray(np.uint8(stereogram))
    stereogram_frames.append(stereogram_image)

  stereogram_frames[0].save(ffilename,
                          save_all=True,
                          append_images=stereogram_frames[1:],
                          loop=0,  # Loop the GIF
                          duration=gif.info['duration'])

def show_stereogram(filename, ffilename):
    image = cv2.imread(filename)
    depth_map = process(get_depth_map(image))
    pattern = generate_pattern(depth_map)
    stereogram = generate_stereogram(depth_map, pattern)
    stereogram_image = np.clip(stereogram*255, 0, 255)
    stereogram_image = Image.fromarray(np.uint8(stereogram_image))
    stereogram_image.save(ffilename)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))  # Create a figure and 3 subplots
    axes[0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    axes[0].set_title('Original Image')
    axes[0].axis('off')

    axes[1].imshow(depth_map, cmap='gray')
    axes[1].set_title('Depth Map')
    axes[1].axis('off')

    axes[2].imshow(stereogram)
    axes[2].set_title('Stereogram')
    axes[2].axis('off')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python script.py show_stereogram <input_image> <output_image>")
        print("  python script.py generate_stereo_gif <input_gif> <output_gif>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "show_stereogram" and len(sys.argv) == 4:
        input_image = sys.argv[2]
        output_image = sys.argv[3]
        show_stereogram(input_image, output_image)
    elif command == "generate_stereo_gif" and len(sys.argv) == 4:
        input_gif = sys.argv[2]
        output_gif = sys.argv[3]
        generate_stereo_gif(input_gif, output_gif)
    else:
        print("Invalid command or arguments.")
        print("Usage:")
        print("  python script.py show_stereogram <input_image> <output_image>")
        print("  python script.py generate_stereo_gif <input_gif> <output_gif>")