"""
Visualization utilities for stock data.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from typing import List, Dict, Optional, Tuple
import mplfinance as mpf

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (14, 7)


def plot_price_history(
    df: pd.DataFrame,
    symbol: str = None,
    column: str = 'Close',
    figsize: Tuple[int, int] = (14, 7),
    title: str = None
) -> plt.Figure:
    """
    Plot price history as line chart.

    Args:
        df: DataFrame with price data
        symbol: Stock symbol for title
        column: Column to plot (default: Close)
        figsize: Figure size tuple
        title: Custom title (optional)

    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Plot data
    ax.plot(df.index, df[column], linewidth=2, label=column)

    # Labels and title
    if title is None:
        title = f"{symbol} - {column} Price" if symbol else f"{column} Price"
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel(f'{column} Price ($)', fontsize=12)

    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)

    # Grid and legend
    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()
    return fig


def plot_candlestick(
    df: pd.DataFrame,
    symbol: str = None,
    volume: bool = True,
    mav: Tuple[int] = (20, 50),
    style: str = 'charles',
    figsize: Tuple[int, int] = (14, 8)
) -> None:
    """
    Plot candlestick chart using mplfinance.

    Args:
        df: DataFrame with OHLCV data
        symbol: Stock symbol for title
        volume: Show volume bars
        mav: Moving average periods tuple (e.g., (20, 50))
        style: Chart style (charles, mike, yahoo, etc.)
        figsize: Figure size tuple
    """
    # Prepare title
    title = f"{symbol} - Candlestick Chart" if symbol else "Candlestick Chart"

    # Plot
    mpf.plot(
        df,
        type='candle',
        volume=volume,
        mav=mav,
        style=style,
        title=title,
        figsize=figsize,
        tight_layout=True
    )


def plot_volume(
    df: pd.DataFrame,
    symbol: str = None,
    figsize: Tuple[int, int] = (14, 5)
) -> plt.Figure:
    """
    Plot volume bars.

    Args:
        df: DataFrame with Volume column
        symbol: Stock symbol for title
        figsize: Figure size tuple

    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Plot volume bars
    colors = ['green' if df['Close'].iloc[i] >= df['Open'].iloc[i] else 'red'
              for i in range(len(df))]
    ax.bar(df.index, df['Volume'], color=colors, alpha=0.6)

    # Labels and title
    title = f"{symbol} - Trading Volume" if symbol else "Trading Volume"
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Volume', fontsize=12)

    # Format y-axis (in millions)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M'))

    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)

    plt.tight_layout()
    return fig


def plot_multiple_symbols(
    data_dict: Dict[str, pd.DataFrame],
    column: str = 'Close',
    normalize: bool = True,
    figsize: Tuple[int, int] = (14, 7)
) -> plt.Figure:
    """
    Plot multiple symbols on same chart for comparison.

    Args:
        data_dict: Dictionary mapping symbol to DataFrame
        column: Column to plot (default: Close)
        normalize: Normalize to 100 at start for comparison
        figsize: Figure size tuple

    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)

    for symbol, df in data_dict.items():
        if column not in df.columns:
            continue

        prices = df[column]

        if normalize:
            # Normalize to 100 at start
            prices = (prices / prices.iloc[0]) * 100

        ax.plot(df.index, prices, linewidth=2, label=symbol, alpha=0.8)

    # Labels and title
    ylabel = 'Normalized Price (Start = 100)' if normalize else f'{column} Price ($)'
    title = f'Stock Comparison - {column}' + (' (Normalized)' if normalize else '')

    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)

    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)

    # Grid and legend
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best')

    plt.tight_layout()
    return fig


def plot_returns(
    df: pd.DataFrame,
    symbol: str = None,
    cumulative: bool = True,
    figsize: Tuple[int, int] = (14, 7)
) -> plt.Figure:
    """
    Plot returns (daily or cumulative).

    Args:
        df: DataFrame with Close prices
        symbol: Stock symbol for title
        cumulative: Plot cumulative returns if True, daily if False
        figsize: Figure size tuple

    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Calculate returns
    returns = df['Close'].pct_change()

    if cumulative:
        # Cumulative returns
        cum_returns = (1 + returns).cumprod() - 1
        ax.plot(df.index, cum_returns * 100, linewidth=2, color='blue')
        ylabel = 'Cumulative Return (%)'
        title_suffix = 'Cumulative Returns'
    else:
        # Daily returns
        ax.plot(df.index, returns * 100, linewidth=1, color='blue', alpha=0.6)
        ylabel = 'Daily Return (%)'
        title_suffix = 'Daily Returns'

    # Labels and title
    title = f"{symbol} - {title_suffix}" if symbol else title_suffix
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)

    # Zero line
    ax.axhline(y=0, color='red', linestyle='--', alpha=0.3)

    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)

    # Grid
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def plot_moving_averages(
    df: pd.DataFrame,
    symbol: str = None,
    periods: Tuple[int] = (20, 50, 200),
    figsize: Tuple[int, int] = (14, 7)
) -> plt.Figure:
    """
    Plot price with moving averages.

    Args:
        df: DataFrame with Close prices
        symbol: Stock symbol for title
        periods: Tuple of MA periods (e.g., (20, 50, 200))
        figsize: Figure size tuple

    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Plot close price
    ax.plot(df.index, df['Close'], linewidth=2, label='Close', alpha=0.8)

    # Plot moving averages
    colors = ['orange', 'green', 'red']
    for i, period in enumerate(periods):
        ma = df['Close'].rolling(window=period).mean()
        color = colors[i % len(colors)]
        ax.plot(df.index, ma, linewidth=2, label=f'MA{period}', alpha=0.7, color=color)

    # Labels and title
    title = f"{symbol} - Moving Averages" if symbol else "Moving Averages"
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Price ($)', fontsize=12)

    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)

    # Grid and legend
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best')

    plt.tight_layout()
    return fig


def plot_correlation_matrix(
    data_dict: Dict[str, pd.DataFrame],
    column: str = 'Close',
    figsize: Tuple[int, int] = (10, 8)
) -> plt.Figure:
    """
    Plot correlation matrix heatmap for multiple symbols.

    Args:
        data_dict: Dictionary mapping symbol to DataFrame
        column: Column to use for correlation (default: Close)
        figsize: Figure size tuple

    Returns:
        Matplotlib figure object
    """
    # Create DataFrame with all symbols
    combined = pd.DataFrame()
    for symbol, df in data_dict.items():
        if column in df.columns:
            combined[symbol] = df[column]

    # Calculate correlation
    corr = combined.corr()

    # Plot heatmap
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(
        corr,
        annot=True,
        cmap='coolwarm',
        center=0,
        fmt='.2f',
        square=True,
        linewidths=1,
        cbar_kws={'label': 'Correlation'},
        ax=ax
    )

    ax.set_title(f'Stock Price Correlation Matrix ({column})', fontsize=16, fontweight='bold')

    plt.tight_layout()
    return fig


def plot_price_and_volume(
    df: pd.DataFrame,
    symbol: str = None,
    figsize: Tuple[int, int] = (14, 8)
) -> plt.Figure:
    """
    Plot price and volume on separate subplots.

    Args:
        df: DataFrame with OHLCV data
        symbol: Stock symbol for title
        figsize: Figure size tuple

    Returns:
        Matplotlib figure object
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True, gridspec_kw={'height_ratios': [3, 1]})

    # Plot price
    ax1.plot(df.index, df['Close'], linewidth=2, color='blue', label='Close')
    title = f"{symbol} - Price and Volume" if symbol else "Price and Volume"
    ax1.set_title(title, fontsize=16, fontweight='bold')
    ax1.set_ylabel('Price ($)', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # Plot volume
    colors = ['green' if df['Close'].iloc[i] >= df['Open'].iloc[i] else 'red'
              for i in range(len(df))]
    ax2.bar(df.index, df['Volume'], color=colors, alpha=0.6)
    ax2.set_ylabel('Volume', fontsize=12)
    ax2.set_xlabel('Date', fontsize=12)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M'))

    # Format x-axis
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)

    plt.tight_layout()
    return fig
