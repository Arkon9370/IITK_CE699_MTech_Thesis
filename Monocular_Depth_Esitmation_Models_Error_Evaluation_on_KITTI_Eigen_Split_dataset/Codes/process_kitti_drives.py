import os
import glob
import argparse
from tqdm import tqdm

# --- IMPORTANT ---
# This script imports the 'create_video' function from the first script.
# Make sure 'frames_to_video.py' is in the same directory.
try:
    from frames_to_video import create_video
except ImportError:
    print("Error: Could not import 'create_video' function.")
    print("Please make sure the file 'frames_to_video.py' is in the same directory as this script.")
    exit()

def process_all_drives(kitti_test_root: str, output_dir: str, fps: float):
    """
    Finds all drives in the KITTI test set and converts each one into a video.

    Args:
        kitti_test_root (str): The path to the 'test' directory of the KITTI dataset.
        output_dir (str): The directory where the output videos will be saved.
        fps (float): The frame rate for the output videos.
    """
    print("--- Starting KITTI Drive Processing ---")
    print(f" > Searching for drives in: {kitti_test_root}")
    
    # --- 1. Discover all unique drives ---
    # A drive is identified by its '*_sync' directory.
    drive_paths = glob.glob(os.path.join(kitti_test_root, "*", "*_sync"))
    drive_paths.sort() # Sort to process in a predictable order

    if not drive_paths:
        print(f"Error: No drives (e.g., '*_sync' folders) found in the specified directory.")
        return

    print(f"Found {len(drive_paths)} drives to process.")
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    print(f" > Videos will be saved in: {output_dir}")

    # --- 2. Process each drive individually ---
    for drive_path in tqdm(drive_paths, desc="Overall Progress", unit="drive"):
        
        # Extract a clean name for the drive for logging and filenames
        date_str = os.path.basename(os.path.dirname(drive_path)) # e.g., 2011_09_26
        drive_name = os.path.basename(drive_path).replace('_sync', '') # e.g., 2011_09_26_drive_0002
        
        tqdm.write(f"\nProcessing drive: {drive_name}")

        # --- 3. Locate the RGB image folder for this drive ---
        # Based on your discovery script, the path is 'image_02/data'
        rgb_image_folder = os.path.join(drive_path, "image_02", "data")

        if not os.path.isdir(rgb_image_folder):
            tqdm.write(f"Warning: RGB image folder not found for drive {drive_name}. Skipping.")
            tqdm.write(f"         (Expected at: {rgb_image_folder})")
            continue

        # --- 4. Define the output video path ---
        output_video_filename = f"{drive_name}.mp4"
        output_video_path = os.path.join(output_dir, output_video_filename)

        # --- 5. Call the video creation function ---
        # The 'create_video' function will handle finding, sorting, and converting the frames.
        # KITTI dataset uses '.png' files for RGB images.
        create_video(
            image_folder=rgb_image_folder,
            output_video_path=output_video_path,
            fps=fps,
            image_ext='png'
        )

    print("\n--- All KITTI drives have been processed. ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process KITTI dataset drives into individual videos.")
    parser.add_argument(
        "--kitti_root",
        type=str,
        required=True,
        help="Path to the root of the KITTI Eigen Split dataset (the folder containing 'test')."
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="/mnt/c/Users/arkad/OneDrive/Desktop/Thesis work/kitti eigen split dataset/kitti_videos",
        help="Directory to save the generated videos. Default: '/mnt/c/Users/arkad/OneDrive/Desktop/Thesis work/kitti eigen split dataset/kitti_videos'."
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=10.0,
        help="Frames per second for the output videos. Default: 10.0 (standard for KITTI)."
    )
    
    args = parser.parse_args()
    
    # Define the path to the test set based on the root
    test_set_path = os.path.join(args.kitti_root, "train_copy")
    
    if not os.path.isdir(test_set_path):
        print(f"Error: The 'test' directory was not found inside '{args.kitti_root}'")
        exit()
        
    process_all_drives(test_set_path, args.output_dir, args.fps)