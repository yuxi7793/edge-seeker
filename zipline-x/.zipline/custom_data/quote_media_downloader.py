'''
This program is for downloading updated quote media data into an h5 file so that it can be processed by the quandl_custom_bundle.py 
script and ETLed into a Zipline compatible bundle

Note: For unknown reasons the quote_media API does not produce an artifact for the daily data request on the first few requests.  So it is necessary
to repeatedly run this script if it is the first run of the day.

Exponential Tech - 10/2024

'''


import pandas as pd
import numpy as np
import requests
import io
import zipfile
import time
from datetime import datetime
from pathlib import Path
from zipline.utils.calendar_utils import get_calendar
from tqdm import tqdm
import warnings
from tables import NaturalNameWarning
warnings.filterwarnings('ignore', category=NaturalNameWarning)


# Set up API key and base URL
API_KEY = "tw2sxkKZo_y1UvMcnSux"
BASE_URL = "https://data.nasdaq.com/api/v3/datatables/QUOTEMEDIA"

# Define file paths
zipline_root = '~/repos/edge-seeker/zipline-x/.zipline'
custom_data_path = Path(zipline_root, 'custom_data')
h5_path = custom_data_path / 'quotemedia_eod_data_latest.h5'

# Function to download data from API
def get_data(endpoint, params):
    url = f"{BASE_URL}/{endpoint}"
    params["api_key"] = API_KEY
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed with status code {response.status_code}")

# Function to download and process ZIP file
def download_and_process_zip(url):
    response = requests.get(url)
    if response.status_code == 200:
        print(f'response: {response}')
        z = zipfile.ZipFile(io.BytesIO(response.content))
        csv_filename = z.namelist()[0]  # Assume the first file in the ZIP is the CSV we want
        with z.open(csv_filename) as f:
            df = pd.read_csv(f)
        return df
    else:
        raise Exception(f"Failed to download ZIP file. Status code: {response.status_code}")

# Download tickers
def download_tickers():
    tickers_response = get_data("TICKERS", {"qopts.export": "true"})
    print(f'tickers response: {tickers_response}')
    tickers_download_link = tickers_response['datatable_bulk_download']['file']['link']
    tickers_df = download_and_process_zip(tickers_download_link)
    return tickers_df

# Download adjusted EOD price data
def download_prices(start_date, end_date):
    params = {
        "date.gte": start_date,
        "date.lte": end_date,
        "qopts.columns": "ticker,date,adj_open,adj_high,adj_low,adj_close,adj_volume",
        "qopts.export": "true"
    }
    price_response = get_data("PRICES", params)
    price_download_link = price_response['datatable_bulk_download']['file']['link']
    prices_df = download_and_process_zip(price_download_link)
    return prices_df

# Reindex prices by trading days
def reindex_trading_days(prices_df, trading_days):
    def reindex_group(group):
        # Sort the group by 'date' to ensure the index is monotonic
        group = group.sort_index()  # This ensures the index is properly sorted
        group = group.droplevel('symbol')
        return group.reindex(trading_days, method='ffill')

    # Apply reindexing to each group
    new_df = prices_df.groupby(level='symbol').apply(reindex_group)

    # Return the updated DataFrame
    return new_df

# Main function to create HDF5
def create_hdf5():
    # Set start and end dates
    start_date = "2008-01-01"
    #start_date = "2024-08-01"
    end_date = datetime.now().strftime("%Y-%m-%d")

    # Download data
    print("Downloading tickers...")
    tickers_df = download_tickers()

    print("Downloading adjusted EOD price data...")
    time.sleep(10)  # Preventing rate-limiting
    prices_df = download_prices(start_date, end_date)

    # Process tickers data
    tickers_df.rename(columns={'ticker': 'symbol'}, inplace=True)
    tickers_df.reset_index(inplace=True, drop=True)
    tickers_df.reset_index(inplace=True)
    tickers_df.rename(columns={'index': 'sid'}, inplace=True)

    # Modify sid to be a valid Python identifier
    #tickers_df['sid'] = 's' + tickers_df['sid'].astype(str)

    # Process prices data
    prices_df["date"] = pd.to_datetime(prices_df["date"])
    prices_df.rename(columns={'ticker':'symbol','adj_open': 'open', 'adj_high': 'high', 'adj_low': 'low', 'adj_close': 'close', 'adj_volume': 'volume'}, inplace=True)
    prices_df.set_index(['symbol', 'date'], inplace=True)

    # Filter by trading days
    nyse_calendar = get_calendar('NYSE')
    trading_days = nyse_calendar.sessions_in_range(start=start_date, end=end_date)
    prices_df = prices_df[prices_df.index.get_level_values('date').isin(trading_days)]

    # Reindex to fill missing trading days
    prices_df = reindex_trading_days(prices_df, trading_days)
    prices_df.index.set_names(['symbol', 'date'], inplace=True)
    prices_df = prices_df.fillna(method='ffill').fillna(method='bfill')

    # Ensure no missing symbols between tickers and prices
    tickers_in_prices = prices_df.index.get_level_values('symbol').unique()
    tickers_df = tickers_df[tickers_df['symbol'].isin(tickers_in_prices)]
    prices_df = prices_df[prices_df.index.get_level_values('symbol').isin(tickers_df['symbol'])]

    # Create sid mapping
    sid_map = tickers_df[['symbol', 'sid']].set_index('symbol')['sid'].to_dict()
    prices_df = prices_df.reset_index()
    prices_df['sid'] = prices_df['symbol'].map(sid_map)
    prices_df.set_index(['sid', 'date'], inplace=True)

    # Store data in HDF5
    # Store prices data for each sid
    with pd.HDFStore(h5_path, mode='w') as store:
        # Store tickers data
        store.put('equities', tickers_df, format='table')

        # Store prices data for each sid
        for sid, group in tqdm(prices_df.groupby(level='sid'), desc="Saving prices to HDF5"):
            sid_data = group.droplevel('sid')[['open', 'high', 'low', 'close', 'volume']]
            sid_data = sid_data.astype({
                'open': 'float32',
                'high': 'float32',
                'low': 'float32',
                'close': 'float32',
                'volume': 'int32'
            })
            store.put(f'prices/{sid}', sid_data, format='table')


    print("Data successfully stored in HDF5 format.")

if __name__ == '__main__':
    create_hdf5()
