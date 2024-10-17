print(f'in: edge-seeker/.zipline/extension.py')
import sys
from pathlib import Path
import pandas as pd

sys.path.append(Path.home().joinpath('repos/edge-seeker/.zipline').as_posix())
print(f'sys.path:{sys.path}')

from zipline.data.bundles import register
from xtech_custom_bundle import ingest_xtech_eodhd_h5_bundle, ingest_xtech_yf_h5_bundle
import pandas_market_calendars as mcal

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

# from norgatedata import StockPriceAdjustmentType
# from zipline_norgatedata import register_norgatedata_equities_bundle,register_norgatedata_futures_bundle

# register_norgatedata_equities_bundle(
#     bundlename = 'norgatedata-aapl',
#     symbol_list = ['AAPL','$SPXTR',], 
#     start_session = '1990-01-02',
# )

print(f'starting csv import')

import pandas as pd
from zipline.data.bundles import register
from zipline.data.bundles.csvdir import csvdir_equities

#start_session = pd.Timestamp(schedule[0], tz=None)
#end_session = pd.Timestamp(schedule[-1], tz=None)

register(
    'xtech_eodhd_csv',
    csvdir_equities(
        ['daily'],  # Use ['daily'] if you only have daily data
        '/datastore/exponential/xtech/daily-prices/us-eqt/huge-python/v1/zl_csv/date=2024-10-14'
    ),
    calendar_name='NYSE',  # Use appropriate exchange calendar
    start_session=start_session,
    end_session=end_session
)
