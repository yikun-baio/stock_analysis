#!/usr/bin/env python3
"""
Script to update existing stock data with latest prices.

Usage:
    python update_data.py --type daily
    python update_data.py --type hourly --interval 1h
    python update_data.py --type daily --symbols AAPL GOOGL
"""

import sys
from pathlib import Path

# Add parent directory to path to import src module
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import logging
from datetime import datetime, timedelta

from src.data_fetcher import StockDataFetcher
from src.data_storage import DataStorage
from config.settings import DEFAULT_INTERVAL, LOG_LEVEL, LOG_FORMAT

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/update_data.log')
    ]
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Update existing stock data with latest prices',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Update all daily data:
    python update_data.py --type daily

  Update all hourly data:
    python update_data.py --type hourly --interval 1h

  Update specific symbols only:
    python update_data.py --type daily --symbols AAPL GOOGL
        """
    )

    parser.add_argument(
        '--type',
        choices=['daily', 'hourly'],
        required=True,
        help='Type of data to update (daily or hourly)'
    )

    parser.add_argument(
        '--symbols',
        nargs='+',
        default=None,
        help='Specific symbols to update (default: all available symbols)'
    )

    parser.add_argument(
        '--interval',
        type=str,
        default=DEFAULT_INTERVAL,
        help=f'Interval for hourly data (default: {DEFAULT_INTERVAL})'
    )

    args = parser.parse_args()

    # Print header
    print("=" * 70)
    print(" Stock Analysis - Data Update")
    print("=" * 70)
    print(f"Update type: {args.type}")
    if args.type == 'hourly':
        print(f"Interval: {args.interval}")
    print("=" * 70)
    print()

    # Initialize fetcher and storage
    fetcher = StockDataFetcher()
    storage = DataStorage()

    # Get symbols to update
    if args.symbols:
        symbols = [s.upper() for s in args.symbols]
    else:
        symbols = storage.get_available_symbols(args.type)
        if not symbols:
            print(f"No existing {args.type} data found. Use download scripts first.")
            return 0

    print(f"Symbols to update: {', '.join(symbols)}")
    print()

    # Update each symbol
    try:
        logger.info(f"Starting {args.type} data update...")
        start_time = datetime.now()

        updated_count = 0
        failed_count = 0

        for symbol in symbols:
            print(f"Updating {symbol}...", end=" ")

            try:
                # Get existing date range
                date_range = storage.get_date_range(symbol, args.type)
                if not date_range:
                    print("SKIP (no existing data)")
                    continue

                last_date = date_range[1]
                today = datetime.now().strftime('%Y-%m-%d')

                # Check if update is needed
                if last_date >= today:
                    print("UP-TO-DATE")
                    continue

                # Download new data
                if args.type == 'daily':
                    # Download from last date to today
                    results = fetcher.download_daily(
                        symbols=[symbol],
                        start_date=last_date,
                        end_date=None,
                        progress=False
                    )
                else:  # hourly
                    # For hourly, download recent period and merge
                    results = fetcher.download_hourly(
                        symbols=[symbol],
                        period='5d',  # Last 5 days to ensure overlap
                        interval=args.interval,
                        progress=False
                    )

                # Save (merge with existing)
                if symbol in results:
                    df = results[symbol]
                    if args.type == 'daily':
                        storage.save_daily(symbol, df, merge=True)
                    else:
                        storage.save_hourly(symbol, df, interval=args.interval, merge=True)

                    # Get new record count
                    new_records = len(df)
                    print(f"OK (+{new_records} records)")
                    updated_count += 1
                else:
                    print("FAILED")
                    failed_count += 1

            except Exception as e:
                print(f"ERROR: {str(e)}")
                logger.error(f"Failed to update {symbol}: {str(e)}")
                failed_count += 1

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Print summary
        print()
        print("=" * 70)
        print(" Update Summary")
        print("=" * 70)
        print(f"Total symbols: {len(symbols)}")
        print(f"Updated: {updated_count}")
        print(f"Failed: {failed_count}")
        print(f"Duration: {duration:.1f} seconds")
        print("=" * 70)
        print()

        logger.info(f"{args.type.capitalize()} data update completed")
        return 0

    except Exception as e:
        logger.error(f"Update failed: {str(e)}", exc_info=True)
        print(f"\nError: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
