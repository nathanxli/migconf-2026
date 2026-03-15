from collections import defaultdict, deque
import numpy as np

## Local Version of Server Side Backtester. This is used for testing and debugging the backtesting logic without needing to run the server. It can be used to verify that the backtesting logic correctly handles various scenarios, such as opening and closing positions, calculating portfolio values, and ensuring that the portfolio does not go negative due to excessive shorting.

class Backtester:
    def __init__(self, prices, actions, cash=25000):
        if prices.shape != actions.shape:
            raise ValueError(f"actions shape {actions.shape} does not match prices shape {prices.shape}")

        actions = np.round(actions).astype(int)

        self.stocks = len(prices)
        self.days = len(prices[0])
        self.prices = prices
        self.actions = actions

        self.initial_cash = cash
        self.cash = cash
        self.positions = [0] * self.stocks
        self.port_values = [0] * self.days

        self._short_positions = defaultdict(deque)

    def calc_pnl(self) -> float:
        return float(self.port_values[-1]) - self.initial_cash

    def _calc_short_value(self, day):
        value = 0
        for stock in self._short_positions.keys():
            for short_price, short_amount in self._short_positions[stock]:
                value += (short_price - self.prices[stock][day]) * short_amount
        return value

    def _calc_portfolio_value(self, day):
        value = self.cash
        for stock in range(self.stocks):
            if self.positions[stock] > 0:
                value += self.prices[stock][day] * self.positions[stock]
        value += self._calc_short_value(day)
        return value

    def _buy_long(self, day, stock):
        if self.cash >= self.prices[stock][day] * self.actions[stock][day]:
            self.cash -= self.prices[stock][day] * self.actions[stock][day]
            self.positions[stock] += self.actions[stock][day]

    def _cover_short(self, day, stock):
        short_close_amount = self.actions[stock][day]

        while short_close_amount > 0 and len(self._short_positions[stock]) > 0:
            positions_to_close = min(self._short_positions[stock][0][1], short_close_amount)
            short_close_amount -= positions_to_close
            self.positions[stock] += positions_to_close
            self.cash += (self._short_positions[stock][0][0] - self.prices[stock][day]) * positions_to_close
            if positions_to_close == self._short_positions[stock][0][1]:
                self._short_positions[stock].popleft()
            else:
                self._short_positions[stock][0][1] -= positions_to_close

        if short_close_amount > 0:
            if self.cash >= self.prices[stock][day] * short_close_amount:
                self.cash -= self.prices[stock][day] * short_close_amount
                self.positions[stock] += short_close_amount

    def _sell_long(self, day, stock):
        sell_amount = min(abs(self.actions[stock][day]), self.positions[stock])
        short_amount = max(abs(self.actions[stock][day]) - self.positions[stock], 0)

        self.cash += self.prices[stock][day] * sell_amount
        self.positions[stock] -= sell_amount

        if short_amount > 0:
            self._short_positions[stock].append([self.prices[stock][day], short_amount])
            self.positions[stock] -= short_amount

    def _open_short(self, day, stock):
        short_amount = abs(self.actions[stock][day])
        self._short_positions[stock].append([self.prices[stock][day], short_amount])
        self.positions[stock] -= short_amount

    def eval_actions(self):
        for day in range(self.days):
            if day > 0 and self.port_values[day - 1] < 0:
                print(f"BACKTEST FAILED: portfolio went negative on day {day - 1} "
                      f"(value: {self.port_values[day - 1]:.2f}). Too many short positions.")
                return None, None

            for stock in range(self.stocks):
                if self.positions[stock] >= 0 and self.actions[stock][day] > 0:
                    self._buy_long(day, stock)
                elif self.positions[stock] < 0 and self.actions[stock][day] > 0:
                    self._cover_short(day, stock)
                elif self.positions[stock] > 0 and self.actions[stock][day] < 0:
                    self._sell_long(day, stock)
                elif self.positions[stock] <= 0 and self.actions[stock][day] < 0:
                    self._open_short(day, stock)

            self.port_values[day] = self._calc_portfolio_value(day)

        pnl = self.calc_pnl()
        print(f"Final portfolio value: {self.port_values[-1]:.2f}")
        print(f"PnL: {pnl:.2f}")
        return self.port_values, pnl
