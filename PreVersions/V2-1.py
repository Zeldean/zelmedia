#  * ===========================================
#  * Author: Zeldean
#  * Project: Movie Maneger V2.0
#  * Date: October 7, 2024
#  * ===========================================
#  *   ______      _      _                     
#  *  |___  /     | |    | |                    
#  *     / /  ___ | |  __| |  ___   __ _  _ __  
#  *    / /  / _ \| | / _` | / _ \ / _` || '_ \ 
#  *   / /__|  __/| || (_| ||  __/| (_| || | | |
#  *  /_____|\___||_| \__,_| \___| \__,_||_| |_|
#  *   
#  * ===========================================

import os
import re
import pickle
import shutil
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO)

UNWANTED_WORDS = {
    "1-[YTS", "-[YTS", "[YTS", "MX]", "AG]", "AM]", "LT]", "REPACK", "WEBRip",
    "720p", "1080P", "2160p",
    "BluRay", "IMAX", "WEBRip", "BrRip", "WEB",
    "x264", "x265", "YIFY", "AAC5","+HI", "AAC", "REPACK", "10bit", ""
    ".mp4", ".mkv", ".avi",
    "mp4", "mkv", "avi",
    "4K", "x265", "YIFY", "()", "(", ")",
    "-", "_", ".", ",",
    "YTSAG", "Deceit"
}

def clean_movie_names(folder_path):
    logging.info("Cleaning movie names in folder %s", folder_path)
    for file_name in tqdm(os.listdir(folder_path), desc="Cleaning movie names"):
        file_path = os.path.join(folder_path, file_name)
        new_file_name = file_name

        # Replace dots with spaces
        new_file_name = new_file_name.replace(".", " ")

        # Remove unwanted words
        for word in UNWANTED_WORDS:
            escaped_word = re.escape(word)
            new_file_name = re.sub(escaped_word, "", new_file_name, flags=re.IGNORECASE).strip()
            logging.debug("Removed unwanted word %s from file %s", word, file_name)

        # Add parentheses to the year
        words = new_file_name.split()
        if len(words) > 1 and words[-1].isdigit() and len(words[-1]) == 4:
            words[-1] = f"({words[-1]})"
            new_file_name = " ".join(words)

        # Remove extra spaces and add ".mp4" extension
        new_file_name = " ".join(new_file_name.split())
        new_file_name += ".mp4"

        # Rename the file if the new name is different
        if new_file_name != file_name:
            new_file_path = os.path.join(folder_path, new_file_name)
            os.rename(file_path, new_file_path)
            logging.info("Renamed file %s to %s", file_name, new_file_name)

    logging.info("Finished cleaning movie names")

def find_video_files(folder_path, count):
    logging.info("Finding video files in folder %s", folder_path)
    video_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.mp4', '.mkv', '.avi')):
                video_files.append(os.path.join(root, file))
                count += 1
                logging.debug("Found video file %s", file)
    logging.info("Found %d video files", count)
    return video_files, count

def move_files_to_folder(file_paths, folder):
    logging.info("Moving files to folder %s", folder)
    # Create the destination folder if it doesn't exist
    os.makedirs(folder, exist_ok=True)

    for file_path in tqdm(file_paths, desc="Moving files"):
        # Construct the new file path in the destination folder
        filename = os.path.basename(file_path)
        new_file_path = os.path.join(folder, filename)

        # Check if the file already exists in the destination folder
        if os.path.exists(new_file_path):
            # Add [DUP] to the filename
            dup_filename = f"[DUP] {filename}"
            dup_file_path = os.path.join(folder, dup_filename)

            # Check if the [DUP] file also exists
            if os.path.exists(dup_file_path):
                logging.warning("File %s already exists in destination folder, skipping", filename)
                continue

            # Move the file with the [DUP] prefix
            try:
                shutil.move(file_path, dup_file_path)
                logging.info("Moved file %s to %s", file_path, dup_file_path)
            except:
                shutil.copy(file_path, dup_file_path)
                logging.warning("Error moving file %s, copying instead", file_path)
        else:
            # Move the file normally
            try:
                shutil.move(file_path, new_file_path)
                logging.info("Moved file %s to %s", file_path, new_file_path)
            except:
                shutil.copy(file_path, new_file_path)
                logging.warning("Error moving file %s, copying instead", file_path)

    logging.info("Finished moving files")

def get_user_input(message):
    user_input = input(message)
    if user_input == '':
        with open('paths.pkl', 'rb') as f:
            paths = pickle.load(f)
        user_input = paths[message]
    return user_input

def save_paths(paths):
    with open('paths.pkl', 'wb') as f:
        pickle.dump(paths, f)

source_folder = get_user_input('Enter the source folder path: ')
destination_folder = get_user_input('Enter the destination folder path: ')

# Save the paths for future use
paths = {
    'Enter the source folder path: ': source_folder,
    'Enter the destination folder path: ': destination_folder
}
save_paths(paths)

count = 0
video_files, count = find_video_files(source_folder, count)
print(f"Found {count} video files:")
print("======================================")
for file in video_files:
    print(file)
print("======================================")

move_files_to_folder(video_files, destination_folder)

clean_movie_names(destination_folder)
