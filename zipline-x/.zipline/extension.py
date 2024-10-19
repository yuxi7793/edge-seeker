print(f'in: edge-seeker/.zipline/extension.py')

#################################################3

import sys
from pathlib import Path
import pandas as pd

sys.path.append(Path.home().joinpath('repos/edge-seeker/zipline-x/.zipline').as_posix())
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
print(f'registered quandl_custom_bundle')