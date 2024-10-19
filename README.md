# README - NO REALLY -- README!#

Welcome to the UChicago Project Lab Community Repo where you will be able to share in a truly open source manner all the brilliant ideas and fails that you come up with. 

Here are some tips that if you learn to follow religiously you will begin a love affair with GIT that will last a lifetime and if you will ignore at your own risk and be a glutton for merge punishment.

One of the reasons we are teaching you this is so that you can leverage this super power when you graduate and are in the real world.

### Procedures for commiting code

* You are not permitted to push code to the "main" banch; to edit code you must create a branch first.  

git clone <repo url>  

### create a branch on the webpage to develop your code changes in
* git fetch
* git checkout <branch>
* git add <files>
* git commit -a -m "commit message"
* git push
* create pull request on the webpage to merge using "rebase and fast forward"

### If you have a branch, and someone else has merge their branch to main resulting in your branch being outdated, you can rebase your branch on main this way:
* git checkout main
* git pull --rebase
* git checkout my-branch
* git rebase main
* git push -f origin my-branch

### How do I tell if my branch is out of date?
Go to the branches page on the bitbucket website
Select all branches
Hover over the modal for your branch and it will say how many commits ahead and behind you are.  You must be 0 behind main before you can push 





# AlphaFactor-Backtester
### **Summer 2024 Project at UChicago in collaboration with Exponential Tech and Deception &amp; Truth Analysis. This tool backtests fundamental factors using the Zipline-Reloaded framework, enabling robust analysis and evaluation of investment strategies.**

---

### Required Installations
To get started, you need to install two additional packages: zipline-reloaded and pyfolio-reloaded.

1.	Clone pyfolio-reloaded for analyzing and plotting backtest results. You can find it [here](https://github.com/YuweiUltra/pyfolio-reloaded). 
This version includes functionality to output plots in an HTML file.
2.	Clone zipline-reloaded for backtesting trading strategies. You can find it [here](https://github.com/YuweiUltra/zipline-reloaded).
3.	Clone this AlphaFactor-Backtester repository.

### project Structure
```
* Put the base of the project wherever you want and simply set this env variable: ZIPLINE_ROOT=/home/morgan/repos/edge-seeker/.zipline
.
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

In this project, I used Quandl EOD data downloaded from Nasdaq Data Link. First, 
I ran a quandl_preprocessing script to store the data in a more readable quandl.h5 file with a unique sid for each ticker. 
(! This step is time consuming and not necessary if you use data from other source.)

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
You can start the backtest by running main.py with terminal arguments for parsing parameters, 
or you can directly run one of the following scripts:

	•	backtest_DollarNeutral.py
	•	backtest_Parallelize.py
	•	backtest_Decile.py


---

## Thanks
We are truly grateful to Jason from Deception & Truth Analysis and Morgan from Exponential Tech for providing us with these fantastic datasets and the opportunity to learn so much during this project. We’re excited about the insights we’ve gained and look forward to seeing how these signals can be applied in real-world trading scenarios.

Finally, enjoy the research and have fun! Good luck and happy trading! 😄




######################################################


Notes on how to create environment

https://www.perplexity.ai/search/how-can-i-install-ta-lab-on-py-7Bjm7KhSQYm25GlzNo9okA#0

To install TA-Lib for Python 3.12 on Ubuntu Linux 20, you'll need to follow a two-step process: first, install the TA-Lib C library, and then install the Python wrapper. Here's a detailed guide:

## Installing TA-Lib C Library

First, you need to install the TA-Lib C library:

1. Open a terminal window.

2. Download the TA-Lib source code:

```
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
```

3. Extract the downloaded file:

```
tar -xzf ta-lib-0.4.0-src.tar.gz
```

4. Navigate to the extracted directory:

```
cd ta-lib/
```

5. Configure, build, and install the library:

```
./configure --prefix=/usr
make
sudo make install
```

**Note:** If the build fails with `make -jX`, simply rerun `make` followed by `sudo make install`[1][3].

## Installing TA-Lib Python Wrapper

After installing the C library, you can proceed to install the Python wrapper:

1. Ensure you have pip installed for Python 3.12. If not, install it:

```
sudo apt-get update
sudo apt-get install python3-pip
```

2. Install the TA-Lib Python wrapper:

```
pip3 install TA-Lib
```

If you encounter any issues, you might need to specify the include and library paths:

```
export TA_INCLUDE_PATH=/usr/include
export TA_LIBRARY_PATH=/usr/lib
pip3 install TA-Lib
```

## Alternative Installation Method

If you're using Anaconda or Miniconda, you can try an alternative method:

1. Open Anaconda prompt or terminal.

2. Run the following command:

```
conda install -c conda-forge ta-lib
```

This method often works across different platforms and is generally easier[2].

## Verifying the Installation

After installation, you can verify if TA-Lib is correctly installed by running Python and importing the library:

```python
import talib
print(talib.__version__)
```

If this runs without errors and prints the version number, TA-Lib has been successfully installed.

Remember to use `python3` or `python3.12` commands instead of `python` if your system has multiple Python versions installed, to ensure you're using Python 3.12.

Citations:
[1] https://pypi.org/project/TA-Lib/
[2] https://blog.quantinsti.com/install-ta-lib-python/
[3] https://ta-lib.github.io/ta-lib-python/install.html








XTech credentials:

API Key: tw2sxkKZo_y1UvMcnSux

https://data.nasdaq.com/databases/EOD

https://quotemedia.com/
