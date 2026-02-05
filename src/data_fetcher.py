"""
Stock data fetching module using yfinance.
"""

import yfinance as yf
import pandas as pd
from typing import List, Optional, Dict
import logging
import time
from datetime import datetime

from .data_utils import validate_symbol, validate_date_range, format_dataframe, validate_price_data
from config.settings import MAX_RETRIES, RETRY_DELAY, TIMEOUT

logger = logging.getLogger(__name__)


class StockDataFetcher:
    """Fetch stock data from Yahoo Finance using yfinance."""

    def __init__(self, max_retries: int = MAX_RETRIES, retry_delay: int = RETRY_DELAY):
        """
        Initialize the data fetcher.

        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Delay in seconds between retries
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def download_daily(
        self,
        symbols: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        progress: bool = True
    ) -> Dict[str, pd.DataFrame]:
        """
        Download daily OHLCV data for given symbols.

        Args:
            symbols: List of stock ticker symbols
            start_date: Start date (YYYY-MM-DD) or None for maximum available
            end_date: End date (YYYY-MM-DD) or None for today
            progress: Show progress bar

        Returns:
            Dictionary mapping symbol to DataFrame
        """
        # Validate inputs
        if not symbols:
            raise ValueError("Symbols list cannot be empty")

        symbols = [s.upper() for s in symbols]
        invalid_symbols = [s for s in symbols if not validate_symbol(s)]
        if invalid_symbols:
            logger.warning(f"Invalid symbols will be skipped: {invalid_symbols}")
            symbols = [s for s in symbols if validate_symbol(s)]

        if not symbols:
            raise ValueError("No valid symbols to download")

        # Validate dates
        start_dt, end_dt = validate_date_range(start_date, end_date)

        logger.info(f"Downloading daily data for {len(symbols)} symbols...")
        logger.info(f"Date range: {start_date or 'max available'} to {end_date or 'today'}")

        results = {}

        for symbol in symbols:
            logger.info(f"Fetching {symbol}...")
            df = self._download_with_retry(
                symbol,
                start=start_date,
                end=end_date,
                interval='1d',
                progress=progress
            )

            if df is not None and not df.empty:
                df = format_dataframe(df, symbol)
                df = validate_price_data(df, symbol)
                results[symbol] = df
                logger.info(f"✓ {symbol}: Downloaded {len(df)} records")
            else:
                logger.error(f"✗ {symbol}: Failed to download data")

        logger.info(f"Download complete: {len(results)}/{len(symbols)} symbols successful")
        return results

    def download_hourly(
        self,
        symbols: List[str],
        period: str = '730d',
        interval: str = '1h',
        progress: bool = True
    ) -> Dict[str, pd.DataFrame]:
        """
        Download hourly/intraday data for given symbols.

        Args:
            symbols: List of stock ticker symbols
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
                    Note: For hourly (1h), max is ~730 days (2 years)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            progress: Show progress bar

        Returns:
            Dictionary mapping symbol to DataFrame
        """
        # Validate inputs
        if not symbols:
            raise ValueError("Symbols list cannot be empty")

        symbols = [s.upper() for s in symbols]
        invalid_symbols = [s for s in symbols if not validate_symbol(s)]
        if invalid_symbols:
            logger.warning(f"Invalid symbols will be skipped: {invalid_symbols}")
            symbols = [s for s in symbols if validate_symbol(s)]

        if not symbols:
            raise ValueError("No valid symbols to download")

        logger.info(f"Downloading {interval} data for {len(symbols)} symbols...")
        logger.info(f"Period: {period}, Interval: {interval}")

        if interval in ['1h', '60m'] and period in ['5y', '10y', 'max']:
            logger.warning(
                "For hourly data, yfinance typically provides ~730 days (2 years) max. "
                f"Period '{period}' may be limited."
            )

        results = {}

        for symbol in symbols:
            logger.info(f"Fetching {symbol}...")
            df = self._download_with_retry(
                symbol,
                period=period,
                interval=interval,
                progress=progress
            )

            if df is not None and not df.empty:
                df = format_dataframe(df, symbol)
                df = validate_price_data(df, symbol)
                results[symbol] = df
                logger.info(f"✓ {symbol}: Downloaded {len(df)} records")
            else:
                logger.error(f"✗ {symbol}: Failed to download data")

        logger.info(f"Download complete: {len(results)}/{len(symbols)} symbols successful")
        return results

    def _download_with_retry(
        self,
        symbol: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        period: Optional[str] = None,
        interval: str = '1d',
        progress: bool = False
    ) -> Optional[pd.DataFrame]:
        """
        Download data with retry logic.

        Args:
            symbol: Stock ticker symbol
            start: Start date (for historical data)
            end: End date (for historical data)
            period: Period string (for recent data)
            interval: Data interval
            progress: Show progress

        Returns:
            DataFrame or None if all retries fail
        """
        for attempt in range(self.max_retries):
            try:
                ticker = yf.Ticker(symbol)

                # Use period or start/end
                if period:
                    df = ticker.history(
                        period=period,
                        interval=interval,
                        timeout=TIMEOUT,
                        progress=progress
                    )
                else:
                    df = ticker.history(
                        start=start,
                        end=end,
                        interval=interval,
                        timeout=TIMEOUT,
                        progress=progress
                    )

                if df is not None and not df.empty:
                    return df
                else:
                    logger.warning(f"No data returned for {symbol}")
                    return None

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/{self.max_retries} failed for {symbol}: {str(e)}")

                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"All retry attempts failed for {symbol}")
                    return None

        return None

    def get_info(self, symbol: str) -> Dict:
        """
        Get stock information and metadata.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dictionary with stock information
        """
        if not validate_symbol(symbol):
            raise ValueError(f"Invalid symbol: {symbol}")

        try:
            ticker = yf.Ticker(symbol.upper())
            return ticker.info
        except Exception as e:
            logger.error(f"Failed to get info for {symbol}: {str(e)}")
            return {}

    def get_latest_price(self, symbol: str) -> Optional[float]:
        """
        Get the latest available price for a symbol.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Latest close price or None
        """
        if not validate_symbol(symbol):
            raise ValueError(f"Invalid symbol: {symbol}")

        try:
            ticker = yf.Ticker(symbol.upper())
            hist = ticker.history(period='1d')
            if not hist.empty:
                return hist['Close'].iloc[-1]
            return None
        except Exception as e:
            logger.error(f"Failed to get latest price for {symbol}: {str(e)}")
            return None
