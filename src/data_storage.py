"""
Data storage module for saving and loading stock data in Parquet format.
"""

import pandas as pd
from pathlib import Path
from typing import Optional, List, Tuple
import logging

from .data_utils import merge_data, get_date_range_str
from config.settings import DAILY_DIR, HOURLY_DIR, EXPORT_DIR

logger = logging.getLogger(__name__)


class DataStorage:
    """Manage stock data persistence using Parquet format."""

    def __init__(self, daily_dir: Path = DAILY_DIR, hourly_dir: Path = HOURLY_DIR):
        """
        Initialize data storage.

        Args:
            daily_dir: Directory for daily data
            hourly_dir: Directory for hourly data
        """
        self.daily_dir = Path(daily_dir)
        self.hourly_dir = Path(hourly_dir)

        # Ensure directories exist
        self.daily_dir.mkdir(parents=True, exist_ok=True)
        self.hourly_dir.mkdir(parents=True, exist_ok=True)

    def save_daily(self, symbol: str, df: pd.DataFrame, merge: bool = True) -> None:
        """
        Save daily data to Parquet file.

        Args:
            symbol: Stock ticker symbol
            df: DataFrame with OHLCV data
            merge: If True, merge with existing data
        """
        if df is None or df.empty:
            logger.warning(f"Cannot save empty data for {symbol}")
            return

        file_path = self.daily_dir / f"{symbol.upper()}.parquet"

        # Merge with existing data if requested
        if merge and file_path.exists():
            existing_df = self.load_daily(symbol)
            df = merge_data(existing_df, df)
            logger.info(f"Merged with existing data for {symbol}")

        # Save to parquet
        df.to_parquet(file_path, compression='snappy', index=True)
        logger.info(f"Saved daily data for {symbol}: {file_path} ({get_date_range_str(df)})")

    def save_hourly(
        self,
        symbol: str,
        df: pd.DataFrame,
        interval: str = '1h',
        merge: bool = True
    ) -> None:
        """
        Save hourly/intraday data to Parquet file.

        Args:
            symbol: Stock ticker symbol
            df: DataFrame with OHLCV data
            interval: Data interval (1h, 30m, etc.)
            merge: If True, merge with existing data
        """
        if df is None or df.empty:
            logger.warning(f"Cannot save empty data for {symbol}")
            return

        # Include interval in filename for different granularities
        file_path = self.hourly_dir / f"{symbol.upper()}_{interval}.parquet"

        # Merge with existing data if requested
        if merge and file_path.exists():
            existing_df = self.load_hourly(symbol, interval)
            df = merge_data(existing_df, df)
            logger.info(f"Merged with existing data for {symbol} ({interval})")

        # Save to parquet
        df.to_parquet(file_path, compression='snappy', index=True)
        logger.info(f"Saved hourly data for {symbol} ({interval}): {file_path} ({get_date_range_str(df)})")

    def load_daily(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """
        Load daily data from Parquet file.

        Args:
            symbol: Stock ticker symbol
            start_date: Filter from this date (YYYY-MM-DD)
            end_date: Filter to this date (YYYY-MM-DD)

        Returns:
            DataFrame or None if file doesn't exist
        """
        file_path = self.daily_dir / f"{symbol.upper()}.parquet"

        if not file_path.exists():
            logger.warning(f"No daily data found for {symbol}: {file_path}")
            return None

        try:
            df = pd.read_parquet(file_path)

            # Apply date filtering
            if start_date:
                df = df[df.index >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df.index <= pd.to_datetime(end_date)]

            logger.info(f"Loaded daily data for {symbol}: {get_date_range_str(df)}")
            return df

        except Exception as e:
            logger.error(f"Failed to load daily data for {symbol}: {str(e)}")
            return None

    def load_hourly(
        self,
        symbol: str,
        interval: str = '1h',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """
        Load hourly/intraday data from Parquet file.

        Args:
            symbol: Stock ticker symbol
            interval: Data interval (1h, 30m, etc.)
            start_date: Filter from this date (YYYY-MM-DD)
            end_date: Filter to this date (YYYY-MM-DD)

        Returns:
            DataFrame or None if file doesn't exist
        """
        file_path = self.hourly_dir / f"{symbol.upper()}_{interval}.parquet"

        if not file_path.exists():
            logger.warning(f"No hourly data found for {symbol} ({interval}): {file_path}")
            return None

        try:
            df = pd.read_parquet(file_path)

            # Apply date filtering
            if start_date:
                df = df[df.index >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df.index <= pd.to_datetime(end_date)]

            logger.info(f"Loaded hourly data for {symbol} ({interval}): {get_date_range_str(df)}")
            return df

        except Exception as e:
            logger.error(f"Failed to load hourly data for {symbol}: {str(e)}")
            return None

    def get_available_symbols(self, data_type: str = 'daily') -> List[str]:
        """
        Get list of symbols with downloaded data.

        Args:
            data_type: 'daily' or 'hourly'

        Returns:
            List of symbol strings
        """
        if data_type == 'daily':
            directory = self.daily_dir
            pattern = '*.parquet'
        elif data_type == 'hourly':
            directory = self.hourly_dir
            pattern = '*.parquet'
        else:
            raise ValueError(f"Invalid data_type: {data_type}. Use 'daily' or 'hourly'")

        files = list(directory.glob(pattern))

        if data_type == 'daily':
            symbols = [f.stem for f in files]  # e.g., AAPL.parquet -> AAPL
        else:
            # For hourly: AAPL_1h.parquet -> AAPL
            symbols = list(set([f.stem.split('_')[0] for f in files]))

        return sorted(symbols)

    def get_date_range(self, symbol: str, data_type: str = 'daily') -> Optional[Tuple[str, str]]:
        """
        Get date range for a symbol's data.

        Args:
            symbol: Stock ticker symbol
            data_type: 'daily' or 'hourly'

        Returns:
            Tuple of (start_date, end_date) as strings or None
        """
        if data_type == 'daily':
            df = self.load_daily(symbol)
        elif data_type == 'hourly':
            df = self.load_hourly(symbol)
        else:
            raise ValueError(f"Invalid data_type: {data_type}")

        if df is None or df.empty:
            return None

        start = df.index.min().strftime('%Y-%m-%d')
        end = df.index.max().strftime('%Y-%m-%d')

        return (start, end)

    def delete_data(self, symbol: str, data_type: str = 'daily') -> bool:
        """
        Delete data file for a symbol.

        Args:
            symbol: Stock ticker symbol
            data_type: 'daily' or 'hourly'

        Returns:
            True if deleted, False if file didn't exist
        """
        if data_type == 'daily':
            file_path = self.daily_dir / f"{symbol.upper()}.parquet"
        elif data_type == 'hourly':
            # Delete all hourly files for this symbol
            files = list(self.hourly_dir.glob(f"{symbol.upper()}_*.parquet"))
            if not files:
                logger.warning(f"No hourly data found for {symbol}")
                return False
            for file_path in files:
                file_path.unlink()
                logger.info(f"Deleted {file_path}")
            return True
        else:
            raise ValueError(f"Invalid data_type: {data_type}")

        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted {file_path}")
            return True
        else:
            logger.warning(f"File not found: {file_path}")
            return False

    def export_to_csv(
        self,
        symbol: str,
        data_type: str = 'daily',
        output_dir: Optional[Path] = None
    ) -> Optional[Path]:
        """
        Export data to CSV format.

        Args:
            symbol: Stock ticker symbol
            data_type: 'daily' or 'hourly'
            output_dir: Output directory (default: EXPORT_DIR)

        Returns:
            Path to exported CSV file or None
        """
        if output_dir is None:
            output_dir = EXPORT_DIR

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Load data
        if data_type == 'daily':
            df = self.load_daily(symbol)
            output_file = output_dir / f"{symbol.upper()}_daily.csv"
        elif data_type == 'hourly':
            df = self.load_hourly(symbol)
            output_file = output_dir / f"{symbol.upper()}_hourly.csv"
        else:
            raise ValueError(f"Invalid data_type: {data_type}")

        if df is None or df.empty:
            logger.error(f"No data to export for {symbol}")
            return None

        # Export to CSV
        df.to_csv(output_file)
        logger.info(f"Exported {symbol} to {output_file}")

        return output_file

    def get_storage_size(self, data_type: str = 'daily') -> float:
        """
        Get total storage size in MB.

        Args:
            data_type: 'daily' or 'hourly'

        Returns:
            Size in megabytes
        """
        if data_type == 'daily':
            directory = self.daily_dir
        elif data_type == 'hourly':
            directory = self.hourly_dir
        else:
            raise ValueError(f"Invalid data_type: {data_type}")

        total_size = sum(f.stat().st_size for f in directory.glob('*.parquet'))
        return total_size / (1024 * 1024)  # Convert to MB
