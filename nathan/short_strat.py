import numpy as np

def get_actions(prices):
    n_stocks, n_days = prices.shape
    actions = np.zeros_like(prices, dtype=int)

    lookback = 20
    min_history = 25
    entry_notional = 200_000
    max_holding = 20

    # Track whether we currently have an active short from this strategy
    short_age = np.zeros(n_stocks, dtype=int)
    in_short = np.zeros(n_stocks, dtype=bool)

    for t in range(1, n_days):
        for s in range(n_stocks):
            if t < min_history:
                continue

            p_t = prices[s, t]
            p_y = prices[s, t - 1]
            window = prices[s, t - lookback:t]
            ma = np.mean(window)

            # Overextension score
            stretch = p_t / ma if ma > 0 else 1.0

            # Entry: price is very stretched vs recent average, but now weakening
            # Uses only info through day t
            entry_signal = (
                (stretch > 1.25) and      # very extended
                (p_t < p_y) and           # down today vs yesterday
                (p_y >= np.max(window))   # yesterday was at/near recent high
            )

            if not in_short[s] and entry_signal:
                shares = int(round(entry_notional / p_t))
                if shares > 0:
                    actions[s, t] = -shares
                    in_short[s] = True
                    short_age[s] = 0
                continue

            if in_short[s]:
                short_age[s] += 1

                # Exit if mean reversion happened or holding period exceeded
                exit_signal = (
                    (p_t <= ma) or
                    (short_age[s] >= max_holding) or
                    (p_t > 1.05 * p_y)   # squeeze / rebound protection
                )

                if exit_signal:
                    # positive action covers outstanding short
                    # use a huge positive so the engine fully covers
                    actions[s, t] = 10**9
                    in_short[s] = False
                    short_age[s] = 0

    return actions