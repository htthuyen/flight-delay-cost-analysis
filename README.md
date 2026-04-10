# American Airlines Flight Delay Cost Analysis (2024)

An end-to-end data analytics project analyzing the operational cost of **departure delays** for American Airlines across all 12 months of 2024, using real BTS (Bureau of Transportation Statistics) On-Time Performance data.

> **Dataset scope:** This dataset covers departure delay performance for all scheduled domestic flights. It records departure delay minutes for every flight and delay cause breakdown (carrier, weather, NAS, security, late aircraft) **only for flights delayed 15+ minutes**. Arrival delay, cancellations, and diversions are not included.

---

## Project Overview

Flight delays cost U.S. airlines billions of dollars annually. This project quantifies those costs for American Airlines specifically, identifies the highest-impact airports and delay causes, and surfaces actionable insights for reducing operational spend.

**Business questions answered:**
1. Which airports generate the highest delay-related operational costs?
2. Which delay causes (carrier, weather, late aircraft, etc.) drive the most cost?
3. When do delays cost the most — by time of day, day of week, and month?
4. Where should American Airlines focus first to reduce costs?

---

## Getting Started

### Prerequisites
- Python 3.8+
- Jupyter Notebook or JupyterLab

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/american-airlines-delay-analysis.git
   cd american-airlines-delay-analysis
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Launch Jupyter:
   ```bash
   jupyter notebook
   ```

### Data

Raw data files are not included in this repository (too large for GitHub). You need to download them manually.

1. Go to the [BTS On-Time Performance database](https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGJ&QO_fu146_anzr=b0-gvzr)
2. On the download page, select the following columns before downloading:

   | Column | Description |
   |---|---|
   | `Year` | Flight year |
   | `Month` | Month number |
   | `DayOfWeek` | Day of week |
   | `Reporting_Airline` | Airline IATA code |
   | `Origin` | Origin airport code |
   | `OriginCityName` | Origin city and state |
   | `Dest` | Destination airport code |
   | `DestCityName` | Destination city and state |
   | `CRSDepTime` | Scheduled departure time |
   | `DepDelay` | Departure delay in minutes |
   | `DepDel15` | 1 if delayed 15+ minutes |
   | `Distance` | Flight distance in miles |
   | `CarrierDelay` | Minutes delayed due to airline |
   | `WeatherDelay` | Minutes delayed due to weather |
   | `NASDelay` | Minutes delayed due to NAS/ATC |
   | `SecurityDelay` | Minutes delayed due to security |
   | `LateAircraftDelay` | Minutes delayed due to late aircraft |

3. Download one ZIP file per month for **Jan–Dec 2024** (12 files total)
4. Create a `unzip_data/` folder in the project root if it doesn't exist:
   ```bash
   mkdir unzip_data
   ```
5. Place all 12 ZIP files inside the `unzip_data/` folder

### Running the Project

Run the notebooks **in order**:

| Step | Notebook | What it does |
|---|---|---|
| 1 | `01_extract.ipynb` | Extracts ZIPs and saves `data/flights_2024.parquet` |
| 2 | `02_clean.ipynb` | Cleans data and saves `data/flights_2024_clean.parquet` |
| 3 | `03_analysis_AA.ipynb` | Runs the full analysis for American Airlines |

> **Want to analyze a different airline?** The notebook uses a `select_airline()` function that accepts any airline code. Just replace `"AA"` with another carrier code, for example:
> ```python
> # American Airlines
> aa_df = select_airline(df, "AA")
>
> # Delta Air Lines
> dl_df = select_airline(df, "DL")
>
> # United Airlines
> ua_df = select_airline(df, "UA")
> ```
> All valid carrier codes are listed in `L_UNIQUE_CARRIERS.csv`.

---

## Data Engineering

### Pipeline
- **Source:** 12 monthly ZIP archives (Jan–Dec 2024) from the BTS On-Time Performance database
- **Extraction:** Automated ZIP extraction using Python (`zipfile`, `glob`, `pathlib`) into structured monthly folders
- **Loading:** Concatenated all monthly CSVs into a single unified DataFrame using `pandas`
- **Lookup table joins:** Decoded numeric codes to human-readable labels via left merges with BTS reference tables:
  - `L_MONTHS.csv` → month names
  - `L_WEEKDAYS.csv` → day names
  - `L_UNIQUE_CARRIERS.csv` → airline names

### Data Cleaning
- Dropped rows missing departure delay data (`DEP_DELAY`, `DEP_DEL15`) — 92,970 rows removed (~1.3%)
- Filled null delay cause columns (`CARRIER_DELAY`, `WEATHER_DELAY`, etc.) with `0` — these fields are only populated by BTS for flights with `DEP_DEL15 = 1` (delayed 15+ minutes); null means no delay from that cause
- Validated data types and null counts post-cleaning

### Feature Engineering
| Feature | Description |
|---|---|
| `DEP_DELAY_COST` | `DEP_DELAY × $100.76`, clipped at 0 — estimated departure delay cost per flight |
| `CARRIER_COST`, `WEATHER_COST`, etc. | Per-cause cost: each delay cause column × $100.76 |
| `TIME_BLOCK` | Binned departure times into Morning / Afternoon / Night |
| `IS_WEEKEND` | Boolean flag for Saturday/Sunday departures |

> Cost rate source: [U.S. Passenger Carrier Delay Costs — airlines.org](https://www.airlines.org/dataset/u-s-passenger-carrier-delay-costs/) — average direct aircraft operating cost for U.S. passenger airlines in 2024 was **$100.76 per block minute**.

---

## Data Dictionary

### Raw Columns (from BTS source)

| Column | Type | Description |
|---|---|---|
| `YEAR` | int64 | Flight year |
| `MONTH` | int64 | Month number (1–12) |
| `DAY_OF_WEEK` | int64 | Day code (1=Monday, 7=Sunday) |
| `OP_UNIQUE_CARRIER` | object | Airline IATA code (e.g. `AA`, `DL`, `UA`) |
| `ORIGIN` | object | Origin airport IATA code (e.g. `DFW`, `LAX`) |
| `ORIGIN_CITY_NAME` | object | Origin city and state (e.g. `Dallas/Fort Worth, TX`) |
| `DEST` | object | Destination airport IATA code |
| `DEST_CITY_NAME` | object | Destination city and state |
| `CRS_DEP_TIME` | int64 | Scheduled departure time in HHMM format (e.g. `0600` = 6:00 AM) |
| `DEP_DELAY` | float64 | Departure delay in minutes; negative = early departure |
| `DEP_DEL15` | float64 | Binary flag: 1 if delayed 15+ minutes, 0 otherwise |
| `DISTANCE` | float64 | Flight distance in miles |
| `CARRIER_DELAY` | float64 | Minutes of delay attributed to the airline (e.g. maintenance, crew) — **populated only when `DEP_DEL15 = 1`** |
| `WEATHER_DELAY` | float64 | Minutes of delay attributed to weather conditions — **populated only when `DEP_DEL15 = 1`** |
| `NAS_DELAY` | float64 | Minutes of delay attributed to the National Airspace System (ATC, airport operations) — **populated only when `DEP_DEL15 = 1`** |
| `SECURITY_DELAY` | float64 | Minutes of delay attributed to security issues — **populated only when `DEP_DEL15 = 1`** |
| `LATE_AIRCRAFT_DELAY` | float64 | Minutes of delay caused by a late-arriving aircraft on a prior flight — **populated only when `DEP_DEL15 = 1`** |

### Decoded Lookup Columns (added in `01_extract.ipynb`)

| Column | Type | Description |
|---|---|---|
| `MONTH_NAME` | object | Human-readable month name (e.g. `January`) — decoded from `L_MONTHS.csv` |
| `DAY` | object | Human-readable day name (e.g. `Monday`) — decoded from `L_WEEKDAYS.csv` |
| `AIRLINE` | object | Full airline name (e.g. `American Airlines Inc.`) — decoded from `L_UNIQUE_CARRIERS.csv` |
| `source_file` | object | Name of the source ZIP/folder the row came from (e.g. `jan-2024`) — used for traceability |

### Engineered Features (added in `02_clean.ipynb`)

| Column | Type | Description |
|---|---|---|
| `DEP_DELAY_COST` | float64 | Estimated cost of departure delay: `DEP_DELAY × $100.76`, clipped at 0 |
| `CARRIER_COST` | float64 | Estimated cost attributable to carrier delay: `CARRIER_DELAY × $100.76` |
| `WEATHER_COST` | float64 | Estimated cost attributable to weather delay: `WEATHER_DELAY × $100.76` |
| `NAS_COST` | float64 | Estimated cost attributable to NAS delay: `NAS_DELAY × $100.76` |
| `SECURITY_COST` | float64 | Estimated cost attributable to security delay: `SECURITY_DELAY × $100.76` |
| `LATE_AIRCRAFT_COST` | float64 | Estimated cost attributable to late aircraft delay: `LATE_AIRCRAFT_DELAY × $100.76` |
| `TIME_BLOCK` | object | Departure time group based on `CRS_DEP_TIME`: `Morning` (05:00–11:59), `Afternoon` (12:00–17:59), `Night` (18:00–04:59) |
| `IS_WEEKEND` | bool | `True` if the flight departs on Saturday or Sunday |

> Cost rate source: [U.S. Passenger Carrier Delay Costs — airlines.org](https://www.airlines.org/dataset/u-s-passenger-carrier-delay-costs/) — $100.76 per block minute (2024).

---

## Data Analytics

### Airport Cost Analysis
- Aggregated total delay cost and computed each airport's cost share
- Multi-metric `groupby` aggregation: total cost, average delay, delay rate, and flight volume per origin airport
- **Finding:** DFW alone accounts for ~19.2% of total delay cost, followed by CLT (12.9%) and MIA (6.6%)

### Delay Cause Breakdown
- Computed cost per delay category across all AA flights
- **Finding:** Late aircraft delay (~48%) and carrier delay (~33%) together account for ~81% of total delay cost — both are controllable internal factors

### Temporal Analysis
- Time-of-day segmentation using the `TIME_BLOCK` column engineered in `02_clean.ipynb`
- Weekend vs. weekday cost comparison
- Month-over-month cost aggregation
- **Finding:** Afternoon departures carry the highest total delay cost ($857M), followed by Night ($769M) and Morning ($661M); summer months (July, May, June) are peak cost periods

### Strategic Focus
- Filtered to the single highest-cost segment: DFW + Night + Late Aircraft delay
- **Conclusion:** Cascading delays at DFW during nighttime operations represent the single largest opportunity for cost reduction

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3 | Core language |
| pandas | Data loading, cleaning, transformation, aggregation |
| matplotlib | Visualization |
| pyarrow | Parquet file read/write between pipeline steps |
| zipfile / glob / pathlib | Automated file extraction pipeline |
| Jupyter Notebook | Interactive analysis and documentation |

---

## Repository Structure

```
.
├── 01_extract.ipynb               # Extract ZIPs, concat CSVs, merge lookups → flights_2024.parquet
├── 02_clean.ipynb                 # Clean nulls, engineer features → flights_clean.parquet
├── 03_analysis_AA.ipynb           # American Airlines delay cost analysis
├── unzip_data/
│   ├── *.zip                      # Raw monthly ZIP files (Jan–Dec 2024)
├── data/
│   ├── flights_2024.parquet       # Output of 01_extract
│   └── flights_2024_clean.parquet # Output of 02_clean
├── extracted_files/               # Extracted CSVs per month
├── utils/
│   ├── logger.py                  # Shared logging setup
│   └── filters.py                 # Reusable filter functions (e.g. select_airline)
├── L_MONTHS.csv                   # BTS month code lookup
├── L_WEEKDAYS.csv                 # BTS weekday code lookup
├── L_UNIQUE_CARRIERS.csv          # BTS airline carrier lookup
└── requirements.txt               # Python dependencies
```

---

## Key Findings Summary

| Question | Finding |
|---|---|
| Highest-cost airport | DFW — ~19.2% of total delay cost |
| Top delay cause | Late aircraft delay — ~48% of cost |
| Most expensive time of day | Afternoon departures (highest total cost) |
| Most expensive months | July, May, June |
| Controllable cost share | ~81% driven by internal factors |
| Recommended focus | Nighttime DFW operations — cascading late aircraft delays |
