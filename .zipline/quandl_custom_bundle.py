import pandas as pd
from pathlib import Path
import warnings
import numpy as np
from tqdm import tqdm
import logging
import os
import h5py

print(f'starting quandl_custom_bundle.py')
#warnings.filterwarnings('ignore')

# Adding a stream handler to ensure logs go to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(console_handler)

zipline_root = os.path.expanduser('~/repos/edge-seeker/.zipline')
custom_data_path = Path(zipline_root, 'custom_data')

hist_data_name = "QUOTEMEDIA_PRICES_247f636d651d8ef83d8ca1e756cf5ee4.csv"
ticker_data_name = 'QUOTEMEDIA_TICKERS_6d75499fefd916e54334b292986eafcc.csv'
idx = pd.IndexSlice

def load_equities():
    try:
        hdf5_path = custom_data_path / 'quotemedia_eod_data.h5'
        logger.debug(f'Attempting to load tickers from HDF5 file at: {hdf5_path}')
        if not hdf5_path.exists():
            logger.error(f'HDF5 file not found at: {hdf5_path}')
            raise FileNotFoundError(f'HDF5 file not found at: {hdf5_path}')
        
        # Check if 'tickers' dataset exists in the file and read it using h5py
        with h5py.File(hdf5_path, 'r') as h5file:
            if 'tickers' not in h5file:
                logger.error(f"Dataset 'tickers' not found in HDF5 file at: {hdf5_path}")
                raise KeyError(f"Dataset 'tickers' not found in HDF5 file at: {hdf5_path}")
            else:
                logger.debug("Dataset 'tickers' found in the HDF5 file.")
                tickers_data = {key: h5file['tickers'][key][()] for key in h5file['tickers'].keys()}
                tickers_df = pd.DataFrame(tickers_data)
                logger.debug(f'Tickers loaded successfully with shape: {tickers_df.shape}')
                return tickers_df
    except Exception as e:
        logger.error(f'Error loading tickers: {e}')
        raise

def ticker_generator():
    """
    Lazily return (sid, ticker, exchange, asset_name) tuple
    """
    tickers_df = load_equities()
    # Adjusting to handle cases where the number of columns is less than expected
    if 'sid' not in tickers_df.columns:
        tickers_df['sid'] = tickers_df.index
    if 'exchange' not in tickers_df.columns:
        tickers_df['exchange'] = 'UNKNOWN'
    if 'asset_name' not in tickers_df.columns:
        tickers_df['asset_name'] = 'UNKNOWN'
    return ((row['sid'], row.get('symbol', 'UNKNOWN'), row['exchange'], row['asset_name']) for _, row in tickers_df.iterrows())

def data_generator():
    for sid, symbol, exchange_, asset_name in ticker_generator():
        try:
            logger.debug(f'Loading price data for sid: {sid}')
            price_path = custom_data_path / 'quotemedia_eod_data.h5'
            if not price_path.exists():
                logger.error(f'HDF5 file not found at: {price_path}')
                raise FileNotFoundError(f'HDF5 file not found at: {price_path}')
            
            # Check if the dataset for the sid exists
            with h5py.File(price_path, 'r') as h5file:
                if f'prices/{sid}' not in h5file:
                    logger.error(f"Dataset 'prices/{sid}' not found in HDF5 file at: {price_path}")
                    raise KeyError(f"Dataset 'prices/{sid}' not found in HDF5 file at: {price_path}")
                else:
                    logger.debug(f"Dataset 'prices/{sid}' found in the HDF5 file.")
                    price_data = {key: h5file[f'prices/{sid}'][key][()] for key in h5file[f'prices/{sid}'].keys()}
                    df = pd.DataFrame(price_data)
                    logger.debug(f'Data for sid {sid} loaded successfully with shape {df.shape}')
                    df.columns = ['open', 'high', 'low', 'close', 'volume']
                    start_date = df.index[0]
                    end_date = df.index[-1]

                    first_traded = start_date.date()
                    auto_close_date = end_date + pd.Timedelta(days=1)

                    yield (sid, df), symbol, asset_name, start_date, end_date, first_traded, auto_close_date, exchange_
        except Exception as e:
            logger.error(f'Error loading price data for sid {sid}: {e}')
            continue

def metadata_frame():
    try:
        dtype = [
            ('symbol', 'object'),
            ('asset_name', 'object'),
            ('start_date', 'datetime64[ns]'),
            ('end_date', 'datetime64[ns]'),
            ('first_traded', 'datetime64[ns]'),
            ('auto_close_date', 'datetime64[ns]'),
            ('exchange', 'object'),
            ('country_code','object')
            ]
        tickers = load_equities()
        logger.debug(f'Creating metadata frame with {len(tickers)} entries')
        return pd.DataFrame(np.empty(len(tickers), dtype=dtype))
    except Exception as e:
        logger.error(f'Error creating metadata frame: {e}')
        raise

def test_h5_file_readable():
    """
    Test to ensure the HDF5 file is readable and contains the expected datasets.
    """
    try:
        hdf5_path = custom_data_path / 'quotemedia_eod_data.h5'
        logger.debug(f'Checking if HDF5 file is readable at: {hdf5_path}')
        if not hdf5_path.exists():
            logger.error(f'HDF5 file not found at: {hdf5_path}')
            raise FileNotFoundError(f'HDF5 file not found at: {hdf5_path}')
        
        with h5py.File(hdf5_path, 'r') as h5file:
            if 'tickers' not in h5file:
                logger.error(f"Dataset 'tickers' not found in HDF5 file at: {hdf5_path}")
                raise KeyError(f"Dataset 'tickers' not found in HDF5 file at: {hdf5_path}")
            if 'prices' not in h5file:
                logger.error(f"Dataset 'prices' not found in HDF5 file at: {hdf5_path}")
                raise KeyError(f"Dataset 'prices' not found in HDF5 file at: {hdf5_path}")
            logger.debug("HDF5 file is readable and contains the required datasets.")
    except Exception as e:
        logger.error(f'Error testing HDF5 file readability: {e}')
        raise

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
        try:
            # Run the test to ensure HDF5 file is readable
            test_h5_file_readable()
            
            metadata = metadata_frame()

            def daily_data_generator():
                return (sid_df for (sid_df, *metadata.iloc[sid_df[0]]) in data_generator())

            logger.info('Writing daily bar data...')
            daily_bar_writer.write(daily_data_generator(), show_progress=True)
            metadata.dropna(inplace=True)
            logger.info(f'Metadata contains {len(metadata)} entries after dropping NAs')
            
            exchange = {'exchange': 'NYSE', 'canonical_name': 'NYSE', 'country_code': 'US'}
            exchange_df = pd.DataFrame(exchange, index=[0])
            asset_db_writer.write(equities=metadata, exchanges=exchange_df)
            
            logger.info('Writing adjustments (splits and dividends)...')
            # Since we used adjusted data here, no need to add splits and dividends
            adjustment_writer.write()
        except Exception as e:
            logger.error(f'Error during ingestion: {e}')
            raise

    return ingest

# Additional logging to debug the module registration
logger.info('quandl_custom_bundle module loaded successfully')
