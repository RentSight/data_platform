import requests
from pathlib import Path
import os


def download_file(url, local_filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

if __name__ == "__main__":
    url = "https://data.insideairbnb.com/brazil/rj/rio-de-janeiro/2025-09-26/visualisations/listings.csv"
    local_filename = "data/raw/airbnb_RJ.csv"
    print(f"Downloading {url} to {local_filename}...")
    Path(os.path.dirname(local_filename)).mkdir(parents=True, exist_ok=True)
    download_file(url, local_filename)
    print("Download completed.")