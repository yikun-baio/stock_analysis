"""
Configuration settings for stock analysis project.
"""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Default stock symbols to track (tech giants)
DEFAULT_SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']

# Data directories
DATA_DIR = PROJECT_ROOT / 'data'
DAILY_DIR = DATA_DIR / 'daily'
HOURLY_DIR = DATA_DIR / 'hourly'
METADATA_DIR = DATA_DIR / 'metadata'
EXPORT_DIR = DATA_DIR / 'exports'

# Log directory
LOG_DIR = PROJECT_ROOT / 'logs'

# Create directories if they don't exist
for directory in [DAILY_DIR, HOURLY_DIR, METADATA_DIR, EXPORT_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Date settings
DEFAULT_START_DATE = '2000-01-01'  # Maximum available
DEFAULT_END_DATE = None  # None means today

# Interval options for intraday data
VALID_INTERVALS = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
DEFAULT_INTERVAL = '1h'  # Hourly data

# Period options for intraday data (yfinance format)
VALID_PERIODS = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
DEFAULT_PERIOD = '730d'  # ~2 years for hourly data

# API settings
MAX_RETRIES = 3  # Number of retry attempts for failed downloads
RETRY_DELAY = 5  # Seconds to wait between retries
TIMEOUT = 30  # Request timeout in seconds

# Data validation
MIN_PRICE = 0.01  # Minimum valid stock price
MAX_PRICE_CHANGE_PCT = 50  # Maximum daily price change % (to detect errors)

# Logging
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
