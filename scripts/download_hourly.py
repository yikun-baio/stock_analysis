#!/usr/bin/env python3
"""
Script to download hourly/intraday stock data.

Usage:
    python download_hourly.py
    python download_hourly.py --symbols AAPL GOOGL
    python download_hourly.py --period 1mo --interval 1h
    python download_hourly.py --symbols TSLA --period 730d --interval 30m
"""

import sys
from pathlib import Path

# Add parent directory to path to import src module
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import logging
from datetime import datetime

from src.data_fetcher import StockDataFetcher
from src.data_storage import DataStorage
from config.settings import (
    DEFAULT_SYMBOLS,
    DEFAULT_PERIOD,
    DEFAULT_INTERVAL,
    VALID_INTERVALS,
    VALID_PERIODS,
    LOG_LEVEL,
    LOG_FORMAT
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/download_hourly.log')
    ]
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Download hourly/intraday stock price data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  Download default symbols with hourly data (2 years):
    python download_hourly.py

  Download specific symbols:
    python download_hourly.py --symbols AAPL GOOGL MSFT

  Download with different interval:
    python download_hourly.py --interval 30m --period 1mo

  Download specific period:
    python download_hourly.py --symbols TSLA --period 730d

Valid intervals: {', '.join(VALID_INTERVALS)}
Valid periods: {', '.join(VALID_PERIODS)}

Note: For hourly (1h) data, yfinance provides ~730 days (2 years) maximum.
      For smaller intervals (1m, 5m, etc.), the period is more limited.
        """
    )

    parser.add_argument(
        '--symbols',
        nargs='+',
        default=DEFAULT_SYMBOLS,
        help=f'Stock ticker symbols (default: {", ".join(DEFAULT_SYMBOLS)})'
    )

    parser.add_argument(
        '--period',
        type=str,
        default=DEFAULT_PERIOD,
        help=f'Time period (default: {DEFAULT_PERIOD}). Options: {", ".join(VALID_PERIODS)}'
    )

    parser.add_argument(
        '--interval',
        type=str,
        default=DEFAULT_INTERVAL,
        help=f'Data interval (default: {DEFAULT_INTERVAL}). Options: {", ".join(VALID_INTERVALS)}'
    )

    parser.add_argument(
        '--no-merge',
        action='store_true',
        help='Do not merge with existing data (overwrite instead)'
    )

    args = parser.parse_args()

    # Validate interval
    if args.interval not in VALID_INTERVALS:
        print(f"Error: Invalid interval '{args.interval}'")
        print(f"Valid intervals: {', '.join(VALID_INTERVALS)}")
        return 1

    # Validate period
    if args.period not in VALID_PERIODS and not args.period.endswith('d'):
        print(f"Error: Invalid period '{args.period}'")
        print(f"Valid periods: {', '.join(VALID_PERIODS)} or number of days (e.g., 730d)")
        return 1

    # Print header
    print("=" * 70)
    print(" Stock Analysis - Hourly/Intraday Data Download")
    print("=" * 70)
    print(f"Symbols: {', '.join(args.symbols)}")
    print(f"Period: {args.period}")
    print(f"Interval: {args.interval}")
    print(f"Merge with existing: {not args.no_merge}")
    print("=" * 70)
    print()

    # Warn about limitations
    if args.interval in ['1h', '60m'] and args.period in ['5y', '10y', 'max']:
        print("WARNING: For hourly data, maximum available period is ~730 days (2 years)")
        print()

    # Initialize fetcher and storage
    fetcher = StockDataFetcher()
    storage = DataStorage()

    # Download data
    try:
        logger.info(f"Starting {args.interval} data download...")
        start_time = datetime.now()

        results = fetcher.download_hourly(
            symbols=args.symbols,
            period=args.period,
            interval=args.interval,
            progress=True
        )

        # Save to storage
        for symbol, df in results.items():
            storage.save_hourly(symbol, df, interval=args.interval, merge=not args.no_merge)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Print summary
        print()
        print("=" * 70)
        print(" Download Summary")
        print("=" * 70)
        print(f"Total symbols: {len(args.symbols)}")
        print(f"Successful: {len(results)}")
        print(f"Failed: {len(args.symbols) - len(results)}")
        print(f"Duration: {duration:.1f} seconds")
        print()

        # Print data info
        for symbol in results:
            date_range = storage.get_date_range(symbol, 'hourly')
            if date_range:
                df = results[symbol]
                print(f"  {symbol}: {date_range[0]} to {date_range[1]} ({len(df)} records)")

        print("=" * 70)
        print()

        # Storage info
        size_mb = storage.get_storage_size('hourly')
        print(f"Total storage (hourly): {size_mb:.2f} MB")
        print()

        logger.info(f"{args.interval} data download completed successfully")
        return 0

    except Exception as e:
        logger.error(f"Download failed: {str(e)}", exc_info=True)
        print(f"\nError: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
