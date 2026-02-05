#!/usr/bin/env python3
"""
Script to download daily stock data.

Usage:
    python download_daily.py
    python download_daily.py --symbols AAPL GOOGL MSFT
    python download_daily.py --start 2020-01-01 --end 2023-12-31
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
from config.settings import DEFAULT_SYMBOLS, DEFAULT_START_DATE, LOG_LEVEL, LOG_FORMAT

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/download_daily.log')
    ]
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Download daily stock price data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Download default symbols with maximum available data:
    python download_daily.py

  Download specific symbols:
    python download_daily.py --symbols AAPL GOOGL MSFT

  Download with date range:
    python download_daily.py --start 2020-01-01 --end 2023-12-31

  Download specific symbols with date range:
    python download_daily.py --symbols TSLA --start 2022-01-01
        """
    )

    parser.add_argument(
        '--symbols',
        nargs='+',
        default=DEFAULT_SYMBOLS,
        help=f'Stock ticker symbols (default: {", ".join(DEFAULT_SYMBOLS)})'
    )

    parser.add_argument(
        '--start',
        type=str,
        default=DEFAULT_START_DATE,
        help=f'Start date YYYY-MM-DD (default: {DEFAULT_START_DATE} for max available)'
    )

    parser.add_argument(
        '--end',
        type=str,
        default=None,
        help='End date YYYY-MM-DD (default: today)'
    )

    parser.add_argument(
        '--no-merge',
        action='store_true',
        help='Do not merge with existing data (overwrite instead)'
    )

    args = parser.parse_args()

    # Print header
    print("=" * 70)
    print(" Stock Analysis - Daily Data Download")
    print("=" * 70)
    print(f"Symbols: {', '.join(args.symbols)}")
    print(f"Start date: {args.start}")
    print(f"End date: {args.end or 'today'}")
    print(f"Merge with existing: {not args.no_merge}")
    print("=" * 70)
    print()

    # Initialize fetcher and storage
    fetcher = StockDataFetcher()
    storage = DataStorage()

    # Download data
    try:
        logger.info("Starting daily data download...")
        start_time = datetime.now()

        results = fetcher.download_daily(
            symbols=args.symbols,
            start_date=args.start,
            end_date=args.end,
            progress=True
        )

        # Save to storage
        for symbol, df in results.items():
            storage.save_daily(symbol, df, merge=not args.no_merge)

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
            date_range = storage.get_date_range(symbol, 'daily')
            if date_range:
                print(f"  {symbol}: {date_range[0]} to {date_range[1]}")

        print("=" * 70)
        print()

        # Storage info
        size_mb = storage.get_storage_size('daily')
        print(f"Total storage (daily): {size_mb:.2f} MB")
        print()

        logger.info("Daily data download completed successfully")
        return 0

    except Exception as e:
        logger.error(f"Download failed: {str(e)}", exc_info=True)
        print(f"\nError: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
