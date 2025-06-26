# ===========================================
# Author: Zeldean
# Project: Movie Manager V2.2
# Date: October 7, 2024
# ===========================================
#   ______      _      _                     
#  |___  /     | |    | |                    
#     / /  ___ | |  __| |  ___   __ _  _ __  
#    / /  / _ \| | / _` | / _ \ / _` || '_ \ 
#   / /__|  __/| || (_| ||  __/| (_| || | | |
#  /_____|\___||_| \__,_| \___| \__,_||_| |_|
# ===========================================

import os
import re
import pickle
import shutil
from tqdm import tqdm
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Set unwanted words and patterns for removal
UNWANTED_WORDS = {
    # Resolutions
    "1080p", "720p", "2160p", "4K",

    # Formats
    "BluRay", "WEBRip", "BRrip", "x264", "AAC5", "YIFY", "YTS", "AM",

    # Other
    "REPACK", "1", "-[YTS", "MX]", "AM]", "[-]", "[ ]", "[", "]"
}

def clean_movie_names(folder_path):
    logging.info("Cleaning movie names in folder %s", folder_path)
    for file_name in tqdm(os.listdir(folder_path), desc="Cleaning movie names"):
        file_path = os.path.join(folder_path, file_name)
        new_file_name = file_name
        
        parts = new_file_name.split('.')
        file_extension = parts[-1] if len(parts) > 1 else ''
        title_parts = parts[:-1]

        cleaned_title_parts = []
        for p in title_parts:
            part_cleaned = False
            
            # Check if the part looks like a year (e.g., 2020)
            if re.match(r'^\d{4}$', p):
                cleaned_title_parts.append(p.strip())  # Keep the year
                continue
            
            for unwanted_word in UNWANTED_WORDS:
                # Add wildcards to the unwanted word
                pattern = f".*{re.escape(unwanted_word)}.*"
                if re.search(pattern, p):
                    # If unwanted word is found, skip this part
                    part_cleaned = True
                    break
    
            if not part_cleaned:
                # If no unwanted word was found, keep this part
                cleaned_title_parts.append(p.strip())  # Trim whitespace

        # Handle edge case where no valid title parts remain
        if not cleaned_title_parts:
            logging.warning("No valid title parts found for file %s. Skipping rename.", file_name)
            continue  # Skip to the next file

        # Replace the original title_parts with the cleaned version
        cleaned_title_parts[-1] = f"({cleaned_title_parts[-1]})"
        new_file_name = f"{' '.join(cleaned_title_parts)}.{file_extension}" if file_extension else ' '.join(cleaned_title_parts)

        # Rename file if new name is different
        if new_file_name != file_name:
            try:
                new_file_path = os.path.join(folder_path, new_file_name)
                os.rename(file_path, new_file_path)
                logging.info("Renamed file %s to %s", file_name, new_file_name)
            except OSError as e:
                logging.error("Error renaming file %s: %s", file_name, e)

    logging.info("Finished cleaning movie names")

def find_video_files(folder_path):
    video_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.mp4', '.mkv', '.avi')):
                video_files.append(os.path.join(root, file))
    return video_files

def move_files_to_folder(file_paths, folder):
    os.makedirs(folder, exist_ok=True)
    for file_path in tqdm(file_paths, desc="Moving files"):
        filename = os.path.basename(file_path)
        new_file_path = os.path.join(folder, filename)

        if os.path.exists(new_file_path):
            dup_file_path = os.path.join(folder, f"[DUP] {filename}")
            if not os.path.exists(dup_file_path):
                shutil.move(file_path, dup_file_path)
        else:
            shutil.move(file_path, new_file_path)

def get_user_input(message):
    user_input = input(message)
    if not user_input:
        try:
            with open('paths.pkl', 'rb') as f:
                paths = pickle.load(f)
            user_input = paths.get(message)
        except (FileNotFoundError, EOFError):
            logging.warning("No saved paths found. Please enter a valid path.")
            user_input = input("Please enter a valid path: ")
    return user_input

def save_paths(paths):
    with open('paths.pkl', 'wb') as f:
        pickle.dump(paths, f)

# Main script logic
if __name__ == "__main__":
    source_folder = get_user_input('Enter the source folder path: ')
    destination_folder = get_user_input('Enter the destination folder path: ')

    # Save the paths for future use
    paths = {
        'Enter the source folder path: ': source_folder,
        'Enter the destination folder path: ': destination_folder
    }
    save_paths(paths)

    video_files = find_video_files(source_folder)
    move_files_to_folder(video_files, destination_folder)
    clean_movie_names(destination_folder)
