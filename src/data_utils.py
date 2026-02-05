"""
Utility functions for data validation and formatting.
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Tuple
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def validate_symbol(symbol: str) -> bool:
    """
    Validate stock symbol format.

    Args:
        symbol: Stock ticker symbol

    Returns:
        True if valid, False otherwise
    """
    if not symbol or not isinstance(symbol, str):
        return False

    # Stock symbols are typically 1-5 uppercase letters
    # Some may have dots (e.g., BRK.A) or hyphens
    pattern = r'^[A-Z]{1,5}(\.[A-Z])?(-[A-Z])?$'
    return bool(re.match(pattern, symbol.upper()))


def validate_date_range(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Tuple[Optional[datetime], Optional[datetime]]:
    """
    Validate and parse date range.

    Args:
        start_date: Start date string (YYYY-MM-DD) or None
        end_date: End date string (YYYY-MM-DD) or None

    Returns:
        Tuple of (start_datetime, end_datetime)

    Raises:
        ValueError: If dates are invalid or in wrong order
    """
    start_dt = None
    end_dt = None

    if start_date:
        try:
            start_dt = pd.to_datetime(start_date)
        except Exception as e:
            raise ValueError(f"Invalid start_date format: {start_date}. Use YYYY-MM-DD") from e

    if end_date:
        try:
            end_dt = pd.to_datetime(end_date)
        except Exception as e:
            raise ValueError(f"Invalid end_date format: {end_date}. Use YYYY-MM-DD") from e

    # Validate date order
    if start_dt and end_dt and start_dt > end_dt:
        raise ValueError(f"start_date ({start_date}) must be before end_date ({end_date})")

    # Check if dates are in the future
    today = pd.Timestamp.now()
    if end_dt and end_dt > today:
        logger.warning(f"end_date ({end_date}) is in the future. Using today instead.")
        end_dt = today

    return start_dt, end_dt


def format_dataframe(df: pd.DataFrame, symbol: str = None) -> pd.DataFrame:
    """
    Standardize DataFrame column names and format.

    Args:
        df: Raw DataFrame from data source
        symbol: Stock symbol (optional, for adding Symbol column)

    Returns:
        Formatted DataFrame with standardized columns
    """
    if df is None or df.empty:
        return df

    # Make a copy to avoid modifying original
    df = df.copy()

    # Standardize column names (handle case variations)
    column_mapping = {
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume',
        'adj close': 'Adj Close',
        'adjclose': 'Adj Close',
    }

    df.columns = [col.strip() for col in df.columns]
    df.rename(columns={col: column_mapping.get(col.lower(), col) for col in df.columns}, inplace=True)

    # Ensure datetime index
    if not isinstance(df.index, pd.DatetimeIndex):
        if 'Date' in df.columns:
            df.set_index('Date', inplace=True)
        elif 'Datetime' in df.columns:
            df.set_index('Datetime', inplace=True)

    # Add symbol column if provided
    if symbol:
        df['Symbol'] = symbol

    # Sort by date
    df.sort_index(inplace=True)

    # Remove duplicates
    df = df[~df.index.duplicated(keep='last')]

    return df


def merge_data(old_df: pd.DataFrame, new_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge old and new data, removing duplicates and sorting.

    Args:
        old_df: Existing DataFrame
        new_df: New DataFrame to merge

    Returns:
        Merged DataFrame
    """
    if old_df is None or old_df.empty:
        return new_df

    if new_df is None or new_df.empty:
        return old_df

    # Concatenate
    merged = pd.concat([old_df, new_df])

    # Remove duplicates (keep last)
    merged = merged[~merged.index.duplicated(keep='last')]

    # Sort by date
    merged.sort_index(inplace=True)

    return merged


def calculate_missing_dates(
    df: pd.DataFrame,
    freq: str = 'B'  # Business days
) -> pd.DatetimeIndex:
    """
    Find missing dates in time series data.

    Args:
        df: DataFrame with datetime index
        freq: Expected frequency ('B' for business days, 'D' for daily, 'H' for hourly)

    Returns:
        DatetimeIndex of missing dates
    """
    if df is None or df.empty:
        return pd.DatetimeIndex([])

    # Generate expected date range
    expected_dates = pd.date_range(
        start=df.index.min(),
        end=df.index.max(),
        freq=freq
    )

    # Find missing dates
    missing = expected_dates.difference(df.index)

    return missing


def validate_price_data(df: pd.DataFrame, symbol: str = None) -> pd.DataFrame:
    """
    Validate price data for anomalies and errors.

    Args:
        df: DataFrame with price data
        symbol: Stock symbol for logging

    Returns:
        DataFrame with validated data (anomalies logged)
    """
    if df is None or df.empty:
        return df

    symbol_str = f" for {symbol}" if symbol else ""

    # Check for null values
    null_count = df.isnull().sum().sum()
    if null_count > 0:
        logger.warning(f"Found {null_count} null values{symbol_str}")

    # Check for negative prices
    price_cols = ['Open', 'High', 'Low', 'Close']
    for col in price_cols:
        if col in df.columns:
            negative = df[df[col] < 0]
            if len(negative) > 0:
                logger.error(f"Found {len(negative)} negative {col} prices{symbol_str}")

    # Check for extreme price changes
    if 'Close' in df.columns:
        df['Price_Change_Pct'] = df['Close'].pct_change() * 100
        extreme = df[abs(df['Price_Change_Pct']) > 50]  # More than 50% change
        if len(extreme) > 0:
            logger.warning(
                f"Found {len(extreme)} extreme price changes (>50%){symbol_str}: "
                f"{extreme.index.tolist()}"
            )
        df.drop('Price_Change_Pct', axis=1, inplace=True)

    return df


def get_date_range_str(df: pd.DataFrame) -> str:
    """
    Get human-readable date range string from DataFrame.

    Args:
        df: DataFrame with datetime index

    Returns:
        String like "2020-01-01 to 2023-12-31 (1000 days)"
    """
    if df is None or df.empty:
        return "No data"

    start = df.index.min().strftime('%Y-%m-%d')
    end = df.index.max().strftime('%Y-%m-%d')
    days = (df.index.max() - df.index.min()).days
    rows = len(df)

    return f"{start} to {end} ({rows} records, {days} days)"
