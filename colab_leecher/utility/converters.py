import os
import re
import shutil
import logging
import zipfile
import tarfile
import rarfile  # Ensure rarfile is installed: pip install rarfile
from py7zr import SevenZipFile, is_7zfile  # Ensure py7zr is installed: pip install py7zr
from natsort import natsorted
from colab_leecher.utility.variables import BOT, Paths
from colab_leecher.utility.helper import fileType, videoExtFix
from subprocess import run, PIPE, STDOUT


def splitArchive(input_file: str, part_size: int = 524288000):  # Default to 500 MB parts.
    """Splits a file (zip or otherwise) into multiple parts.
    Uses 7z for splitting as it is more reliable.
    """
    if not os.path.exists(input_file):
        logging.error(f"Input file does not exist: {input_file}")
        return

    file_name = os.path.basename(input_file)
    file_dir = os.path.dirname(input_file)
    base_name, _ = os.path.splitext(file_name)
    output_dir = os.path.join(file_dir, f"{base_name}_parts")  # Subdirectory for parts
    os.makedirs(output_dir, exist_ok=True)

    # Use 7z command-line for splitting
    command = [
        "7z",
        "a",  # Add to archive
        "-v" + sizeUnit(part_size),  # Volume size (e.g., "500m")
        "-mx0",  # No compression (store only) for speed
        os.path.join(output_dir, f"{base_name}.7z"),
        input_file,
    ]
    process = run(command, stdout=PIPE, stderr=STDOUT, text=True, cwd=file_dir) # added cwd so 7z can run in the same directory as the file
    if process.returncode != 0:
        logging.error(f"7z splitting failed:\n{process.stdout}")
        return None  # Or raise an exception if you prefer

    logging.info(f"File split into parts in: {output_dir}")
    return output_dir #return the output dir



def archive(dir_path: str, is_split: bool, remove: bool):
    """Archives files in a folder, optionally splitting the archive."""

    if not os.path.exists(dir_path):
        logging.error(f"Directory does not exist: {dir_path}")
        return

    if not os.listdir(dir_path):
        logging.error(f"Directory is empty: {dir_path}")
        return

    dir_name = os.path.basename(dir_path)
    zip_path = os.path.join(Paths.temp_zpath, f"{dir_name}.zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_STORED, allowZip64=True) as zf:
        for dirname, _, files in os.walk(dir_path):
            for file in natsorted(files):
                file_path = os.path.join(dirname, file)
                rel_path = os.path.relpath(file_path, dir_path)  # Path relative to the directory being zipped
                zf.write(file_path, rel_path)  # Use the *relative* path inside the zip

    if remove:
        shutil.rmtree(dir_path)  # Remove the original directory

    if is_split:
        #split_file(zip_path, var.LEECH_SPLIT_SIZE)
        splitArchive(zip_path, BOT.LEECH.SPLIT_SIZE) #changed to split using 7z
        if os.path.exists(zip_path):
            os.remove(zip_path)


def extract(file_path: str, remove: bool = False):
    """Extracts various archive types (zip, rar, tar, 7z) to a designated directory."""
    if not os.path.exists(file_path):
        logging.error(f"File does not exist: {file_path}")
        return False, None

    file_name = os.path.basename(file_path)
    extract_path = Paths.temp_unzip_path  # Consistent extraction path
    # Determine archive type and extract

    try:
        if file_name.endswith(".zip"):
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall(extract_path)
        elif file_name.endswith((".tar.gz", ".tgz", ".tar")):
            with tarfile.open(file_path, "r") as tar_ref:
                # Safe extraction (handling absolute paths and "..")
                def is_within_directory(directory, target):
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                    prefix = os.path.commonprefix([abs_directory, abs_target])
                    return prefix == abs_directory

                for member in tar_ref.getmembers():
                    member_path = os.path.join(extract_path, member.name)
                    if not is_within_directory(extract_path, member_path):
                        logging.warning(f"Skipping unsafe tar entry: {member.name}")
                        continue
                    tar_ref.extract(member, extract_path)

        elif file_name.endswith(".rar"):
            try:
                with rarfile.RarFile(file_path, "r") as rar_ref:
                    rar_ref.extractall(extract_path)
            except rarfile.NeedFirstVolume:  # Handle multi-part RAR
                logging.warning(f"Multi-part RAR detected, attempting extraction: {file_name}")
                try:
                    command = ["unrar", "x", file_path, extract_path]
                    process = run(command, stdout=PIPE, stderr=STDOUT, text=True)
                    if process.returncode != 0:
                        logging.error(f"unrar extraction failed: {process.stdout}")
                        return False, None # Return None if error occurred
                except FileNotFoundError:
                    logging.error("unrar command not found. Please install unrar (e.g., apt install unrar).")
                    return False, None
        elif is_7zfile(file_path):
            with SevenZipFile(file_path, mode="r") as seven_z:
                seven_z.extractall(extract_path)

        else:
            logging.warning(f"Unsupported archive format: {file_name}")
            return False, None # Indicate failure


    except Exception as e:
        logging.exception(f"Error during extraction of {file_name}: {e}")
        return False, None

    if remove:
        os.remove(file_path)

    logging.info(f"Extracted {file_name} to {extract_path}")
    return True, extract_path

def sizeChecker(file_path: str, remove: bool) -> bool:
    """Checks if the file size exceeds the split size.
       Returns `True` if the file needed to be split/zipped, `False` otherwise.
    """
    if os.path.getsize(file_path) > BOT.LEECH.SPLIT_SIZE:
        file_name = os.path.basename(file_path)
        base_name, ext = os.path.splitext(file_name)

        if BOT.Options.equal_splits:
            logging.info(f"Splitting: {file_name}...")
            dir_path = splitArchive(file_path, BOT.LEECH.SPLIT_SIZE) # split with 7z

        else: #.zip and split
            dir_path = os.path.join(os.path.dirname(file_path), base_name)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            shutil.move(file_path, os.path.join(dir_path, file_name))
            logging.info(f"Zipping and Splitting: {file_name}...")
            archive(dir_path, is_split=True, remove=remove)

        return True  # Indicates that splitting/zipping occurred

    else:
        return False # No split

def sizeUnit(size):
    B = 1024
    KB = B * 1024
    MB = KB * 1024
    GB = MB * 1024
    TB = GB * 1024
    if size >= TB:
        size = str(round(size / TB, 2)) + 'T'
    elif size >= GB:
        size = str(round(size / GB, 2)) + 'G'
    elif size >= MB:
        size = str(round(size / MB, 2)) + 'M'
    elif size >= KB:
        size = str(round(size / KB, 2)) + 'K'
    else :
        size = str(round(size, 2)) + 'B'
    return size

async def videoConverter(file_path: str):
    output_path = file_path + ".converted.mp4"  # Use a consistent, temporary name
    try:
        if fileType(file_path) == 'vid':
            if not file_path.lower().endswith(".mp4"):
                command = [
                "ffmpeg",
                "-i", file_path,
                "-c:v", "libx264",      # H.264 video codec (widely compatible)
                "-preset", "medium",    # Encoding speed/quality tradeoff
                "-crf", "23",          # Constant Rate Factor (quality, lower=better, 18-28 is a good range)
                "-c:a", "aac",        # AAC audio codec
                "-b:a", "128k",        # Audio bitrate
                "-movflags", "+faststart",  # Optimize for streaming
                output_path,
                "-y", # Overwrite output
                ]

                process = run(command, stdout=PIPE, stderr=STDOUT, text=True)

                if process.returncode != 0:
                    logging.error(f"ffmpeg conversion failed:\n{process.stdout}")
                    return file_path  # Return original file on failure

                if os.path.exists(output_path):
                    os.remove(file_path)  # Remove the original file
                    videoExtFix(os.path.dirname(output_path)) # Rename to mp4
                    return  os.path.splitext(output_path)[0] + ".mp4"  # Return the converted file path
                else:
                    logging.error(f"ffmpeg conversion failed: Output file not found: {output_path}")
                    return file_path

            else: # already mp4
                return file_path

    except FileNotFoundError:
        logging.error("ffmpeg not found.  Please ensure ffmpeg is installed and in your system's PATH.")
        return file_path # Return original
    except Exception as e:
        logging.exception(f"Error during video conversion: {e}")
        return file_path  # Return original if error
