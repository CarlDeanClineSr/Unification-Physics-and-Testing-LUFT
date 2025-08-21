import requests
import os
from datetime import datetime

# Auto-download CERN Open Data for LUFT analysis
def download_cern_data(dataset_id, output_dir="data", max_files=10):
    base_url = "https://opendata.cern.ch/record/"
    try:
        # Placeholder: Query CERN Open Data API (simplified)
        response = requests.get(f"{base_url}{dataset_id}/files")
        if response.status_code != 200:
            print(f"Error fetching dataset {dataset_id}")
            return
        files = response.json().get("files", [])[:max_files]
        os.makedirs(output_dir, exist_ok=True)
        for file in files:
            file_url = file["url"]
            file_name = file["name"]
            with open(f"{output_dir}/{file_name}", "wb") as f:
                f.write(requests.get(file_url).content)
            print(f"Downloaded {file_name}")
        # Log to winsat_data_log.md
        log_entry = f"""
| {file_name} | CERN {dataset_id} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {file_name.split('.')[-1]} | {file['size']} | ALICE/LHC data for LUFT scan |
"""
        with open("data/winsat_data_log.md", "a") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error: {e}")

# Example: download_cern_data("12345", output_dir="data/cern_data")
