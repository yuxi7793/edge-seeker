import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import pyfolio as pf
import warnings
import argparse
from utils import (
    get_russell1000_data,
    get_russell2000_data,
    get_sp500_etf_data,
)

warnings.filterwarnings("ignore")


def plotting(results, results_dir, benchmark, LIVE_DATE='2023-01-01'):
    """
    Plot various financial metrics and save results as a tear sheet.

    Parameters:
        results (pd.DataFrame): The backtest results data.
        results_dir (str): Directory where results will be saved.
        benchmark (pd.Series): Benchmark returns to compare against.
        LIVE_DATE (str): Date when the live trading started.
    """
    # Extract performance metrics from the backtest results
    returns, positions, transactions = pf.utils.extract_rets_pos_txn_from_zipline(results)
    rewrite = True  # Flag to determine if existing plots should be overwritten

    # Define the filename for the aggregated full tear sheet
    aggregated_filename = "xtech_tearsheet.html"
    aggregated_file_path = os.path.join(results_dir, aggregated_filename)

    # Check if the file already exists
    if os.path.exists(aggregated_file_path):
        if rewrite:
            os.remove(aggregated_file_path)  # Remove the file if rewrite is True
        else:
            print('Plotting already exists and rewrite is set to False')
            return

    # Extract cash values from the results
    cash = results['ending_cash']

    # Create a plot for cash over time
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 4))  # Adjust figure size as needed
    ax.plot(cash.index, cash, label='Cash', color='orange')
    ax.set_title('Cash Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Cash')
    ax.legend()
    ax.grid(True)

    fig.tight_layout()
    plt.savefig(os.path.join("./plots/temp", 'ending_cash.png'), bbox_inches='tight')

    # Generate and save a full tear sheet using pyfolio
    pf.create_full_tear_sheet(returns,
                              positions=positions,
                              transactions=transactions,
                              benchmark_rets=benchmark,
                              round_trips=True,
                              results_dir=results_dir,
                              live_start_date=LIVE_DATE
                              )


def process_backtest_results(results_dir,live_date):
    """
    Process backtest results from a given directory.

    Parameters:
        results_dir (str): Directory containing the backtest results and settings.
    """
    # Load the backtest settings from the JSON file
    settings_file = os.path.join(results_dir, 'BacktestSetting.json')
    if not os.path.exists(settings_file):
        print(f"Settings file not found in {results_dir}. Skipping...")
        return

    with open(settings_file, 'r') as f:
        BacktestSetting = json.load(f)

    # Determine the benchmark data based on the primary index in the settings
    if BacktestSetting['primaryindex'] == "S&P 500":
        benchmark = get_sp500_etf_data(BacktestSetting['start_date'], BacktestSetting['end_date'])
    elif BacktestSetting['primaryindex'] == "Russell 2000":
        benchmark = get_russell2000_data(BacktestSetting['start_date'], BacktestSetting['end_date'])
    elif BacktestSetting['primaryindex'] == "Russell 1000":
        benchmark = get_russell1000_data(BacktestSetting['start_date'], BacktestSetting['end_date'])
    else:
        print(f"Unknown primary index {BacktestSetting['primaryindex']} in {results_dir}. Skipping...")
        return

    # Load the results from the HDF5 file
    results_file = os.path.join(results_dir, 'results.h5')
    if not os.path.exists(results_file):
        print(f"Results file not found in {results_dir}. Skipping...")
        return

    results = pd.read_hdf(results_file, 'results')

    # Generate and save the plots and tear sheet
    LIVE_DATE = '2023-01-01'
    plotting(results, results_dir, benchmark, live_date)

def main(live_date='2010-01-01', result_name=None):
    """
    Main function to process backtest results based on the provided parameters.

    Parameters:
    live_date (str): The date used to filter live results. Default is '2010-01-01'.
    result_name (str): The specific result name to process. If None, processes all in the results directory.
    """
    root_dir = os.path.expanduser("~/repos/edge-seeker/zipline-x/results")
    base_dir = f'{root_dir}/plots/temp'
    os.makedirs(os.path.dirname(f'{base_dir}'), exist_ok=True)
    os.chdir(root_dir)
    # Loop through all directories in the base directory or process a specific result name
    if result_name:
        results_dir = os.path.join(base_dir, result_name)
        if os.path.isdir(results_dir):
            print(f"Processing backtest results in {results_dir}...")
            process_backtest_results(results_dir,live_date)
        else:
            print(f"Error: Specified result name '{result_name}' does not exist in {base_dir}.")
    else:
        # Loop through all directories if no specific result name is provided
        for dir_name in os.listdir(base_dir):
            results_dir = os.path.join(base_dir, dir_name)
            if os.path.isdir(results_dir):  # Process only directories
                print(f"Processing backtest results in {results_dir}...")
                process_backtest_results(results_dir,live_date)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process backtest results based on specified parameters.')
    parser.add_argument('--live_date', type=str, default='2010-01-01', help='The date used to filter live results.')
    parser.add_argument('--result_name', type=str, default='20241022_011816', help='Specific result name to process. If not provided, processes all results.')
    
    args = parser.parse_args()
    
    main(live_date=args.live_date, result_name=args.result_name)
