import pandas as pd
from pathlib import Path
import warnings
import numpy as np
from tqdm import tqdm
import logging
import os
import h5py


# Adding a stream handler to ensure logs go to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
import sys
from pathlib import Path

sys.path.append(Path('~', '.zipline').expanduser().as_posix())
print(f'sys.path:{sys.path}')
zipline_root = os.path.expanduser('~/repos/edge-seeker/.zipline')
custom_data_path = Path(zipline_root, 'custom_data')
from zipline.data.bundles import load
from zipline.assets import AssetFinder

bundle_data = load('quandl_custom_bundle')
finder = bundle_data.asset_finder

# List all assets with country 'US'
us_assets = finder.retrieve_all(finder.sids)
for asset in us_assets:
    print(asset)
