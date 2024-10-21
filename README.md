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


