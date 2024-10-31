from typing import Tuple
from lumibot.strategies.strategy import Strategy
import numpy as np


class PriceActionStrategy(Strategy):
    """
    A trading strategy that makes decisions based on price action and market volatility.
    """

    def initialize(
        self,
        symbol: str = "AAPL",
        cash_at_risk: float = 0.5,
        sleeptime: str = "24H",
        ma_short_period: int = 20,
        ma_long_period: int = 50,
        volatility_threshold: float = 0.03,
        volatility_period: int = 14,
        volatility_factor: float = 0.1,
    ):
        self.symbol = symbol
        self.sleeptime = sleeptime
        self.cash_at_risk = cash_at_risk
        self.ma_short_period = ma_short_period
        self.ma_long_period = ma_long_period
        self.volatility_threshold = volatility_threshold
        self.volatility_period = volatility_period
        self.volatility_factor = volatility_factor
        self.last_trade = None

        print(f"Sleep time: {self.sleeptime}")
        print(f"Cash at risk: {self.cash_at_risk}")
        print(f"Short MA period: {self.ma_short_period}")
        print(f"Long MA period: {self.ma_long_period}")
        print(f"Volatility threshold: {self.volatility_threshold}")
        print(f"Volatility period: {self.volatility_period}")

    def on_trading_iteration(self):
        cash, last_price, quantity = self._position_sizing(self.symbol)
        short_ma, long_ma = self._get_moving_averages(self.symbol)

        if cash <= last_price:
            return

        # Buy signal: short MA crosses above long MA, confirming uptrend
        if short_ma > long_ma and self.last_trade != "buy":
            self._execute_buy_order(self.symbol, quantity, last_price)

        # Sell signal: short MA crosses below long MA, confirming downtrend
        elif short_ma < long_ma and self.last_trade != "sell":
            self._execute_sell_order(self.symbol, quantity, last_price)

    def _position_sizing(self, symbol) -> Tuple[float, float, int]:
        """Calculate the position size based on available cash and risk."""
        cash = self.get_cash()
        last_price = self.get_last_price(symbol)
        quantity = round(cash * self.cash_at_risk / last_price, 0)
        return cash, last_price, quantity

    def _get_moving_averages(self, symbol) -> Tuple[float, float]:
        """Calculate short and long moving averages for a symbol."""
        close_prices = self.get_historical_prices(
            symbol, self.ma_long_period, timestep="day"
        ).df["close"]

        short_ma = np.mean(close_prices[-self.ma_short_period :])
        long_ma = np.mean(close_prices)

        return short_ma, long_ma

    def _execute_buy_order(self, symbol: str, quantity: int, last_price: float):
        """Execute a buy order with dynamic stop-loss based on volatility."""
        stop_loss_price = last_price * (1 - self.volatility_factor)
        order = self.create_order(
            symbol, quantity, "buy", type="bracket", stop_loss_price=stop_loss_price
        )
        self.submit_order(order)
        self.last_trade = "buy"

    def _execute_sell_order(self, symbol: str, quantity: int, last_price: float):
        """Execute a sell order with dynamic stop-loss based on volatility."""
        stop_loss_price = last_price * (1 + self.volatility_factor)
        order = self.create_order(
            symbol, quantity, "sell", type="bracket", stop_loss_price=stop_loss_price
        )
        self.submit_order(order)
        self.last_trade = "sell"
