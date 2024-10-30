'''
This is still test code and I don't believe is used for anything as 
of 10/29/24.



'''


# import pandas as pd
# from pathlib import Path
# import warnings
# import numpy as np
# from tqdm import tqdm

# warnings.filterwarnings('ignore')

# zipline_root = '~/repos/edge-seeker/zipline-x/.zipline'
# custom_data_path = Path(zipline_root, 'custom_data')

# hist_data_name = "QUOTEMEDIA_PRICES_247f636d651d8ef83d8ca1e756cf5ee4.csv"
# ticker_data_name = 'QUOTEMEDIA_TICKERS_6d75499fefd916e54334b292986eafcc.csv'
# idx = pd.IndexSlice

# def load_equities():
#     return pd.read_hdf(custom_data_path / 'quotemedia_eod_data_v3.h5', 'equities')

# def ticker_generator():
#     """
#     Lazily return (sid, ticker) tuple
#     """
#     return (v for v in load_equities().values)

# def data_generator():
#     """
#     Generator for price data and metadata.
#     """
#     for row in ticker_generator():
#         sid, symbol, exchange, asset_name = row
#         try:
#             df = pd.read_hdf(custom_data_path / 'quotemedia_eod_data_v3.h5', f'prices/{sid}')
#         except KeyError:
#             print(f"Error: No data found for sid {sid}")
#             continue

#         # Ensure correct columns and datatype
#         df.columns = ['open', 'high', 'low', 'close', 'volume']

#         # Verify if index is date and of correct type
#         if not isinstance(df.index, pd.DatetimeIndex):
#             print(f"Warning: Index for sid {sid} is not a DatetimeIndex.")

#         # Additional type checking for the data columns
#         expected_types = {
#             'open': 'float32',
#             'high': 'float32',
#             'low': 'float32',
#             'close': 'float32',
#             'volume': 'int32'
#         }

#         for col, expected_dtype in expected_types.items():
#             if df[col].dtype != expected_dtype:
#                 print(f"Warning: Column '{col}' for sid {sid} is of type {df[col].dtype} but expected {expected_dtype}")

#         start_date = df.index[0]
#         end_date = df.index[-1]
#         first_traded = start_date.date()
#         auto_close_date = end_date + pd.Timedelta(days=1)
#         exchange = 'NYSE'

#         yield (sid, df), symbol, asset_name, start_date, end_date, first_traded, auto_close_date, exchange

# # def data_generator():
# #     for sid, symbol, exchange_, asset_name in ticker_generator():
# #         df = pd.read_hdf(custom_data_path / 'quotemedia_eod_data_v3.h5', 'prices/{}'.format(sid))
# #         df.columns = ['open', 'high', 'low', 'close', 'volume']
# #         start_date = df.index[0]
# #         end_date = df.index[-1]

# #         first_traded = start_date.date()
# #         auto_close_date = end_date + pd.Timedelta(days=1)
# #         exchange = 'NYSE'

# #         yield (sid, df), symbol, asset_name, start_date, end_date, first_traded, auto_close_date, exchange


# def metadata_frame():
#     dtype = [
#         ('symbol', 'object'),
#         ('asset_name', 'object'),
#         ('start_date', 'datetime64[ns]'),
#         ('end_date', 'datetime64[ns]'),
#         ('first_traded', 'datetime64[ns]'),
#         ('auto_close_date', 'datetime64[ns]'),
#         ('exchange', 'object')]
#     return pd.DataFrame(np.empty(len(load_equities()), dtype=dtype))


# def qm_to_bundle(interval='1d'):
#     def ingest(environ,
#                asset_db_writer,
#                minute_bar_writer,
#                daily_bar_writer,
#                adjustment_writer,
#                calendar,
#                start_session,
#                end_session,
#                cache,
#                show_progress,
#                output_dir
#                ):
#         metadata = metadata_frame()

#         def daily_data_generator():
#             return (sid_df for (sid_df, *metadata.iloc[sid_df[0]]) in data_generator())

#         daily_bar_writer.write(daily_data_generator(), show_progress=True)
#         metadata.dropna(inplace=True)
#         exchange = {'exchange': 'NYSE', 'canonical_name': 'NYSE', 'country_code': 'US'}
#         exchange_df = pd.DataFrame(exchange, index=[0])
#         asset_db_writer.write(equities=metadata, exchanges=exchange_df)

#         '''
#         Since we used adjusted data here, no need to add splits and dividends
#             splits = pd.read_hdf(custom_data_path / 'quandl.h5', 'splits')
#             splits['sid'] = splits['sid'].astype(np.int64)
#             dividends = pd.read_hdf(custom_data_path / 'quandl.h5', 'dividends')
#             dividends['sid'] = dividends['sid'].astype(np.int64)
#             adjustment_writer.write(splits=splits,dividends=dividends)
#         '''
#         adjustment_writer.write()

#     return ingest

import pandas as pd
from pathlib import Path
import warnings
import numpy as np
from tqdm import tqdm

warnings.filterwarnings('ignore')

zipline_root = '~/repos/edge-seeker/zipline-x/.zipline'
custom_data_path = Path(zipline_root, 'custom_data')
h5_path = custom_data_path / 'quotemedia_eod_data_v3.h5'

def load_equities():
    # Load the metadata for all symbols
    return pd.read_hdf(h5_path, 'equities')

def ticker_generator():
    """
    Lazily return (sid, symbol, exchange, asset_name) tuple.
    """
    equities_df = load_equities()
    return (row for row in equities_df.itertuples(index=False))

def data_generator():
    """
    Generator for price data and metadata.
    """
    for row in ticker_generator():
        sid, symbol, exchange, asset_name = row
        try:
            df = pd.read_hdf(h5_path, f'prices/{sid}')
        except KeyError:
            print(f"Error: No data found for sid {sid}")
            continue

        # Ensure correct columns and datatype
        df.columns = ['open', 'high', 'low', 'close', 'volume']

        # Additional type checking for the data columns
        expected_types = {
            'open': 'float32',
            'high': 'float32',
            'low': 'float32',
            'close': 'float32',
            'volume': 'int32'
        }

        for col, expected_dtype in expected_types.items():
            if df[col].dtype != expected_dtype:
                print(f"Warning: Column '{col}' for sid {sid} is of type {df[col].dtype} but expected {expected_dtype}")

        start_date = df.index[0]
        end_date = df.index[-1]
        first_traded = start_date.date()
        auto_close_date = end_date + pd.Timedelta(days=1)
        exchange = 'NYSE'

        # Yield both the price data and metadata
        yield (sid, df), symbol, asset_name, start_date, end_date, first_traded, auto_close_date, exchange

def metadata_frame():
    """
    Create a metadata frame for all symbols.
    """
    # Collect metadata dynamically
    metadata_list = []

    for (sid, sid_data), symbol, asset_name, start_date, end_date, first_traded, auto_close_date, exchange in data_generator():
        metadata_list.append({
            'symbol': symbol,
            'asset_name': asset_name,
            'start_date': start_date,
            'end_date': end_date,
            'first_traded': first_traded,
            'auto_close_date': auto_close_date,
            'exchange': exchange
        })

    # Create the DataFrame from the collected list of metadata
    metadata = pd.DataFrame(metadata_list, columns=[
        'symbol',
        'asset_name',
        'start_date',
        'end_date',
        'first_traded',
        'auto_close_date',
        'exchange'
    ])

    return metadata

def qm_to_bundle(interval='1d'):
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
        # Create metadata frame
        metadata = metadata_frame()
        print("Metadata successfully created with the following columns:")
        print(metadata.columns)

        # Define a daily data generator for writing price data
        def daily_data_generator():
            for (sid, sid_data), _, _, _, _, _, _, _ in data_generator():
                # Add some debug info to inspect sid and data being yielded
                print(f"Yielding data for sid: {sid} with {len(sid_data)} records.")
                yield sid, sid_data

        # Write daily price data
        try:
            daily_bar_writer.write(daily_data_generator(), show_progress=True)
        except Exception as e:
            print(f"Error during daily_bar_writer.write: {e}")

        # Write metadata to the asset database
        try:
            asset_db_writer.write(equities=metadata, exchanges=pd.DataFrame([{
                'exchange': 'NYSE',
                'canonical_name': 'NYSE',
                'country_code': 'US'
            }]))
            print("Metadata written to asset database successfully.")
        except Exception as e:
            print(f"Error writing metadata to asset database: {e}")

        # No splits and dividends used here
        try:
            adjustment_writer.write()
            print("Adjustment writer completed successfully.")
        except Exception as e:
            print(f"Error writing adjustments: {e}")

    return ingest

