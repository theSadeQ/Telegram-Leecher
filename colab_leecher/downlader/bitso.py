import requests
import os
from tqdm import tqdm
import urllib.parse
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
                file_name = extract_filename_from_url(url) or "unknown_filename"  #  Assumes you might want to use extract_filename_from_url (from deltaleech.py) here.  If not, just use the URL directly.
                f.write(f"{url}, {file_name}\n")
        logging.info(f"List of failed {downloader_name} downloads saved to: {file_path}")
    except Exception as e:
        logging.error(f"Error writing failed downloads to file: {e}")



def download_file_bitso(url, file_name, download_directory, referer_url="", _identity_value="", phpsessid_value=""):
    """Downloads a single file from bitso.ir, handling cookies and referer."""
    cookies = {}
    if _identity_value:
        cookies["_identity"] = urllib.parse.quote_plus(_identity_value)
    if phpsessid_value:
        cookies["PHPSESSID"] = urllib.parse.quote_plus(phpsessid_value)

    headers = {
        "Referer": referer_url,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.99 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, cookies=cookies, stream=True, timeout=60)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024
        full_file_path = os.path.join(download_directory, file_name)
        os.makedirs(os.path.dirname(full_file_path), exist_ok=True)

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
        if isinstance(e, requests.exceptions.Timeout):
            logging.info(" (The request timed out. ⏳)")
        elif isinstance(e, requests.exceptions.HTTPError):
            logging.info(f" (HTTP Error: {response.status_code} - {response.reason} 🚫)")
        return False
    except Exception as e:
        logging.exception(f"An unexpected error occurred while downloading {file_name}: {e}")
        return False

    return True


def download_multiple_files_bitso(urls, file_names, download_directory, referer_url="", _identity_value="", phpsessid_value=""):
    """Downloads multiple files from bitso.ir."""
    if len(urls) != len(file_names):
        logging.error("Error: The number of URLs and filenames must match! 📏")
        return

    failed_downloads = []
    for url, file_name in zip(urls, file_names):
        if not download_file_bitso(url, file_name, download_directory, referer_url, _identity_value, phpsessid_value):
            failed_downloads.append(url)

    write_failed_downloads_to_file(failed_downloads, "bitso", download_directory)
