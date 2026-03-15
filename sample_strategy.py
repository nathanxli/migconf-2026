"""
MIG Quant Competition — Sample Strategy
========================================

Your submission must define a top-level function:

    get_actions(prices: np.ndarray) -> np.ndarray

Arguments
---------
prices : np.ndarray, shape (num_stocks, num_days)
    Open price for each stock on each trading day.
    Rows are stocks sorted alphabetically by ticker.
    Columns are days in chronological order.

Returns
-------
actions : np.ndarray, shape (num_stocks, num_days)
    Number of shares to trade per stock per day.
      +N  →  buy N shares
      -N  →  sell / open short N shares
       0  →  hold (no trade)
    Values are rounded to the nearest integer (no fractional shares).

Competition Rules (summary)
---------------------------
- Starting capital: $25,000
- Fractional shares: NOT supported
- Runtime limit: 60 seconds
- Memory limit: 512 MB
- No network access inside the sandbox
- No file I/O inside the sandbox
- Strategy must be deterministic

Available packages (pre-installed in sandbox)
---------------------------------------------
numpy>=1.26, pandas>=2.0, scipy, scikit-learn>=1.3,
statsmodels, ta-lib>=0.6.5, numba, joblib

For extra packages, include a requirements.txt inside a .zip submission.
"""

import numpy as np


def get_actions(prices: np.ndarray) -> np.ndarray:
    """
    Simple 5 / 20-day moving-average crossover strategy.

    For each stock independently:
      - Buy 1 share when the 5-day MA crosses above the 20-day MA.
      - Sell 1 share (close the long) when it crosses back below.

    This is intentionally minimal — use it as a starting template.
    """
    num_stocks, num_days = prices.shape
    actions = np.zeros_like(prices)

    short_window = 5
    long_window = 20

    for i in range(num_stocks):
        position = 0  # current holding: 0 = flat, 1 = long 1 share

        for t in range(long_window, num_days):
            short_ma = prices[i, t - short_window : t].mean()
            long_ma = prices[i, t - long_window : t].mean()

            if short_ma > long_ma and position == 0:
                actions[i, t] = 1   # buy 1 share
                position = 1
            elif short_ma <= long_ma and position == 1:
                actions[i, t] = -1  # sell 1 share (close long)
                position = 0

    return actions
