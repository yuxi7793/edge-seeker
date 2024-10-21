# AlphaFactor-Backtester
### **Summer 2024 Project at UChicago in collaboration with Exponential Tech and Deception &amp; Truth Analysis. This tool backtests fundamental factors using the Zipline-Reloaded framework, enabling robust analysis and evaluation of investment strategies.**

---

### Set you environment variables
* in ~/.bashrc (~/.zshrc on macOS) set the location of the root folder of the project which will include three different cloned repos and a .zipline data directory.  It is technically an .SQLLite database.
export ZIPLINE_ROOT=/home/morgan/repos/edge-seeker/zipline-x/.zipline

* Add the QUANDL_API key to your ~/.bashrc (~/.zshrc on macOS) 
export QUANDL_API_KEY=tw2sxkKZo_y1UvMcnSux

### Required Installations
To get started, you need to install two additional packages: zipline-reloaded and pyfolio-reloaded.
1. Create a folder called zipline_x
2.	Clone pyfolio-reloaded for analyzing and plotting backtest results. You can find it [here](https://github.com/YuweiUltra/pyfolio-reloaded). This version includes functionality to output plots in an HTML file.
3.	Clone zipline-reloaded for backtesting trading strategies. You can find it [here](https://github.com/YuweiUltra/zipline-reloaded).
4.	Clone this AlphaFactor-Backtester repository.

### Create a conda environment and install repos
Warning: Do not deviate from this sequence or you may have dependency clashes

conda create --name zip_312 python=3.12
conda activate zipline_x_312
pip install numpy==1.26.4

From pyfolio-reloaded:
pip install .
From zipline-reloaded:
pip install .

### project Structure
```
zipline_x
├── .zipline/                  # Configuration and data for Zipline
├── AlphaFactor-Backtester/    # Main project directory
├── pyfolio-reloaded/          # Pyfolio library for performance analysis and visualization
└── zipline-reloaded/          # Zipline Reloaded library for backtesting trading
```
If .zipline/ does not exist in your root directory, run the following command in your terminal:
```
zipline ingest
```

### Creating a Custom Bundle
Zipline uses bundle data to speed up backtests. Therefore, we need to create and ingest our custom bundle data.

In this project, I used Quandl EOD data downloaded from Nasdaq Data Link. First, I ran a quandl_preprocessing script to store the data in a more readable quandl.h5 file with a unique sid for each ticker. (! This step is time consuming and not necessary if you use data from other source.)

Next, create quandl_custom_bundle.py (the name can vary) and extension.py in the .zipline/ directory.

Your .zipline/ directory should look like this:
```
~/.zipline/
│
├── quandl_custom_bundle.py
└── extension.py
```
Once everything is set up correctly, run the following command to ingest the custom bundle:
```
zipline ingest -b quandl_custom_bundle
```
After successfully ingesting the data, the directory structure will look like this:
```
~/.zipline/
│
├── data
│   └── quandl_custom_bundle
│       └── 2024-08-15T07:00:21.328524
├── quandl_custom_bundle.py
└── extension.py
```

### Starting the Backtest 
You can start the backtest by running main.py with terminal arguments for parsing parameters, or you can directly run one of the following scripts:

	•	backtest_DollarNeutral.py
	•	backtest_Parallelize.py
	•	backtest_Decile.py

---

## Thanks
We are truly grateful to Jason from Deception & Truth Analysis and Morgan from Exponential Tech for providing us with these fantastic datasets and the opportunity to learn so much during this project. We’re excited about the insights we’ve gained and look forward to seeing how these signals can be applied in real-world trading scenarios.

Finally, enjoy the research and have fun! Good luck and happy trading! 😄


XTech credentials:

API Key: tw2sxkKZo_y1UvMcnSux
https://data.nasdaq.com/databases/EOD
https://quotemedia.com/
