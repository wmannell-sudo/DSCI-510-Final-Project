# **DSCI 510 Final Project**

## **California Coastal Sea-Level and Housing Risk Analysis**

---

## **Project Description**

This project was completed for **DSCI 510: Principles of Programming for Data Science**. The objective of the project is to demonstrate the ability to design a reproducible data science workflow that includes data acquisition, data cleaning, analysis, and visualization using Python.

The project analyzes recent sea-level variability at NOAA tide gauge stations along the California coast and combines this information with nearby housing values to conceptualize relative coastal risk. The analysis is exploratory and intended for instructional purposes.

---

## **Repository Structure**

The repository follows the structure required by the course rubric with approved deviations.

`.`  
`.`  
`├── data/`  
`│   ├── raw/`  
`│   │   ├── ca_noaa_stations.csv`  
`│   │   └── timeseries-cache/`  
`│   │       ├── 9410170_water_level.csv`  
`│   │       ├── 9410230_water_level.csv`  
`│   │       ├── 9410660_water_level.csv`  
`│   │       ├── 9410840_water_level.csv`  
`│   │       ├── 9411340_water_level.csv`  
`│   │       ├── 9412110_water_level.csv`  
`│   │       ├── 9413450_water_level.csv`  
`│   │       ├── 9414290_water_level.csv`  
`│   │       ├── 9414523_water_level.csv`  
`│   │       ├── 9414750_water_level.csv`  
`│   │       ├── 9414863_water_level.csv`  
`│   │       ├── 9415020_water_level.csv`  
`│   │       ├── 9416841_water_level.csv`  
`│   │       ├── 9418767_water_level.csv`  
`│   │       ├── 9419750_water_level.csv`  
`│   │       └── additional_station_water_level.csv`  
`│   │`  
`│   └── processed/`  
`│       ├── combined_ca_water_levels.csv`  
`│       ├── combined_risk_data.csv`  
`│       └── stations_with_housing.csv`  
`│`  
`├── results/`  
`│   ├── ca_coastal_risk_map.html   #folium map`  
`│   ├── scatter_trend_vs_housing.png    #scatter plot of risk`  
`│   ├── bar_risk_scores.png     #Bar graph of risk score`  
`│   ├── line_trends.png		#Line graph of water-level trend`  
`│   ├── Final Report.PDF    #PDF of final report`  
`│   ├── data/ #data folder created by notebook, contains same files as`   
`the other data folder; approved by Dr. Hen`  
`│   │   ├── raw/`  
`│   │   └── processed/`  
`│   └── notebooks/`  
`│       ├── DSCI510 - Final Notebook for Wila and Sofia.pdf #PDF Vers.`  
`│       └── DSCIFINALNOTEBOOK (2) (3).ipynb #End-to-end notebook`   
`containing the code from the .py files but run inline to show the orchestration and load visualizations`  
`│`  
`├── src/`  
`│   ├── get_data.py`      
`│   ├── clean_data.py`  
`│   ├── run_analysis.py`  
`│   ├── visualize_results.py`  
`│`  
`├── requirements.txt`  
`├── README.md`  
`└── Updated Plan for Final project.pdf`

### **Folder Descriptions**

* **`data/`**  
   Contains all datasets used in the project.

  * `raw/` holds data downloaded directly from APIs with no modification.

  * `processed/` holds cleaned and transformed datasets used for analysis.

* **`results/`**  
   Contains final outputs of the analysis, including visualizations and copies of data used to generate figures.

  * Four final visualizations are stored at the top level of this folder.

  * A `data/` subfolder mirrors the structure of the main `data/` directory for reproducibility.

  * A `notebooks/` subfolder contains Jupyter notebooks used to run and present the analysis.

* **`src/`**  
   Contains modular Python scripts implementing each stage of the data science workflow:

  * Data acquisition

  * Data cleaning

  * Analysis

  * Visualization

* **Top-level files**

  * `requirements.txt` lists required Python packages.

  * `README.md` documents the project structure and usage.

  * `Updated Plan for Final project.pdf` contains the original project proposal.

---

## **Data Acquisition (`get_data.py`)**

Raw data is obtained from two sources:

1. **NOAA Tides and Currents API**  
    Used to download:

   * California coastal tide gauge station metadata

   * Recent water level time series for each station

2. **California Housing Dataset (Scikit-learn)**  
    Used to obtain:

   * Median house value

   * Geographic coordinates

All data downloaded directly from APIs is saved in the `data/raw/` directory as CSV files, in accordance with the rubric.

---

## **Data Cleaning and Processing (`clean_data.py`)**

The data cleaning step includes:

* Type conversion and handling of missing values

* Filtering to California coastal stations

* Formatting and standardizing column names

* Preparing datasets for analysis

Cleaned and transformed datasets are saved to the `data/processed/` directory.

---

## **Analysis (`run_analysis.py`)**

The analysis step includes:

* Computing linear sea-level trends from water level time series

* Identifying the nearest housing data point for each tide station using a KDTree

* Normalizing sea-level trends and housing values

* Computing a simple, relative risk score

The analysis is exploratory and designed to demonstrate programming and data analysis concepts rather than produce a predictive model.

---

## **Visualization (`visualize_results.py`)**

The visualization step produces:

* An interactive map showing California coastal tide stations

* A scatter plot of sea-level trend versus median housing value

* A bar chart of calculated risk scores by station

* A line plot of sea-level trends by station

Visualizations are created using `matplotlib` and `folium`.

---

## **Notebook Execution**

The primary execution and demonstration of the project is provided in:

`notebook/DSCIFINALNOTEBOOK (2) (3).ipynb`

The notebook:

* Runs the full workflow end-to-end

* Calls the same logic implemented in the `src/` scripts

* Displays intermediate results and final visualizations inline

The notebook is intended to clearly demonstrate the project workflow for grading and reproducibility.

---

## **How to Run the Project**

### **Install Requirements**

`pip install -r requirements.txt`

### **Run via Notebook (Recommended)**

Open and run all cells in:

`notebook/DSCIFINALNOTEBOOK (2) (3).ipynb`

### **Run via Python Scripts (Optional)**

Each stage may also be run independently:

`python src/get_data.py`  
`python src/clean_data.py`  
`python src/run_analysis.py`  
`python src/visualize_results.py`

---

## **Limitations**

* Sea-level trends are computed over a short time window and may reflect short-term variability.

* Housing data is used as a proxy for exposure and does not represent real-time market values.

* The calculated risk score is conceptual and intended for instructional purposes only.  
    
* Duplicate data is stored in two locations as a result of how the notebook functions

---

## **Authors**

* Sofia Young

* Wila Mannela

