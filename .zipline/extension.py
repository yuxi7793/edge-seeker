print(f'in: edge-seeker/.zipline/extension.py')
import sys
from pathlib import Path
import pandas as pd
#sys.path.append(Path('~', '/repos/edge-seeker/alpha-flux/xtech_bundle').expanduser().as_posix())
#sys.path.append(Path('~', '/repos/edge-seeker/.zipline').expanduser().as_posix())
sys.path.append(Path.home().joinpath('repos/edge-seeker/.zipline').as_posix())

#sys.path.append(Path('~', '.zipline').expanduser().as_posix())
print(f'sys.path:{sys.path}')
from zipline.data.bundles import register
from xtech_custom_bundle import ingest_xtech_eodhd_h5_bundle
from xtech_custom_bundle import ingest_xtech_yf_h5_bundle
#import xtech_custom_bundle

print(f'Done with imports inside edge-seeker/.zipline/extension.py')



register(
    'xtech_custom_eodhd_bundle',
    ingest_xtech_eodhd_h5_bundle,
    calendar_name='NYSE', 
    start_session=pd.Timestamp('2007-01-01', tz='UTC'),
    end_session=pd.Timestamp('2024-10-11', tz='UTC'),
)




print(f'Done with EODHD bundle')

register(
    'xtech_custom_yf_bundle',
    ingest_xtech_yf_h5_bundle,
    calendar_name='NYSE', 
    start_session=pd.Timestamp('2007-01-01', tz='UTC'),
    end_session=pd.Timestamp('2024-10-11', tz='UTC'),
)


print(f'Done with YFinance bundle')