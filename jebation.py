from typing import List
from PIL import Image, ImageSequence
from math import cos, radians
from traceback import print_exc
import argparse

import sys
import numpy as np


def rainbow_angle(number: float) -> float:
    """Sinusoidal function."""
    return abs(cos(radians(number)))


def rainbow_list(image: Image.Image, color_change_rate: float) -> List[Image.Image]:
    """Make List of rainbow image."""
    frames = ImageSequence.all_frames(image)
    if len(frames) > 1:
        np_frames = []
        for frame in frames:
            np_frame = np.array(frame.convert("RGBA"))
            np_frames.append((np_frame, frame.info))
    else:
        np_image = np.array(image.convert("RGBA"))
        np_frames = [(np.copy(np_image), image.info) for _ in range(30)]

    colored_frames = []
    for i, (np_frame, info) in enumerate(np_frames):
        change_color = i * color_change_rate / len(np_frames)
        alpha_channel = np_frame[..., 3]
        np_frame[..., 0] = np_frame[..., 0] * rainbow_angle(change_color + 45)
        np_frame[..., 1] = np_frame[..., 1] * rainbow_angle(change_color + 90)
        np_frame[..., 2] = np_frame[..., 2] * rainbow_angle(change_color)
        np_frame[..., 3] = alpha_channel  # Preserve original alpha channel
        img = Image.fromarray(np_frame)
        img.info = info
        colored_frames.append(img)
    return colored_frames


def rainbow(path: str, dest: str, color_change_rate: float) -> None:
    """Make rainbow image of image at `path`."""
    image = Image.open(path)
    frames = rainbow_list(image, color_change_rate)
    frames[0].save(
        dest,
        background=frames[0].info.get("background", 255),
        format='GIF',
        version="GIF89a",
        save_all=True,
        append_images=frames[1:],
        optimize=False,
        duration=[frame.info.get("duration", 40) for frame in frames],
        loop=image.info.get("loop", 0),
        palette=Image.WEB,
        disposal=[2 for _ in frames],  # Use disposal=2 to clear out old frames
        comment="Made by Dashstrom"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Apply a rainbow effect to an image.')
    parser.add_argument('paths', metavar='PATH', type=str, nargs='+',
                        help='one or more paths to the images to be processed')
    parser.add_argument('--rate', dest='color_change_rate', type=float, default=180.0,
                        help='the rate at which the color changes (default: 180.0)')

    args = parser.parse_args()

    for progress, path in enumerate(args.paths, start=1):
        print(f"\rConvert {path} ({progress}/{len(args.paths)})")
        try:
            rainbow(path, path + ".rainbow.gif", args.color_change_rate)
        except Exception:
            print_exc()
