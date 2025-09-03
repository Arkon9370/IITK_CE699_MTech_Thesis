import cv2
import os
import glob
import argparse
from tqdm import tqdm
import re

def create_video(image_folder: str, output_video_path: str, fps: float, image_ext: str):
    """
    Converts a folder of image frames into a video without altering image resolution.

    Args:
        image_folder (str): Path to the folder containing the image frames.
        output_video_path (str): Path to save the output video file (e.g., 'output.mp4').
        fps (float): Frames per second for the output video.
        image_ext (str): The file extension of the images (e.g., 'png', 'jpg').
    """
    print(f"--- Starting Video Creation ---")
    print(f" > Input folder: {image_folder}")
    print(f" > Output video: {output_video_path}")
    print(f" > Frame rate: {fps} FPS")
    print(f" > Image type: .{image_ext}")

    # --- 1. Find and Sort Image Files ---
    # Construct the search pattern
    search_pattern = os.path.join(image_folder, f'*.{image_ext}')
    image_files = glob.glob(search_pattern)

    if not image_files:
        print(f"Error: No images with extension '.{image_ext}' found in '{image_folder}'.")
        return

    # IMPORTANT: Sort the images correctly.
    # Simple string sort can fail (e.g., 'frame10.png' before 'frame2.png').
    # We sort based on the numerical part of the filename for robustness.
    # This assumes filenames like 'frame_001', 'img_12', etc.
    try:
        image_files.sort(key=lambda f: int(re.search(r'\d+', os.path.basename(f)).group()))
        print(f"Found and sorted {len(image_files)} image frames.")
    except (AttributeError, ValueError):
        print("Warning: Could not sort files numerically. Falling back to alphabetical sort.")
        print("For best results, use zero-padded filenames (e.g., frame_0001.png, frame_0002.png).")
        image_files.sort()

    # --- 2. Determine Video Dimensions (CRITICAL STEP) ---
    # Read the first image to get the exact width and height.
    # This ensures the video has the same resolution as the source images.
    first_frame = cv2.imread(image_files[0])
    if first_frame is None:
        print(f"Error: Could not read the first image: {image_files[0]}")
        return
        
    height, width, layers = first_frame.shape
    size = (width, height)
    print(f"Video dimensions will be: {width}x{height}")

    # --- 3. Initialize Video Writer ---
    # Define the codec. 'mp4v' is a good choice for .mp4 files.
    # For .avi files, you might use 'XVID'.
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
    video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, size)

    # --- 4. Write Frames to Video ---
    print("Writing frames to video...")
    for image_path in tqdm(image_files, desc="Processing Frames"):
        frame = cv2.imread(image_path)
        
        # A sanity check to ensure all frames have the same size.
        if frame.shape[0] != height or frame.shape[1] != width:
            print(f"\nError: Image '{os.path.basename(image_path)}' has a different resolution.")
            print(f"Expected {width}x{height}, but got {frame.shape[1]}x{frame.shape[0]}.")
            print("Aborting to prevent a corrupted video file.")
            video_writer.release() # Clean up the partially created file
            os.remove(output_video_path) # Remove the incomplete file
            return

        video_writer.write(frame)

    # --- 5. Finalize ---
    video_writer.release()
    print("\n--- Video Creation Complete ---")
    print(f"Successfully saved video to '{output_video_path}'")


if __name__ == "__main__":
    # Set up the command-line argument parser
    parser = argparse.ArgumentParser(description="Convert a set of image frames into a video without altering resolution.")
    parser.add_argument(
        "-i", "--image_folder",
        type=str,
        required=True,
        help="Path to the folder containing the image frames."
    )
    parser.add_argument(
        "-o", "--output_video",
        type=str,
        default="output.mp4",
        help="Path and filename for the output video. Default: 'output.mp4'."
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=10.0,
        help="Frames per second for the output video. Default: 10.0."
    )
    parser.add_argument(
        "--ext",
        type=str,
        default="png",
        help="File extension of the images (e.g., 'png', 'jpg'). Default: 'png'."
    )

    args = parser.parse_args()

    # Call the main function with the parsed arguments
    create_video(args.image_folder, args.output_video, args.fps, args.ext)