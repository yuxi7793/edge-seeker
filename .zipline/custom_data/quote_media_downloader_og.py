#######################
#This code downloads daily quotemedia data
#
#
#
##########################


import pandas as pd
import numpy as np
import requests
import h5py
from datetime import datetime
import io
import zipfile

# Set up API key and base URL
API_KEY = "tw2sxkKZo_y1UvMcnSux"
BASE_URL = "https://data.nasdaq.com/api/v3/datatables/QUOTEMEDIA"

# Function to download data from API
def get_data(endpoint, params):
    url = f"{BASE_URL}/{endpoint}"
    params["api_key"] = API_KEY
    print(f"sending request {url}")
    response = requests.get(url, params=params)
    print(f"response {response} {response.json}")
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed with status code {response.status_code}")

# Function to download and process ZIP file
def download_and_process_zip(url):
    print(f"Downloading data from {url}")
    response = requests.get(url)
    if response.status_code == 200:
        z = zipfile.ZipFile(io.BytesIO(response.content))
        csv_filename = z.namelist()[0]  # Assume the first file in the ZIP is the CSV we want
        with z.open(csv_filename) as f:
            df = pd.read_csv(f)
        return df
    else:
        raise Exception(f"Failed to download ZIP file. Status code: {response.status_code}")

# Download tickers
print("Downloading tickers...")
tickers_response = get_data("TICKERS", {"qopts.export": "true"})
tickers_download_link = tickers_response['datatable_bulk_download']['file']['link']
tickers_df = download_and_process_zip(tickers_download_link)

# Download adjusted EOD price data
print("Downloading adjusted EOD price data...")
start_date = "2000-01-01"
end_date = datetime.now().strftime("%Y-%m-%d")

params = {
    "date.gte": start_date,
    "date.lte": end_date,
    "qopts.columns": "ticker,date,adj_open,adj_high,adj_low,adj_close,adj_volume",
    "qopts.export": "true"
}

price_response = get_data("PRICES", params)
price_download_link = price_response['datatable_bulk_download']['file']['link']
prices_df = download_and_process_zip(price_download_link)

# Convert date column to datetime
prices_df["date"] = pd.to_datetime(prices_df["date"])
prices_df.rename(columns={"adj_open":'open','adj_high':'high','adj_low':'low','adj_close':'close','adj_volume':'volume'},inplace=True)
# Store data in H5 format
print("Storing data in H5 format...")
with h5py.File("quotemedia_eod_data.h5", "w") as f:
    # Store tickers data
    tickers_group = f.create_group("tickers")
    for column in tickers_df.columns:
        if tickers_df[column].dtype == 'object':
            # Convert string columns to ASCII
            ascii_values = [s.encode('ascii', 'ignore') if isinstance(s, str) else b'' for s in tickers_df[column].values]
            tickers_group.create_dataset(column, data=ascii_values, dtype=h5py.special_dtype(vlen=bytes))
        else:
            tickers_group.create_dataset(column, data=tickers_df[column].values)
    
    # Store prices data
    prices_group = f.create_group("prices")
    for column in prices_df.columns:
        if column == "date":
            prices_group.create_dataset(column, data=prices_df[column].astype(int))
        elif prices_df[column].dtype == 'object':
            # Convert string columns to ASCII
            ascii_values = [s.encode('ascii', 'ignore') if isinstance(s, str) else b'' for s in prices_df[column].values]
            prices_group.create_dataset(column, data=ascii_values, dtype=h5py.special_dtype(vlen=bytes))
        else:
            prices_group.create_dataset(column, data=prices_df[column].values)

print("Data successfully stored in quotemedia_eod_data.h5")
