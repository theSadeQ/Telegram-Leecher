import requests
import os
from tqdm import tqdm
import urllib.parse
import re
import logging


def write_failed_downloads_to_file(failed_downloads, downloader_name, download_directory):
    """Writes the list of failed URLs and their corresponding filenames (or extracted names) to a text file."""
    if not failed_downloads:
        return  # Nothing to write

    file_path = os.path.join(download_directory, f"failed_downloads_{downloader_name}.txt")
    try:
        with open(file_path, "w") as f:
            for url in failed_downloads:
                # Try to extract a filename; use a placeholder if it fails
                file_name = extract_filename_from_url(url) or "unknown_filename"
                f.write(f"{url}, {file_name}\n")
        logging.info(f"List of failed {downloader_name} downloads saved to: {file_path}")
    except Exception as e:
        logging.error(f"Error writing failed downloads to file: {e}")



def clean_filename(filename):
    """Cleans filenames by removing/replacing invalid characters."""
    try:
        filename = urllib.parse.unquote(filename, encoding='utf-8')  # Decode URL-encoded characters
    except Exception:
        pass  # Ignore decoding errors

    filename = filename.replace('%20', ' ').replace('?', '').replace('&', '_and_').replace('#', '_hash_').replace('=', '_equals_')
    cleaned_filename = re.sub(r'[^\w\.\-]', '.', filename)
    cleaned_filename = re.sub(r'\.{2,}', '.', cleaned_filename)
    cleaned_filename = cleaned_filename.strip('._')
    cleaned_filename = cleaned_filename.replace("_", "").replace("-", "")
    return cleaned_filename


def extract_filename_from_url(url):
    """Extracts and cleans the filename from a given URL."""
    try:
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        filename = os.path.basename(path)
        return clean_filename(filename)
    except Exception as e:
        logging.warning(f"Error extracting filename from URL: {e}")
        return None


def download_file_deltaleech(url, file_name, cf_clearance, download_directory):
    """Downloads a single file with improved error handling and progress bar."""
    cookies = {"cf_clearance": cf_clearance} if cf_clearance else {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": url
    }

    try:
        response = requests.get(url, headers=headers, cookies=cookies, stream=True, timeout=30)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024

        full_file_path = os.path.join(download_directory, file_name)
        os.makedirs(os.path.dirname(full_file_path), exist_ok=True)

        with open(full_file_path, "wb") as file, tqdm(
                total=total_size,
                unit='B',
                unit_scale=True,
                desc=f"Downloading 🚀 {os.path.basename(file_name)}",
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    file.write(chunk)
                    progress_bar.update(len(chunk))
            logging.info(f"{file_name} Download complete! 🎉")

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to download {file_name}: {e}")
        if isinstance(e, requests.exceptions.Timeout):
            logging.info(" (The request timed out. ⏳)")
        elif isinstance(e, requests.exceptions.HTTPError):
            logging.info(f" (HTTP Error: {response.status_code} - {response.reason} 🚫)")
        return False  # Indicate failure
    except Exception as e:
        logging.exception(f"An unexpected error occurred while downloading {file_name}: {e}")
        return False  # Indicate failure

    return True  # Indicate success


def download_multiple_files_deltaleech(urls, file_names, cf_clearance, download_directory):
    """Downloads multiple files from DeltaLeech, handling potential errors."""
    if len(urls) != len(file_names):
        logging.error("Error: The number of URLs and filenames must match! 📏")
        return

    failed_downloads = []
    for url, file_name in zip(urls, file_names):
        if not download_file_deltaleech(url, file_name, cf_clearance, download_directory):
            failed_downloads.append(url)

    write_failed_downloads_to_file(failed_downloads, "deltaleech", download_directory)
