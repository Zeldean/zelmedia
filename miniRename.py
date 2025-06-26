import os
import re
import logging
from tqdm import tqdm

def find_video_files(folder_path):
    video_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.mp4', '.mkv', '.avi')):
                video_files.append(os.path.join(root, file))
    return video_files

for file in find_video_files(r"/home/zeldean/Media/vid/Movies/"):
    file_name = os.path.basename(file)
    new_file_name = file_name.replace(' ', '_')
    new_file_path = os.path.join(os.path.dirname(file), new_file_name)
    if new_file_name != file_name:
        try:
            os.rename(file, new_file_path)
            print(f"Renamed '{file_name}' to '{new_file_name}'")
        except OSError as e:
            logging.error("Error renaming file %s: %s", file_name, e)
