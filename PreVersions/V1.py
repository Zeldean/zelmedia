#  * ===========================================
#  * Author: Zeldean
#  * Project: Movie Maneger V1.0
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

UNWANTED_WORDS = {
    "1-[YTS", "-[YTS", "[YTS", "MX]", "AG]", "AM]", "LT]", "REPACK", "WEBRip",
    "[5.1]", "[5 1]", 
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
    """
    Cleans movie names in the given folder by removing unwanted words and adding parentheses to the year.

    :param folder_path: The path to the folder containing the movie files
    """

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        new_file_name = file_name

        # Replace dots with spaces
        new_file_name = new_file_name.replace(".", " ")

        # Remove unwanted words
        for word in UNWANTED_WORDS:
            escaped_word = re.escape(word)
            new_file_name = re.sub(escaped_word, "", new_file_name, flags=re.IGNORECASE).strip()

        # Add parentheses to the year
        words = new_file_name.split()
        if len(words) > 1 and words[-1].isdigit() and len(words[-1]) == 4:
            words[-1] = f"({words[-1]})"
            new_file_name = " ".join(words)

        # Remove extra spaces and add ".mp4" extension
        new_file_name = " ".join(new_file_name.split())
        new_file_name += ".mp4"

        # Rename the file if the new name is different
        if new_file_name!= file_name:
            new_file_path = os.path.join(folder_path, new_file_name)
            os.rename(file_path, new_file_path)

    print("Movie names cleaned")

def find_video_files(folder_path, count):
    """
    Find all the video files in a folder and sub-folders.

    :param folder_path: The path to the folder
    :param count: The varible to store the number of video files found
    """
    video_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.mp4', '.mkv', '.avi')):
                video_files.append(os.path.join(root, file))
                count += 1

    return video_files, count

def move_files_to_folder(file_paths, folder):
    """
    Moves all files in the given list to a new folder.

    :param file_paths: A list of file paths to be moved
    :param folder: The path to the destination folder
    """
    # Create the destination folder if it doesn't exist
    os.makedirs(destination_folder, exist_ok=True)

    for file_path in file_paths:
        # Construct the new file path in the destination folder
        new_file_path = os.path.join(destination_folder, os.path.basename(file_path))

        # Move the file to the new location
        try:
            shutil.move(file_path, new_file_path)
        except:
            shutil.copy(file_path, new_file_path)

    print(f"Moved {len(file_paths)} files to {folder}")

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
