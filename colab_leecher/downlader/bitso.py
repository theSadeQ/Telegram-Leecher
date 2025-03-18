import requests
import os
from tqdm import tqdm
import urllib.parse
import re
import logging
from colab_leecher.utility.helper import clean_filename, extract_filename_from_url # Import helper functions

def write_failed_downloads_to_file(failed_downloads, download_directory):
    """Writes the list of failed URLs and their corresponding filenames to a text file."""
    if not failed_downloads:
        return

    file_path = os.path.join(download_directory, "failed_downloads_bitso.txt")
    try:
        with open(file_path, "w") as f:
            for url in failed_downloads:
                file_name = extract_filename_from_url(url) or url  # Use URL if extraction fails
                f.write(f"{url}, {file_name}\n")
        logging.info(f"List of failed Bitso downloads saved to: {file_path}")
    except Exception as e:
        logging.error(f"Error writing failed downloads to file: {e}")

def download_file_bitso(url, file_name, download_directory, referer_url="", _identity_value="", phpsessid_value=""):
    """Downloads a file from bitso.ir, handling cookies and referer."""
    cookies = {}
    if _identity_value:
        cookies["_identity"] = urllib.parse.quote_plus(_identity_value)  # URL-encode cookies
    if phpsessid_value:
        cookies["PHPSESSID"] = urllib.parse.quote_plus(phpsessid_value)

    headers = {
        "Referer": referer_url,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.99 Safari/537.36"  # Use a standard User-Agent
    }

    try:
        response = requests.get(url, headers=headers, cookies=cookies, stream=True, timeout=60)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024
        full_file_path = os.path.join(download_directory, file_name)
        os.makedirs(os.path.dirname(full_file_path), exist_ok=True)  # Ensure directory exists

        with open(full_file_path, "wb") as file, tqdm(
                total=total_size, unit='B', unit_scale=True, desc=f"Downloading 🚀 {file_name}"
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    file.write(chunk)
                    progress_bar.update(len(chunk))
            logging.info(f"Download complete: {file_name} 🎉")

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to download {file_name}: {e}")
        return False  # Indicate failure
    except Exception as e:
        logging.exception(f"An unexpected error occurred while downloading {file_name}: {e}")
        return False  # Indicate failure

    return True  # Indicate success

def download_multiple_files_bitso(urls, file_names, download_directory, referer_url="", _identity_value="", phpsessid_value=""):
    """Downloads multiple files from bitso.ir."""
    if len(urls) != len(file_names):
        logging.error("Error: The number of URLs and filenames must match! 📏")
        return

    failed_downloads = []
    for url, file_name in zip(urls, file_names):
        if not download_file_bitso(url, file_name, download_directory, referer_url, _identity_value, phpsessid_value):
            failed_downloads.append(url)

    write_failed_downloads_to_file(failed_downloads, download_directory)
