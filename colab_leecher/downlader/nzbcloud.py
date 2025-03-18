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

def extract_filename_from_url(url):
    """Extracts and cleans the filename from a given URL."""
    try:
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        filename = os.path.basename(path)
        return clean_filename(filename) #clean_filename is defined in deltaleech downloader.
    except Exception as e:
        logging.warning(f"Error extracting filename from URL: {e}")
        return None

def download_files_nzbcloud(url_template, variable_segments, filenames, cf_clearance, download_directory):
    """Downloads files using requests, tqdm progress bar, and cf_clearance cookie (nzbCloud).
       Now accepts a URL template and a list of variable segments.
    """
    cookies = {"cf_clearance": cf_clearance}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://app.nzbcloud.com/",  # Adjust as needed
    }
    failed_downloads = []  # Keep track of failed URLs

    if len(variable_segments) != len(filenames):
      logging.error("The number of variable segments must match the number of file names")
      return

    for idx, (variable_segment, file_name) in enumerate(zip(variable_segments, filenames)):
        file_name = file_name.strip()
        variable_segment = variable_segment.strip()
        if not variable_segment or not file_name:
            logging.warning(f"Skipping (nzbCloud): Variable segment or filename is missing for pair {idx + 1}.")
            continue

        url = url_template.format(variable_segment) # Construct the full URL

        try:
            response = requests.get(url, headers=headers, cookies=cookies, stream=True, timeout=30)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024

            logging.info(f"Downloading (nzbCloud) {file_name}...")
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"Downloading {file_name}", position=0,
                      leave=True) as t:
                full_file_path = os.path.join(download_directory, file_name)
                os.makedirs(os.path.dirname(full_file_path), exist_ok=True)  # Ensure directory exists
                with open(full_file_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=block_size):
                        if chunk:  # filter out keep-alive new chunks
                            file.write(chunk)
                            t.update(len(chunk))
            logging.info(f"Download complete (nzbCloud): {file_name}")

        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to download (nzbCloud) {file_name}: {e}")
            failed_downloads.append(url)  # Add the failed URL to the list
            if isinstance(e, requests.exceptions.Timeout):
                logging.info(" (The request timed out. ⏳)")
            elif isinstance(e, requests.exceptions.HTTPError):
                logging.info(f" (HTTP Error: {response.status_code} - {response.reason} 🚫)")

        except Exception as e:
            logging.exception(f"An unexpected error occurred (nzbCloud) while downloading {file_name}: {e}")
            failed_downloads.append(url)  # Add the failed URL to the list

    write_failed_downloads_to_file(failed_downloads, "nzbcloud", download_directory)
