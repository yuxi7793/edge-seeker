print(f'in: edge-seeker/.zipline/extension.py')

#################################################3

import sys
from pathlib import Path
import pandas as pd

sys.path.append(Path.home().joinpath('repos/edge-seeker/.zipline').as_posix())
print(f'sys.path:{sys.path}')
import sys


#sys.path.append(Path('~', '.zipline').expanduser().as_posix())
#print(f'sys.path:{sys.path}')

from zipline.data.bundles import register
from quandl_custom_bundle import quandl_to_bundle


register('quandl_custom_bundle',
         quandl_to_bundle(),
         calendar_name='NYSE',
         )
exit()
################################################


from zipline.data.bundles import register
from xtech_custom_bundle import ingest_xtech_eodhd_h5_bundle, ingest_xtech_yf_h5_bundle, ingest_xtech_sp500_data_bundle
import pandas_market_calendars as mcal

import pandas as pd
from zipline.data.bundles import register
from zipline.data.bundles.csvdir import csvdir_equities

print(f'Done with imports inside edge-seeker/.zipline/extension.py')

# Fetch the NYSE calendar
nyse_calendar = mcal.get_calendar('NYSE')

# Generate the valid trading sessions (days) between start_date and end_date
schedule = nyse_calendar.valid_days(start_date='1984-11-07', end_date='2024-10-11')

# Ensure the timestamps are timezone-naive
start_session = pd.Timestamp(schedule[0]).tz_localize(None)
end_session = pd.Timestamp(schedule[-1]).tz_localize(None)

# Register the EODHD bundle
register(
    'xtech_custom_eodhd_bundle',
    ingest_xtech_eodhd_h5_bundle,
    calendar_name='NYSE',    
    start_session=start_session,
    end_session=end_session,
)

print(f'Done with EODHD bundle')

# Register the YFinance bundle
register(
    'xtech_custom_yf_bundle',
    ingest_xtech_yf_h5_bundle,
    calendar_name='NYSE',
    start_session=start_session,
    end_session=end_session,
)

print(f'Done with YFinance bundle')

print(f'registering xtech_sp500_data_bundle')
register(
    'xtech_sp500_data_bundle',
    ingest_xtech_sp500_data_bundle,
    calendar_name='NYSE',
    start_session=pd.Timestamp('2000-01-03').floor('D'),
    end_session=pd.Timestamp.now().floor('D'),
)
print(f'done registering xtech_sp500_data_bundle')

print('starting xtech_sp500_csvdata_bundle import')
register(
    'xtech_sp500_csvdata_bundle',
    csvdir_equities(
        ['daily'],
        '/datastore/exponential/xtech/daily-prices/us-eqt/huge-python/v1/zl_csv/date=2024-10-17'        
    ),
    calendar_name='NYSE',
    start_session=pd.Timestamp('2000-01-03').floor('D'),
    end_session=pd.Timestamp.now().floor('D'),
)
print('done with xtech_sp500_csvdata_bundle import')



# from norgatedata import StockPriceAdjustmentType
# from zipline_norgatedata import register_norgatedata_equities_bundle,register_norgatedata_futures_bundle

# register_norgatedata_equities_bundle(
#     bundlename = 'norgatedata-aapl',
#     symbol_list = ['AAPL','$SPXTR',], 
#     start_session = '1990-01-02',
# )

print(f'starting csv import')


#start_session = pd.Timestamp(schedule[0], tz=None)
#end_session = pd.Timestamp(schedule[-1], tz=None)

register(
    'xtech_eodhd_csv',
    csvdir_equities(
        ['daily'],  # Use ['daily'] if you only have daily data
        '/datastore/exponential/xtech/daily-prices/us-eqt/huge-python/v1/zl_csv/date=2024-10-17'
    ),
    calendar_name='NYSE',  # Use appropriate exchange calendar
    start_session=start_session,
    end_session=end_session
)
print(f'done with csv import')




























###########################Norgate Stuff That didn't work##################################3
# import logging
# logging.basicConfig(level=logging.DEBUG)

# import sys
# from pathlib import Path
# import pandas as pd

# sys.path.append('z:\\.zipline')
# print(f'sys.path:{sys.path}')

# from zipline_norgatedata import register_norgatedata_equities_bundle
# from norgatedata import StockPriceAdjustmentType
# import pandas as pd

# # Set up Norgate Data parameters
# start_date = pd.Timestamp('2000-01-01').floor('D')
# end_date = pd.Timestamp.now().floor('D')  # This will remove the time component


# # Register the Norgate Data bundle
# bundle_name = 'norgate_nyse_equity'
# stock_price_adjustment_setting = StockPriceAdjustmentType.TOTALRETURN
# watchlists = ['XTech US Equity']  # Replace with the appropriate Norgate Data watchlist

# register_norgatedata_equities_bundle(
#     bundlename=bundle_name,
#     stock_price_adjustment_setting=stock_price_adjustment_setting,
#     watchlists=watchlists,
#     start_session=start_date,
#     end_session=end_date,
#     calendar_name='NYSE'
# )

# print(f"Bundle '{bundle_name}' registered successfully.")
# print(f"Start date: {start_date}")
# print(f"End date: {end_date}")



# ##################################################################33
# #Create a bundle for all US Stocks Past and Present
# # Create a bundle for all US Stocks Past and Present
# import norgatedata

# current_stocks = norgatedata.database('US Equities')
# delisted_stocks = norgatedata.database('US Equities Delisted')
# all_stocks = current_stocks + delisted_stocks

# valid_stocks = []

# # Validate symbols with Norgate Data API
# for stock in all_stocks:
#     try:
#         if norgatedata.assetid(stock) > 0:
#             valid_stocks.append(stock)
#     except ValueError:
#         #print(f"Skipping invalid symbol: {stock}")
#         pass

# print(f'Returned {len(valid_stocks)} valid stocks')

# from zipline_norgatedata import register_norgatedata_equities_bundle
# from norgatedata import StockPriceAdjustmentType
# from pandas import Timestamp

# register_norgatedata_equities_bundle(
#     bundlename='xtech_us_equity_sl_bundle',
#     stock_price_adjustment_setting=StockPriceAdjustmentType.TOTALRETURN,
#     symbol_list=valid_stocks,  # Use only validated symbols
#     start_session=Timestamp("2000-01-01").floor('D'),
#     end_session=Timestamp.now().floor('D'),
#     calendar_name='NYSE'
# )

# print(f"Bundle 'xtech_us_equity_bundle' registered successfully.")

# #### Use XTech S&P 500  Equity Watchlist


# from zipline_norgatedata import register_norgatedata_equities_bundle
# from norgatedata import StockPriceAdjustmentType
# import pandas as pd

# # Set up Norgate Data parameters
# start_date = pd.Timestamp('2000-01-01').floor('D')
# end_date = pd.Timestamp.now().floor('D')  # This will remove the time component

# # Register the Norgate Data bundle
# bundle_name = 'xtech_sp500_equity_bundle'
# stock_price_adjustment_setting = StockPriceAdjustmentType.TOTALRETURN
# watchlists = ['XTechPITSP500']  # Replace with the appropriate Norgate Data watchlist

# register_norgatedata_equities_bundle(
#     bundlename=bundle_name,
#     stock_price_adjustment_setting=stock_price_adjustment_setting,
#     watchlists=watchlists,
#     start_session=start_date,
#     end_session=end_date,
#     calendar_name='NYSE'
# )

# print(f"Bundle '{bundle_name}' registered successfully.")