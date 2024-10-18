# Configure logging to maximum level
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Set the logging level for all loggers to DEBUG to ensure we capture everything
for logger_name in logging.root.manager.loggerDict:
    logging.getLogger(logger_name).setLevel(logging.DEBUG)

# Adding a stream handler to ensure logs go to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)




import pandas as pd
import numpy as np
import tables
from zipline.data.bundles import register
#from zipline.utils.calendars import get_calendar
import pandas_market_calendars as mcal
#EOD Historical Data Bundle
def ingest_xtech_eodhd_h5_bundle(environ,
                           asset_db_writer,
                           minute_bar_writer,
                           daily_bar_writer,
                           adjustment_writer,
                           calendar,
                           start_session,
                           end_session,
                           cache,
                           show_progress,
                           output_dir):
    h5_file = '/datastore/exponential/xtech/daily-prices/us-eqt/huge-python/v1/zl/2024-10-11_zipline_bundle.h5'
    
    with pd.HDFStore(h5_file, 'r') as store:
        symbols = store.keys()  # Get all symbol keys from the HDF5 file
        symbols = [s.replace('/data/', '') for s in symbols]  # Extract the symbol name
        
        metadata = []  # To store metadata for asset_db_writer
                
        def daily_data_generator():
            # Get the NYSE calendar
            nyse_calendar = mcal.get_calendar('NYSE')
            
            # Generate the trading sessions (valid trading days) between start_session and end_session
            schedule = nyse_calendar.valid_days(start_date=start_session, end_date=end_session)
            
            for sid, symbol in enumerate(symbols):
                print(f"Processing symbol: {symbol}")
                
                df = store[f'data/{symbol}']
                df.index = pd.to_datetime(df.index)
                df.index = df.index.tz_localize('UTC')  # Make df.index timezone-aware (UTC)

        
                # Reindex the DataFrame to include all sessions (forward-fill missing data)
                df = df.reindex(schedule, method='ffill')
                
                # Ensure the DataFrame has the required columns
                df = df[['open', 'high', 'low', 'close', 'volume']]  # Adjust if needed
                
                # Store metadata for asset_db_writer
                metadata.append({
                    'sid': sid,
                    'symbol': symbol,
                    'asset_name': symbol,
                    'start_date': df.index[0],
                    'end_date': df.index[-1],
                    'first_traded': df.index[0],
                    'auto_close_date': df.index[-1] + pd.Timedelta(days=1),
                    'exchange': 'NYSE',
                    'country_code': 'US' 
                })
                
                yield sid, df

        
        # Write the daily data using the daily_bar_writer
        daily_bar_writer.write(daily_data_generator(), show_progress=show_progress)
        
        # Write asset metadata to asset_db_writer
        asset_db_writer.write(equities=pd.DataFrame(metadata))

    # Handle adjustments if needed (currently omitted)
    adjustment_writer.write()
    
#YFinance Bundle


def ingest_xtech_yf_h5_bundle(environ,
                           asset_db_writer,
                           minute_bar_writer,
                           daily_bar_writer,
                           adjustment_writer,
                           calendar,
                           start_session,
                           end_session,
                           cache,
                           show_progress,
                           output_dir):
    h5_file = '/datastore/exponential/xtech/daily-prices/us-eqt/wise-owl/v1/zl/2024-10-11_zipline_bundle.h5'
    
    with pd.HDFStore(h5_file, 'r') as store:
        symbols = store.keys()  # Get all symbol keys from the HDF5 file
        symbols = [s.replace('/data/', '') for s in symbols]  # Extract the symbol name, remove the '/data/' prefix
        
        metadata = []  # To store metadata for asset_db_writer
                
        def daily_data_generator():
            # Get the NYSE calendar
            nyse_calendar = mcal.get_calendar('NYSE')
            
            # Generate the trading sessions (valid trading days) between start_session and end_session
            schedule = nyse_calendar.valid_days(start_date=start_session, end_date=end_session)
            
            for sid, symbol in enumerate(symbols):
                print(f"Processing symbol: {symbol}")
                
                df = store[f'data/{symbol}']
                df.index = pd.to_datetime(df.index)
                df.index = df.index.tz_localize('UTC')  # Make df.index timezone-aware (UTC)
        
                # Reindex the DataFrame to include all sessions (forward-fill missing data)
                df = df.reindex(schedule, method='ffill')
                
                # Ensure the DataFrame has the required columns
                print(f"Available columns for {symbol}: {df.columns}")
                required_columns = ['open', 'high', 'low', 'close', 'volume']
                missing_columns = [col for col in required_columns if col not in df.columns]

                if missing_columns:
                    print(f"Warning: Missing columns {missing_columns} for {symbol}. Filling with NaN/0.")
                    for col in missing_columns:
                        if col == 'volume':
                            df[col] = 0  # Default to 0 for missing volume
                        else:
                            df[col] = np.nan  # Use NaN for missing OHLC prices

                df = df[required_columns]  # Filter to required columns
                
                # Store metadata for asset_db_writer
                metadata.append({
                    'sid': sid,
                    'symbol': symbol,
                    'asset_name': symbol,
                    'start_date': df.index[0],
                    'end_date': df.index[-1],
                    'first_traded': df.index[0],
                    'auto_close_date': df.index[-1] + pd.Timedelta(days=1),
                    'exchange': 'NYSE',  # Default exchange to NYSE
                    'country_code': 'US' 
                })
                
                yield sid, df
        
        # Write the daily data using the daily_bar_writer
        daily_bar_writer.write(daily_data_generator(), show_progress=show_progress)

        # Debugging: Ensure all metadata entries have an 'exchange' field
        for entry in metadata:
            if 'exchange' not in entry:
                print(f"Warning: Missing 'exchange' for {entry['symbol']}. Setting to 'NYSE'.")
                entry['exchange'] = 'NYSE'

        # Log metadata for debugging
        print("Metadata before writing to asset_db_writer:", metadata)
        
        # Write asset metadata to asset_db_writer
        asset_db_writer.write(equities=pd.DataFrame(metadata))

    # Handle adjustments if needed (currently omitted)
    adjustment_writer.write()



# def ingest_xtech_sp500_data_bundle(environ, asset_db_writer, minute_bar_writer, daily_bar_writer, adjustment_writer, calendar, start_session, end_session, cache, show_progress, output_dir):
#     daily_data_path = f'/datastore/exponential/xtech/daily-prices/us-eqt/huge-python/v1/zl_csv/date=2024-10-17'
#     asset_meta_path = f'/datastore/exponential/xtech/daily-prices/us-eqt/huge-python/v1/zl_csv/date=2024-10-17/asset_meta.csv'
    
#     asset_metadata = pd.read_csv(asset_meta_path)
#     asset_db_writer.write(asset_metadata)
    
#     sessions = calendar.sessions_in_range(start_session, end_session)
#     symbols = asset_metadata['symbol'].unique()

#     def pricing_iter():
#         for _, row in asset_metadata.iterrows():
#             asset_id = row['asset_id']
#             symbol = row['symbol']
#             file_path = f"{daily_data_path}/daily/{symbol}.csv"
#             df = pd.read_csv(file_path, parse_dates=['date'], index_col='date')
#             yield asset_id, df.reindex(sessions, method='ffill')  # Use asset_id instead of symbol

#     daily_bar_writer.write(pricing_iter(), show_progress=show_progress)


def ingest_xtech_sp500_data_bundle(environ, asset_db_writer, minute_bar_writer, daily_bar_writer, adjustment_writer, calendar, start_session, end_session, cache, show_progress, output_dir):
    daily_data_path = f'/datastore/exponential/xtech/daily-prices/us-eqt/huge-python/v1/zl_csv/date=2024-10-17'
    asset_meta_path = f'/datastore/exponential/xtech/daily-prices/us-eqt/huge-python/v1/zl_csv/date=2024-10-17/asset_meta.csv'
    '''
    asset_meta_data.append({
            'sid': sid,
            'symbol': symbol,
            'asset_name': symbol,            
            'exchange': 'NYSE',            
            'start_date': df[df['symbol'] == symbol]['date'].min(),
            'end_date': df[df['symbol'] == symbol]['date'].max()+ timedelta(days=1),
            'first_traded': df[df['symbol'] == symbol]['date'].min(),
            'auto_close_date': df[df['symbol'] == symbol]['date'].max() + timedelta(days=2) 
        })
        id, start_date, symbol, end_date, share_class_symbol, company_symbol, sid
    '''    
    asset_metadata = pd.read_csv(asset_meta_path)
    asset_metadata = pd.read_csv(asset_meta_path)
    if 'sid' not in asset_metadata.columns:
        asset_metadata['sid'] = range(1, len(asset_metadata) + 1)
    print(asset_metadata)

    logging.debug("Loaded asset metadata columns: %s", asset_metadata.columns)
    logging.debug(f'asset_metadata: {asset_metadata}')
    asset_db_writer.write(asset_metadata)
     #sid, exchange, start_date, end_date, asset_name, first_traded, auto_close_date)
    sessions = calendar.sessions_in_range(start_session, end_session)
    symbols = asset_metadata['symbol'].unique()
    #
    # Corrected asset_id column to sid
    asset_id_map = {row['symbol']: row['sid'] for _, row in asset_metadata.iterrows()}

    def pricing_iter():
        for _, row in asset_metadata.iterrows():
            sid = row['sid']  # Corrected asset_id column to sid
            symbol = row['symbol']
            file_path = f"{daily_data_path}/daily/{symbol}.csv"
            df = pd.read_csv(file_path, parse_dates=['date'], index_col='date')
            yield sid, df.reindex(sessions, method='ffill')  # Use asset_id instead of symbol

    daily_bar_writer.write(pricing_iter(), show_progress=show_progress)

# def ingest_xtech_sp500_data_bundle(environ, asset_db_writer, minute_bar_writer, daily_bar_writer, adjustment_writer, calendar, start_session, end_session, cache, show_progress, output_dir):
#     daily_data_path = f'/datastore/exponential/xtech/daily-prices/us-eqt/huge-python/v1/zl_csv/date=2024-10-17'
#     asset_meta_path = f'/datastore/exponential/xtech/daily-prices/us-eqt/huge-python/v1/zl_csv/date=2024-10-17/asset_meta.csv'
        
#     asset_metadata = pd.read_csv(asset_meta_path)
#     logging.debug("Loaded asset metadata columns:", asset_metadata.columns)
#     logging.debug(f'asset_metadata: {asset_metadata}')
#     asset_db_writer.write(asset_metadata)
    
#     sessions = calendar.sessions_in_range(start_session, end_session)
#     symbols = asset_metadata['symbol'].unique()
#     asset_id_map = {row['symbol']: row['asset_id'] for _, row in asset_metadata.iterrows()}

#     def pricing_iter():
#         for _, row in asset_metadata.iterrows():
#             asset_id = row['asset_id']
#             symbol = row['symbol']
#             file_path = f"{daily_data_path}/daily/{symbol}.csv"
#             df = pd.read_csv(file_path, parse_dates=['date'], index_col='date')
#             yield asset_id, df.reindex(sessions, method='ffill')  # Use asset_id instead of symbol

#     daily_bar_writer.write(pricing_iter(), show_progress=show_progress)

# def ingest_xtech_sp500_data_bundle(environ, asset_db_writer, minute_bar_writer, daily_bar_writer, adjustment_writer, calendar, start_session, end_session, cache, show_progress, output_dir):
    # daily_data_path = f'/datastore/exponential/xtech/daily-prices/us-eqt/huge-python/v1/zl_csv/date=2024-10-17'
    # asset_meta_path = f'/datastore/exponential/xtech/daily-prices/us-eqt/huge-python/v1/zl_csv/date=2024-10-17/asset_meta.csv'

    # logging.debug('Loading asset metadata from: %s', asset_meta_path)
    # asset_metadata = pd.read_csv(asset_meta_path)

    # # Ensure 'asset_id' column exists in asset_metadata
    # if 'asset_id' not in asset_metadata.columns:
    #     asset_metadata['asset_id'] = range(1, len(asset_metadata) + 1)

    # logging.debug('Loaded asset metadata columns: %s', asset_metadata.columns)
    # logging.debug('Asset metadata:\n%s', asset_metadata)
    # asset_db_writer.write(asset_metadata)

    # sessions = calendar.sessions_in_range(start_session, end_session)
    # symbols = asset_metadata['symbol'].unique()
    # asset_id_map = {row['symbol']: row['asset_id'] for _, row in asset_metadata.iterrows()}

    # # Define retry mechanism
    # retries = 2  # Maximum number of retries

    # for attempt in range(retries):
    #     try:
    #         # Removing fixed list of errata dates for this attempt
    #         if attempt == 0:
    #             sessions_to_use = sessions
    #         else:
    #             logging.warning('Retrying: Removing extra sessions and filling missing sessions.')
    #             extra_sessions = set(sessions_to_use) - set(sessions)
    #             if extra_sessions:
    #                 logging.debug('Extra sessions being removed: %s', extra_sessions)
    #                 sessions_to_use = sessions_to_use.difference(extra_sessions)
                
    #             # Ensure no missing sessions; fill forward where necessary
    #             missing_sessions = set(sessions) - set(sessions_to_use)
    #             if missing_sessions:
    #                 logging.debug('Filling missing sessions: %s', missing_sessions)
    #                 sessions_to_use = pd.DatetimeIndex(sorted(set(sessions_to_use).union(missing_sessions)))

    #         logging.debug('Adjusted sessions for attempt %d: %s', attempt + 1, sessions_to_use)

    #         def pricing_iter():
    #             for _, row in asset_metadata.iterrows():
    #                 asset_id = row['asset_id']
    #                 symbol = row['symbol']
    #                 file_path = f"{daily_data_path}/daily/{symbol}.csv"
    #                 logging.debug('Processing symbol: %s, asset_id: %s, file_path: %s', symbol, asset_id, file_path)
    #                 df = pd.read_csv(file_path, parse_dates=['date'], index_col='date')
    #                 df = df.reindex(sessions_to_use, method='ffill')  # Use asset_id instead of symbol
    #                 yield asset_id, df

    #         daily_bar_writer.write(pricing_iter(), show_progress=show_progress)
    #         logging.info('Successfully wrote daily bar data on attempt %d', attempt + 1)
    #         break  # Exit loop if successful

    #     except AssertionError as e:
    #         logging.error('Attempt %d failed with AssertionError: %s', attempt + 1, e)

    #         if attempt + 1 == retries:
    #             logging.critical('Maximum retries reached. Unable to successfully ingest bundle.')
    #             raise e  # Re-raise the exception if all retries fail

# def ingest_xtech_sp500_data_bundle(environ, asset_db_writer, minute_bar_writer, daily_bar_writer, adjustment_writer, calendar, start_session, end_session, cache, show_progress, output_dir):
#     daily_data_path = f'/datastore/exponential/xtech/daily-prices/us-eqt/huge-python/v1/zl_csv/date=2024-10-17'
#     asset_meta_path = f'/datastore/exponential/xtech/daily-prices/us-eqt/huge-python/v1/zl_csv/date=2024-10-17/asset_meta.csv'
    
#     logging.debug('Loading asset metadata from: %s', asset_meta_path)
#     asset_metadata = pd.read_csv(asset_meta_path)
    
#     # Ensure 'asset_id' column exists in asset_metadata
#     if 'asset_id' not in asset_metadata.columns:
#         logging.warning("'asset_id' column not found in asset_metadata, generating 'asset_id' values.")
#         asset_metadata['asset_id'] = range(1, len(asset_metadata) + 1)
    
#     # Check if asset_id is properly assigned
#     if asset_metadata['asset_id'].isnull().any():
#         logging.error("Null values found in 'asset_id' column, retrying assignment.")
#         asset_metadata['asset_id'] = range(1, len(asset_metadata) + 1)
    
#     logging.debug('Loaded asset metadata columns: %s', asset_metadata.columns)
#     logging.debug('Asset metadata:%s', asset_metadata)
#     logging.debug('---------------------------------------------------------')
#     asset_db_writer.write(asset_metadata)
    
#     sessions = calendar.sessions_in_range(start_session, end_session)
#     symbols = asset_metadata['symbol'].unique()
#     asset_id_map = {row['symbol']: row['asset_id'] for _, row in asset_metadata.iterrows()}

#     # Removing fixed list of errata dates
#     sessions = sessions.difference(errata_dates)
#     logging.debug('Adjusted sessions after removing errata dates: %s', sessions)

#     def pricing_iter():
#         for _, row in asset_metadata.iterrows():
#             asset_id = row['asset_id']
#             symbol = row['symbol']
#             file_path = f"{daily_data_path}/daily/{symbol}.csv"
#             logging.debug('Processing symbol: %s, asset_id: %s, file_path: %s', symbol, asset_id, file_path)
#             try:
#                 df = pd.read_csv(file_path, parse_dates=['date'], index_col='date')
#                 # Handle missing or extra dates by reindexing
#                 df = df.reindex(sessions, method='ffill')
#                 yield asset_id, df
#             except FileNotFoundError:
#                 logging.error('File not found for symbol: %s at path: %s', symbol, file_path)
#             except Exception as e:
#                 logging.error('Error processing symbol: %s, error: %s', symbol, str(e))

#     daily_bar_writer.write(pricing_iter(), show_progress=show_progress)
