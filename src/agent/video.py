from moviepy.editor import VideoFileClip
import numpy as np
from datetime import timedelta
from pathlib import Path
import math
from PIL import Image, ImageChops
from agent.logging import logger


def format_timedelta(td):
    """Utility function to format timedelta objects in a cool way (e.g 00:00:20.05)
    omitting microseconds and retaining milliseconds"""
    result = str(td)
    try:
        result, ms = result.split(".")
    except ValueError:
        return (result + ".00").replace(":", "-")
    ms = int(ms)
    ms = round(ms / 1e4)
    return f"{result}.{ms:02}".replace(":", "-")


def calculate_rmse(image1_path, image2_path):
    """
    Calculate the Root Mean Square Error (RMSE) between two images.
    """
    with Image.open(image1_path) as img1, Image.open(image2_path) as img2:
        # Convert both images to a consistent format (e.g., RGBA)
        img1 = img1.convert("RGBA")
        img2 = img2.convert("RGBA")

        # Ensure the images have the same size for comparison
        if img1.size != img2.size:
            return float(
                "inf"
            )  # Consider images with different sizes as completely different

        # Calculate the difference between the images
        diff = ImageChops.difference(img1, img2)

        # Calculate the squared difference of each pixel
        h = diff.histogram()
        sum_of_squares = sum(value * ((idx % 256) ** 2) for idx, value in enumerate(h))

        # Calculate the RMSE
        rmse = math.sqrt(sum_of_squares / (img1.size[0] * img1.size[1]))
        return rmse


def keep_unique_images(directory, threshold=5.0):
    """
    Find and keep only unique images in a directory based on pixel content similarity.
    Delete images that are almost identical to others.
    """
    unique_images = []
    image_paths = list(Path(directory).glob("**/*.png"))
    image_paths.extend(list(Path(directory).glob("**/*.jpeg")))
    image_paths.extend(list(Path(directory).glob("**/*.jpg")))
    image_paths.extend(list(Path(directory).glob("**/*.webp")))

    # Loop through all PNG files and compare them pairwise
    while image_paths:
        current_image = image_paths.pop(0)
        unique_images.append(current_image)

        for other_image in image_paths[:]:
            try:
                # Calculate the RMSE between the current image and another
                rmse = calculate_rmse(current_image, other_image)

                # If RMSE is below the threshold, consider them almost identical
                if rmse < threshold:
                    logger.debug(
                        f"Deleting nearly identical image: {other_image} (RMSE: {rmse:.2f})"
                    )
                    other_image.unlink()
                    image_paths.remove(other_image)
            except Exception as e:
                logger.error(f"Error comparing {current_image} and {other_image}: {e}")

    return unique_images


def extract_frames(video_file: Path, frames_per_second: int = 1):
    # load the video clip
    video_clip = VideoFileClip(str(video_file))

    # if the SAVING_FRAMES_PER_SECOND is above video FPS, then set it to FPS (as maximum)
    saving_frames_per_second = min(video_clip.fps, frames_per_second)
    # if SAVING_FRAMES_PER_SECOND is set to 0, step is 1/fps, else 1/SAVING_FRAMES_PER_SECOND
    step = (
        1 / video_clip.fps
        if saving_frames_per_second == 0
        else 1 / saving_frames_per_second
    )

    # iterate over each possible frame
    for current_duration in np.arange(0, video_clip.duration, step):
        # format the file name and save it
        frame_duration_formatted = format_timedelta(timedelta(seconds=current_duration))
        frame_filename = video_file.parent / f"frame{frame_duration_formatted}.png"
        # save the frame with the current duration
        video_clip.save_frame(frame_filename, current_duration)

    keep_unique_images(video_file.parent)
