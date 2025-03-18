# --- Main Control ---
 import requests
 import os
 from tqdm import tqdm
 import urllib.parse
 import re
 import logging
 from colab_leecher.downlader import nzbcloud, deltaleech, bitso # Import the downloader modules
 from colab_leecher.utility.helper import clean_filename, extract_filename_from_url

 def main():

     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

     downloader_choice = input("Choose downloader (1: nzbCloud, 2: DeltaLeech, 3: Bitso): ")

     if downloader_choice == "1":  # nzbCloud
         url_template = input("Enter the URL template (use {} as a placeholder): ")
         variable_segments_input = input("Enter variable segments, one per line (separated by commas): ")
         variable_segments = [seg.strip() for seg in variable_segments_input.split(',')]

         cf_clearance = input("Enter Cloudflare clearance cookie (optional): ").strip() or None
         download_directory = input("Enter download directory (default: /content/Upload): ").strip() or "/content/Upload"
         filenames_input = input("Enter filenames, one per line (separated by commas) (nzbCloud): ")
         filenames = [filename.strip() for filename in filenames_input.split(',')]

         nzbcloud.download_files_nzbcloud(url_template, variable_segments, filenames, cf_clearance, download_directory)

     elif downloader_choice == "2":  # DeltaLeech
         url_template = input("Enter the URL template (use {} as a placeholder): ")
         variable_segments_input = input("Enter variable segments, one per line (separated by commas): ")
         variable_segments = [seg.strip() for seg in variable_segments_input.split(',')]

         cf_clearance = input("Enter Cloudflare clearance cookie (optional): ").strip() or None
         download_directory = input("Enter download directory (default: /content/Upload): ").strip() or "/content/Upload"

         use_url_filenames_input = input("Use filenames from URLs? (y/n) (DeltaLeech): ").lower()
         use_url_filenames = use_url_filenames_input == 'y'

         if use_url_filenames:
              # This part needs adjustment for the template
             filenames = [extract_filename_from_url(url_template.format(seg)) for seg in variable_segments]

             if None in filenames:
                 logging.error("Some URLs could not have their filename extracted. 🙁")
                 return
         else:
             filenames_input = input("Enter filenames, one per line (separated by commas) (DeltaLeech): ")
             filenames = [filename.strip() for filename in filenames_input.split(',')]
             if len(variable_segments) != len(filenames):
               logging.error("Variable segments and filenames do not match in length.")
               return


         deltaleech.download_multiple_files_deltaleech(url_template, variable_segments, filenames, cf_clearance, download_directory)

     elif downloader_choice == "3": #Bitso
         cf_clearance = None
         download_directory = "/content/upload"
         referer_url = "https://panel.bitso.ir/"
         _identity_value = ""  # Replace with your actual _identity value if needed
         phpsessid_value = ""   # Replace with your actual PHPSESSID value if needed

         urls_input = input("Enter URLs, one per line (separated by commas): ")
         urls = []
         for line in urls_input.splitlines():
             line = line.strip()
             if line:
                 urls.extend([url.strip() for url in line.split(',') if url.strip()])

         filenames_input = input("Enter filenames manually, one per line (separated by commas) (Bitso): ")
         filenames = []
         for line in filenames_input.splitlines():
             line = line.strip()
             if line:
                 filenames.extend([fn.strip() for fn in line.split(',') if fn.strip()])

         for url in urls:
             try:
                 result = urllib.parse.urlparse(url)
                 if not all([result.scheme, result.netloc]):
                     raise ValueError
             except ValueError:
                 logging.error(f"Invalid URL: {url} 🚫")
                 return

         if len(urls) != len(filenames):
             logging.error("Error: The number of URLs and filenames must match! 📏")
             logging.info(f" Number of URLs: {len(urls)} 🔢")
             logging.info(f" Number of filenames: {len(filenames)} 🔢")
             return
         bitso.download_multiple_files_bitso(urls, filenames, download_directory, referer_url, _identity_value, phpsessid_value)
     else:
         logging.error("Invalid downloader choice. 🚫")


 if __name__ == "__main__":
     main()
