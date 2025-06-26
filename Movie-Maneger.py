# ===========================================
# Author: Zeldean
# Project: Movie Manager V2.3
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
    "1080p", "720p", "2160p", "4K",
    "BluRay", "WEBRip", "BRrip", "x264", "AAC5", "YIFY", "YTS", "AM",
    "REPACK", "1", "-[YTS", "MX]", "AM]", "[-]", "[ ]", "[", "]"
}

def clean_movie_names(folder_path):
    logging.info("Renaming Movie Files")
    print("Renaming Movie Files")
    print("----------------------------------------------------------------------------------------")

    new_file_names = []
    
    movie_files = os.listdir(folder_path)
    total_files = len(movie_files)
    
    for file_name in tqdm(movie_files, desc="Cleaning movie names", total=total_files):
        file_path = os.path.join(folder_path, file_name)
        new_file_name = file_name
        
        parts = new_file_name.split('.')
        file_extension = parts[-1] if len(parts) > 1 else ''
        title_parts = parts[:-1]

        cleaned_title_parts = []
        for p in title_parts:
            part_cleaned = False
            
            if re.match(r'^\d{4}$', p):
                cleaned_title_parts.append(p.strip())
                continue
            
            for unwanted_word in UNWANTED_WORDS:
                pattern = f".*{re.escape(unwanted_word)}.*"
                if re.search(pattern, p):
                    part_cleaned = True
                    break
    
            if not part_cleaned:
                cleaned_title_parts.append(p.strip())

        if not cleaned_title_parts:
            logging.warning("No valid title parts found for file %s. Skipping rename.", file_name)
            continue

        if len(cleaned_title_parts[-1]) == 4:
            new_file_name = f"{'_'.join(cleaned_title_parts)}.{file_extension}" if file_extension else ' '.join(cleaned_title_parts)

        if new_file_name != file_name:
            new_file_names.append(new_file_name)
            print(f"{len(new_file_names)}-\t{new_file_name}")  # Print new movie name
            try:
                new_file_path = os.path.join(folder_path, new_file_name)
                print(f"Renaming {file_name} to {new_file_name}")
                os.rename(file_path, new_file_path)
            except OSError as e:
                logging.error("Error renaming file %s: %s", file_name, e)

    print("====================================================")


def find_video_files(folder_path):
    video_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.mp4', '.mkv', '.avi')):
                video_files.append(os.path.join(root, file))
    return video_files

def move_files_to_folder(file_paths, folder):
    print("Moving Movie Files")
    print("----------------------------------------------------------------------------------------")
    total_files = len(file_paths)

    for file_path in tqdm(file_paths, desc="Moving files", total=total_files):
        filename = os.path.basename(file_path)
        new_file_path = os.path.join(folder, filename)

        if os.path.exists(new_file_path):
            dup_file_path = os.path.join(folder, f"[DUP] {filename}")
            if not os.path.exists(dup_file_path):
                shutil.move(file_path, dup_file_path)
        else:
            shutil.move(file_path, new_file_path)
        print(f"{file_paths.index(file_path) + 1}-\t{filename}")  # Print moved movie name

    print("====================================================")

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

    paths = {
        'Enter the source folder path: ': source_folder,
        'Enter the destination folder path: ': destination_folder
    }
    save_paths(paths)

    video_files = find_video_files(source_folder)
    move_files_to_folder(video_files, destination_folder)
    clean_movie_names(destination_folder)
