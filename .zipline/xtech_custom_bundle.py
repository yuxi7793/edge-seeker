import pandas as pd
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




