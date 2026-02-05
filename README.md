# Stock Analysis System

A comprehensive Python-based system for downloading, storing, and analyzing stock market data. This project provides tools to fetch historical price data, store it efficiently in Parquet format, and perform technical analysis with visualization capabilities.

## Features

- **Data Acquisition**: Download daily and hourly stock data using yfinance (Yahoo Finance)
- **Efficient Storage**: Store data in compressed Parquet format (5-10x smaller than CSV)
- **Multiple Interfaces**: Both Python API and command-line scripts
- **Rich Visualizations**: Candlestick charts, technical indicators, multi-stock comparisons
- **Technical Analysis**: Moving averages, RSI, Bollinger Bands, and more
- **Jupyter Notebooks**: Interactive tutorials and analysis examples

## Quick Start

### 1. Installation

Create the conda environment:

```bash
conda env create -f environment.yml
conda activate stock_analysis
```

### 2. Download Stock Data

Download daily data for the default tech giants (AAPL, GOOGL, MSFT, AMZN, TSLA):

```bash
python scripts/download_daily.py
```

Download hourly data:

```bash
python scripts/download_hourly.py
```

### 3. Explore in Jupyter

Launch Jupyter Lab and open the quick start notebook:

```bash
jupyter lab
# Open notebooks/01_quick_start.ipynb
```

## Project Structure

```
stock_analysis/
├── config/
│   └── settings.py           # Configuration (symbols, paths, etc.)
├── src/
│   ├── data_fetcher.py       # Download stock data from Yahoo Finance
│   ├── data_storage.py       # Save/load data in Parquet format
│   ├── data_utils.py         # Utility functions
│   └── visualizer.py         # Plotting and visualization
├── scripts/
│   ├── download_daily.py     # Download daily data
│   ├── download_hourly.py    # Download hourly/intraday data
│   └── update_data.py        # Update existing data
├── notebooks/
│   ├── 01_quick_start.ipynb      # Getting started tutorial
│   ├── 02_data_exploration.ipynb # Data exploration & quality
│   ├── 03_basic_analysis.ipynb   # Technical analysis
│   └── 04_visualization.ipynb    # Advanced visualizations
├── data/                     # Data storage (created automatically)
│   ├── daily/               # Daily OHLCV data (Parquet files)
│   └── hourly/              # Hourly data (Parquet files)
└── logs/                    # Log files (created automatically)
```

## Usage

### Command-Line Scripts

**Download daily data:**
```bash
# Download default symbols with maximum available history
python scripts/download_daily.py

# Download specific symbols
python scripts/download_daily.py --symbols AAPL GOOGL MSFT

# Download with date range
python scripts/download_daily.py --start 2020-01-01 --end 2023-12-31
```

**Download hourly data:**
```bash
# Download default symbols with hourly data (~2 years)
python scripts/download_hourly.py

# Download with specific interval
python scripts/download_hourly.py --interval 30m --period 1mo

# Download specific symbols
python scripts/download_hourly.py --symbols TSLA --period 730d
```

**Update existing data:**
```bash
# Update all daily data to latest
python scripts/update_data.py --type daily

# Update hourly data
python scripts/update_data.py --type hourly --interval 1h

# Update specific symbols
python scripts/update_data.py --type daily --symbols AAPL GOOGL
```

### Python API

```python
from src.data_fetcher import StockDataFetcher
from src.data_storage import DataStorage
from src.visualizer import plot_price_history

# Download data
fetcher = StockDataFetcher()
data = fetcher.download_daily(['AAPL'], start_date='2020-01-01')

# Save to storage
storage = DataStorage()
storage.save_daily('AAPL', data['AAPL'])

# Load from storage
df = storage.load_daily('AAPL', start_date='2023-01-01')

# Visualize
import matplotlib.pyplot as plt
fig = plot_price_history(df, symbol='AAPL', column='Close')
plt.show()
```

## Configuration

Edit [config/settings.py](config/settings.py) to customize:

- **Default symbols**: Change `DEFAULT_SYMBOLS` list
- **Data paths**: Modify `DATA_DIR`, `DAILY_DIR`, `HOURLY_DIR`
- **Date ranges**: Set `DEFAULT_START_DATE`
- **API settings**: Adjust `MAX_RETRIES`, `RETRY_DELAY`

## Data Storage

### Format
- **Daily data**: `data/daily/SYMBOL.parquet` (e.g., `AAPL.parquet`)
- **Hourly data**: `data/hourly/SYMBOL_INTERVAL.parquet` (e.g., `AAPL_1h.parquet`)

### Benefits of Parquet
- **Compression**: 5-10x smaller than CSV
- **Speed**: Faster read/write operations
- **Type preservation**: Maintains datetime and numeric types
- **Columnar format**: Efficient for analytical queries

### Storage Examples
- 5 stocks × 5 years daily data: ~25 MB (vs ~150 MB for CSV)
- 5 stocks × 2 years hourly data: ~240 MB (vs ~1.2 GB for CSV)

## Technical Analysis Features

The notebooks demonstrate various technical analysis techniques:

- **Returns Analysis**: Daily returns, cumulative returns, volatility
- **Moving Averages**: SMA 20, 50, 200
- **RSI**: Relative Strength Index (overbought/oversold)
- **Bollinger Bands**: Volatility bands
- **Correlation Analysis**: Multi-stock correlation matrices
- **Volume Analysis**: Trading volume patterns

## Notebooks

### [01_quick_start.ipynb](notebooks/01_quick_start.ipynb)
- Download your first stock data
- Save and load data
- Basic visualization
- Complete workflow example

### [02_data_exploration.ipynb](notebooks/02_data_exploration.ipynb)
- Load multiple stocks
- Data quality checks
- Statistical summaries
- Correlation analysis

### [03_basic_analysis.ipynb](notebooks/03_basic_analysis.ipynb)
- Calculate returns
- Moving averages
- RSI indicator
- Bollinger Bands

### [04_visualization.ipynb](notebooks/04_visualization.ipynb)
- Candlestick charts
- Multi-stock comparisons
- Volume analysis
- Correlation heatmaps

## Data Limitations

### Hourly/Intraday Data (yfinance)
- **1h interval**: ~730 days (2 years) maximum
- **5m interval**: ~60 days maximum
- **1m interval**: ~7 days maximum

For longer historical intraday data, consider using alternative APIs (alpha_vantage, etc.)

### Daily Data
- Most stocks: Decades of historical data available
- Data quality: Generally reliable, but validate for critical use

## Troubleshooting

**Issue: No data downloaded**
- Check internet connection
- Verify symbol is valid (use uppercase, e.g., AAPL not aapl)
- Check yfinance service status

**Issue: Import errors**
- Ensure conda environment is activated: `conda activate stock_analysis`
- Reinstall environment: `conda env remove -n stock_analysis && conda env create -f environment.yml`

**Issue: Slow downloads**
- Reduce number of symbols
- Check network speed
- yfinance sometimes has rate limits

## Future Enhancements

Potential features to add:
- Real-time data streaming
- Options data analysis
- Fundamental data (financials, ratios)
- Machine learning predictions
- Web dashboard (Streamlit/Dash)
- Database backend (PostgreSQL + TimescaleDB)
- Backtesting framework

## Requirements

- Python 3.11+
- See [environment.yml](environment.yml) for full dependency list

## License

This project is for educational and personal use.

## Acknowledgments

- Data source: [yfinance](https://github.com/ranaroussi/yfinance) (Yahoo Finance API)
- Visualization: [mplfinance](https://github.com/matplotlib/mplfinance)