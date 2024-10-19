import pandas as pd
from pathlib import Path
import warnings
import numpy as np
from tqdm import tqdm

warnings.filterwarnings('ignore')

zipline_root = '~/repos/edge-seeker/zipline-x/.zipline'
custom_data_path = Path(zipline_root, 'custom_data')
h5_path = custom_data_path / 'quotemedia_eod_data.h5'  # Define the HDF5 file path

# Function to load equities metadata (tickers data)
def load_equities():
    """
    Load the tickers data using pandas HDFStore for more explicit control.
    """
    with pd.HDFStore(h5_path, mode='r') as store:
        if 'tickers' in store:
            tickers_df = store['tickers']
            # Add an 'sid' column using the DataFrame index as the sid
            tickers_df = tickers_df.reset_index().rename(columns={"index": "sid"})
            tickers_df.rename(columns={'ticker':'symbol','company_name':'asset_name'},inplace=True)
            print("Loaded tickers columns:", tickers_df.columns)
            return tickers_df
        else:
            raise KeyError("Dataset 'tickers' not found in the HDF5 file.")

# Ticker generator to yield (sid, ticker)
def ticker_generator():
    """
    Lazily return (sid, ticker) tuple from the tickers DataFrame.
    """
    equities_df = load_equities()
    for row in equities_df.itertuples(index=False):
        yield row  # Provides a tuple for each row, containing sid, symbol, exchange, asset_name

# Generator for price data
def data_generator():
    # Load the entire prices dataset
    prices_df = pd.read_hdf(h5_path, key='prices')

    # Iterate over each ticker in the tickers data
    for row in ticker_generator():
        sid = row.sid
        symbol = row.symbol
        exchange_ = row.exchange
        asset_name = row.asset_name

        # Filter the prices DataFrame by the 'ticker' (symbol) column
        sid_data = prices_df[prices_df['ticker'] == symbol]

        # Drop the 'ticker' column since it's no longer needed
        sid_data = sid_data.drop(columns=['ticker'])

        # Ensure 'date' is set as the index
        sid_data.set_index('date', inplace=True)

        # Set expected columns explicitly to avoid mismatches
        sid_data = sid_data[['open', 'high', 'low', 'close', 'volume']]

        # Collect necessary metadata
        start_date = sid_data.index[0]
        end_date = sid_data.index[-1]
        first_traded = start_date.date()
        auto_close_date = end_date + pd.Timedelta(days=1)
        exchange = 'NYSE'  # Assuming 'NYSE' for simplicity

        yield (sid, sid_data), symbol, asset_name, start_date, end_date, first_traded, auto_close_date, exchange

def metadata_frame():
    equities_df = load_equities()
    dtype = [
        ('symbol', 'object'),
        ('asset_name', 'object'),
        ('start_date', 'datetime64[ns]'),
        ('end_date', 'datetime64[ns]'),
        ('first_traded', 'datetime64[ns]'),
        ('auto_close_date', 'datetime64[ns]'),
        ('exchange', 'object')
    ]
    metadata = pd.DataFrame(np.empty(len(equities_df), dtype=dtype))

    # Use a combined loop instead of recreating the data generator each time
    for idx, ((sid, sid_data), symbol, asset_name, start_date, end_date, first_traded, auto_close_date, exchange) in enumerate(data_generator()):
        metadata.iloc[idx] = (
            symbol,
            asset_name,
            start_date,
            end_date,
            first_traded,
            auto_close_date,
            exchange
        )

    return metadata


# Updated ingestion function
def quandl_to_bundle(interval='1d'):
    def ingest(environ,
               asset_db_writer,
               minute_bar_writer,
               daily_bar_writer,
               adjustment_writer,
               calendar,
               start_session,
               end_session,
               cache,
               show_progress,
               output_dir
               ):
        metadata = metadata_frame()

        def daily_data_generator():
            return (sid_df for (sid_df, *metadata.iloc[sid_df[0]]) in data_generator())

        # Write daily price data using daily_bar_writer
        daily_bar_writer.write(daily_data_generator(), show_progress=True)

        # Drop any empty metadata rows
        metadata.dropna(inplace=True)

        # Write metadata to the asset database
        exchange = {'exchange': 'NYSE', 'canonical_name': 'NYSE', 'country_code': 'US'}
        exchange_df = pd.DataFrame(exchange, index=[0])
        asset_db_writer.write(equities=metadata, exchanges=exchange_df)

        # Since we used adjusted data here, no need to add splits and dividends
        adjustment_writer.write()

    return ingest
